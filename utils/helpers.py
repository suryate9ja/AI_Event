import os
import json
from pathlib import Path
from typing import Dict, Any, List
import cv2
import numpy as np
from datetime import datetime

def ensure_dir(directory: str) -> Path:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory (str): Directory path
        
    Returns:
        Path: Path object for the directory
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path

def save_json(data: Dict[str, Any], filepath: str) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data (Dict[str, Any]): Data to save
        filepath (str): Path to save the JSON file
    """
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def load_json(filepath: str) -> Dict[str, Any]:
    """
    Load data from a JSON file.
    
    Args:
        filepath (str): Path to the JSON file
        
    Returns:
        Dict[str, Any]: Loaded data
    """
    with open(filepath, 'r') as f:
        return json.load(f)

def get_video_info(video_path: str) -> Dict[str, Any]:
    """
    Get information about a video file.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        Dict[str, Any]: Video information
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    info = {
        'fps': cap.get(cv2.CAP_PROP_FPS),
        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'duration': int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
    }
    
    cap.release()
    return info

def generate_timestamp() -> str:
    """
    Generate a timestamp string for file naming.
    
    Returns:
        str: Timestamp string
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def list_video_files(directory: str, extensions: List[str] = None) -> List[str]:
    """
    List video files in a directory.
    
    Args:
        directory (str): Directory to search
        extensions (List[str]): List of video file extensions to include
        
    Returns:
        List[str]: List of video file paths
    """
    if extensions is None:
        extensions = ['.mp4', '.avi', '.mov', '.mkv']
        
    video_files = []
    for ext in extensions:
        video_files.extend(list(Path(directory).glob(f"*{ext}")))
    
    return [str(f) for f in video_files]

def resize_frame(frame: np.ndarray, max_size: int = 1280) -> np.ndarray:
    """
    Resize a frame while maintaining aspect ratio.
    
    Args:
        frame (np.ndarray): Input frame
        max_size (int): Maximum dimension size
        
    Returns:
        np.ndarray: Resized frame
    """
    height, width = frame.shape[:2]
    
    if max(height, width) <= max_size:
        return frame
        
    scale = max_size / max(height, width)
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    return cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

def create_thumbnail(video_path: str, output_path: str, frame_number: int = 0) -> str:
    """
    Create a thumbnail from a video frame.
    
    Args:
        video_path (str): Path to the video file
        output_path (str): Path to save the thumbnail
        frame_number (int): Frame number to use for thumbnail
        
    Returns:
        str: Path to the saved thumbnail
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
        
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise ValueError(f"Could not read frame {frame_number}")
        
    # Resize frame if needed
    frame = resize_frame(frame)
    
    # Save thumbnail
    cv2.imwrite(output_path, frame)
    return output_path 