import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
import torch
from ultralytics import YOLO
import os

class FaceAnalyzer:
    def __init__(self, face_model_path: str = "models/yolov8n-face.pt"):
        """
        Initialize the face analyzer.
        
        Args:
            face_model_path (str): Path to the YOLO face detection model
        """
        if not os.path.exists(face_model_path):
            raise FileNotFoundError(
                f"Face detection model not found at {face_model_path}. "
                "Please run download_models.py first."
            )
            
        try:
            # Load the base YOLOv8n model
            self.face_model = YOLO('yolov8n.pt')
            
            # Load the face detection weights
            state_dict = torch.load(face_model_path, map_location='cpu')
            self.face_model.model.load_state_dict(state_dict)
            
            # Set device
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.face_model.to(self.device)
            
        except Exception as e:
            raise RuntimeError(f"Error loading face detection model: {str(e)}")
        
    def detect_faces(self, frame: np.ndarray, min_confidence: float = 0.5) -> List[Dict[str, Any]]:
        """
        Detect faces in a frame.
        
        Args:
            frame (np.ndarray): Input frame
            min_confidence (float): Minimum confidence threshold for face detection
            
        Returns:
            List[Dict[str, Any]]: List of detected faces with bounding boxes and confidence scores
        """
        results = self.face_model(frame, conf=min_confidence)[0]
        faces = []
        
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = float(box.conf[0])
            faces.append({
                'bbox': (x1, y1, x2, y2),
                'confidence': confidence
            })
            
        return faces
    
    def analyze_emotions(self, frame: np.ndarray, faces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze emotions of detected faces.
        
        Args:
            frame (np.ndarray): Input frame
            faces (List[Dict[str, Any]]): List of detected faces
            
        Returns:
            List[Dict[str, Any]]: List of faces with emotion analysis
        """
        analyzed_faces = []
        for face in faces:
            x1, y1, x2, y2 = face['bbox']
            face_img = frame[y1:y2, x1:x2]
            
            # Convert to grayscale for emotion analysis
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            
            # Simple emotion detection based on facial features
            # This is a placeholder - you should implement proper emotion detection
            emotion = "neutral"
            confidence = 0.8
            
            analyzed_faces.append({
                **face,
                'emotion': emotion,
                'emotion_confidence': confidence
            })
            
        return analyzed_faces
    
    def detect_crowd_reaction(self, frame: np.ndarray, min_faces: int = 5, min_happy_ratio: float = 0.7) -> Dict[str, Any]:
        """
        Analyze crowd reaction based on face emotions.
        
        Args:
            frame (np.ndarray): Input frame
            min_faces (int): Minimum number of faces to consider for crowd reaction
            min_happy_ratio (float): Minimum ratio of happy faces to consider positive reaction
            
        Returns:
            Dict[str, Any]: Crowd reaction analysis
        """
        faces = self.detect_faces(frame)
        if len(faces) < min_faces:
            return {
                'reaction': 'neutral',
                'confidence': 0.0,
                'face_count': len(faces)
            }
        
        analyzed_faces = self.analyze_emotions(frame, faces)
        happy_faces = sum(1 for face in analyzed_faces if face['emotion'] == 'happy')
        happy_ratio = happy_faces / len(analyzed_faces)
        
        reaction = 'positive' if happy_ratio >= min_happy_ratio else 'neutral'
        confidence = happy_ratio if reaction == 'positive' else 1 - happy_ratio
        
        return {
            'reaction': reaction,
            'confidence': confidence,
            'face_count': len(faces),
            'happy_ratio': happy_ratio
        }
    
    def draw_analysis(self, frame: np.ndarray, analyzed_faces: List[Dict[str, Any]]) -> np.ndarray:
        """
        Draw face detection and emotion analysis results on the frame.
        
        Args:
            frame (np.ndarray): Input frame
            analyzed_faces (List[Dict[str, Any]]): List of analyzed faces
            
        Returns:
            np.ndarray: Frame with visualization
        """
        for face in analyzed_faces:
            x1, y1, x2, y2 = face['bbox']
            emotion = face['emotion']
            confidence = face['confidence']
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw emotion label
            label = f"{emotion} ({confidence:.2f})"
            cv2.putText(frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
        return frame 