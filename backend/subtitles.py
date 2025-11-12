import os
import datetime
from typing import Dict
import logging

logger = logging.getLogger(__name__)


def _format_timestamp(seconds: float) -> str:
    """Format seconds to SRT timestamp (HH:MM:SS,mmm)"""
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int((td.total_seconds() - int(td.total_seconds())) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def create_srt_from_transcription(transcription: Dict, out_path: str) -> str:
    """
    Create a simple SRT file from a Whisper-style transcription dict.

    Expects transcription to contain a top-level 'segments' list where each
    segment has at least 'start', 'end', and 'text'. Falls back to using the
    top-level 'text' split into chunks if segments are not present.
    Returns the path to the written SRT file.
    """
    segments = transcription.get("segments") or []

    if not segments:
        # Fallback: split text into ~10-word chunks with synthetic timings
        full_text = transcription.get("text", "")
        words = full_text.split()
        segs = []
        idx = 0
        # naive timing: assume 0.5s per word as fallback
        while idx < len(words):
            chunk_words = words[idx: idx + 10]
            chunk = " ".join(chunk_words)
            start = idx * 0.5
            end = start + max(2.0, len(chunk_words) * 0.5)
            segs.append({"start": start, "end": end, "text": chunk})
            idx += 10
        segments = segs

    # Write SRT
    with open(out_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start_ts = _format_timestamp(seg.get("start", 0.0))
            end_ts = _format_timestamp(seg.get("end", seg.get("start", 0.0) + 3.0))
            text = seg.get("text", "").strip()
            # sanitize newlines
            text = text.replace("\n", " ")

            f.write(f"{i}\n")
            f.write(f"{start_ts} --> {end_ts}\n")
            f.write(f"{text}\n\n")

    logger.info(f"Wrote SRT: {out_path}")
    return out_path


def create_vtt_from_srt(srt_path: str, vtt_path: str) -> str:
    """Convert a simple SRT file into a VTT file by adjusting header and timestamp format."""
    with open(srt_path, "r", encoding="utf-8") as sf, open(vtt_path, "w", encoding="utf-8") as vf:
        vf.write("WEBVTT\n\n")
        for line in sf:
            # SRT uses comma for milliseconds; VTT uses dot
            vf.write(line.replace(",", "."))

    logger.info(f"Wrote VTT: {vtt_path}")
    return vtt_path
import os
import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def _format_timestamp(seconds: float) -> str:
    """Format seconds to SRT timestamp (HH:MM:SS,mmm)"""
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int((td.total_seconds() - int(td.total_seconds())) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def create_srt_from_transcription(transcription: Dict, out_path: str) -> str:
    """
    Create a simple SRT file from a Whisper-style transcription dict.

    Expects transcription to contain a top-level 'segments' list where each
    segment has at least 'start', 'end', and 'text'. Falls back to using the
    top-level 'text' split into chunks if segments are not present.
    Returns the path to the written SRT file.
    """
    segments = transcription.get("segments") or []

    if not segments:
        # Fallback: split text into 5-second chunks
        full_text = transcription.get("text", "")
        words = full_text.split()
        segs = []
        idx = 0
        # Create segments of ~10 words each
        while idx < len(words):
            chunk = " ".join(words[idx: idx + 10])
            segs.append({"start": idx * 0.1, "end": (idx + 10) * 0.1, "text": chunk})
            idx += 10
        segments = segs

    # Write SRT
    with open(out_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start_ts = _format_timestamp(seg.get("start", 0.0))
            end_ts = _format_timestamp(seg.get("end", seg.get("start", 0.0) + 3.0))
            text = seg.get("text", "").strip()
            # sanitize newlines
            text = text.replace("\n", " ")

            f.write(f"{i}\n")
            f.write(f"{start_ts} --> {end_ts}\n")
            f.write(f"{text}\n\n")

    logger.info(f"Wrote SRT: {out_path}")
    return out_path


def create_vtt_from_srt(srt_path: str, vtt_path: str) -> str:
    """Convert a simple SRT file into a VTT file by adjusting header and timestamp format."""
    with open(srt_path, "r", encoding="utf-8") as sf, open(vtt_path, "w", encoding="utf-8") as vf:
        vf.write("WEBVTT\n\n")
        for line in sf:
            # SRT uses comma for milliseconds; VTT uses dot
            vf.write(line.replace(",", "."))

    logger.info(f"Wrote VTT: {vtt_path}")
    return vtt_path
