"""
Cron job to sync YouTube view counts daily
Run this with a scheduler (cron, Windows Task Scheduler, or cloud scheduler)

Example cron: 0 2 * * * python backend/cron_sync_views.py
(Runs daily at 2 AM)
"""

import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = os.getenv("API_URL", "http://localhost:8000")

def sync_views():
    """Trigger view sync endpoint"""
    try:
        logger.info("Starting YouTube view sync...")
        
        response = requests.post(f"{API_URL}/youtube/sync-views")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✓ Synced {data['updated_count']}/{data['total_jobs']} videos")
            return True
        else:
            logger.error(f"✗ Sync failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Sync error: {e}")
        return False

if __name__ == "__main__":
    success = sync_views()
    exit(0 if success else 1)
