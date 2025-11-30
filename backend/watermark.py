"""
Watermark service for preview clips
Creates watermarked versions of clips for non-paid users
"""

import os
import tempfile
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import moviepy
try:
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    logger.warning("MoviePy not available - watermarking disabled")


def create_watermarked_preview(
    input_path: str,
    output_path: Optional[str] = None,
    watermark_text: str = "ClipGen Preview",
    opacity: float = 0.7
) -> Optional[str]:
    """
    Create a watermarked preview version of a clip
    
    Args:
        input_path: Path to original clip
        output_path: Path for watermarked output (auto-generated if None)
        watermark_text: Text to overlay
        opacity: Watermark opacity (0-1)
    
    Returns:
        Path to watermarked file, or None if failed
    """
    if not MOVIEPY_AVAILABLE:
        logger.warning("MoviePy not available, returning original path")
        return input_path
    
    if not os.path.exists(input_path):
        logger.error(f"Input file not found: {input_path}")
        return None
    
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_preview{ext}"
    
    try:
        # Load video
        video = VideoFileClip(input_path)
        
        # Create watermark text
        txt_clip = TextClip(
            watermark_text,
            fontsize=50,
            color='white',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=2
        ).set_opacity(opacity)
        
        # Position in center
        txt_clip = txt_clip.set_position('center')
        txt_clip = txt_clip.set_duration(video.duration)
        
        # Create diagonal repeating watermark effect
        watermarks = []
        positions = [
            ('center', 'center'),
            (0.2, 0.3),
            (0.8, 0.3),
            (0.2, 0.7),
            (0.8, 0.7),
        ]
        
        for pos in positions:
            wm = TextClip(
                watermark_text,
                fontsize=30,
                color='white',
                font='Arial',
                stroke_color='black',
                stroke_width=1
            ).set_opacity(opacity * 0.5)
            
            if isinstance(pos[0], float):
                wm = wm.set_position((pos[0], pos[1]), relative=True)
            else:
                wm = wm.set_position(pos)
            
            wm = wm.set_duration(video.duration)
            watermarks.append(wm)
        
        # Composite
        final = CompositeVideoClip([video] + watermarks + [txt_clip])
        
        # Write output
        final.write_videofile(
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
        final.close()
        
        logger.info(f"Created watermarked preview: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Watermarking failed: {e}")
        return None


def create_preview_thumbnail(
    video_path: str,
    output_path: Optional[str] = None,
    timestamp: float = 1.0
) -> Optional[str]:
    """
    Create a thumbnail from video with watermark
    
    Args:
        video_path: Path to video
        output_path: Path for thumbnail (auto-generated if None)
        timestamp: Time in seconds to capture
    
    Returns:
        Path to thumbnail, or None if failed
    """
    if not MOVIEPY_AVAILABLE:
        return None
    
    if output_path is None:
        base, _ = os.path.splitext(video_path)
        output_path = f"{base}_thumb.jpg"
    
    try:
        video = VideoFileClip(video_path)
        
        # Get frame at timestamp
        frame_time = min(timestamp, video.duration - 0.1)
        frame = video.get_frame(frame_time)
        
        # Save frame
        from PIL import Image, ImageDraw, ImageFont
        img = Image.fromarray(frame)
        
        # Add watermark
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        text = "ClipGen Preview"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (img.width - text_width) // 2
        y = (img.height - text_height) // 2
        
        # Draw text with shadow
        draw.text((x+2, y+2), text, fill=(0, 0, 0, 128), font=font)
        draw.text((x, y), text, fill=(255, 255, 255, 200), font=font)
        
        img.save(output_path, "JPEG", quality=85)
        
        video.close()
        
        logger.info(f"Created thumbnail: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Thumbnail creation failed: {e}")
        return None
