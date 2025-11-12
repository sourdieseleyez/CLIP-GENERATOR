"""
Realtime stream ingestion endpoints.

This module provides a lightweight WebSocket endpoint and HTTP hooks for
ingesting short events during a live stream (audio peaks, face snapshots,
chat spike events). It's intentionally small and uses Redis pub/sub when
available to forward events to background workers (live_processor).

Production notes:
- Use a dedicated ingest/relay (NGINX RTMP or media server) to receive RTMP/HLS
  streams and emit events (webhooks) to this service with low latency.
- For high throughput, run multiple worker processes and use Redis streams or
  message brokers (Kafka) for durable event handling.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
import os
import json
import logging
from typing import Optional
from storage import get_storage

logger = logging.getLogger(__name__)

router = APIRouter()

# Optional Redis publisher (lazy)
redis_pub = None
try:
    from redis import Redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_pub = Redis.from_url(redis_url)
except Exception:
    redis_pub = None


@router.websocket("/ws/live/{stream_id}")
async def websocket_live_stream(websocket: WebSocket, stream_id: str):
    """WebSocket endpoint to receive real-time events from a streaming relay.

    Messages are expected to be JSON with a `type` field, e.g.:
      {"type": "audio_peak", "start": 123.4, "end": 124.0, "rms": 0.8}
      {"type": "face_snapshot", "timestamp": 123.4, "image_b64": "..."}
      {"type": "chat_spike", "timestamp": 124.0, "topic": "hype", "count": 42}

    The endpoint will publish events to Redis if available, or log them.
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for stream {stream_id}")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                evt = json.loads(data)
            except Exception:
                logger.warning("Received non-json message on live websocket")
                continue

            evt["stream_id"] = stream_id
            # publish to Redis channel for background workers
            if redis_pub:
                try:
                    redis_pub.publish(f"live:{stream_id}", json.dumps(evt))
                except Exception as e:
                    logger.warning(f"Failed to publish live event: {e}")
            else:
                logger.info(f"Live event (no redis): {evt}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for stream {stream_id}")


@router.post("/hooks/live/{stream_id}")
async def live_hook(stream_id: str, payload: dict):
    """HTTP webhook for streaming relay to POST short events.

    Accepts the same JSON shape as the WebSocket messages. This is useful for
    integration with services that cannot open websockets.
    """
    payload["stream_id"] = stream_id
    if redis_pub:
        try:
            redis_pub.publish(f"live:{stream_id}", json.dumps(payload))
            return {"status": "ok", "published": True}
        except Exception as e:
            logger.error(f"Failed to publish live hook: {e}")
            raise HTTPException(status_code=500, detail="Failed to publish event")
    else:
        logger.info(f"Live hook received (no redis): {payload}")
        return {"status": "ok", "published": False}
