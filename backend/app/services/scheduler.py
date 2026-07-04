from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def fetch_civic_updates():
    """
    Simulates fetching daily updates from a government API.
    In a real app, this would hit an external service and update the vector DB.
    """
    try:
        logger.info("Running daily civic update fetcher...")
        # Simulate network fetch from govt sites
        updates = [
            {"title": "New Aadhaar Linking Deadline", "date": datetime.now().isoformat(), "details": "The deadline has been extended to next month."},
            {"title": "Passport Processing Changes", "date": datetime.now().isoformat(), "details": "Walk-in appointments now available."}
        ]
        
        # Save to local file
        updates_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "procedure_updates.json")
        os.makedirs(os.path.dirname(updates_path), exist_ok=True)
        
        with open(updates_path, "w") as f:
            json.dump({"updates": updates, "last_checked": datetime.now().isoformat()}, f)
            
        logger.info("Successfully fetched and saved civic updates.")
    except Exception as e:
        logger.error(f"Failed to fetch civic updates: {e}")

def start_scheduler():
    scheduler.add_job(
        fetch_civic_updates,
        CronTrigger(hour=0, minute=0), # Run daily at midnight
        id="daily_civic_updates",
        replace_existing=True
    )
    # Also run immediately once on startup
    scheduler.add_job(fetch_civic_updates, id="startup_civic_updates")
    
    scheduler.start()
    logger.info("APScheduler started successfully.")

def shutdown_scheduler():
    scheduler.shutdown()
    logger.info("APScheduler shut down.")
