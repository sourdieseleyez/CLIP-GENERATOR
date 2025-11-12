"""
Simple RQ worker entrypoint for Clip Generator.

Usage (PowerShell):
    $env:REDIS_URL = "redis://localhost:6379/0"
    python backend/worker.py

This script connects to Redis and starts an RQ worker for the "default" queue.
"""
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

if __name__ == "__main__":
    try:
        from redis import Redis
        from rq import Worker, Queue, Connection
    except Exception as e:
        logger.error("Missing dependencies for RQ worker. Please install 'redis' and 'rq'.")
        raise

    redis_conn = Redis.from_url(REDIS_URL)
    listen = ["default"]

    with Connection(redis_conn):
        worker = Worker(map(Queue, listen))
        logger.info(f"Starting RQ worker listening on queues: {listen}")
        worker.work()
