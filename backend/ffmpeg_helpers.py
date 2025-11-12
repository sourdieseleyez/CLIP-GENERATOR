import subprocess
import tempfile
import os
import wave
import math
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


def extract_audio_to_wav(video_path: str, out_wav: Optional[str] = None, sample_rate: int = 16000) -> str:
    """
    Extract audio from a video into a single-channel WAV using ffmpeg.

    Returns the path to the WAV file.
    """
    if out_wav is None:
        tf = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        out_wav = tf.name
        tf.close()

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vn",
        "-ar",
        str(sample_rate),
        "-ac",
        "1",
        "-f",
        "wav",
        out_wav,
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return out_wav
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg extract audio failed: {e.stderr.decode(errors='ignore')}")
        raise


def compute_rms_windows(wav_path: str, window_size_sec: float = 1.0) -> List[Dict]:
    """
    Compute RMS (root mean square) energy for consecutive windows in a WAV file.

    Returns a list of {start, end, rms} dictionaries.
    """
    import numpy as np

    with wave.open(wav_path, 'rb') as w:
        nchannels = w.getnchannels()
        sampwidth = w.getsampwidth()
        framerate = w.getframerate()
        nframes = w.getnframes()
        duration = nframes / float(framerate)

        window_frames = int(window_size_sec * framerate)
        results = []

        w.rewind()
        start = 0.0
        while True:
            frames = w.readframes(window_frames)
            if not frames:
                break

            # Convert bytes to numpy array
            if sampwidth == 2:
                dtype = np.int16
            elif sampwidth == 4:
                dtype = np.int32
            else:
                # fallback
                dtype = np.int16

            audio = np.frombuffer(frames, dtype=dtype)
            if nchannels > 1:
                audio = audio.reshape(-1, nchannels)
                audio = audio.mean(axis=1)

            if audio.size == 0:
                rms = 0.0
            else:
                rms = float(np.sqrt(np.mean(np.square(audio.astype('float64')))))

            end = start + (len(frames) / (sampwidth * nchannels * float(framerate))) if frames else start

            results.append({
                "start": round(start, 3),
                "end": round(start + window_size_sec, 3),
                "rms": rms,
            })

            start += window_size_sec

        return results


def get_top_energy_windows(video_path: str, window_size_sec: float = 1.0, top_k: int = 10) -> List[Dict]:
    """
    Convenience function: extract audio and compute RMS windows, returning top_k windows sorted by rms desc.
    Each item: {start, end, rms}
    """
    wav = None
    try:
        wav = extract_audio_to_wav(video_path)
        windows = compute_rms_windows(wav, window_size_sec=window_size_sec)
        windows_sorted = sorted(windows, key=lambda x: x["rms"], reverse=True)
        return windows_sorted[:top_k]
    finally:
        # best-effort cleanup
        try:
            if wav and os.path.exists(wav):
                os.remove(wav)
        except Exception:
            pass


def fast_clip_copy(input_path: str, start: float, duration: float, output_path: str) -> str:
    """
    Create a fast, lossless clip using ffmpeg stream copy (-c copy).

    This is much faster than re-encoding but relies on keyframes. Use this for quick previews.
    """
    # Ensure output directory exists
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        str(start),
        "-i",
        input_path,
        "-t",
        str(duration),
        "-c",
        "copy",
        output_path,
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    except subprocess.CalledProcessError as e:
        logger.warning("ffmpeg fast copy failed, falling back to re-encode. Error: %s", e.stderr.decode(errors='ignore'))
        # Fallback: re-encode with libx264
        cmd2 = [
            "ffmpeg",
            "-y",
            "-ss",
            str(start),
            "-i",
            input_path,
            "-t",
            str(duration),
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            output_path,
        ]
        subprocess.run(cmd2, check=True)
        return output_path
