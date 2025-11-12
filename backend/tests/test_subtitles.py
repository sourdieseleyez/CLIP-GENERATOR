import tempfile
import os
from backend import subtitles


def test_create_srt_and_vtt():
	transcription = {
		"text": "Hello world. This is a test.",
		"segments": [
			{"start": 0.0, "end": 1.5, "text": "Hello world."},
			{"start": 1.6, "end": 3.5, "text": "This is a test."}
		]
	}

	srt_fd, srt_path = tempfile.mkstemp(suffix=".srt")
	os.close(srt_fd)
	vtt_fd, vtt_path = tempfile.mkstemp(suffix=".vtt")
	os.close(vtt_fd)

	try:
		out_srt = subtitles.create_srt_from_transcription(transcription, srt_path)
		assert os.path.exists(out_srt)
		with open(out_srt, "r", encoding="utf-8") as f:
			content = f.read()
			assert "Hello world." in content
			assert "This is a test." in content

		out_vtt = subtitles.create_vtt_from_srt(srt_path, vtt_path)
		assert os.path.exists(out_vtt)
		with open(out_vtt, "r", encoding="utf-8") as f:
			vtt_content = f.read()
			assert vtt_content.startswith("WEBVTT")
			assert "Hello world." in vtt_content

	finally:
		try:
			os.remove(srt_path)
		except Exception:
			pass
		try:
			os.remove(vtt_path)
		except Exception:
			pass
