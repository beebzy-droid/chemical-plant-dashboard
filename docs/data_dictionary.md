# Data Dictionary
## Chemical Plant Performance Monitoring Dashboard
**Version:** 1.0  
**Last Updated:** May 2026  
**Author:** Chemical Plant Data Team

---

## 📋 Table of Contents
1. [sensor_readings](#sensor_readings)
2. [sensor_readings_processed](#sensor_readings_processed)
3. [production_runs](#production_runs)
4. [downtime_events](#downtime_events)
5. [quality_checks](#quality_checks)
6. [energy_logs](#energy_logs)
7. [kpi_oee](#kpi_oee)
8. [kpi_yield](#kpi_yield)
9. [kpi_downtime](#kpi_downtime)
10. [kpi_defects](#kpi_defects)

---

## sensor_readings
**Description:** Raw timestamped sensor readings from all plant units.  
**Source:** Synthetic data generator (etl/generate_data.py)  
**Rows:** 314,499  
**Refresh:** Every 5 minutes

| Column | Type | Unit | Description | Example |
|---|---|---|---|---|
| id | INTEGER | — | Primary key, auto-increment | 1 |
| timestamp | TIMESTAMP | — | Date and time of reading | 2025-01-01 00:00:00 |
| unit_id | VARCHAR | — | Plant unit identifier | UNIT-01 |
| shift | VARCHAR | — | Work shift name | Morning |
| temperature | NUMERIC | °C | Reactor temperature | 185.32 |
| pressure | NUMERIC | barg | Feed pressure | 8.52 |
| flowrate | NUMERIC | kg/h | Feed flow rate | 1201.45 |
| ph | NUMERIC | pH | Reactor pH level | 7.21 |
| tank_level | NUMERIC | % | Storage tank fill level | 64.87 |
| energy_kwh | NUMERIC | kWh | Energy consumption | 451.23 |
| created_at | TIMESTAMP | — | Record insertion time | 2025-01-01 00:00:01 |

**Normal operating ranges:**
| Sensor | Min | Nominal | Max | Warn Low | Warn High |
|---|---|---|---|---|---|
| Temperature | 150°C | 185°C | 220°C | 165°C | 200°C |
| Pressure | 5 barg | 8.5 barg | 15 barg | 6.5 barg | 11 barg |
| Flow Rate | 800 kg/h | 1,200 kg/h | 1,600 kg/h | 900 kg/h | 1,450 kg/h |
| pH | 4 | 7.2 | 10 | 6.5 | 8.0 |
| Tank Level | 0% | 65% | 100% | 20% | 85% |
| Energy | 300 kWh | 450 kWh | 700 kWh | — | — |

---

## sensor_readings_processed
**Description:** Cleaned and feature-engineered sensor data.  
**Source:** ETL pipeline (etl/etl_pipeline.py)  
**Rows:** 314,499  

| Column | Type | Unit | Description | Example |
|---|---|---|---|---|
| id | INTEGER | — | Primary key | 1 |
| timestamp | TIMESTAMP | — | Date and time of reading | 2025-01-01 00:00:00 |
| unit_id | VARCHAR | — | Plant unit identifier | UNIT-01 |
| shift | VARCHAR | — | Work shift name | Morning |
| temperature | NUMERIC | °C | Cleaned temperature | 185.32 |
| pressure | NUMERIC | barg | Cleaned pressure | 8.52 |
| flowrate | NUMERIC | kg/h | Cleaned flow rate | 1201.45 |
| ph | NUMERIC | pH | Cleaned pH | 7.21 |
| tank_level | NUMERIC | % | Cleaned tank level | 64.87 |
| energy_kwh | NUMERIC | kWh | Cleaned energy | 451.23 |
| temp_rolling_avg | NUMERIC | °C | 15-min rolling average temperature | 185.10 |
| pressure_rolling_avg | NUMERIC | barg | 15-min rolling average pressure | 8.50 |
| flowrate_rolling_avg | NUMERIC | kg/h | 15-min rolling average flow rate | 1200.00 |
| temp_roc | NUMERIC | °C/reading | Temperature rate of change | 0.25 |
| pressure_roc | NUMERIC | barg/reading | Pressure rate of change | 0.01 |
| is_temp_anomaly | BOOLEAN | — | TRUE if temp > 2.5σ from mean | FALSE |
| is_pressure_anomaly | BOOLEAN | — | TRUE if pressure > 2.5σ from mean | FALSE |
| is_fault | BOOLEAN | — | TRUE if any anomaly detected | FALSE |
| hour | SMALLINT | — | Hour of reading (0-23) | 8 |
| day_of_week | SMALLINT | — | Day of week (0=Mon, 6=Sun) | 0 |
| month | SMALLINT | — | Month (1-12) | 1 |
| created_at | TIMESTAMP | — | Record insertion time | 2025-01-01 00:00:01 |

---

## kpi_oee
**Description:** Overall Equipment Effectiveness per date/unit/shift.  
**Source:** KPI calculator (etl/calculate_kpis.py)  
**Rows:** 3,279 (365 days × 3 units × 3 shifts)

| Column | Type | Unit | Description | Formula |
|---|---|---|---|---|
| id | INTEGER | — | Primary key | — |
| date | DATE | — | Date of KPI | — |
| unit_id | VARCHAR | — | Plant unit | — |
| shift | VARCHAR | — | Work shift | — |
| planned_time_min | NUMERIC | minutes | Planned shift duration | 480 min (8 hrs) |
| downtime_min | NUMERIC | minutes | Total downtime in shift | fault_count × 5 min |
| availability | NUMERIC | ratio | Equipment availability | (Planned − Downtime) / Planned |
| performance | NUMERIC | ratio | Speed efficiency | Avg Flowrate / Max Flowrate |
| quality | NUMERIC | ratio | Quality rate | Good Readings / Total Readings |
| oee | NUMERIC | ratio | Overall Equipment Effectiveness | Availability × Performance × Quality |

**Target:** OEE ≥ 0.85 (85%)  
**Actual average:** 0.714 (71.4%)

---

## kpi_yield
**Description:** Product yield per date/unit/shift.  
**Source:** KPI calculator (etl/calculate_kpis.py)  
**Rows:** 3,279

| Column | Type | Unit | Description | Formula |
|---|---|---|---|---|
| id | INTEGER | — | Primary key | — |
| date | DATE | — | Date of KPI | — |
| unit_id | VARCHAR | — | Plant unit | — |
| shift | VARCHAR | — | Work shift | — |
| raw_input | NUMERIC | kg | Total raw material input | Sum of flowrate × (5/60 hr) |
| actual_output | NUMERIC | kg | Actual good output | raw_input × efficiency × 0.92 |
| yield_pct | NUMERIC | % | Yield percentage | (actual_output / raw_input) × 100 |

**Target:** Yield ≥ 90%  
**Actual average:** 89.72%

---

## kpi_downtime
**Description:** Downtime metrics per date/unit/shift.  
**Source:** KPI calculator (etl/calculate_kpis.py)  
**Rows:** 3,279

| Column | Type | Unit | Description | Formula |
|---|---|---|---|---|
| id | INTEGER | — | Primary key | — |
| date | DATE | — | Date of KPI | — |
| unit_id | VARCHAR | — | Plant unit | — |
| shift | VARCHAR | — | Work shift | — |
| downtime_min | NUMERIC | minutes | Total downtime | fault_count × 5 min |
| fault_count | INTEGER | count | Number of fault events | — |
| mtbf_min | NUMERIC | minutes | Mean Time Between Failures | Uptime / Fault Count |
| mttr_min | NUMERIC | minutes | Mean Time To Repair | Downtime / Fault Count |

**Actual averages:** MTBF = 330.7 min, MTTR = 3.6 min

---

## kpi_defects
**Description:** Defect percentage per date/unit/shift.  
**Source:** KPI calculator (etl/calculate_kpis.py)  
**Rows:** 3,279

| Column | Type | Unit | Description | Formula |
|---|---|---|---|---|
| id | INTEGER | — | Primary key | — |
| date | DATE | — | Date of KPI | — |
| unit_id | VARCHAR | — | Plant unit | — |
| shift | VARCHAR | — | Work shift | — |
| total_readings | INTEGER | count | Total sensor readings | — |
| defect_count | INTEGER | count | Fault readings | — |
| defect_pct | NUMERIC | % | Defect percentage | (defect_count / total_readings) × 100 |

**Target:** Defect % ≤ 2%  
**Actual average:** 2.47%