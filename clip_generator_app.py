import os
import requests
import tempfile
from typing import Tuple

import streamlit as st
import whisper
from transformers import pipeline
from pytube import YouTube
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.fx.crop import crop
from moviepy.video.tools.subtitles import SubtitlesClip


# ─── App Config ───
st.set_page_config(page_title="CLIP GENERATOR + Media Assets", layout="wide")
st.title("CLIP GENERATOR")
st.write(
    "Generate viral clips from your long-form videos, then access trending GIFs, "
    "copyright-free sounds, and free logo templates—refreshed every 24 hours."
)


# ─── Secrets for API keys (Streamlit Cloud or .streamlit/secrets.toml) ───
GIPHY_API_KEY = st.secrets.get("GIPHY_API_KEY", "")
FREESOUND_API_KEY = st.secrets.get("FREESOUND_API_KEY", "")
PIXABAY_API_KEY = st.secrets.get("PIXABAY_API_KEY", "")


# ─── Daily-cached fetchers (TTL = 24 h) ───
@st.cache_data(ttl=24 * 60 * 60)
def fetch_trending_gifs(limit: int = 12):
    if not GIPHY_API_KEY:
        return []
    url = f"https://api.giphy.com/v1/gifs/trending?api_key={GIPHY_API_KEY}&limit={limit}"
    return [
        item["images"]["downsized_medium"]["url"]
        for item in requests.get(url).json().get("data", [])
    ]


@st.cache_data(ttl=24 * 60 * 60)
def fetch_free_sounds(limit: int = 8):
    if not FREESOUND_API_KEY:
        return []
    url = (
        "https://freesound.org/apiv2/search/text/"
        f"?query=&sort=downloads_desc&fields=name,previews"
        f"&page_size={limit}&token={FREESOUND_API_KEY}"
    )
    results = requests.get(url).json().get("results", [])
    return [{"name": r["name"], "preview": r["previews"]["preview-lq-mp3"]} for r in results]


@st.cache_data(ttl=24 * 60 * 60)
def fetch_logo_templates(limit: int = 8):
    if not PIXABAY_API_KEY:
        return []
    url = (
        "https://pixabay.com/api/"
        f"?key={PIXABAY_API_KEY}&q=logo+template&image_type=vector&per_page={limit}"
    )
    hits = requests.get(url).json().get("hits", [])
    return [h["previewURL"] for h in hits]


# ─── Clip-Gen Model Loading ───
@st.cache_resource
def load_models() -> Tuple[object, object]:
    whisper_model = whisper.load_model("tiny")
    sentiment_model = pipeline("sentiment-analysis")
    return whisper_model, sentiment_model


# ─── Helpers: download sources ───
def download_youtube(url: str) -> str:
    yt = YouTube(url)
    stream = (
        yt.streams.filter(file_extension="mp4", progressive=True)
        .order_by("resolution")
        .desc()
        .first()
    )
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    # pytube's download writes to filename in output_path
    stream.download(output_path=os.path.dirname(tmp.name), filename=os.path.basename(tmp.name))
    return tmp.name


def download_url(url: str) -> str:
    suffix = os.path.splitext(url)[1] or ".mp4"
    tmp = tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=suffix)
    r = requests.get(url, stream=True)
    r.raise_for_status()
    for chunk in r.iter_content(chunk_size=8192):
        if chunk:
            tmp.write(chunk)
    tmp.close()
    return tmp.name


# ─── Clip-Gen UI ───
NUM_CLIPS = 20
LENGTH_OPTIONS = [15, 30, 45, 60]
RESOLUTION_MAP = {
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "1440p": (2560, 1440),
    "2160p": (3840, 2160),
}


mode = st.radio("Video input", ("Upload file", "YouTube URL", "Direct URL"))
video_path = None
if mode == "Upload file":
    vid = st.file_uploader("Choose a video", type=["mp4", "mov", "mkv", "avi", "flv", "wmv", "m4v", "webm", "mpeg", "mpg", "3gp", "ts"])
    if vid:
        tmp = tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=os.path.splitext(vid.name)[1])
        tmp.write(vid.read())
        tmp.close()
        video_path = tmp.name
    else:
        st.stop()

elif mode == "YouTube URL":
    link = st.text_input("YouTube URL")
    if link:
        with st.spinner("Downloading from YouTube…"):
            video_path = download_youtube(link)
    else:
        st.stop()

else:
    link = st.text_input("Direct video URL")
    if link:
        with st.spinner("Downloading from URL…"):
            video_path = download_url(link)
    else:
        st.stop()


# Load Whisper & sentiment models
whisper_model, sentiment_model = load_models()


if st.button("Process & Show Top Segments"):
    with st.spinner("Transcribing…"):
        result = whisper_model.transcribe(video_path)

    # Score & pick top segments
    segments = sorted(
        [
            {
                "start": s["start"],
                "end": s["end"],
                "text": s["text"].strip(),
                "score": sentiment_model(s["text"])[0]["score"],
            }
            for s in result.get("segments", [])
        ],
        key=lambda x: x["score"],
        reverse=True,
    )[:NUM_CLIPS]

    # UI: length & resolution selectors
    clip_len = st.selectbox("Clip length (s)", LENGTH_OPTIONS, index=1)
    res_opts = st.multiselect("Resolutions", list(RESOLUTION_MAP.keys()), default=["1080p"])

    # Build segment choices
    choices = [
        f"{i+1}: {seg['start']:.1f}s | \"{seg['text'][:50]}...\" (score {seg['score']:.2f})"
        for i, seg in enumerate(segments)
    ]
    selected = st.multiselect("Select segments to export:", choices, default=choices[:3])

    # Generate & export
    if st.button("Generate & Export Clips"):
        vfile = VideoFileClip(video_path)
        for choice in selected:
            idx = int(choice.split(":")[0]) - 1
            seg = segments[idx]
            start = seg["start"]
            end = min(start + clip_len, vfile.duration)

            clip = vfile.subclip(start, end)
            subtitle = SubtitlesClip(
                [((0, end - start), seg["text"])],
                lambda t: TextClip(
                    seg["text"], fontsize=24, font="Arial", method="caption", size=(int(clip.w * 0.8), None)
                ),
            )
            final = CompositeVideoClip([clip, subtitle.set_pos(("center", "bottom"))])

            for res in res_opts:
                w, h = RESOLUTION_MAP[res]
                for tag, (ow, oh) in {"landscape": (w, h), "portrait": (h, w), "square": (h, h)}.items():
                    out_clip = final.resize(width=ow)
                    out_clip = crop(
                        out_clip, width=ow, height=oh, x_center=out_clip.w / 2, y_center=out_clip.h / 2
                    )
                    out_path = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{res}_{tag}.mp4").name
                    out_clip.write_videofile(out_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
                    st.video(out_path)

        st.success("Clips generated and formatted!")


# ─── Daily Media Assets UI ───
st.markdown("---")
st.subheader("🎯 Trending Media (refreshes every 24 h)")

with st.expander("📺 Trending GIFs"):
    gifs = fetch_trending_gifs()
    if gifs:
        st.image(gifs, width=150, caption=[f"GIF #{i+1}" for i in range(len(gifs))])
    else:
        st.info("Add GIPHY_API_KEY to Secrets to see GIFs.")

with st.expander("🔊 Copyright-Free Sounds"):
    sounds = fetch_free_sounds()
    if sounds:
        for s in sounds:
            st.write(f"• {s['name']}")
            st.audio(s["preview"])
    else:
        st.info("Add FREESOUND_API_KEY to Secrets to see sounds.")

with st.expander("🎨 Free Logo Templates"):
    logos = fetch_logo_templates()
    if logos:
        st.image(logos, width=150, caption=[f"Logo #{i+1}" for i in range(len(logos))])
    else:
        st.info("Add PIXABAY_API_KEY to Secrets to see logo templates.")
