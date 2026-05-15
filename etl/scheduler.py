import schedule
import time
import subprocess
import logging
from datetime import datetime
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

# ─── Logging setup ────────────────────────────────────────
os.makedirs('docs', exist_ok=True)
logging.basicConfig(
    level    = logging.INFO,
    format   = '%(asctime)s — %(levelname)s — %(message)s',
    handlers = [
        logging.FileHandler('docs/pipeline.log'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ─── Pipeline steps ───────────────────────────────────────
SCRIPTS = [
    ('ETL Pipeline',     'etl/etl_pipeline.py'),
    ('KPI Calculation',  'etl/calculate_kpis.py'),
    ('Validation',       'notebooks/validation.py'),
]

def run_pipeline():
    log.info("=" * 50)
    log.info("Pipeline started")
    log.info("=" * 50)

    all_passed = True
    for name, script in SCRIPTS:
        log.info(f"Running: {name}...")
        try:
            result = subprocess.run(
                ['python', script],
                capture_output = True,
                text           = True,
                timeout        = 300,
                env            = {**os.environ, 'PYTHONIOENCODING': 'utf-8'}
            )
            if result.returncode == 0:
                log.info(f"✅ {name} completed successfully")
            else:
                log.error(f"❌ {name} failed!")
                log.error(result.stderr)
                all_passed = False
        except subprocess.TimeoutExpired:
            log.error(f"❌ {name} timed out after 5 minutes!")
            all_passed = False
        except Exception as e:
            log.error(f"❌ {name} error: {e}")
            all_passed = False

    if all_passed:
        log.info("✅ Pipeline completed successfully!")
    else:
        log.error("⚠️ Pipeline completed with errors — check log")
    log.info("=" * 50)

# ─── Schedule ─────────────────────────────────────────────
# Run every hour
schedule.every(1).hours.do(run_pipeline)

# Also run at specific times
schedule.every().day.at("06:00").do(run_pipeline)  # Morning shift start
schedule.every().day.at("14:00").do(run_pipeline)  # Afternoon shift start
schedule.every().day.at("22:00").do(run_pipeline)  # Night shift start

log.info("Scheduler started — pipeline runs every hour")
log.info("Also scheduled at 06:00, 14:00, 22:00 daily")
log.info("Press Ctrl+C to stop")

# ─── Run once immediately on startup ──────────────────────
run_pipeline()

# ─── Keep running ─────────────────────────────────────────
while True:
    schedule.run_pending()
    time.sleep(60)