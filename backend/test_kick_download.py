import os
import shutil
import sys
import traceback

URL = "https://kick.com/sourdieseleyez/videos/28ed76f1-ec0b-4603-abb7-efe306edb19a"

print(f"Starting Kick download test for: {URL}")

try:
    # Check for yt-dlp availability
    try:
        import yt_dlp as ytdlp
        print("yt-dlp available, version:", getattr(ytdlp, '__version__', 'unknown'))
    except Exception:
        ytdlp = None
        print("yt-dlp not available in environment")

    # Check ffmpeg availability
    ffmpeg_path = shutil.which('ffmpeg')
    print('ffmpeg on PATH:' , ffmpeg_path if ffmpeg_path else 'not found')

    # Import processor and instantiate without running __init__
    from gemini_processor import GeminiVideoProcessor
    proc = object.__new__(GeminiVideoProcessor)

    # Call the downloader
    print('Attempting download...')
    # If there's a cookies.txt file in this folder, read and pass it to the downloader
    cookies_text = None
    if os.path.exists('cookies.txt'):
        print('Found cookies.txt, using it for download')
        with open('cookies.txt', 'r', encoding='utf-8') as cf:
            cookies_text = cf.read()

    path = proc.download_video_from_url(URL, cookies_text=cookies_text)

    if path and os.path.exists(path):
        size = os.path.getsize(path)
        print(f"Download successful: {path} ({size} bytes)")
    else:
        print("Download returned no file or file not found")
        sys.exit(2)

except Exception as e:
    print('Download failed with exception:')
    traceback.print_exc()
    sys.exit(1)

sys.exit(0)
