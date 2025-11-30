"""
Lightweight emotion and audio-event detector helpers.

This module provides inexpensive heuristics to detect "hype" moments
from audio (sustained RMS spikes) and an optional face emotion analysis
hook that uses DeepFace if installed. These are intentionally best-effort
and optional (they won't crash if the optional deps are missing).
"""
import logging
from typing import List, Dict
import os

logger = logging.getLogger(__name__)

try:
    import numpy as np
except Exception:
    np = None

# Try both relative and absolute imports for flexibility
try:
    from ffmpeg_helpers import extract_audio_to_wav, compute_rms_windows
except ImportError:
    try:
        from .ffmpeg_helpers import extract_audio_to_wav, compute_rms_windows
    except ImportError:
        # If ffmpeg_helpers isn't available, we'll provide graceful fallbacks.
        extract_audio_to_wav = None
        compute_rms_windows = None

try:
    # Optional: DeepFace for face emotion recognition
    from deepface import DeepFace
except Exception:
    DeepFace = None


def detect_audio_hype_events(video_path: str, window_size_sec: float = 0.5, rms_multiplier: float = 2.0) -> List[Dict]:
    """
    Heuristic detector for "hype" audio events (laughter, cheering, shouts) based on RMS spikes.

    Returns a list of events: {start, end, rms, score}
    """
    events = []
    if np is None or compute_rms_windows is None or extract_audio_to_wav is None:
        logger.debug("NumPy or ffmpeg_helpers not available — skipping audio hype detection")
        return events

    try:
        wav = extract_audio_to_wav(video_path)
        windows = compute_rms_windows(wav, window_size_sec=window_size_sec)

        if not windows:
            return events

        rms_vals = [w['rms'] for w in windows]
        mean_rms = float(np.mean(rms_vals))
        std_rms = float(np.std(rms_vals))

        # detect windows where rms is significantly above mean
        threshold = mean_rms + rms_multiplier * max(std_rms, 1e-6)

        current = None
        for w in windows:
            if w['rms'] >= threshold:
                if current is None:
                    current = {"start": w['start'], "end": w['end'], "rms_vals": [w['rms']]}
                else:
                    current['end'] = w['end']
                    current['rms_vals'].append(w['rms'])
            else:
                if current is not None:
                    avg_rms = float(sum(current['rms_vals']) / len(current['rms_vals']))
                    events.append({
                        "start": current['start'],
                        "end": current['end'],
                        "rms": avg_rms,
                        "score": float((avg_rms - mean_rms) / (std_rms + 1e-6))
                    })
                    current = None

        if current is not None:
            avg_rms = float(sum(current['rms_vals']) / len(current['rms_vals']))
            events.append({
                "start": current['start'],
                "end": current['end'],
                "rms": avg_rms,
                "score": float((avg_rms - mean_rms) / (std_rms + 1e-6))
            })

    except Exception as e:
        logger.exception(f"Audio hype detection failed: {e}")

    return events


def analyze_face_emotions(video_path: str, timestamps: List[float], target_face: bool = False) -> List[Dict]:
    """
    For the provided timestamps, extract a single frame near each timestamp
    and run face emotion analysis (if DeepFace is installed). Returns a list
    of {timestamp, emotions: {happy:0.9,...}, dominant_emotion}

    This function is optional and will return [] when DeepFace is not available.
    """
    results = []
    if DeepFace is None:
        logger.debug("DeepFace not installed — skipping face emotion analysis")
        return results

    # Use ffmpeg to extract frames near timestamps
    for t in timestamps:
        try:
            # Create a temporary image file
            import tempfile
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            tmp.close()
            # Use ffmpeg to capture the frame at time t
            cmd = f"ffmpeg -y -hide_banner -loglevel error -ss {t} -i \"{video_path}\" -frames:v 1 \"{tmp.name}\""
            os.system(cmd)

            analysis = DeepFace.analyze(img_path=tmp.name, actions=['emotion'], enforce_detection=False)
            emotions = analysis.get('emotion') if isinstance(analysis, dict) else {}
            dominant = analysis.get('dominant_emotion') if isinstance(analysis, dict) else None
            results.append({"timestamp": t, "emotions": emotions, "dominant": dominant})

            try:
                os.remove(tmp.name)
            except Exception:
                pass
        except Exception as e:
            logger.exception(f"Face emotion analysis failed for t={t}: {e}")

    return results
