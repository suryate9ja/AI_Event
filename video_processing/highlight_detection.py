import cv2
import numpy as np
from typing import List, Dict, Any
from ultralytics import YOLO
from pathlib import Path
from .face_analyzer import FaceAnalyzer
from .audio_analyzer import AudioAnalyzer

class HighlightDetector:
    def __init__(self, 
                 model_path: str = "yolov8n.pt",
                 face_model_path: str = "yolov8n-face.pt"):
        """
        Initialize the highlight detector with YOLO model and analyzers.
        
        Args:
            model_path (str): Path to YOLO model weights
            face_model_path (str): Path to YOLO face detection model
        """
        self.model = YOLO(model_path)
        self.face_analyzer = FaceAnalyzer(face_model_path)
        self.audio_analyzer = AudioAnalyzer()
        self.important_classes = {'person', 'dancing', 'cheering', 'celebrating'}
        
    def detect_highlights(self, 
                         video_path: str,
                         min_confidence: float = 0.5,
                         min_duration: float = 2.0,
                         analyze_audio: bool = True,
                         analyze_faces: bool = True) -> List[Dict[str, Any]]:
        """
        Detect highlight moments in a video.
        
        Args:
            video_path (str): Path to input video
            min_confidence (float): Minimum confidence threshold
            min_duration (float): Minimum duration for a highlight in seconds
            analyze_audio (bool): Whether to analyze audio for applause
            analyze_faces (bool): Whether to analyze faces for reactions
            
        Returns:
            List[Dict[str, Any]]: List of highlight moments with timestamps
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        highlights = []
        current_highlight = None
        
        # Extract audio if needed
        audio_data = None
        if analyze_audio:
            audio_data, _ = self.audio_analyzer.extract_audio(video_path)
            applause_segments = self.audio_analyzer.detect_applause(audio_data)
            crowd_reactions = self.audio_analyzer.analyze_crowd_reaction(audio_data)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            timestamp = frame_number / fps
            
            # Detect objects in frame
            results = self.model(frame, conf=min_confidence)[0]
            
            # Check for important events
            important_detections = [
                det for det in results.boxes
                if results.names[int(det.cls[0])] in self.important_classes
            ]
            
            # Analyze faces if enabled
            face_analysis = None
            if analyze_faces:
                face_analysis = self.face_analyzer.detect_crowd_reaction(frame)
            
            # Check for applause if enabled
            has_applause = False
            if analyze_audio:
                for segment in applause_segments:
                    if segment['start'] <= timestamp <= segment['end']:
                        has_applause = True
                        break
            
            # Determine if this is a highlight moment
            is_highlight = (
                len(important_detections) > 0 or
                (face_analysis and face_analysis['is_crowd'] and 
                 face_analysis['reaction'] in ['positive', 'surprised']) or
                has_applause
            )
            
            if is_highlight:
                if current_highlight is None:
                    current_highlight = {
                        'start_time': timestamp,
                        'end_time': timestamp,
                        'detections': [],
                        'face_analysis': [],
                        'has_applause': False
                    }
                else:
                    current_highlight['end_time'] = timestamp
                
                # Add detections
                current_highlight['detections'].extend([
                    {
                        'class': results.names[int(det.cls[0])],
                        'confidence': float(det.conf[0])
                    }
                    for det in important_detections
                ])
                
                # Add face analysis
                if face_analysis:
                    current_highlight['face_analysis'].append(face_analysis)
                
                # Update applause status
                if has_applause:
                    current_highlight['has_applause'] = True
                    
            elif current_highlight is not None:
                # Check if highlight duration meets minimum requirement
                duration = current_highlight['end_time'] - current_highlight['start_time']
                if duration >= min_duration:
                    # Calculate average face analysis
                    if current_highlight['face_analysis']:
                        avg_face_analysis = {
                            'face_count': np.mean([f['face_count'] for f in current_highlight['face_analysis']]),
                            'happy_ratio': np.mean([f['happy_ratio'] for f in current_highlight['face_analysis']]),
                            'surprise_ratio': np.mean([f['surprise_ratio'] for f in current_highlight['face_analysis']])
                        }
                        current_highlight['avg_face_analysis'] = avg_face_analysis
                    
                    highlights.append(current_highlight)
                current_highlight = None
                
        cap.release()
        
        # Add final highlight if exists
        if current_highlight is not None:
            duration = current_highlight['end_time'] - current_highlight['start_time']
            if duration >= min_duration:
                highlights.append(current_highlight)
                
        return highlights
    
    def extract_highlight_clips(self, 
                              video_path: str,
                              highlights: List[Dict[str, Any]],
                              output_dir: str,
                              add_visualization: bool = True) -> List[str]:
        """
        Extract highlight clips from the video.
        
        Args:
            video_path (str): Path to input video
            highlights (List[Dict[str, Any]]): List of highlight moments
            output_dir (str): Directory to save highlight clips
            add_visualization (bool): Whether to add visualization overlays
            
        Returns:
            List[str]: Paths to extracted highlight clips
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        output_paths = []
        
        for i, highlight in enumerate(highlights):
            start_frame = int(highlight['start_time'] * fps)
            end_frame = int(highlight['end_time'] * fps)
            
            output_path = output_dir / f"highlight_{i+1}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            for _ in range(end_frame - start_frame):
                ret, frame = cap.read()
                if not ret:
                    break
                    
                if add_visualization:
                    # Add visualization overlays
                    if 'face_analysis' in highlight:
                        faces = self.face_analyzer.detect_faces(frame)
                        analyzed_faces = self.face_analyzer.analyze_emotions(frame, faces)
                        frame = self.face_analyzer.draw_analysis(frame, analyzed_faces)
                    
                    # Add highlight information
                    info_text = f"Duration: {highlight['end_time'] - highlight['start_time']:.1f}s"
                    if highlight.get('has_applause'):
                        info_text += " | Applause"
                    cv2.putText(frame, info_text, (10, 30),
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                out.write(frame)
                
            out.release()
            output_paths.append(str(output_path))
            
        cap.release()
        return output_paths 