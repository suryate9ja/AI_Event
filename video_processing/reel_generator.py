import subprocess
import os
from typing import List, Dict, Any, Optional
import json
import requests
from pathlib import Path
import tempfile

class ReelGenerator:
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        Initialize the reel generator.
        
        Args:
            ffmpeg_path (str): Path to FFmpeg executable
        """
        self.ffmpeg_path = ffmpeg_path
        
    def merge_clips(self, 
                   input_files: List[str],
                   output_file: str,
                   transition_duration: float = 0.5,
                   progress_callback: Optional[callable] = None) -> str:
        """
        Merge multiple video clips with transitions.
        
        Args:
            input_files (List[str]): List of input video files
            output_file (str): Output video file path
            transition_duration (float): Duration of transition between clips
            progress_callback (Optional[callable]): Callback function to report progress (0-100)
            
        Returns:
            str: Path to the merged video file
        """
        # Create a temporary file for the concat list
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for input_file in input_files:
                f.write(f"file '{input_file}'\n")
            concat_list = f.name
        
        try:
            # Get total duration of input files
            total_duration = 0
            for input_file in input_files:
                try:
                    # Use ffprobe instead of ffmpeg for duration
                    probe_cmd = [
                        'ffprobe',
                        '-v', 'error',
                        '-show_entries', 'format=duration',
                        '-of', 'default=noprint_wrappers=1:nokey=1',
                        input_file
                    ]
                    duration = float(subprocess.check_output(probe_cmd).decode().strip())
                    total_duration += duration
                except (subprocess.CalledProcessError, ValueError) as e:
                    print(f"Warning: Could not get duration for {input_file}: {str(e)}")
                    # Use a default duration if we can't get the actual duration
                    total_duration += 10.0  # Assume 10 seconds if duration can't be determined
            
            # Merge clips with transitions
            command = [
                self.ffmpeg_path,
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-strict', 'experimental',
                '-b:a', '192k',
                '-pix_fmt', 'yuv420p',
                output_file
            ]
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Monitor progress
            if progress_callback:
                while True:
                    output = process.stderr.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        # Extract time from FFmpeg output
                        if "time=" in output:
                            try:
                                time_str = output.split("time=")[1].split()[0]
                                hours, minutes, seconds = map(float, time_str.split(':'))
                                current_time = hours * 3600 + minutes * 60 + seconds
                                progress = min(100, int((current_time / total_duration) * 100))
                                progress_callback(progress)
                            except (ValueError, IndexError):
                                # Skip invalid time formats
                                continue
            
            process.wait()
            if process.returncode != 0:
                error_output = process.stderr.read()
                raise subprocess.CalledProcessError(
                    process.returncode,
                    command,
                    f"FFmpeg error: {error_output}"
                )
            
            return output_file
            
        finally:
            # Clean up temporary file
            os.unlink(concat_list)
    
    def add_captions(self,
                    input_file: str,
                    output_file: str,
                    captions: List[Dict[str, Any]],
                    font_size: int = 24,
                    font_color: str = "white",
                    font_file: Optional[str] = None) -> str:
        """
        Add dynamic captions to a video.
        
        Args:
            input_file (str): Input video file
            output_file (str): Output video file
            captions (List[Dict[str, Any]]): List of caption dictionaries with 'text', 'start_time', and 'end_time'
            font_size (int): Font size for captions
            font_color (str): Font color
            font_file (Optional[str]): Path to custom font file
            
        Returns:
            str: Path to the output video file
        """
        # Create a temporary file for the captions
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False) as f:
            for i, caption in enumerate(captions, 1):
                start_time = self._format_timestamp(caption['start_time'])
                end_time = self._format_timestamp(caption['end_time'])
                f.write(f"{i}\n{start_time} --> {end_time}\n{caption['text']}\n\n")
            srt_file = f.name
        
        try:
            # Build FFmpeg command
            command = [
                self.ffmpeg_path,
                '-i', input_file,
                '-vf', f"subtitles={srt_file}:force_style='FontSize={font_size},PrimaryColour=&H{font_color}'",
                '-c:a', 'copy',
                output_file
            ]
            
            if font_file:
                command[3] = f"subtitles={srt_file}:force_style='FontSize={font_size},PrimaryColour=&H{font_color},FontName={font_file}'"
            
            subprocess.run(command, check=True)
            return output_file
            
        finally:
            # Clean up temporary file
            os.unlink(srt_file)
    
    def apply_vintage_filter(self,
                           input_file: str,
                           output_file: str,
                           api_key: str,
                           filter_style: str = "vintage") -> str:
        """
        Apply a vintage filter using RunwayML API.
        
        Args:
            input_file (str): Input video file
            output_file (str): Output video file
            api_key (str): RunwayML API key
            filter_style (str): Style of filter to apply
            
        Returns:
            str: Path to the filtered video file
        """
        # Upload video to RunwayML
        upload_url = "https://api.runwayml.com/v1/upload"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        with open(input_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(upload_url, headers=headers, files=files)
            response.raise_for_status()
            video_id = response.json()['id']
        
        # Apply filter
        filter_url = f"https://api.runwayml.com/v1/filters/{filter_style}"
        data = {
            'video_id': video_id,
            'style': filter_style
        }
        
        response = requests.post(filter_url, headers=headers, json=data)
        response.raise_for_status()
        filter_id = response.json()['id']
        
        # Download processed video
        download_url = f"https://api.runwayml.com/v1/download/{filter_id}"
        response = requests.get(download_url, headers=headers)
        response.raise_for_status()
        
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        return output_file
    
    def add_title_screen(self,
                        input_file: str,
                        output_file: str,
                        title: str,
                        duration: float = 3.0,
                        background_color: str = "black",
                        font_size: int = 48,
                        font_color: str = "white") -> str:
        """
        Add a title screen to the video.
        
        Args:
            input_file (str): Input video file
            output_file (str): Output video file
            title (str): Title text
            duration (float): Duration of title screen in seconds
            background_color (str): Background color
            font_size (int): Font size
            font_color (str): Font color
            
        Returns:
            str: Path to the output video file
        """
        # Create title screen
        title_command = [
            self.ffmpeg_path,
            '-f', 'lavfi',
            '-i', f'color=c={background_color}:s=1920x1080:d={duration}',
            '-vf', f"drawtext=text='{title}':fontsize={font_size}:fontcolor={font_color}:x=(w-text_w)/2:y=(h-text_h)/2",
            '-c:v', 'libx264',
            '-t', str(duration),
            'title.mp4'
        ]
        
        subprocess.run(title_command, check=True)
        
        try:
            # Concatenate title screen with main video
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("file 'title.mp4'\n")
                f.write(f"file '{input_file}'\n")
                concat_list = f.name
            
            merge_command = [
                self.ffmpeg_path,
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list,
                '-c', 'copy',
                output_file
            ]
            
            subprocess.run(merge_command, check=True)
            return output_file
            
        finally:
            # Clean up temporary files
            os.unlink('title.mp4')
            os.unlink(concat_list)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}" 