"""
Background worker process for scheduled ingestion.

Run with: python -m app.ingest.worker
"""

import logging
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.ingest.pipeline import run_full_ingestion_pipeline

# Configure logging to stdout only (Railway has ephemeral filesystem)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger(__name__)


async def scheduled_ingestion_job():
    """Wrapper for scheduled ingestion that handles errors."""
    try:
        logger.info("=" * 80)
        logger.info(f"Scheduled ingestion started at {datetime.utcnow().isoformat()}")
        logger.info("=" * 80)
        
        metrics = await run_full_ingestion_pipeline()
        
        logger.info("Scheduled ingestion completed successfully")
        logger.info(f"Metrics: {metrics}")
        
    except Exception as e:
        logger.error(f"Scheduled ingestion failed: {str(e)}", exc_info=True)


async def main():
    """Main worker process."""
    logger.info("=" * 80)
    logger.info("Starting ETI Ingestion Worker")
    logger.info("=" * 80)
    logger.info("Schedule: Every 30 minutes")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 80)
    
    # Create scheduler
    scheduler = AsyncIOScheduler()
    
    # Add job: run every 30 minutes
    scheduler.add_job(
        scheduled_ingestion_job,
        trigger=IntervalTrigger(minutes=30),
        id='ingestion_job',
        name='Full Ingestion Pipeline',
        replace_existing=True,
        max_instances=1,  # Prevent overlapping runs
    )
    
    # Start scheduler
    scheduler.start()
    logger.info("Scheduler started successfully")
    
    # Run once immediately on startup
    logger.info("Running initial ingestion...")
    await scheduled_ingestion_job()
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down worker...")
        scheduler.shutdown()
        logger.info("Worker stopped")


if __name__ == "__main__":
    asyncio.run(main())