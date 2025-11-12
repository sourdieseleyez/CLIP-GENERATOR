"""
Chat ingestion connectors for Twitch and Kick

This module provides lightweight connectors that can listen to Twitch IRC
or Kick chat (when available) and emit simple "spike" events when chat
activity (messages/sec) exceeds a configured threshold. Connectors are
intended to run in background threads or worker processes and call a
user-provided callback with timestamped spike events.

Notes:
- Twitch: uses IRC websocket at wss://irc-ws.chat.twitch.tv:443. You need
  an OAuth token ("oauth:..."), the bot username, and a channel to join.
- Kick: Kick's chat API is not standardized here; this is a placeholder
  socket implementation that can be extended when you have an API key.

These connectors do not persist events; they call the provided callback
so the application can store/associate spikes with a running job.
"""
import threading
import time
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class TwitchChatConnector:
    def __init__(self, channel: str, oauth_token: str, username: str, on_spike: Callable[[dict], None],
                 sample_seconds: int = 5, spike_multiplier: float = 3.0):
        """Create a Twitch chat connector.

        Args:
            channel: channel name (without #)
            oauth_token: oauth token e.g. "oauth:xxxx"
            username: bot username
            on_spike: callback(event_dict) called when spike detected
            sample_seconds: window length for rate calculation
            spike_multiplier: multiplier above average to consider a spike
        """
        self.channel = channel
        self.oauth = oauth_token
        self.username = username
        self.on_spike = on_spike
        self.sample_seconds = sample_seconds
        self.spike_multiplier = spike_multiplier
        self._running = False
        self._thread = None

        # lightweight in-memory queue of timestamps (seconds) of messages
        self._timestamps = []

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self):
        # This is a placeholder implementation that simulates listening to chat.
        # Replace with a real websocket/IRC client that appends timestamps to
        # self._timestamps when messages arrive.
        logger.info(f"Starting TwitchChatConnector for channel: {self.channel}")
        try:
            while self._running:
                now = time.time()
                # Simulate random chat activity in dev; in production this would be
                # triggered by received messages.
                time.sleep(0.5)

                # Purge old timestamps
                cutoff = now - max(60, self.sample_seconds * 4)
                self._timestamps = [t for t in self._timestamps if t >= cutoff]

                # Compute current rate for the sample window
                window_cut = now - self.sample_seconds
                recent = [t for t in self._timestamps if t >= window_cut]
                rate = len(recent) / max(1.0, self.sample_seconds)

                # Compute baseline (longer window)
                baseline_cut = now - max(60, self.sample_seconds * 4)
                baseline = [t for t in self._timestamps if t >= baseline_cut]
                baseline_rate = len(baseline) / max(1.0, (now - baseline_cut))

                if baseline_rate > 0 and rate > baseline_rate * self.spike_multiplier:
                    event = {"type": "chat_spike", "channel": self.channel, "rate": rate, "baseline": baseline_rate, "ts": now}
                    try:
                        self.on_spike(event)
                    except Exception:
                        logger.exception("on_spike callback raised")

        except Exception:
            logger.exception("TwitchChatConnector failed")


class KickChatConnector:
    def __init__(self, channel: str, on_spike: Callable[[dict], None], sample_seconds: int = 5, spike_multiplier: float = 3.0):
        self.channel = channel
        self.on_spike = on_spike
        self.sample_seconds = sample_seconds
        self.spike_multiplier = spike_multiplier
        self._running = False
        self._thread = None
        self._timestamps = []

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self):
        # Placeholder: Kick chat connector should be implemented using Kick's
        # websocket/chat APIs. For now, this simulates activity similar to Twitch.
        logger.info(f"Starting KickChatConnector for channel: {self.channel}")
        try:
            import random
            while self._running:
                time.sleep(0.5)
                now = time.time()
                # simulate events
                if random.random() < 0.02:
                    self._timestamps.append(now)

                cutoff = now - max(60, self.sample_seconds * 4)
                self._timestamps = [t for t in self._timestamps if t >= cutoff]

                window_cut = now - self.sample_seconds
                recent = [t for t in self._timestamps if t >= window_cut]
                rate = len(recent) / max(1.0, self.sample_seconds)

                baseline_cut = now - max(60, self.sample_seconds * 4)
                baseline = [t for t in self._timestamps if t >= baseline_cut]
                baseline_rate = len(baseline) / max(1.0, (now - baseline_cut))

                if baseline_rate > 0 and rate > baseline_rate * self.spike_multiplier:
                    event = {"type": "chat_spike", "channel": self.channel, "rate": rate, "baseline": baseline_rate, "ts": now}
                    try:
                        self.on_spike(event)
                    except Exception:
                        logger.exception("on_spike callback raised")
        except Exception:
            logger.exception("KickChatConnector failed")
