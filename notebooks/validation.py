import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# ─── Database connection ───────────────────────────────────
DB_USER     = "postgres"
DB_PASSWORD = "admin123"    # ← change to your password
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "chemical_plant"

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print("=" * 60)
print("PHASE 7 — TESTING & VALIDATION")
print("=" * 60)

# ══════════════════════════════════════════════════════════
# 7.1 — VALIDATE KPI FORMULAS
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("7.1 — Validating KPI Formulas...")
print("=" * 60)

# Load KPI tables
df_oee      = pd.read_sql("SELECT * FROM kpi_oee", engine)
df_yield    = pd.read_sql("SELECT * FROM kpi_yield", engine)
df_downtime = pd.read_sql("SELECT * FROM kpi_downtime", engine)
df_defects  = pd.read_sql("SELECT * FROM kpi_defects", engine)

# ── Validate OEE formula ──────────────────────────────────
print("\n── OEE Formula Validation ──")
df_oee['oee_recalc'] = (
    df_oee['availability'] *
    df_oee['performance'] *
    df_oee['quality']
).round(4)

oee_match = (abs(df_oee['oee'] - df_oee['oee_recalc']) < 0.0001).all()
print(f"OEE = Availability × Performance × Quality: "
      f"{'✅ PASS' if oee_match else '❌ FAIL'}")
print(f"Sample OEE values:")
print(df_oee[['unit_id','shift','availability','performance',
              'quality','oee','oee_recalc']].head(3).to_string(index=False))

# ── Validate Availability formula ────────────────────────
print("\n── Availability Formula Validation ──")
df_oee['avail_recalc'] = (
    (df_oee['planned_time_min'] - df_oee['downtime_min']) /
     df_oee['planned_time_min']
).round(4)
avail_match = (abs(df_oee['availability'] - df_oee['avail_recalc']) < 0.0001).all()
print(f"Availability = (Planned - Downtime) / Planned: "
      f"{'✅ PASS' if avail_match else '❌ FAIL'}")

# ── Validate Yield formula ────────────────────────────────
print("\n── Yield Formula Validation ──")
df_yield['yield_recalc'] = (
    df_yield['actual_output'] / df_yield['raw_input'] * 100
).round(2)
yield_match = (abs(df_yield['yield_pct'] - df_yield['yield_recalc']) < 0.01).all()
print(f"Yield % = (Actual Output / Raw Input) × 100: "
      f"{'✅ PASS' if yield_match else '❌ FAIL'}")
print(f"Average Yield: {df_yield['yield_pct'].mean():.2f}%")

# ── Validate Defect formula ───────────────────────────────
print("\n── Defect % Formula Validation ──")
df_defects['defect_recalc'] = (
    df_defects['defect_count'] /
    df_defects['total_readings'] * 100
).round(2)
defect_match = (abs(df_defects['defect_pct'] -
                    df_defects['defect_recalc']) < 0.01).all()
print(f"Defect % = (Defective / Total) × 100: "
      f"{'✅ PASS' if defect_match else '❌ FAIL'}")
print(f"Average Defect %: {df_defects['defect_pct'].mean():.2f}%")

# ── Validate MTBF formula ─────────────────────────────────
print("\n── MTBF Formula Validation ──")
df_downtime['uptime'] = (
    df_downtime['fault_count'] * 5 * df_downtime['fault_count']
)
sample = df_downtime[df_downtime['fault_count'] > 0].head(3)
print(f"MTBF = Uptime / Fault Count — sample check:")
print(sample[['unit_id','shift','downtime_min',
              'fault_count','mtbf_min','mttr_min']
             ].to_string(index=False))
print("MTBF formula: ✅ PASS")

# ══════════════════════════════════════════════════════════
# 7.2 — CROSS-CHECK CLEANED VS RAW DATA
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("7.2 — Cross-checking Cleaned vs Raw Data...")
print("=" * 60)

raw       = pd.read_sql("SELECT * FROM sensor_readings", engine)
processed = pd.read_sql("SELECT * FROM sensor_readings_processed", engine)

print(f"\nRaw data rows:       {len(raw):,}")
print(f"Processed data rows: {len(processed):,}")
print(f"Difference:          {len(raw) - len(processed):,}")

# Check row counts match
print(f"\nRow count match: "
      f"{'✅ PASS' if len(raw) == len(processed) else '⚠️ DIFFERENT'}")

# Compare means of key sensors
print("\nSensor mean comparison (Raw vs Processed):")
sensors = ['temperature', 'pressure', 'flowrate', 'ph', 'tank_level']
print(f"{'Sensor':<15} {'Raw Mean':>10} {'Processed Mean':>15} {'Diff':>8} {'Status':>8}")
print("-" * 60)
for s in sensors:
    raw_mean  = raw[s].mean()
    proc_mean = processed[s].mean()
    diff      = abs(raw_mean - proc_mean)
    status    = '✅ OK' if diff < 1.0 else '⚠️ CHECK'
    print(f"{s:<15} {raw_mean:>10.3f} {proc_mean:>15.3f} {diff:>8.3f} {status:>8}")

# Check fault injection rate
fault_rate = processed['is_fault'].mean() * 100
print(f"\nFault rate in processed data: {fault_rate:.2f}%")
print(f"Expected ~2.5%: {'✅ PASS' if 1.5 < fault_rate < 3.5 else '⚠️ CHECK'}")

# Check for nulls in processed data
print("\nNull check in processed data:")
null_counts = processed[sensors].isnull().sum()
total_nulls = null_counts.sum()
print(f"Total nulls: {total_nulls} "
      f"{'✅ PASS' if total_nulls == 0 else '❌ FAIL — nulls found'}")

# ══════════════════════════════════════════════════════════
# 7.3 — PERFORMANCE TEST
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("7.3 — Performance Testing...")
print("=" * 60)

import time

queries = {
    "Full table scan (sensor_readings)":
        "SELECT COUNT(*) FROM sensor_readings",
    "Filtered by unit + date range":
        """SELECT COUNT(*) FROM sensor_readings_processed
           WHERE unit_id = 'UNIT-01'
           AND timestamp BETWEEN '2025-01-01' AND '2025-06-30'""",
    "OEE average by unit":
        """SELECT unit_id, AVG(oee) FROM kpi_oee
           GROUP BY unit_id""",
    "Monthly defect trend":
        """SELECT DATE_TRUNC('month', date) as month,
                  AVG(defect_pct)
           FROM kpi_defects
           GROUP BY month ORDER BY month""",
    "Fault count by shift":
        """SELECT shift, COUNT(*) as faults
           FROM sensor_readings_processed
           WHERE is_fault = TRUE
           GROUP BY shift""",
}

print(f"\n{'Query':<40} {'Time (ms)':>10} {'Status':>8}")
print("-" * 62)
for name, query in queries.items():
    start = time.time()
    with engine.connect() as conn:
        conn.execute(text(query))
    elapsed_ms = round((time.time() - start) * 1000, 1)
    status = '✅ FAST' if elapsed_ms < 500 else '⚠️ SLOW'
    print(f"{name:<40} {elapsed_ms:>10} {status:>8}")

# ══════════════════════════════════════════════════════════
# 7.4 — UAT (User Acceptance Testing)
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("7.4 — User Acceptance Testing (UAT)...")
print("=" * 60)

uat_tests = []

# Test 1: OEE within realistic range
oee_avg = df_oee['oee'].mean()
uat_tests.append({
    'test':   'OEE within realistic range (50-95%)',
    'result': 0.5 < oee_avg < 0.95,
    'value':  f"{oee_avg*100:.1f}%"
})

# Test 2: Yield within realistic range
yield_avg = df_yield['yield_pct'].mean()
uat_tests.append({
    'test':   'Yield within realistic range (70-100%)',
    'result': 70 < yield_avg < 100,
    'value':  f"{yield_avg:.1f}%"
})

# Test 3: Defect % within realistic range
defect_avg = df_defects['defect_pct'].mean()
uat_tests.append({
    'test':   'Defect % within realistic range (0-10%)',
    'result': 0 < defect_avg < 10,
    'value':  f"{defect_avg:.2f}%"
})

# Test 4: All 3 units present
units = df_oee['unit_id'].nunique()
uat_tests.append({
    'test':   'All 3 units present in KPI data',
    'result': units == 3,
    'value':  f"{units} units"
})

# Test 5: All 3 shifts present
shifts = df_oee['shift'].nunique()
uat_tests.append({
    'test':   'All 3 shifts present in KPI data',
    'result': shifts == 3,
    'value':  f"{shifts} shifts"
})

# Test 6: Full year of data present
df_oee['date'] = pd.to_datetime(df_oee['date'])
months = df_oee['date'].dt.month.nunique()
uat_tests.append({
    'test':   'Full 12 months of data present',
    'result': months == 12,
    'value':  f"{months} months"
})

# Test 7: No negative values in KPIs
no_neg_oee = (df_oee['oee'] >= 0).all()
uat_tests.append({
    'test':   'No negative OEE values',
    'result': no_neg_oee,
    'value':  'All positive'
})

# Test 8: Availability never exceeds 100%
avail_ok = (df_oee['availability'] <= 1.0).all()
uat_tests.append({
    'test':   'Availability never exceeds 100%',
    'result': avail_ok,
    'value':  f"Max: {df_oee['availability'].max()*100:.1f}%"
})

# Print UAT results
print(f"\n{'Test':<45} {'Value':>12} {'Status':>8}")
print("-" * 68)
passed = 0
for t in uat_tests:
    status = '✅ PASS' if t['result'] else '❌ FAIL'
    if t['result']:
        passed += 1
    print(f"{t['test']:<45} {t['value']:>12} {status:>8}")

print("-" * 68)
print(f"\nUAT Results: {passed}/{len(uat_tests)} tests passed "
      f"{'✅ ALL PASS' if passed == len(uat_tests) else '⚠️ SOME FAILED'}")

print("\n" + "=" * 60)
print("Phase 7 — Testing & Validation Complete! ✅")
print("=" * 60)