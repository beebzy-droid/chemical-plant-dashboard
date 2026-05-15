import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sqlalchemy import create_engine
import os

# ─── Database connection ───────────────────────────────────
DB_USER     = "postgres"
DB_PASSWORD = "admin123"    # ← change to your password
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "chemical_plant"

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ─── Load data ─────────────────────────────────────────────
print("Loading data...")
df = pd.read_sql(
    "SELECT * FROM sensor_readings_processed", engine
)
df['timestamp'] = pd.to_datetime(df['timestamp'])
print(f"Loaded {len(df):,} rows")

os.makedirs('docs', exist_ok=True)

# ══════════════════════════════════════════════════════════
# 5.1 — CORRELATION ANALYSIS
# ══════════════════════════════════════════════════════════
print("\n" + "="*55)
print("5.1 — Correlation Analysis...")
print("="*55)

sensor_cols = ['temperature', 'pressure', 'flowrate',
               'ph', 'tank_level', 'energy_kwh']

# Correlation of each sensor with is_fault
df['is_fault_int'] = df['is_fault'].astype(int)
correlations = df[sensor_cols + ['is_fault_int']].corr()['is_fault_int'] \
                 .drop('is_fault_int').sort_values(key=abs, ascending=False)

print("\nCorrelation with faults:")
for sensor, corr in correlations.items():
    bar = '█' * int(abs(corr) * 50)
    print(f"  {sensor:<15} {corr:+.4f}  {bar}")

# Plot correlation heatmap
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Correlation Analysis — Chemical Plant', fontsize=14, fontweight='bold')

# Heatmap
corr_matrix = df[sensor_cols].corr()
sns.heatmap(
    corr_matrix, annot=True, fmt='.2f', cmap='RdYlGn',
    ax=axes[0], square=True, linewidths=0.5
)
axes[0].set_title('Sensor Correlation Matrix')

# Bar chart — correlation with faults
colors = ['#ef4444' if c > 0 else '#10b981' for c in correlations]
axes[1].barh(correlations.index, correlations.values, color=colors)
axes[1].axvline(x=0, color='white', linewidth=0.5)
axes[1].set_title('Sensor Correlation with Faults')
axes[1].set_xlabel('Correlation Coefficient')
axes[1].set_facecolor('#111827')
fig.patch.set_facecolor('#0a0e14')
for ax in axes:
    ax.set_facecolor('#111827')
    ax.tick_params(colors='white')
    ax.title.set_color('white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')

plt.tight_layout()
plt.savefig('docs/correlation_analysis.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved: docs/correlation_analysis.png ✅")

# ══════════════════════════════════════════════════════════
# 5.2 — STATISTICAL PROCESS CONTROL (SPC)
# ══════════════════════════════════════════════════════════
print("\n" + "="*55)
print("5.2 — Statistical Process Control (SPC)...")
print("="*55)

spc_sensors = ['temperature', 'pressure', 'ph']
unit        = 'UNIT-01'
df_unit     = df[df['unit_id'] == unit].sort_values('timestamp').head(500)

fig, axes = plt.subplots(3, 1, figsize=(16, 12))
fig.suptitle(f'SPC Control Charts — {unit}', fontsize=14, fontweight='bold',
             color='white')
fig.patch.set_facecolor('#0a0e14')

for idx, sensor in enumerate(spc_sensors):
    ax     = axes[idx]
    values = df_unit[sensor].values
    mean   = np.mean(values)
    std    = np.std(values)
    ucl    = mean + 3 * std   # Upper Control Limit
    lcl    = mean - 3 * std   # Lower Control Limit
    uwl    = mean + 2 * std   # Upper Warning Limit
    lwl    = mean - 2 * std   # Lower Warning Limit

    # Identify out-of-control points
    ooc = (values > ucl) | (values < lcl)

    ax.plot(values, color='#f59e0b', linewidth=0.8, label=sensor)
    ax.scatter(np.where(ooc)[0], values[ooc],
               color='#ef4444', s=20, zorder=5, label='Out of Control')
    ax.axhline(mean, color='#10b981',  linewidth=1.5, linestyle='-',  label=f'Mean: {mean:.2f}')
    ax.axhline(ucl,  color='#ef4444',  linewidth=1,   linestyle='--', label=f'UCL: {ucl:.2f}')
    ax.axhline(lcl,  color='#ef4444',  linewidth=1,   linestyle='--', label=f'LCL: {lcl:.2f}')
    ax.axhline(uwl,  color='#f59e0b',  linewidth=0.8, linestyle=':',  label=f'UWL: {uwl:.2f}')
    ax.axhline(lwl,  color='#f59e0b',  linewidth=0.8, linestyle=':',  label=f'LWL: {lwl:.2f}')
    ax.fill_between(range(len(values)), lwl, uwl, alpha=0.05, color='#10b981')

    ooc_count = ooc.sum()
    ax.set_title(f'{sensor.upper()} — {ooc_count} out-of-control points '
                 f'({ooc_count/len(values)*100:.1f}%)', color='white')
    ax.set_facecolor('#111827')
    ax.tick_params(colors='white')
    ax.legend(loc='upper right', fontsize=7, facecolor='#1f2937',
              labelcolor='white', ncol=3)
    ax.spines['bottom'].set_color('#1f2937')
    ax.spines['top'].set_color('#1f2937')
    ax.spines['left'].set_color('#1f2937')
    ax.spines['right'].set_color('#1f2937')

    print(f"  {sensor:<15} Mean: {mean:.2f}  UCL: {ucl:.2f}  "
          f"LCL: {lcl:.2f}  OOC: {ooc_count}")

plt.tight_layout()
plt.savefig('docs/spc_charts.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved: docs/spc_charts.png ✅")

# ══════════════════════════════════════════════════════════
# 5.3 — PARETO ANALYSIS
# ══════════════════════════════════════════════════════════
print("\n" + "="*55)
print("5.3 — Pareto Analysis...")
print("="*55)

# Categorize fault causes based on which sensor triggered it
def categorize_fault(row):
    if not row['is_fault']:
        return None
    if row['is_temp_anomaly'] and row['is_pressure_anomaly']:
        return 'Temp + Pressure Anomaly'
    if row['is_temp_anomaly']:
        return 'Temperature Anomaly'
    if row['is_pressure_anomaly']:
        return 'Pressure Anomaly'
    return 'Other'

df['fault_cause'] = df.apply(categorize_fault, axis=1)
fault_counts = df[df['is_fault']]['fault_cause'].value_counts()
fault_pct    = fault_counts / fault_counts.sum() * 100
cumulative   = fault_pct.cumsum()

print("\nFault causes:")
for cause, count in fault_counts.items():
    print(f"  {cause:<30} {count:,} ({fault_pct[cause]:.1f}%)")

fig, ax1 = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor('#0a0e14')
ax1.set_facecolor('#111827')

bars = ax1.bar(fault_counts.index, fault_counts.values,
               color=['#ef4444','#f59e0b','#3b82f6','#10b981'])
ax1.set_ylabel('Fault Count', color='white')
ax1.tick_params(colors='white')
ax1.set_title('Pareto Chart — Fault Causes', color='white', fontsize=14)

ax2 = ax1.twinx()
ax2.plot(fault_counts.index, cumulative.values,
         color='white', marker='o', linewidth=2, label='Cumulative %')
ax2.axhline(80, color='#f59e0b', linestyle='--', linewidth=1, label='80% line')
ax2.set_ylabel('Cumulative %', color='white')
ax2.tick_params(colors='white')
ax2.set_ylim(0, 110)
ax2.legend(facecolor='#1f2937', labelcolor='white')
ax2.set_facecolor('#111827')

for spine in ax1.spines.values():
    spine.set_color('#1f2937')

plt.tight_layout()
plt.savefig('docs/pareto_analysis.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved: docs/pareto_analysis.png ✅")

# ══════════════════════════════════════════════════════════
# 5.4 — ANOMALY DETECTION SUMMARY
# ══════════════════════════════════════════════════════════
print("\n" + "="*55)
print("5.4 — Anomaly Detection Summary...")
print("="*55)

anomaly_by_unit = df.groupby('unit_id').agg(
    total_readings  = ('is_fault', 'count'),
    total_faults    = ('is_fault', 'sum'),
    temp_anomalies  = ('is_temp_anomaly', 'sum'),
    pressure_anomalies = ('is_pressure_anomaly', 'sum'),
).reset_index()
anomaly_by_unit['fault_pct'] = \
    (anomaly_by_unit['total_faults'] / anomaly_by_unit['total_readings'] * 100).round(2)

print("\nAnomaly summary by unit:")
print(anomaly_by_unit.to_string(index=False))

# Monthly fault trend
df['month'] = df['timestamp'].dt.month
monthly_faults = df.groupby('month')['is_fault'].mean() * 100

fig, axes = plt.subplots(1, 2, figsize=(16, 5))
fig.patch.set_facecolor('#0a0e14')
fig.suptitle('Anomaly Detection Summary', color='white', fontsize=14)

# Anomalies by unit
x = np.arange(len(anomaly_by_unit))
w = 0.35
axes[0].bar(x - w/2, anomaly_by_unit['temp_anomalies'],
            w, label='Temp Anomalies',     color='#ef4444')
axes[0].bar(x + w/2, anomaly_by_unit['pressure_anomalies'],
            w, label='Pressure Anomalies', color='#f59e0b')
axes[0].set_xticks(x)
axes[0].set_xticklabels(anomaly_by_unit['unit_id'])
axes[0].set_title('Anomalies by Unit', color='white')
axes[0].legend(facecolor='#1f2937', labelcolor='white')

# Monthly fault trend
months = ['Jan','Feb','Mar','Apr','May','Jun',
          'Jul','Aug','Sep','Oct','Nov','Dec']
axes[1].plot(months, monthly_faults.values,
             color='#f59e0b', marker='o', linewidth=2)
axes[1].axhline(monthly_faults.mean(), color='#10b981',
                linestyle='--', label=f'Avg: {monthly_faults.mean():.2f}%')
axes[1].set_title('Monthly Fault Rate Trend', color='white')
axes[1].legend(facecolor='#1f2937', labelcolor='white')

for ax in axes:
    ax.set_facecolor('#111827')
    ax.tick_params(colors='white')
    ax.title.set_color('white')
    for spine in ax.spines.values():
        spine.set_color('#1f2937')

plt.tight_layout()
plt.savefig('docs/anomaly_summary.png', dpi=150, bbox_inches='tight')
plt.show()
print("Saved: docs/anomaly_summary.png ✅")

print("\n" + "="*55)
print("Phase 5 Complete! ✅")
print("Charts saved to docs/ folder")
print("="*55)