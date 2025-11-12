Live, real-time clipping architecture
====================================

This document explains the lightweight scaffolding added for live stream
monitoring and automatic clip creation. The implementation in this repo is a
scaffold with placeholder detection functions — replace them with production
models and a media relay in your infra.

Key components added
- `backend/realtime.py` — WebSocket endpoint and HTTP webhook for ingesting
  short live events (audio peaks, face snapshots, chat spikes). Publishes
  received events to Redis when configured.
- `backend/live_processor.py` — simple Redis pub/sub consumer that performs
  placeholder detection (audio RMS threshold, mock face-emotion) and logs
  hype moments. Intended to run as a separate worker process.
- `backend/worker.py` — RQ worker (existing) for offline clip generation jobs.

How it works (high-level)
1. The streaming relay (e.g., NGINX RTMP, SRT relay, or media server) receives
   the live stream and runs a small detector that emits events to `realtime`.
   Events may be emitted over WebSocket or posted as an HTTP webhook.
2. `realtime` publishes events to Redis (channel `live:{stream_id}`) which the
   `live_processor` subscribes to.
3. `live_processor` runs detection logic. When a hype moment is detected it
   triggers clip creation by either enqueuing a job (RQ) or calling the clip
   generator directly.

Integration points you will want to implement
- Audio frame extractor: use ffmpeg to extract short audio windows and run a
  trained classifier for laughter/cheer/kill-streak detection.
- Face emotion detection: use a small ONNX or Torch model on resized frames.
- Chat sentiment: connect to Twitch PubSub or Kick Pub/Sub to monitor chat
  message rate and sentiment spikes.
- Auto camera cuts: if multiple camera feeds are available, implement a
  short-term shot-selection model or use audio/score heuristics.

Scaling & production notes
- Use a dedicated media relay and push events to Redis Streams or Kafka for
  better durability and replay than pub/sub.
- Run separate worker pools: cheap VMs for CPU-only workloads (audio STT), and
  GPU-enabled workers for face/emotion models if necessary.
- Add monitoring (Prometheus) and structured logs; instrument events with
  timestamps and trace IDs.
- Consider privacy and consent for recording/processing faces and chat logs.

Next actions (recommended)
1. Replace placeholder detectors in `live_processor.py` with ML models (ONNX
   models for CPU inference or optimized Torch for GPU).
2. Implement a micro-service that receives frames from your streaming server
   (e.g., snapshots at 1 fps) and posts `face_snapshot` events.
3. Add a small React "Clip Dashboard" that connects to a WebSocket to receive
   detected hype events and preview clips in near real-time.
