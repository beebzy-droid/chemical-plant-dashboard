# Chemical Plant Performance Monitoring Dashboard

## Overview
Real-time monitoring dashboard for a chemical plant (Phenol Synthesis Unit).
Tracks process KPIs, sensor data, downtime, quality, and energy consumption.

## KPI Targets
- OEE ≥ 85%
- Yield ≥ 90%
- Defect % ≤ 2%
- Downtime ≤ 5% of planned time
- Energy per ton ≤ 3.0 GJ/t

## Tech Stack
- Data Generation: Python + NumPy + Faker
- Database: PostgreSQL 18
- ETL: Python + Pandas + SQLAlchemy
- Visualization: Power BI
- Version Control: Git

## Folder Structure
- data/       → Raw & processed datasets
- sql/        → Schema definitions & queries
- etl/        → Python ETL scripts
- notebooks/  → EDA & analysis
- dashboard/  → Power BI files
- docs/       → Documentation