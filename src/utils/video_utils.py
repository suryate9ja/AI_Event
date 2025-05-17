import cv2
import numpy as np
from typing import Tuple, List
import ffmpeg

def load_video(video_path: str) -> Tuple[cv2.VideoCapture, dict]:
    """
    Load a video file and return the video capture object and video properties.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        Tuple[cv2.VideoCapture, dict]: Video capture object and video properties
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    properties = {
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    }
    
    return cap, properties

def extract_frames(video_path: str, sample_rate: int = 1) -> List[np.ndarray]:
    """
    Extract frames from a video file at specified sample rate.
    
    Args:
        video_path (str): Path to the video file
        sample_rate (int): Extract every nth frame
        
    Returns:
        List[np.ndarray]: List of frames as numpy arrays
    """
    cap, _ = load_video(video_path)
    frames = []
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % sample_rate == 0:
            frames.append(frame)
        frame_count += 1
    
    cap.release()
    return frames

def save_video(frames: List[np.ndarray], output_path: str, fps: int = 30) -> None:
    """
    Save a list of frames as a video file.
    
    Args:
        frames (List[np.ndarray]): List of frames to save
        output_path (str): Path to save the video
        fps (int): Frames per second for the output video
    """
    if not frames:
        raise ValueError("No frames provided")
    
    height, width = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for frame in frames:
        out.write(frame)
    
    out.release()

def get_video_duration(video_path: str) -> float:
    """
    Get the duration of a video file in seconds using FFmpeg.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        float: Duration in seconds
    """
    try:
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        return duration
    except ffmpeg.Error as e:
        raise RuntimeError(f"Error getting video duration: {str(e)}") 