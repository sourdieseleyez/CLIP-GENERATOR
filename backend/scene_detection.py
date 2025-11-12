"""
Simple scene (camera cut) detection using ffmpeg.

This module provides a lightweight wrapper around ffmpeg's scene
detection filter to return a list of timestamps where scene changes
occur. It relies on the ffmpeg binary being available on PATH.

The implementation is intentionally minimal and robust: it parses
ffmpeg's stderr output for "showinfo" messages which include
pts_time for frames that passed the scene threshold.
"""
import subprocess
import re
import logging
from typing import List

logger = logging.getLogger(__name__)


_SHOWINFO_RE = re.compile(r"pts_time:([0-9\.]+)")


def detect_scenes(video_path: str, scene_threshold: float = 0.4) -> List[float]:
    """
    Run ffmpeg scene detection and return a sorted list of scene-change timestamps (in seconds).

    Args:
        video_path: path to input video file
        scene_threshold: sensitivity for scene changes (0.0-1.0). Lower = more cuts.

    Returns:
        List of timestamps (float seconds) where scene changes were detected.
    """
    timestamps = []
    # Build ffmpeg command: select frames where scene > threshold and showinfo to stderr
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-i", video_path,
        "-filter_complex", f"select='gt(scene,{scene_threshold})',showinfo",
        "-f", "null",
        "-"
    ]

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _, stderr = proc.communicate(timeout=120)

        # Parse pts_time from showinfo lines
        for line in stderr.splitlines():
            m = _SHOWINFO_RE.search(line)
            if m:
                try:
                    t = float(m.group(1))
                    timestamps.append(t)
                except Exception:
                    continue
    except FileNotFoundError:
        logger.warning("ffmpeg not found in PATH; scene detection disabled")
    except subprocess.TimeoutExpired:
        proc.kill()
        logger.warning("ffmpeg scene detection timed out")
    except Exception as e:
        logger.exception(f"Scene detection failed: {e}")

    timestamps = sorted(set(timestamps))
    return timestamps
