# clip_generator_app.py

import os
import requests
import tempfile

import streamlit as st
import whisper
from transformers import pipeline
from pytube import YouTube
import moviepy.editor as mp
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.fx.all import crop

# ─── App Config ───
st.set_page_config(page_title="CLIP GENERATOR + Media Assets", layout="wide")
st.title("CLIP GENERATOR")
st.write(
    "Generate viral clips from your long-form videos, then access trending GIFs, "
    "copyright-free sounds, and free logo templates—refreshed every 24 hours."
)

# ─── Secrets for API keys ───
GIPHY_API_KEY     = st.secrets.get("GIPHY_API_KEY", "")
FREESOUND_API_KEY = st.secrets.get("FREESOUND_API_KEY", "")
PIXABAY_API_KEY   = st.secrets.get("PIXABAY_API_KEY", "")

# ─── Daily-cached fetchers (TTL = 24 h) ───
@st.cache_data(ttl=24*60*60)
def fetch_trending_gifs(limit=12):
    if not GIPHY_API_KEY:
        return []
    url = f"https://api.giphy.com/v1/gifs/trending?api_key={GIPHY_API_KEY}&limit={limit}"
    return [g["images"]["downsized_medium"]["url"] for g in requests.get(url).json().get("data", [])]

@st.cache_data(ttl=24*60*60)
def fetch_free_sounds(limit=8):
    if not FREESOUND_API_KEY:
        return []
    url = (
        "https://freesound.org/apiv2/search/text/"
        f"?query=&sort=downloads_desc&fields=name,previews"
        f"&page_size={limit}&token={FREESOUND_API_KEY}"
    )
    items = requests.get(url).json().get("results", [])
    return [{"name": i["name"], "preview": i["previews"]["preview-lq-mp3"]} for i in items]

@st.cache_data(ttl=24*60*60)
def fetch_logo_templates(limit=8):
    if not PIXABAY_API_KEY:
        return []
    url = (
        "https://pixabay.com/api/"
        f"?key={PIXABAY_API_KEY}&q=logo+template&image_type=vector&per_page={limit}"
    )
    return [h["previewURL"] for h in requests.get(url).json().get("hits", [])]

# ─── Clip-Gen Model Loading ───
@st.cache_resource
def load_models():
    whisper_model = whisper.load_model("tiny")
    sentiment_model = pipeline("sentiment-analysis")
    return whisper_model, sentiment_model

# ─── Helpers: download sources ───
def download_youtube(url):
    yt = YouTube(url)
    stream = yt.streams.filter(file_extension="mp4", progressive=True).order_by("resolution").desc().first()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    stream.download(output_path=os.path.dirname(tmp.name), filename=os.path.basename(tmp.name))
    return tmp.name

def download_url(url):
    suffix = os.path.splitext(url)[1] or ".mp4"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    r = requests.get(url, stream=True); r.raise_for_status()
    for chunk in r.iter_content(8192):
        tmp.write(chunk)
    return tmp.name

# ─── Clip-Gen UI ───
NUM_CLIPS = 20
LENGTH_OPTIONS = [15, 30, 45, 60]
RESOLUTION_MAP = {
    "720p":  (1280,  720),
    "1080p": (1920, 1080),
    "1440p": (2560,1440),
    "2160p": (3840,2160),
}

mode = st.radio("Video input", ("Upload file", "YouTube URL", "Direct URL"))
if mode == "Upload file":
    vid = st.file_uploader("Choose a video", type=["mp4","mov","mkv","avi","flv","wmv","m4v","webm","mpeg","mpg","3gp","ts"])
    if vid:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(vid.name)[1])
        tmp.write(vid.read()); video_path = tmp.name
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

whisper_model, sentiment_model = load_models()
if st.button("Process & Show Top Segments"):
    with st.spinner("Transcribing…"):
        result = whisper_model.transcribe(video_path)
    segments = sorted(
        [
            {"start":s["start"], "end":s["end"], "text":s["text"].strip(),
             "score": sentiment_model(s["text"])[0]["score"]}
            for s in result["segments"]
        ],
        key=lambda x: x["score"], reverse=True
    )[:NUM_CLIPS]

    clip_len = st.selectbox("Clip length (s)", LENGTH_OPTIONS, index=1)
    res_opts = st.multiselect("Resolutions", list(RESOLUTION_MAP.keys()), default=["1080p"])
    choices = [
        f"{i+1}: {seg['start']:.1f}s | “{seg['text'][:50]}…” (score {seg['score']:.2f})"
        for i, seg in enumerate(segments)
    ]
    selected = st.multiselect("Select segments to export:", choices, default=choices[:3])

    if st.button("Generate & Export Clips"):
        vfile = mp.VideoFileClip(video_path)
        for choice in selected:
            idx = int(choice.split(":")[0]) - 1
            seg = segments[idx]
            start = seg["start"]
            end = min(start + clip_len, vfile.duration)
            clip = vfile.subclip(start, end)

            subtitle = SubtitlesClip(
                [((0, end-start), seg["text"])],
                lambda t: mp.TextClip(seg["text"], fontsize=24, font="Arial", method="caption",
                                      size=(clip.w*0.8, None))
            )
            final = mp.CompositeVideoClip([clip, subtitle.set_pos(("center","bottom"))])

            for res in res_opts:
                w,h = RESOLUTION_MAP[res]
                for tag,(ow,oh) in {"landscape":(w,h),"portrait":(h,w),"square":(h,h)}.items():
                    out = final.resize(width=ow)
                    out = crop(out, width=ow, height=oh, x_center=out.w/2, y_center=out.h/2)
                    path = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{res}_{tag}.mp4").name
                    out.write_videofile(path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
                    st.video(path)
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

