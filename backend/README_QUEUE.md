Redis + RQ queue (optional)

This project supports optional Redis-backed job queueing using RQ. In development the server uses FastAPI BackgroundTasks. For production or heavier workloads, enable queueing with Redis and run a worker process.

Environment variables
- USE_QUEUE=true           # enable queueing
- REDIS_URL=redis://host:6379/0
- JOB_TIMEOUT=3600         # per-job timeout in seconds (optional)

Starting a worker (PowerShell)

```powershell
$env:REDIS_URL = "redis://localhost:6379/0"
$env:USE_QUEUE = "true"
python backend/worker.py
```

Enqueueing
When `USE_QUEUE=true` and Redis is reachable, the `/videos/process` endpoint will enqueue jobs to the `default` queue. Failed jobs are retried (2 retries by default).

Admin endpoints (FastAPI)
- GET /admin/queue/status  -> returns basic queue counts
- GET /admin/queue/failed  -> list failed job ids and basic info

Notes
- Install dependencies: `pip install -r backend/requirements.txt` (this now includes `redis` and `rq`).
- Worker runs in a separate process. Ensure file-system paths (uploads, temp dirs) are accessible to both the API and worker processes.
