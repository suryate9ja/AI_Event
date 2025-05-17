from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Dict, Tuple, Any

class YOLODetector:
    def __init__(self, model_path: str = "yolov8n.pt"):
        """
        Initialize YOLO detector with specified model.
        
        Args:
            model_path (str): Path to YOLO model weights
        """
        self.model = YOLO(model_path)
        
    def detect(self, frame: np.ndarray, conf_threshold: float = 0.25) -> List[Dict[str, Any]]:
        """
        Perform object detection on a single frame.
        
        Args:
            frame (np.ndarray): Input frame
            conf_threshold (float): Confidence threshold for detections
            
        Returns:
            List[Dict[str, Any]]: List of detections with bounding boxes and class information
        """
        results = self.model(frame, conf=conf_threshold)[0]
        detections = []
        
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = results.names[class_id]
            
            detections.append({
                'bbox': (int(x1), int(y1), int(x2), int(y2)),
                'confidence': confidence,
                'class_id': class_id,
                'class_name': class_name
            })
            
        return detections
    
    def detect_video(self, video_path: str, output_path: str = None, 
                    conf_threshold: float = 0.25) -> List[List[Dict[str, Any]]]:
        """
        Perform object detection on a video file.
        
        Args:
            video_path (str): Path to input video
            output_path (str): Path to save annotated video (optional)
            conf_threshold (float): Confidence threshold for detections
            
        Returns:
            List[List[Dict[str, Any]]]: List of detections for each frame
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
            
        all_detections = []
        frame_count = 0
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Initialize video writer if output path is provided
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Perform detection
            detections = self.detect(frame, conf_threshold)
            all_detections.append(detections)
            
            # Draw detections if output video is requested
            if writer:
                for det in detections:
                    x1, y1, x2, y2 = det['bbox']
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"{det['class_name']}: {det['confidence']:.2f}"
                    cv2.putText(frame, label, (x1, y1 - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                writer.write(frame)
            
            frame_count += 1
            
        cap.release()
        if writer:
            writer.release()
            
        return all_detections 