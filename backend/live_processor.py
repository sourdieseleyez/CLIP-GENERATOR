"""
Background live processor.

This module contains a simple consumer loop that listens to Redis pub/sub
events (channel: 'live:{stream_id}') and performs lightweight detection:
- audio hype detection (RMS threshold)
- face emotion detection (placeholder)
- chat sentiment spike handling

When a 'hype' event is detected the processor enqueues a clip generation job
using the existing `process_video_task_sync` or directly invokes `video_processor`.

This is intentionally a minimal scaffold — replace placeholder detection with
proper models (PyTorch/ONNX) for production.
"""
import os
import json
import logging
import base64
from time import sleep
from typing import Optional

logger = logging.getLogger(__name__)

# Optional imports
redis_conn = None
try:
    from redis import Redis
    redis_conn = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
except Exception:
    redis_conn = None

# Lazy import processor functions from main to enqueue jobs
try:
    from main import process_video_task_sync, video_processor
except Exception:
    process_video_task_sync = None
    video_processor = None


def detect_audio_hype(rms: float, threshold: float = 0.6) -> bool:
    """Simple RMS threshold-based hype detection. Replace with ML model later."""
    return float(rms) >= threshold


def detect_face_emotion(image_b64: str) -> Optional[str]:
    """Placeholder face emotion detection. Accepts base64 image bytes.

    Replace with an actual face/emotion model (e.g., ONNX, DeepFace, or a
    lightweight CNN). For now we return None or a mock label.
    """
    try:
        # decode to bytes if needed to run a model
        _ = base64.b64decode(image_b64)
        # TODO: run model here
        return "happy"
    except Exception:
        return None


def process_event(evt: dict):
    """Process a single live event dict.

    If a hype moment is detected, trigger clip generation (placeholder).
    """
    etype = evt.get("type")
    stream_id = evt.get("stream_id")
    logger.info(f"Processing live event type={etype} stream={stream_id}")

    if etype == "audio_peak":
        rms = float(evt.get("rms", 0.0))
        if detect_audio_hype(rms):
            logger.info(f"Hype detected by audio (rms={rms}) for stream {stream_id}")
            # Placeholder: enqueue a job or call clip generator
            # You might call process_video_task_sync(job_id, payload, user_email)
    elif etype == "face_snapshot":
        image_b64 = evt.get("image_b64")
        emotion = detect_face_emotion(image_b64)
        logger.info(f"Detected face emotion={emotion} for stream {stream_id}")
    elif etype == "chat_spike":
        topic = evt.get("topic")
        count = int(evt.get("count", 0))
        logger.info(f"Chat spike topic={topic} count={count} for stream {stream_id}")
        # if count exceeds threshold, treat as hype
        if count >= int(os.getenv("CHAT_HYPE_THRESHOLD", 30)):
            logger.info(f"Hype detected by chat spike for stream {stream_id}")


def run_loop(poll_interval: float = 0.1):
    """Run a blocking loop subscribing to live:* channels in Redis.

    This function is intended to be launched in a dedicated worker process.
    """
    if not redis_conn:
        logger.error("Redis not configured - live processor cannot run")
        return

    pubsub = redis_conn.pubsub(ignore_subscribe_messages=True)
    # subscribe to wildcard via pattern
    pubsub.psubscribe("live:*")
    logger.info("Live processor subscribed to live:* channels")

    try:
        for msg in pubsub.listen():
            if msg is None:
                sleep(poll_interval)
                continue
            try:
                data = msg.get("data")
                if isinstance(data, bytes):
                    payload = json.loads(data.decode("utf-8"))
                else:
                    payload = data
                process_event(payload)
            except Exception as e:
                logger.exception(f"Failed to process live message: {e}")
    finally:
        try:
            pubsub.close()
        except Exception:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_loop()
