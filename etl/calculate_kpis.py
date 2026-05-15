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

# ─── Load processed data ───────────────────────────────────
print("Loading processed data...")
df = pd.read_sql(
    "SELECT * FROM sensor_readings_processed ORDER BY unit_id, timestamp",
    engine
)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date']      = df['timestamp'].dt.date
print(f"Loaded {len(df):,} rows")

# ══════════════════════════════════════════════════════════
# 4.1 — OEE CALCULATION
# OEE = Availability × Performance × Quality
# ══════════════════════════════════════════════════════════
print("\n" + "="*55)
print("4.1 — Calculating OEE...")
print("="*55)

PLANNED_TIME_MIN  = 480   # 8-hour shift = 480 minutes
MAX_FLOWRATE      = 1600  # theoretical max kg/h

oee_records = []

for (date, unit, shift), group in df.groupby(['date', 'unit_id', 'shift']):
    # Availability = (Planned - Downtime) / Planned
    fault_readings  = group['is_fault'].sum()
    downtime_min    = round(fault_readings * 5, 2)  # each reading = 5 mins
    availability    = round(
        max(0, (PLANNED_TIME_MIN - downtime_min) / PLANNED_TIME_MIN), 4
    )

    # Performance = Actual Flowrate / Max Flowrate
    avg_flowrate = group['flowrate'].mean()
    performance  = round(min(1.0, avg_flowrate / MAX_FLOWRATE), 4)

    # Quality = Non-fault readings / Total readings
    total    = len(group)
    good     = total - fault_readings
    quality  = round(good / total, 4) if total > 0 else 0

    # OEE
    oee = round(availability * performance * quality, 4)

    oee_records.append({
        'date':             date,
        'unit_id':          unit,
        'shift':            shift,
        'planned_time_min': PLANNED_TIME_MIN,
        'downtime_min':     downtime_min,
        'availability':     availability,
        'performance':      performance,
        'quality':          quality,
        'oee':              oee,
    })

df_oee = pd.DataFrame(oee_records)
print(f"OEE records calculated: {len(df_oee):,}")
print(f"Average OEE: {df_oee['oee'].mean()*100:.1f}%")
print(f"Average Availability: {df_oee['availability'].mean()*100:.1f}%")
print(f"Average Performance:  {df_oee['performance'].mean()*100:.1f}%")
print(f"Average Quality:      {df_oee['quality'].mean()*100:.1f}%")

# ══════════════════════════════════════════════════════════
# 4.2 — YIELD CALCULATION
# Yield % = (Actual Output / Raw Input) × 100
# ══════════════════════════════════════════════════════════
print("\n" + "="*55)
print("4.2 — Calculating Yield...")
print("="*55)

yield_records = []

for (date, unit, shift), group in df.groupby(['date', 'unit_id', 'shift']):
    # Raw input = sum of flowrate readings × time interval (5 min = 5/60 hr)
    raw_input     = round(group['flowrate'].sum() * (5/60), 2)

    # Actual output = raw input × efficiency factor (non-fault readings)
    fault_pct     = group['is_fault'].mean()
    efficiency    = 1 - fault_pct
    actual_output = round(raw_input * efficiency * 0.92, 2)

    # Yield %
    yield_pct = round((actual_output / raw_input * 100), 2) if raw_input > 0 else 0

    yield_records.append({
        'date':          date,
        'unit_id':       unit,
        'shift':         shift,
        'raw_input':     raw_input,
        'actual_output': actual_output,
        'yield_pct':     yield_pct,
    })

df_yield = pd.DataFrame(yield_records)
print(f"Yield records calculated: {len(df_yield):,}")
print(f"Average Yield: {df_yield['yield_pct'].mean():.1f}%")

# ══════════════════════════════════════════════════════════
# 4.3 — DOWNTIME METRICS (MTBF, MTTR)
# ══════════════════════════════════════════════════════════
print("\n" + "="*55)
print("4.3 — Calculating Downtime Metrics...")
print("="*55)

downtime_records = []

for (date, unit, shift), group in df.groupby(['date', 'unit_id', 'shift']):
    group       = group.sort_values('timestamp').reset_index(drop=True)
    fault_count = int(group['is_fault'].sum())
    downtime_min= round(fault_count * 5, 2)

    total_min   = len(group) * 5
    uptime_min  = total_min - downtime_min

    # MTBF = Uptime / Number of fault events
    mtbf = round(uptime_min / fault_count, 2) if fault_count > 0 else uptime_min

    # MTTR = Downtime / Number of fault events
    mttr = round(downtime_min / fault_count, 2) if fault_count > 0 else 0

    downtime_records.append({
        'date':         date,
        'unit_id':      unit,
        'shift':        shift,
        'downtime_min': downtime_min,
        'fault_count':  fault_count,
        'mtbf_min':     mtbf,
        'mttr_min':     mttr,
    })

df_downtime = pd.DataFrame(downtime_records)
print(f"Downtime records calculated: {len(df_downtime):,}")
print(f"Average Downtime: {df_downtime['downtime_min'].mean():.1f} min/shift")
print(f"Average MTBF:     {df_downtime['mtbf_min'].mean():.1f} min")
print(f"Average MTTR:     {df_downtime['mttr_min'].mean():.1f} min")

# ══════════════════════════════════════════════════════════
# 4.4 — DEFECT % CALCULATION
# ══════════════════════════════════════════════════════════
print("\n" + "="*55)
print("4.4 — Calculating Defect %...")
print("="*55)

defect_records = []

for (date, unit, shift), group in df.groupby(['date', 'unit_id', 'shift']):
    total_readings = len(group)
    defect_count   = int(group['is_fault'].sum())
    defect_pct     = round(defect_count / total_readings * 100, 2) \
                     if total_readings > 0 else 0

    defect_records.append({
        'date':           date,
        'unit_id':        unit,
        'shift':          shift,
        'total_readings': total_readings,
        'defect_count':   defect_count,
        'defect_pct':     defect_pct,
    })

df_defects = pd.DataFrame(defect_records)
print(f"Defect records calculated: {len(df_defects):,}")
print(f"Average Defect %: {df_defects['defect_pct'].mean():.2f}%")

# ══════════════════════════════════════════════════════════
# LOAD ALL KPIs TO PostgreSQL
# ══════════════════════════════════════════════════════════
print("\n" + "="*55)
print("Loading KPIs to PostgreSQL...")
print("="*55)

start_time = time.time()

kpi_tables = {
    'kpi_oee':      df_oee,
    'kpi_yield':    df_yield,
    'kpi_downtime': df_downtime,
    'kpi_defects':  df_defects,
}

with engine.connect() as conn:
    for table in kpi_tables:
        conn.execute(text(f"TRUNCATE TABLE {table}"))
        conn.commit()

for table_name, df_kpi in kpi_tables.items():
    df_kpi.to_sql(
        table_name, engine,
        if_exists = 'append',
        index     = False,
    )
    print(f"  ✅ {table_name}: {len(df_kpi):,} rows loaded")

elapsed = round(time.time() - start_time, 1)
print(f"\nAll KPIs loaded in {elapsed}s ✅")

# ─── Save KPI CSVs ─────────────────────────────────────────
df_oee.to_csv('data/kpi_oee.csv', index=False)
df_yield.to_csv('data/kpi_yield.csv', index=False)
df_downtime.to_csv('data/kpi_downtime.csv', index=False)
df_defects.to_csv('data/kpi_defects.csv', index=False)
print("KPI CSVs saved to data/ folder ✅")