# ETL Pipeline Documentation
## Chemical Plant Performance Monitoring Dashboard
**Version:** 1.0  
**Last Updated:** May 2026

---

## 📊 Pipeline Overview

---

## 📁 Scripts

| Script | Location | Purpose | Runtime |
|---|---|---|---|
| generate_data.py | etl/ | Generate synthetic sensor data | ~5s |
| ingest_data.py | etl/ | Load CSV into PostgreSQL | ~14s |
| etl_pipeline.py | etl/ | Clean & engineer features | ~26s |
| calculate_kpis.py | etl/ | Calculate all KPIs | ~30s |
| validation.py | notebooks/ | Validate all outputs | ~10s |

---

## 🔄 Step 1 — Data Generation
**Script:** `etl/generate_data.py`  
**Input:** None  
**Output:** `data/sensor_readings_raw.csv`

**What it does:**
- Generates 314,499 rows of synthetic sensor data
- Covers January 1 — December 31, 2025
- One reading every 5 minutes × 3 units
- Uses random walk with mean reversion
- Injects 1% fault readings

**Key parameters:**
```python
START_DATE    = datetime(2025, 1, 1)
END_DATE      = datetime(2025, 12, 31)
INTERVAL_SECS = 300   # 5 minutes
UNITS         = ['UNIT-01', 'UNIT-02', 'UNIT-03']
```

---

## 🔄 Step 2 — Data Ingestion
**Script:** `etl/ingest_data.py`  
**Input:** `data/sensor_readings_raw.csv`  
**Output:** PostgreSQL table `sensor_readings`

**What it does:**
- Reads CSV into Pandas DataFrame
- Loads into PostgreSQL in chunks of 5,000 rows
- Ingests 314,499 rows in ~14 seconds

---

## 🔄 Step 3 — ETL Pipeline
**Script:** `etl/etl_pipeline.py`  
**Input:** PostgreSQL `sensor_readings`  
**Output:** PostgreSQL `sensor_readings_processed`

**Cleaning steps:**
1. Linear interpolation for missing values (max 5 consecutive)
2. Remove physically impossible values
3. Round to 2 decimal places

**Feature engineering:**
1. Rolling averages (15-min window)
2. Rate of change (diff from previous reading)
3. Z-score anomaly flags (threshold: 2.5σ)
4. Time features (hour, day_of_week, month)

---

## 🔄 Step 4 — KPI Calculation
**Script:** `etl/calculate_kpis.py`  
**Input:** PostgreSQL `sensor_readings_processed`  
**Output:** PostgreSQL tables `kpi_oee`, `kpi_yield`, `kpi_downtime`, `kpi_defects`

**KPIs calculated:**
- OEE = Availability × Performance × Quality
- Yield % = (Actual Output / Raw Input) × 100
- MTBF = Uptime / Fault Count
- MTTR = Downtime / Fault Count
- Defect % = (Defective / Total) × 100

---

## 🗄️ Database Schema

---

## ⚙️ Environment Setup

```bash
# 1. Install Python dependencies
pip install faker numpy pandas sqlalchemy psycopg2-binary matplotlib seaborn scipy

# 2. Create PostgreSQL database
psql -U postgres
CREATE DATABASE chemical_plant;
\c chemical_plant
\i sql/schema.sql

# 3. Run pipeline in order
python etl/generate_data.py
python etl/ingest_data.py
python etl/etl_pipeline.py
python etl/calculate_kpis.py
python notebooks/validation.py
```

---

## 🔁 Re-running the Pipeline

To refresh all data from scratch:

```bash
# 1. Regenerate data
python etl/generate_data.py

# 2. Truncate and reload raw table
python etl/ingest_data.py

# 3. Re-run ETL
python etl/etl_pipeline.py

# 4. Recalculate KPIs
python etl/calculate_kpis.py

# 5. Validate
python notebooks/validation.py
```

---

## ⚠️ Common Issues

| Issue | Cause | Fix |
|---|---|---|
| `psycopg2 connection error` | Wrong password | Check DB_PASSWORD in script |
| `ModuleNotFoundError` | Missing library | Run `pip install <library>` |
| `FileNotFoundError` | Wrong directory | Run scripts from project root |
| Tableau not refreshing | Stale CSV | Re-export CSVs from database |

