import os
import json
import tempfile
import whisper
import openai
from pytube import YouTube
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.fx.crop import crop
from typing import List, Dict, Optional
import requests


class VideoProcessor:
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.whisper_model = None
        openai.api_key = openai_api_key
    
    def load_whisper_model(self):
        """Load Whisper model for transcription"""
        if self.whisper_model is None:
            print("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
        return self.whisper_model
    
    def download_youtube_video(self, url: str) -> str:
        """Download YouTube video and return local path"""
        try:
            yt = YouTube(url)
            stream = (
                yt.streams.filter(file_extension="mp4", progressive=True)
                .order_by("resolution")
                .desc()
                .first()
            )
            
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            temp_path = temp_file.name
            temp_file.close()
            
            # Download to temp location
            stream.download(
                output_path=os.path.dirname(temp_path),
                filename=os.path.basename(temp_path)
            )
            
            return temp_path
        except Exception as e:
            raise Exception(f"Failed to download YouTube video: {str(e)}")
    
    def download_video_from_url(self, url: str) -> str:
        """Download video from direct URL"""
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            temp_path = temp_file.name
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return temp_path
        except Exception as e:
            raise Exception(f"Failed to download video from URL: {str(e)}")
    
    def transcribe_video(self, video_path: str) -> Dict:
        """Transcribe video using Whisper"""
        try:
            model = self.load_whisper_model()
            print(f"Transcribing video: {video_path}")
            result = model.transcribe(video_path)
            return result
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def get_viral_segments(self, transcription: str, num_clips: int = 5) -> List[Dict]:
        """Use GPT to identify viral-worthy segments"""
        try:
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            prompt = f'''You are a viral video expert. Analyze this video transcription and identify the top {num_clips} most engaging moments.

Look for:
- Controversial or surprising statements
- Emotional peaks (excitement, shock, humor)
- Quotable moments
- Story climaxes or revelations
- Strong opinions or hot takes

For each moment, provide:
1. Start time in seconds (as a number)
2. End time in seconds (as a number)
3. The exact text from that segment
4. A brief reason why it's viral-worthy

Return ONLY a valid JSON array with this structure:
[
  {{
    "start": 10.5,
    "end": 25.3,
    "text": "exact quote from video",
    "reason": "why this is viral"
  }}
]

Transcription:
{transcription}

Return only the JSON array, no other text.'''

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that returns only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            segments = json.loads(content)
            return segments
            
        except Exception as e:
            raise Exception(f"AI segment selection failed: {str(e)}")
    
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
            # Load video
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
                # Create text clip
                txt_clip = TextClip(
                    text,
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
        resolution: str = "portrait"
    ) -> Dict:
        """Complete pipeline: transcribe -> identify segments -> generate clips"""
        
        # Resolution presets
        resolutions = {
            "portrait": (1080, 1920),  # 9:16 for TikTok/Reels
            "landscape": (1920, 1080),  # 16:9 for YouTube
            "square": (1080, 1080)      # 1:1 for Instagram
        }
        
        target_resolution = resolutions.get(resolution, resolutions["portrait"])
        
        try:
            # Step 1: Transcribe
            print("Step 1: Transcribing video...")
            transcription_result = self.transcribe_video(video_path)
            full_text = transcription_result["text"]
            
            # Step 2: Get viral segments
            print("Step 2: Identifying viral segments with AI...")
            segments = self.get_viral_segments(full_text, num_clips)
            
            # Step 3: Generate clips
            print("Step 3: Generating clips...")
            generated_clips = []
            
            for i, segment in enumerate(segments):
                output_path = tempfile.mktemp(suffix=f"_clip_{i+1}.mp4")
                
                # Adjust end time based on desired clip duration
                start = segment["start"]
                end = min(segment["end"], start + clip_duration)
                
                clip_path = self.generate_clip(
                    video_path=video_path,
                    start_time=start,
                    end_time=end,
                    text=segment["text"][:100],  # Limit subtitle length
                    output_path=output_path,
                    resolution=target_resolution,
                    add_subtitles=True
                )
                
                generated_clips.append({
                    "clip_number": i + 1,
                    "path": clip_path,
                    "start_time": start,
                    "end_time": end,
                    "text": segment["text"],
                    "reason": segment.get("reason", ""),
                    "duration": end - start
                })
            
            return {
                "success": True,
                "transcription": full_text,
                "segments": segments,
                "clips": generated_clips,
                "total_clips": len(generated_clips)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
