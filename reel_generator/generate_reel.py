import ffmpeg
import json
from pathlib import Path
from typing import List, Dict, Any
import random

class ReelGenerator:
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the reel generator.
        
        Args:
            output_dir (str): Directory to save generated reels
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def create_reel(self, 
                   clips: List[str],
                   output_name: str,
                   duration: float = 60.0,
                   transition_duration: float = 1.0,
                   music_path: str = None) -> str:
        """
        Create a highlight reel from video clips.
        
        Args:
            clips (List[str]): List of video clip paths
            output_name (str): Name of the output reel
            duration (float): Target duration of the reel in seconds
            transition_duration (float): Duration of transitions between clips
            music_path (str): Path to background music (optional)
            
        Returns:
            str: Path to the generated reel
        """
        output_path = self.output_dir / f"{output_name}.mp4"
        
        # Calculate clip durations
        total_clips = len(clips)
        clip_duration = (duration - (transition_duration * (total_clips - 1))) / total_clips
        
        # Create filter complex for transitions
        filter_complex = []
        inputs = []
        
        for i, clip in enumerate(clips):
            # Add input
            inputs.append(f"[{i}:v]")
            
            # Add clip with duration
            filter_complex.append(f"[{i}:v]trim=0:{clip_duration},setpts=PTS-STARTPTS[v{i}];")
            
            # Add transition if not last clip
            if i < total_clips - 1:
                filter_complex.append(
                    f"[v{i}][{i+1}:v]xfade=transition=fade:duration={transition_duration}:"
                    f"offset={clip_duration * (i+1) - transition_duration}[v{i+1}];"
                )
        
        # Add audio if provided
        if music_path:
            # Get music duration
            probe = ffmpeg.probe(music_path)
            music_duration = float(probe['format']['duration'])
            
            # Trim music to match video duration
            filter_complex.append(
                f"[{total_clips}:a]atrim=0:{duration},asetpts=PTS-STARTPTS[a];"
            )
            
            # Mix audio from clips and music
            filter_complex.append(
                f"[a]amix=inputs=1:duration=first[aout]"
            )
        
        # Combine all clips
        filter_complex.append(f"[v{total_clips-1}]")
        
        # Build FFmpeg command
        stream = ffmpeg.input('pipe:', format='rawvideo', pix_fmt='rgb24')
        
        for clip in clips:
            stream = ffmpeg.input(clip)
        
        if music_path:
            stream = ffmpeg.input(music_path)
        
        # Apply filters and output
        stream = ffmpeg.output(
            stream,
            str(output_path),
            vcodec='libx264',
            acodec='aac',
            filter_complex=''.join(filter_complex),
            preset='medium',
            movflags='faststart'
        )
        
        # Run FFmpeg
        stream.run(overwrite_output=True)
        
        return str(output_path)
    
    def add_effects(self, 
                   video_path: str,
                   effects: List[Dict[str, Any]]) -> str:
        """
        Add effects to a video.
        
        Args:
            video_path (str): Path to input video
            effects (List[Dict[str, Any]]): List of effects to apply
            
        Returns:
            str: Path to the processed video
        """
        output_path = self.output_dir / f"effects_{Path(video_path).name}"
        
        # Build filter complex for effects
        filter_complex = []
        
        for effect in effects:
            effect_type = effect['type']
            if effect_type == 'speed':
                filter_complex.append(f"setpts={1/effect['value']}*PTS")
            elif effect_type == 'brightness':
                filter_complex.append(f"eq=brightness={effect['value']}")
            elif effect_type == 'contrast':
                filter_complex.append(f"eq=contrast={effect['value']}")
            elif effect_type == 'saturation':
                filter_complex.append(f"eq=saturation={effect['value']}")
        
        # Apply effects
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.output(
            stream,
            str(output_path),
            vf=','.join(filter_complex),
            acodec='copy'
        )
        
        # Run FFmpeg
        stream.run(overwrite_output=True)
        
        return str(output_path)
    
    def add_text_overlay(self,
                        video_path: str,
                        text: str,
                        position: str = 'bottom',
                        font_size: int = 24,
                        color: str = 'white') -> str:
        """
        Add text overlay to a video.
        
        Args:
            video_path (str): Path to input video
            text (str): Text to overlay
            position (str): Position of text ('top', 'bottom', 'center')
            font_size (int): Font size
            color (str): Text color
            
        Returns:
            str: Path to the processed video
        """
        output_path = self.output_dir / f"text_{Path(video_path).name}"
        
        # Calculate position
        if position == 'top':
            y_pos = 50
        elif position == 'bottom':
            y_pos = 'h-th-50'
        else:  # center
            y_pos = '(h-th)/2'
        
        # Build filter complex
        filter_complex = (
            f"drawtext=text='{text}':fontsize={font_size}:"
            f"fontcolor={color}:x=(w-tw)/2:y={y_pos}"
        )
        
        # Apply text overlay
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.output(
            stream,
            str(output_path),
            vf=filter_complex,
            acodec='copy'
        )
        
        # Run FFmpeg
        stream.run(overwrite_output=True)
        
        return str(output_path) 