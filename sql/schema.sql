-- ─── Create Database (run this separately in psql first) ───
-- CREATE DATABASE chemical_plant;

-- ─── Sensor Readings (raw input data) ─────────────────────
CREATE TABLE IF NOT EXISTS sensor_readings (
    id           SERIAL PRIMARY KEY,
    timestamp    TIMESTAMP NOT NULL,
    unit_id      VARCHAR(10) NOT NULL,
    shift        VARCHAR(20) NOT NULL,
    temperature  NUMERIC(6,2),
    pressure     NUMERIC(6,2),
    flowrate     NUMERIC(8,2),
    ph           NUMERIC(4,2),
    tank_level   NUMERIC(5,2),
    energy_kwh   NUMERIC(8,2),
    created_at   TIMESTAMP DEFAULT NOW()
);

-- ─── Production Runs ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS production_runs (
    id              SERIAL PRIMARY KEY,
    unit_id         VARCHAR(10) NOT NULL,
    shift           VARCHAR(20) NOT NULL,
    start_time      TIMESTAMP NOT NULL,
    end_time        TIMESTAMP,
    planned_output  NUMERIC(10,2),
    actual_output   NUMERIC(10,2),
    good_units      NUMERIC(10,2),
    defective_units NUMERIC(10,2),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ─── Downtime Events ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS downtime_events (
    id           SERIAL PRIMARY KEY,
    unit_id      VARCHAR(10) NOT NULL,
    start_time   TIMESTAMP NOT NULL,
    end_time     TIMESTAMP,
    duration_min NUMERIC(8,2),
    reason       VARCHAR(100),
    category     VARCHAR(50),
    created_at   TIMESTAMP DEFAULT NOW()
);

-- ─── Quality Checks ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS quality_checks (
    id              SERIAL PRIMARY KEY,
    timestamp       TIMESTAMP NOT NULL,
    unit_id         VARCHAR(10) NOT NULL,
    shift           VARCHAR(20) NOT NULL,
    total_units     NUMERIC(10,2),
    defective_units NUMERIC(10,2),
    defect_pct      NUMERIC(5,2),
    inspector       VARCHAR(50),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ─── Energy Logs ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS energy_logs (
    id           SERIAL PRIMARY KEY,
    timestamp    TIMESTAMP NOT NULL,
    unit_id      VARCHAR(10) NOT NULL,
    equipment_id VARCHAR(20),
    energy_kwh   NUMERIC(8,2),
    created_at   TIMESTAMP DEFAULT NOW()
);

-- ─── Indexes for fast queries ─────────────────────────────
CREATE INDEX IF NOT EXISTS idx_sensor_timestamp ON sensor_readings(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_unit      ON sensor_readings(unit_id);
CREATE INDEX IF NOT EXISTS idx_downtime_unit    ON downtime_events(unit_id);
CREATE INDEX IF NOT EXISTS idx_quality_unit     ON quality_checks(unit_id);