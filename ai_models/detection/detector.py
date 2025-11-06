"""
Object detection using YOLOv8 for road infrastructure elements
"""

import cv2
import numpy as np
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from ultralytics import YOLO
import torch

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.config_manager import ConfigManager


class ObjectDetector:
    """YOLOv8-based object detector for road infrastructure"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.model_path = config.get("models.detection.yolo_model", "yolov8n.pt")
        self.confidence_threshold = config.get("models.detection.confidence_threshold", 0.5)
        self.iou_threshold = config.get("models.detection.iou_threshold", 0.45)
        self.input_size = config.get("models.detection.input_size", [640, 640])
        
        # Load model
        self.model = self._load_model()
        
        # Map class IDs to road infrastructure elements
        self.class_mapping = self._get_class_mapping()
    
    def _load_model(self) -> YOLO:
        """Load YOLOv8 model"""
        model_path = Path(self.model_path)
        
        # If model doesn't exist locally, download it
        if not model_path.exists():
            models_dir = Path(self.config.get("storage.models_dir", "models"))
            models_dir.mkdir(parents=True, exist_ok=True)
            model_path = models_dir / self.model_path
        
        try:
            model = YOLO(str(model_path))
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            # Fallback to pretrained model
            return YOLO(self.model_path)
    
    def _get_class_mapping(self) -> Dict[int, str]:
        """Map YOLO class IDs to road infrastructure elements"""
        # This is a simplified mapping - in production, you'd train a custom model
        # or use a more sophisticated mapping
        return {
            0: "pavement_crack",  # person -> pavement_crack (example mapping)
            1: "faded_marking",   # bicycle -> faded_marking
            2: "missing_stud",    # car -> missing_stud
            3: "damaged_sign",    # motorcycle -> damaged_sign
            4: "roadside_furniture_damage",  # airplane -> furniture
            5: "vru_path_obstruction",  # bus -> vru_path
        }
    
    async def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect objects in a frame
        
        Args:
            frame: Input image frame (BGR format)
        
        Returns:
            List of detections with bbox, confidence, class
        """
        # Run inference
        results = self.model.predict(
            frame,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            imgsz=self.input_size,
            verbose=False
        )
        
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            
            for box in boxes:
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())
                
                # Map to road infrastructure element
                element_type = self.class_mapping.get(
                    class_id, f"unknown_{class_id}"
                )
                
                detection = {
                    "element_type": element_type,
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "confidence": confidence,
                    "class_id": class_id,
                    "area": (x2 - x1) * (y2 - y1)
                }
                
                detections.append(detection)
        
        return detections
    
    def classify_severity(
        self,
        detection: Dict,
        frame: np.ndarray
    ) -> str:
        """
        Classify severity of detected issue
        
        Args:
            detection: Detection dictionary
            frame: Image frame for context
        
        Returns:
            Severity level: "minor", "moderate", or "severe"
        """
        # Simple heuristic-based severity classification
        # In production, use a trained classifier
        
        confidence = detection.get("confidence", 0.5)
        area = detection.get("area", 0)
        
        # Normalize area (assuming 1280x720 frame)
        normalized_area = area / (1280 * 720)
        
        # Combine confidence and area for severity
        severity_score = confidence * 0.6 + normalized_area * 0.4
        
        if severity_score > 0.7:
            return "severe"
        elif severity_score > 0.4:
            return "moderate"
        else:
            return "minor"


# Custom model for road infrastructure (placeholder for training script)
class RoadInfrastructureDetector(ObjectDetector):
    """Custom trained detector for road infrastructure elements"""
    
    def __init__(self, config: ConfigManager, model_path: str):
        self.config = config
        self.model_path = model_path
        self.confidence_threshold = config.get("models.detection.confidence_threshold", 0.5)
        self.iou_threshold = config.get("models.detection.iou_threshold", 0.45)
        
        # Load custom trained model
        self.model = YOLO(model_path)
        
        # Custom class names for road infrastructure
        self.class_names = [
            "pavement_crack",
            "faded_marking",
            "missing_stud",
            "damaged_sign",
            "roadside_furniture_damage",
            "vru_path_obstruction"
        ]
    
    def _get_class_mapping(self) -> Dict[int, str]:
        """Map class IDs to road infrastructure elements"""
        return {i: name for i, name in enumerate(self.class_names)}

