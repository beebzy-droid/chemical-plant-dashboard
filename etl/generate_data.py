import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import os

fake = Faker()
np.random.seed(42)

# ─── Configuration ────────────────────────────────────────
START_DATE    = datetime(2025, 1, 1)
END_DATE      = datetime(2025, 12, 31)
INTERVAL_SECS = 300          # one reading every 5 minutes
UNITS         = ['UNIT-01', 'UNIT-02', 'UNIT-03']
SHIFTS        = ['Morning', 'Afternoon', 'Night']

# ─── Helper: assign shift based on hour ───────────────────
def get_shift(hour):
    if 6 <= hour < 14:  return 'Morning'
    if 14 <= hour < 22: return 'Afternoon'
    return 'Night'

# ─── Helper: random walk with mean reversion ──────────────
def random_walk(n, nominal, std, min_val, max_val):
    values = [nominal]
    for _ in range(n - 1):
        drift  = np.random.normal(0, std)
        revert = (nominal - values[-1]) * 0.05
        new    = np.clip(values[-1] + drift + revert, min_val, max_val)
        values.append(round(new, 2))
    return values

# ─── Generate timestamps ───────────────────────────────────
timestamps = []
current = START_DATE
while current <= END_DATE:
    timestamps.append(current)
    current += timedelta(seconds=INTERVAL_SECS)

n = len(timestamps)
print(f"Generating {n:,} sensor readings...")

# ─── Generate readings for each unit ──────────────────────
all_data = []

for unit in UNITS:
    # Each unit has slightly different nominal values
    offset = UNITS.index(unit) * 2

    temperature  = random_walk(n, 185 + offset, 3.0,  150, 220)
    pressure     = random_walk(n, 8.5,          0.3,  5,   15 )
    flowrate     = random_walk(n, 1200,          30,   800, 1600)
    ph           = random_walk(n, 7.2,           0.1,  4,   10 )
    tank_level   = random_walk(n, 65,            2.0,  0,   100)
    energy_kwh   = random_walk(n, 450,           15,   300, 700)

    # Inject occasional faults (1% of readings)
    fault_indices = np.random.choice(n, size=int(n * 0.01), replace=False)
    for i in fault_indices:
        temperature[i]  = round(np.random.choice([np.random.uniform(150, 158),
                                                   np.random.uniform(212, 220)]), 2)
        pressure[i]     = round(np.random.choice([np.random.uniform(5, 5.8),
                                                   np.random.uniform(12, 15)]), 2)

    for i, ts in enumerate(timestamps):
        all_data.append({
            'timestamp':   ts,
            'unit_id':     unit,
            'shift':       get_shift(ts.hour),
            'temperature': temperature[i],
            'pressure':    pressure[i],
            'flowrate':    flowrate[i],
            'ph':          ph[i],
            'tank_level':  tank_level[i],
            'energy_kwh':  energy_kwh[i],
        })

# ─── Build DataFrame ───────────────────────────────────────
df = pd.DataFrame(all_data)
df = df.sort_values('timestamp').reset_index(drop=True)

# ─── Save to CSV ───────────────────────────────────────────
os.makedirs('data', exist_ok=True)
output_path = 'data/sensor_readings_raw.csv'
df.to_csv(output_path, index=False)

print(f"Done! {len(df):,} rows saved to {output_path}")
print(f"\nSample data:")
print(df.head(5).to_string())
print(f"\nBasic stats:")
print(df[['temperature','pressure','flowrate','ph','tank_level','energy_kwh']].describe().round(2))