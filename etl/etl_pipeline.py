import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import time

# ─── Database connection ───────────────────────────────────
DB_USER     = "postgres"
DB_PASSWORD = "admin123"    # ← change to your password
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "chemical_plant"

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ══════════════════════════════════════════════════════════
# STEP 3.1 — EXTRACT
# ══════════════════════════════════════════════════════════
print("=" * 55)
print("STEP 3.1 — Extracting data from PostgreSQL...")
print("=" * 55)

df = pd.read_sql(
    "SELECT * FROM sensor_readings ORDER BY unit_id, timestamp",
    engine
)
print(f"Extracted {len(df):,} rows")
print(f"Columns: {list(df.columns)}")
print(f"Date range: {df['timestamp'].min()} → {df['timestamp'].max()}")

# ══════════════════════════════════════════════════════════
# STEP 3.2 — TRANSFORM (Clean)
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("STEP 3.2 — Cleaning data...")
print("=" * 55)

# 1. Check for missing values
print(f"\nMissing values before cleaning:")
print(df.isnull().sum())

# 2. Interpolate missing sensor values
sensor_cols = ['temperature', 'pressure', 'flowrate', 'ph', 'tank_level', 'energy_kwh']
df[sensor_cols] = df[sensor_cols].interpolate(method='linear', limit=5)

# 3. Remove physical impossibilities (outside absolute limits)
before = len(df)
df = df[
    (df['temperature'].between(140, 230)) &
    (df['pressure'].between(3, 17))       &
    (df['flowrate'].between(700, 1700))   &
    (df['ph'].between(3, 11))             &
    (df['tank_level'].between(0, 100))    &
    (df['energy_kwh'].between(200, 800))
]
removed = before - len(df)
print(f"\nRows removed as physically impossible: {removed:,}")
print(f"Rows remaining: {len(df):,}")

# 4. Round all sensor values to 2 decimal places
df[sensor_cols] = df[sensor_cols].round(2)

print("Cleaning done ✅")

# ══════════════════════════════════════════════════════════
# STEP 3.3 — FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("STEP 3.3 — Engineering features...")
print("=" * 55)

# Process each unit separately so rolling averages don't bleed across units
units = df['unit_id'].unique()
processed_units = []

for unit in units:
    print(f"\n  Processing {unit}...")
    u = df[df['unit_id'] == unit].copy()
    u = u.sort_values('timestamp').reset_index(drop=True)

    # Rolling averages (15-min window = 3 readings at 5-min intervals)
    window = 3
    u['temp_rolling_avg']     = u['temperature'].rolling(window, min_periods=1).mean().round(2)
    u['pressure_rolling_avg'] = u['pressure'].rolling(window, min_periods=1).mean().round(2)
    u['flowrate_rolling_avg'] = u['flowrate'].rolling(window, min_periods=1).mean().round(2)

    # Rate of change (difference from previous reading)
    u['temp_roc']     = u['temperature'].diff().round(4)
    u['pressure_roc'] = u['pressure'].diff().round(4)

    # Anomaly flags using Z-score (flag if > 2.5 std from mean)
    temp_mean     = u['temperature'].mean()
    temp_std      = u['temperature'].std()
    pressure_mean = u['pressure'].mean()
    pressure_std  = u['pressure'].std()

    u['is_temp_anomaly']     = (abs(u['temperature'] - temp_mean) > 2.5 * temp_std)
    u['is_pressure_anomaly'] = (abs(u['pressure'] - pressure_mean) > 2.5 * pressure_std)

    # Fault flag (temp or pressure anomaly)
    u['is_fault'] = u['is_temp_anomaly'] | u['is_pressure_anomaly']

    # Time features
    u['hour']        = u['timestamp'].dt.hour
    u['day_of_week'] = u['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
    u['month']       = u['timestamp'].dt.month

    processed_units.append(u)
    print(f"    Anomalies flagged: {u['is_fault'].sum():,} "
          f"({u['is_fault'].mean()*100:.1f}%)")

df_processed = pd.concat(processed_units).reset_index(drop=True)

# Fill NaN in roc columns (first row of each unit)
df_processed[['temp_roc', 'pressure_roc']] = \
    df_processed[['temp_roc', 'pressure_roc']].fillna(0)

print(f"\nFeature engineering done ✅")
print(f"Final shape: {df_processed.shape}")
print(f"New columns: temp_rolling_avg, pressure_rolling_avg, "
      f"flowrate_rolling_avg, temp_roc, pressure_roc, "
      f"is_temp_anomaly, is_pressure_anomaly, is_fault, "
      f"hour, day_of_week, month")

# ══════════════════════════════════════════════════════════
# STEP 3.4 — LOAD
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("STEP 3.4 — Loading processed data to PostgreSQL...")
print("=" * 55)

# Select only columns that match our processed table
cols = [
    'timestamp', 'unit_id', 'shift',
    'temperature', 'pressure', 'flowrate', 'ph', 'tank_level', 'energy_kwh',
    'temp_rolling_avg', 'pressure_rolling_avg', 'flowrate_rolling_avg',
    'temp_roc', 'pressure_roc',
    'is_temp_anomaly', 'is_pressure_anomaly', 'is_fault',
    'hour', 'day_of_week', 'month'
]
df_final = df_processed[cols]

# Clear existing processed data
with engine.connect() as conn:
    conn.execute(text("TRUNCATE TABLE sensor_readings_processed"))
    conn.commit()

# Load in chunks
CHUNK_SIZE = 5000
total      = len(df_final)
start_time = time.time()

for i in range(0, total, CHUNK_SIZE):
    chunk = df_final.iloc[i:i + CHUNK_SIZE]
    chunk.to_sql(
        "sensor_readings_processed",
        engine,
        if_exists = "append",
        index     = False,
    )
    pct = min(100, round((i + CHUNK_SIZE) / total * 100))
    print(f"  Progress: {pct}% ({min(i+CHUNK_SIZE, total):,} / {total:,})")

elapsed = round(time.time() - start_time, 1)

# ─── Final verification ────────────────────────────────────
with engine.connect() as conn:
    count = conn.execute(
        text("SELECT COUNT(*) FROM sensor_readings_processed")
    ).scalar()
    faults = conn.execute(
        text("SELECT COUNT(*) FROM sensor_readings_processed WHERE is_fault = TRUE")
    ).scalar()

print(f"\nDone in {elapsed}s ✅")
print(f"Rows loaded:    {count:,}")
print(f"Faults flagged: {faults:,} ({round(faults/count*100, 1)}%)")

# ─── Save processed CSV too ────────────────────────────────
df_final.to_csv("data/sensor_readings_processed.csv", index=False)
print(f"Processed CSV saved to data/sensor_readings_processed.csv ✅")