import tempfile
import os
import shutil
from backend.gemini_processor import GeminiVideoProcessor
import backend.ffmpeg_helpers as ffmpeg_helpers
import backend.subtitles as subtitles


def test_process_video_for_clips_smoke(monkeypatch, tmp_path):
    """Smoke test for process_video_for_clips that mocks heavy external deps.

    This test does not require ffmpeg or moviepy; it patches methods that would
    otherwise call those binaries or external services.
    """
    # Create a dummy "video" file path (the processor won't actually read it because we mock)
    dummy_video = tmp_path / "dummy.mp4"
    dummy_video.write_bytes(b"")

    proc = GeminiVideoProcessor(gemini_api_key="test-key", stt_engine="whisper")

    # Mock transcribe_video to return a simple transcription
    def fake_transcribe(video_path):
        return {
            "text": "hello world",
            "segments": [
                {"start": 0.0, "end": 2.0, "text": "hello world"},
                {"start": 2.5, "end": 5.0, "text": "more text here"}
            ]
        }

    monkeypatch.setattr(proc, "transcribe_video", fake_transcribe)

    # Mock analyze_with_gemini to select two segments
    def fake_analyze(transcription, num_clips=5, progress_callback=None, use_streaming=True):
        return [
            {"start": 0.0, "end": 2.0, "text": "hello world", "hook": "hello", "reason": "test", "category": "general", "virality_score": 8},
            {"start": 2.5, "end": 5.0, "text": "more text here", "hook": "more", "reason": "test", "category": "general", "virality_score": 6}
        ][:num_clips]

    monkeypatch.setattr(proc, "analyze_with_gemini", fake_analyze)

    # Mock ffmpeg_helpers functions used by processor
    monkeypatch.setattr(ffmpeg_helpers, "get_top_energy_windows", lambda *a, **k: [])
    monkeypatch.setattr(ffmpeg_helpers, "fast_clip_copy", lambda *a, **k: None)

    # Mock generate_clip to write an empty file and return the path
    def fake_generate_clip(video_path, start_time, end_time, text, output_path, resolution, add_subtitles=True):
        with open(output_path, "wb") as f:
            f.write(b"")
        return output_path

    monkeypatch.setattr(proc, "generate_clip", fake_generate_clip)

    # Run the processing (should not raise)
    result = proc.process_video_for_clips(str(dummy_video), num_clips=2, clip_duration=15, resolution="portrait", progress_callback=None)

    assert result["success"] is True
    assert result["total_clips"] == 2
    assert len(result["clips"]) == 2
    # srt/vtt should have been created on disk
    assert result.get("srt_path") is not None
    assert result.get("vtt_path") is not None
    assert os.path.exists(result.get("srt_path"))
    assert os.path.exists(result.get("vtt_path"))

    # Cleanup files
    try:
        os.remove(result.get("srt_path"))
    except Exception:
        pass
    try:
        os.remove(result.get("vtt_path"))
    except Exception:
        pass
    for clip in result.get("clips", []):
        try:
            if clip.get("path") and os.path.exists(clip.get("path")):
                os.remove(clip.get("path"))
        except Exception:
            pass
