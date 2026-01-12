"""
RQ Worker for Clip Generator background job processing

UPDATED January 2025:
- RQ requires Redis >= 5 or Valkey >= 7.2
- Added graceful shutdown handling
- Improved logging and error handling

Usage (PowerShell):
    $env:REDIS_URL = "redis://localhost:6379/0"
    python backend/worker.py

Usage (Bash):
    REDIS_URL="redis://localhost:6379/0" python backend/worker.py
"""
import os
import sys
import logging
import signal

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Graceful shutdown handler
def handle_shutdown(signum, frame):
    logger.info("Received shutdown signal, finishing current job...")
    sys.exit(0)

if __name__ == "__main__":
    try:
        from redis import Redis
        from rq import Worker, Queue, Connection
    except ImportError as e:
        logger.error("Missing dependencies for RQ worker. Install with: pip install redis rq")
        raise

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    try:
        redis_conn = Redis.from_url(REDIS_URL)
        # Test connection
        redis_conn.ping()
        logger.info(f"Connected to Redis at {REDIS_URL}")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        sys.exit(1)

    listen = ["default"]

    with Connection(redis_conn):
        worker = Worker(map(Queue, listen))
        logger.info(f"Starting RQ worker listening on queues: {listen}")
        worker.work(with_scheduler=True)  # Enable scheduler for delayed jobs
