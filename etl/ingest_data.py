import pandas as pd
from sqlalchemy import create_engine
import time

# ─── Database connection ───────────────────────────────────
DB_USER     = "postgres"
DB_PASSWORD = "admin123"    # ← change this to your password
DB_HOST     = "localhost"
DB_PORT     = "5432"
DB_NAME     = "chemical_plant"

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ─── Load CSV ─────────────────────────────────────────────
print("Loading CSV...")
df = pd.read_csv("data/sensor_readings_raw.csv", parse_dates=["timestamp"])
print(f"Loaded {len(df):,} rows")

# ─── Ingest in chunks ─────────────────────────────────────
CHUNK_SIZE = 5000
total      = len(df)
start_time = time.time()

print(f"\nIngesting into PostgreSQL in chunks of {CHUNK_SIZE:,}...")

for i in range(0, total, CHUNK_SIZE):
    chunk = df.iloc[i:i + CHUNK_SIZE]
    chunk.to_sql(
        "sensor_readings",
        engine,
        if_exists = "append",
        index     = False,
    )
    pct = min(100, round((i + CHUNK_SIZE) / total * 100))
    print(f"  Progress: {pct}% ({min(i + CHUNK_SIZE, total):,} / {total:,} rows)")

elapsed = round(time.time() - start_time, 1)
print(f"\nDone! {total:,} rows ingested in {elapsed}s")

# ─── Verify ───────────────────────────────────────────────
with engine.connect() as conn:
    from sqlalchemy import text
    result = conn.execute(text("SELECT COUNT(*) FROM sensor_readings"))
    count  = result.scalar()
    print(f"Rows in database: {count:,} ✅")