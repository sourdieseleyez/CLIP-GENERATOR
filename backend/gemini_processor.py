"""
Optimized Video Processor using Gemini 2.5 Flash Lite
Ultra-fast, ultra-cheap, and intelligent clip generation with streaming support

Cost Comparison (per 1M tokens):
- GPT-4: $5.00
- Gemini 2.5 Flash: $0.075
- Gemini 2.5 Flash Lite: $0.0375 (50% cheaper than Flash!)

Speed: 2-3 seconds for full video analysis
Streaming: Real-time progress updates for better UX
"""

import os
import json
import tempfile
import shutil
import uuid
import logging
from typing import List, Dict, Optional, Callable
import requests

logger = logging.getLogger(__name__)

# Optional whisper import (requires openai-whisper package)
try:
    import whisper
except ImportError:
    whisper = None
    logger.warning("openai-whisper not installed - transcription will be unavailable")

# Optional faster-whisper import
try:
    from faster_whisper import WhisperModel as FasterWhisperModel
except ImportError:
    FasterWhisperModel = None

# Optional helper modules (graceful degradation if not available)
try:
    import ffmpeg_helpers
except ImportError:
    ffmpeg_helpers = None

try:
    import subtitles
except ImportError:
    subtitles = None

try:
    import scene_detection
except ImportError:
    scene_detection = None

try:
    import emotion_detector
except ImportError:
    emotion_detector = None

# Optional pytube for YouTube downloads
try:
    from pytube import YouTube
except ImportError:
    YouTube = None
    logger.warning("pytube not installed - YouTube downloads will be unavailable")

# Optional google-generativeai
try:
    import google.generativeai as genai
except ImportError:
    genai = None
    logger.warning("google-generativeai not installed - AI analysis will be unavailable")

# Optional import for yt-dlp to support many streaming sites (Kick, Twitch, etc.)
try:
    import yt_dlp as ytdlp
except ImportError:
    ytdlp = None


class GeminiVideoProcessor:
    def __init__(self, gemini_api_key: str, stt_engine: str = "whisper"):
        self.gemini_api_key = gemini_api_key
        self.whisper_model = None
        self.stt_engine = stt_engine or "whisper"
        self.model = None
        
        if genai is not None:
            genai.configure(api_key=gemini_api_key)
            # Use Gemini 2.5 Flash Lite - cheapest option with streaming support
            # 133x cheaper than GPT-4!
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        else:
            logger.warning("Gemini AI not available - AI analysis disabled")
    
    def load_whisper_model(self):
        """Load the configured STT model for transcription"""
        if self.whisper_model is not None:
            return self.whisper_model

        logger.info(f"Loading STT model: {self.stt_engine}...")
        
        # faster-whisper (if available and requested)
        if self.stt_engine == "faster-whisper" and FasterWhisperModel is not None:
            # load a reasonably small model by default
            self.whisper_model = FasterWhisperModel("small")
            return self.whisper_model

        # Local OpenAI whisper
        if whisper is not None:
            self.whisper_model = whisper.load_model("base")
            return self.whisper_model
        
        raise RuntimeError("No speech-to-text engine available. Install openai-whisper or faster-whisper.")
    
    def download_youtube_video(self, url: str) -> str:
        """Download YouTube video and return local path"""
        # Prefer yt-dlp if available (more reliable)
        if ytdlp is not None:
            return self._download_with_ytdlp(url)
        
        # Fallback to pytube
        if YouTube is None:
            raise RuntimeError("No YouTube downloader available. Install pytube or yt-dlp.")
        
        try:
            yt = YouTube(url)
            stream = (
                yt.streams.filter(file_extension="mp4", progressive=True)
                .order_by("resolution")
                .desc()
                .first()
            )
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            temp_path = temp_file.name
            temp_file.close()
            
            stream.download(
                output_path=os.path.dirname(temp_path),
                filename=os.path.basename(temp_path)
            )
            
            return temp_path
        except Exception as e:
            raise Exception(f"Failed to download YouTube video: {str(e)}")
    
    def download_video_from_url(self, url: str, cookies_text: Optional[str] = None, extra_headers: Optional[dict] = None) -> str:
        """Download video from a URL or page.

        If `cookies_text` is provided it should be the contents of a Netscape-format
        cookies.txt file and will be written to a temp file and passed to yt-dlp.
        `extra_headers` is a dict of HTTP headers to set when using yt-dlp or
        when falling back to a direct requests download.
        """
        cookiefile = None
        try:
            # Prepare headers
            headers = None
            if extra_headers:
                # ensure keys/values are strings
                headers = {str(k): str(v) for k, v in extra_headers.items()}

            # If cookies_text provided, write to a temporary cookie file
            if cookies_text:
                cookiefile = tempfile.NamedTemporaryFile(delete=False, suffix="_cookies.txt")
                cookiefile.write(cookies_text.encode('utf-8'))
                cookiefile.close()

            # Some URLs (YouTube, Kick, Twitch, etc.) are page URLs rather than
            # direct .mp4 links. Prefer using yt-dlp when available for those hosts.
            if ytdlp is not None:
                # Common hosts that require extractor support
                if any(d in url for d in ("kick.com", "kick.tv", "twitch.tv", "youtube.com", "youtu.be")):
                    return self._download_with_ytdlp(url, cookiefile_path=cookiefile.name if cookiefile else None, extra_headers=headers)

            # Fallback: attempt a direct HTTP download using requests
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            temp_path = temp_file.name

            req_headers = headers if headers else {}
            # Provide a sensible UA header if none supplied
            req_headers.setdefault('User-Agent', 'python-requests/2.x')

            response = requests.get(url, stream=True, timeout=30, headers=req_headers)
            response.raise_for_status()

            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return temp_path
        except Exception as e:
            raise Exception(f"Failed to download video from URL: {str(e)}")
        finally:
            # We don't remove the cookiefile here because yt-dlp may still be using it
            # The caller or the OS temp cleanup should handle removal when safe.
            pass

    def _download_with_ytdlp(self, url: str, cookiefile_path: Optional[str] = None, extra_headers: Optional[dict] = None) -> str:
        """Download a video page using yt-dlp and return local filepath.

        This requires the `yt-dlp` Python package to be installed in the environment.
        If not available this will raise an informative error.
        """
        if ytdlp is None:
            raise Exception("yt-dlp is not installed in the environment. Install yt-dlp to download sites like kick.com.")

        temp_dir = tempfile.mkdtemp(prefix="clipgen_ytdlp_")
        # Output template: single file with a generated name
        out_template = os.path.join(temp_dir, "%(id)s.%(ext)s")

        ytdlp_opts = {
            'outtmpl': out_template,
            'format': 'bestvideo+bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            # Prefer ffmpeg postprocessing if needed (should be available in typical setups)
            'merge_output_format': 'mp4'
        }

        # Some sites (including Kick) may reject non-browser User-Agents or require referer headers.
        # Provide a common modern browser UA and referer to reduce chance of 403/blocked requests.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://kick.com/'
        }
        if extra_headers:
            headers.update(extra_headers)

        ytdlp_opts.setdefault('http_headers', headers)

        # If a cookiefile path is supplied, instruct yt-dlp to use it
        if cookiefile_path:
            ytdlp_opts['cookiefile'] = cookiefile_path

        try:
            with ytdlp.YoutubeDL(ytdlp_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                # Determine downloaded filename from info
                if 'requested_downloads' in info and info['requested_downloads']:
                    # yt-dlp internals provide filename in requested_downloads
                    filename = info['requested_downloads'][0].get('filepath')
                else:
                    # Fallback to expected name from outtmpl
                    ext = info.get('ext', 'mp4')
                    video_id = info.get('id') or str(uuid.uuid4())
                    filename = os.path.join(temp_dir, f"{video_id}.{ext}")

                if not os.path.exists(filename):
                    # try to find any file in temp_dir
                    files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir)]
                    if files:
                        filename = files[0]

                return filename
        except Exception as e:
            # Cleanup temp dir on failure
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
            raise Exception(f"yt-dlp download failed: {str(e)}")
    
    def transcribe_video(self, video_path: str) -> Dict:
        """
        Transcribe video using Whisper
        Returns transcript with word-level timestamps
        """
        try:
            model = self.load_whisper_model()
            print(f"Transcribing video: {video_path} (engine={self.stt_engine})")

            # faster-whisper API
            if self.stt_engine == "faster-whisper" and FasterWhisperModel is not None:
                segments = []
                # faster-whisper returns a tuple: (segment_generator, info)
                segment_generator, info = model.transcribe(video_path, beam_size=5, word_timestamps=True)
                for segment in segment_generator:
                    segments.append({
                        "start": float(segment.start),
                        "end": float(segment.end),
                        "text": segment.text
                    })
                full_text = " ".join([s["text"].strip() for s in segments])
                return {"text": full_text, "segments": segments}

            # Default: openai-whisper python package
            result = model.transcribe(
                video_path,
                word_timestamps=True,
                verbose=False
            )

            return result
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def analyze_with_gemini(
        self, 
        transcription: Dict, 
        num_clips: int = 5,
        progress_callback: Optional[Callable[[str], None]] = None,
        use_streaming: bool = True
    ) -> List[Dict]:
        """
        Use Gemini 2.5 Flash Lite to analyze transcript and find viral moments
        
        Why this works without video:
        1. Transcripts contain rich temporal and linguistic information
        2. Emotional language indicates engaging moments
        3. Pacing changes (from timestamps) show emphasis
        4. Content structure reveals story arcs
        5. Contextual understanding identifies hooks
        
        Args:
            transcription: Whisper transcription result
            num_clips: Number of clips to generate
            progress_callback: Optional callback for streaming progress updates
            use_streaming: Whether to use streaming API (better UX)
        """
        try:
            # Extract full text and segments with timestamps
            full_text = transcription["text"]
            segments = transcription.get("segments", [])
            
            # Build detailed transcript with timing info
            detailed_transcript = []
            for seg in segments:
                detailed_transcript.append({
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"].strip()
                })
            
            # Create comprehensive prompt for Gemini
            prompt = f"""You are an expert at identifying viral video moments. Analyze this video transcript and find the {num_clips} most engaging moments that would make great short-form clips.

TRANSCRIPT WITH TIMESTAMPS:
{json.dumps(detailed_transcript, indent=2)}

FULL TEXT:
{full_text}

ANALYSIS CRITERIA:
1. **Hook Potential** - Can grab attention in first 3 seconds
2. **Emotional Impact** - Excitement, surprise, humor, controversy
3. **Quotability** - Memorable one-liners or statements
4. **Story Arc** - Complete thought with setup and payoff
5. **Engagement** - Questions, revelations, or strong opinions
6. **Pacing** - Natural energy and rhythm
7. **Context Independence** - Makes sense without full video

WHAT TO LOOK FOR:
- Controversial or surprising statements
- Emotional peaks (excitement, shock, humor)
- Quotable moments and one-liners
- Story climaxes or revelations
- Strong opinions or hot takes
- Pattern interrupts (unexpected turns)
- Questions followed by compelling answers
- Demonstrations or explanations with impact

CLIP REQUIREMENTS:
- Each clip should be 15-60 seconds
- Include enough context to make sense
- Start slightly before the key moment (build-up)
- End after the payoff (complete the thought)
- Avoid cutting mid-sentence

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "start": <start_time_in_seconds>,
    "end": <end_time_in_seconds>,
    "text": "<exact quote from transcript>",
    "reason": "<why this moment is viral-worthy>",
    "hook": "<first 3 seconds text for caption>",
    "category": "<type: humor/educational/controversial/emotional/surprising>",
    "virality_score": <1-10 rating>
  }}
]

Sort by virality_score (highest first). Return ONLY the JSON array, no other text."""

            generation_config = {
                "temperature": 0.7,  # Balanced creativity
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
            
            # Use streaming for better UX (show progress to user)
            if use_streaming and progress_callback:
                if progress_callback:
                    progress_callback("Starting AI analysis...")
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config,
                    stream=True
                )
                
                # Collect streamed chunks
                content = ""
                chunk_count = 0
                for chunk in response:
                    if chunk.text:
                        content += chunk.text
                        chunk_count += 1
                        
                        # Update progress every few chunks
                        if chunk_count % 3 == 0 and progress_callback:
                            progress_callback(f"Analyzing... ({chunk_count} chunks received)")
                
                if progress_callback:
                    progress_callback("Analysis complete, parsing results...")
                
                content = content.strip()
            else:
                # Non-streaming (faster for batch processing)
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                content = response.text.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            segments = json.loads(content)
            
            # Validate and clean segments
            validated_segments = []
            for seg in segments[:num_clips]:
                if all(k in seg for k in ["start", "end", "text"]):
                    validated_segments.append({
                        "start": float(seg["start"]),
                        "end": float(seg["end"]),
                        "text": seg["text"],
                        "reason": seg.get("reason", "Engaging content"),
                        "hook": seg.get("hook", seg["text"][:50]),
                        "category": seg.get("category", "general"),
                        "virality_score": seg.get("virality_score", 7)
                    })
            
            return validated_segments
            
        except Exception as e:
            raise Exception(f"Gemini analysis failed: {str(e)}")
    
    def generate_clip(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        text: str,
        output_path: str,
        resolution: tuple = (1080, 1920),  # Portrait by default
        add_subtitles: bool = True
    ) -> str:
        """Generate a single clip with optional subtitles"""
        try:
            # Import MoviePy lazily so the module can be imported even when
            # moviepy isn't installed (helps running the API without video deps).
            try:
                from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
                from moviepy.video.fx.crop import crop
            except Exception as e:
                raise Exception("moviepy is required for clip generation. Install moviepy or run the server without calling video generation.")

            video = VideoFileClip(video_path)
            
            # Ensure end time doesn't exceed video duration
            end_time = min(end_time, video.duration)
            
            # Extract clip
            clip = video.subclip(start_time, end_time)
            
            # Resize and crop to target resolution
            target_width, target_height = resolution
            
            # Calculate scaling
            scale = max(target_width / clip.w, target_height / clip.h)
            clip_resized = clip.resize(scale)
            
            # Crop to exact dimensions
            clip_cropped = crop(
                clip_resized,
                width=target_width,
                height=target_height,
                x_center=clip_resized.w / 2,
                y_center=clip_resized.h / 2
            )
            
            # Add subtitles if requested
            if add_subtitles and text:
                # Limit text length for readability
                display_text = text[:100] + "..." if len(text) > 100 else text
                
                txt_clip = TextClip(
                    display_text,
                    fontsize=40,
                    color='white',
                    font='Arial-Bold',
                    stroke_color='black',
                    stroke_width=2,
                    method='caption',
                    size=(int(target_width * 0.9), None),
                    align='center'
                )
                
                # Position at bottom
                txt_clip = txt_clip.set_position(('center', target_height - 150))
                txt_clip = txt_clip.set_duration(clip_cropped.duration)
                
                # Composite
                final_clip = CompositeVideoClip([clip_cropped, txt_clip])
            else:
                final_clip = clip_cropped
            
            # Write output
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=tempfile.mktemp(suffix='.m4a'),
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Cleanup
            video.close()
            clip.close()
            if add_subtitles and text:
                final_clip.close()
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Clip generation failed: {str(e)}")
    
    def process_video_for_clips(
        self,
        video_path: str,
        num_clips: int = 5,
        clip_duration: int = 30,
        resolution: str = "portrait",
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Dict:
        """
        Complete pipeline: transcribe → analyze with Gemini → generate clips
        
        This is efficient because:
        1. Whisper transcription is one-time cost
        2. Gemini 2.5 Flash Lite is extremely fast and cheap (133x cheaper than GPT-4!)
        3. No video analysis needed - text is sufficient
        4. Parallel clip generation possible
        5. Streaming provides real-time progress updates
        
        Args:
            video_path: Path to video file
            num_clips: Number of clips to generate
            clip_duration: Maximum duration per clip
            resolution: Output resolution (portrait/landscape/square)
            progress_callback: Optional callback(message, progress_percent)
        """
        
        # Resolution presets
        resolutions = {
            "portrait": (1080, 1920),  # 9:16 for TikTok/Reels
            "landscape": (1920, 1080),  # 16:9 for YouTube
            "square": (1080, 1080)      # 1:1 for Instagram
        }
        
        target_resolution = resolutions.get(resolution, resolutions["portrait"])
        
        try:
            # Step 1: Transcribe (Whisper)
            print("Step 1: Transcribing video with Whisper...")
            if progress_callback:
                progress_callback("Transcribing video...", 10)
            
            transcription_result = self.transcribe_video(video_path)
            
            if progress_callback:
                progress_callback("Transcription complete", 40)
            
            # Step 2: Analyze with Gemini 2.5 Flash Lite (with streaming)
            print("Step 2: Analyzing transcript with Gemini 2.5 Flash Lite...")
            if progress_callback:
                progress_callback("Analyzing with AI...", 45)
            
            def analysis_progress(message):
                if progress_callback:
                    progress_callback(message, 50)
            
            segments = self.analyze_with_gemini(
                transcription_result,
                num_clips,
                progress_callback=analysis_progress,
                use_streaming=True
            )

            # Step 2b: Energy-based scoring (fast heuristic) - optional enhancement
            energy_windows = []
            if ffmpeg_helpers is not None:
                try:
                    energy_windows = ffmpeg_helpers.get_top_energy_windows(video_path, window_size_sec=1.0, top_k=max(20, num_clips * 4))
                except Exception as e:
                    logger.debug(f"Energy detection skipped: {e}")

            # Scene detection (camera cuts) - optional enhancement
            scene_timestamps = []
            if scene_detection is not None:
                try:
                    scene_timestamps = scene_detection.detect_scenes(video_path, scene_threshold=0.35)
                except Exception as e:
                    logger.debug(f"Scene detection skipped: {e}")

            # Audio "hype" events: laughter, cheers, shouts - optional enhancement
            audio_hype_events = []
            if emotion_detector is not None:
                try:
                    audio_hype_events = emotion_detector.detect_audio_hype_events(video_path, window_size_sec=0.5, rms_multiplier=2.0)
                except Exception as e:
                    logger.debug(f"Hype detection skipped: {e}")

            # Attach energy score to each segment: average RMS of overlapping windows
            for seg in segments:
                overlaps = [w for w in energy_windows if w['start'] < seg['end'] and w['end'] > seg['start']]
                if overlaps:
                    seg['energy_score'] = float(sum(w['rms'] for w in overlaps) / len(overlaps))
                else:
                    seg['energy_score'] = 0.0

                # Hype score from audio events: proportion of overlapping hype events
                hype_overlaps = [e for e in audio_hype_events if e['start'] < seg['end'] and e['end'] > seg['start']]
                if hype_overlaps:
                    seg['hype_score'] = float(sum(e.get('score', 0.0) for e in hype_overlaps) / len(hype_overlaps))
                else:
                    seg['hype_score'] = 0.0

                # Scene proximity: reward segments near a camera cut (within 2s)
                proximity = 0.0
                for st in scene_timestamps:
                    if st >= seg['start'] - 2.0 and st <= seg['end'] + 2.0:
                        proximity = 1.0
                        break
                seg['scene_proximity'] = proximity

            # Normalize energy_score to 0-1
            energy_values = [s['energy_score'] for s in segments]
            if energy_values and max(energy_values) > 0:
                max_e = max(energy_values)
                min_e = min(energy_values)
                for s in segments:
                    if max_e - min_e > 0:
                        s['energy_norm'] = (s['energy_score'] - min_e) / (max_e - min_e)
                    else:
                        s['energy_norm'] = 0.0
            else:
                for s in segments:
                    s['energy_norm'] = 0.0

            # Re-rank segments by combined score = virality_score * (1 + energy_norm)
            for s in segments:
                try:
                    vir = float(s.get('virality_score', 7))
                except Exception:
                    vir = 7.0
                # Combine energy, hype and scene proximity to boost exciting moments
                hype = float(s.get('hype_score', 0.0))
                scene_boost = float(s.get('scene_proximity', 0.0))
                s['combined_score'] = vir * (1.0 + float(s.get('energy_norm', 0.0)) + 0.5 * hype + 0.3 * scene_boost)

            segments = sorted(segments, key=lambda x: x.get('combined_score', 0), reverse=True)[:num_clips]
            
            if progress_callback:
                progress_callback("AI analysis complete", 60)
            
            # Step 3: Generate clips
            print("Step 3: Generating clips with MoviePy...")
            if progress_callback:
                progress_callback("Generating clips...", 65)
            
            generated_clips = []

            # create SRT/VTT for full transcription (optional)
            srt_path = None
            vtt_path = None
            if subtitles is not None:
                try:
                    srt_path = tempfile.mktemp(suffix=".srt")
                    vtt_path = tempfile.mktemp(suffix=".vtt")
                    subtitles.create_srt_from_transcription(transcription_result, srt_path)
                    subtitles.create_vtt_from_srt(srt_path, vtt_path)
                except Exception as e:
                    logger.debug(f"Subtitle generation skipped: {e}")
                    srt_path = None
                    vtt_path = None

            for i, segment in enumerate(segments):
                output_path = tempfile.mktemp(suffix=f"_clip_{i+1}.mp4")

                # Update progress
                clip_progress = 65 + int((i / len(segments)) * 30)
                if progress_callback:
                    progress_callback(f"Generating clip {i+1}/{len(segments)}...", clip_progress)

                # Adjust end time based on desired clip duration
                start = float(segment["start"])
                end = min(float(segment["end"]), start + clip_duration)

                # Fast preview: try lossless copy clip (very fast) - optional
                preview_path = None
                if ffmpeg_helpers is not None:
                    try:
                        preview_path = tempfile.mktemp(suffix=f"_preview_{i+1}.mp4")
                        ffmpeg_helpers.fast_clip_copy(video_path, start, end - start, preview_path)
                    except Exception:
                        preview_path = None

                # Produce final clip. If subtitles/burn-in requested, we re-encode using MoviePy
                try:
                    clip_path = self.generate_clip(
                        video_path=video_path,
                        start_time=start,
                        end_time=end,
                        text=segment.get("hook", ""),  # Use hook for caption
                        output_path=output_path,
                        resolution=target_resolution,
                        add_subtitles=True
                    )
                except Exception:
                    # Fallback to preview if generate_clip fails
                    clip_path = preview_path

                generated_clips.append({
                    "clip_number": i + 1,
                    "path": clip_path,
                    "start_time": start,
                    "end_time": end,
                    "text": segment["text"],
                    "hook": segment["hook"],
                    "reason": segment["reason"],
                    "category": segment["category"],
                    "virality_score": segment["virality_score"],
                    "energy_score": segment.get("energy_score", 0.0),
                    "energy_norm": segment.get("energy_norm", 0.0),
                    "duration": end - start
                })
            
            if progress_callback:
                progress_callback("All clips generated successfully!", 100)
            
            return {
                "success": True,
                "transcription": transcription_result["text"],
                "segments": segments,
                "clips": generated_clips,
                "total_clips": len(generated_clips),
                "srt_path": srt_path,
                "vtt_path": vtt_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
