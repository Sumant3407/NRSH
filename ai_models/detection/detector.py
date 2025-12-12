import sys
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import numpy as np
import torch

_original_torch_load = torch.load


# Function: _patched_torch_load
def _patched_torch_load(*args, **kwargs):
    """Patched torch.load that defaults weights_only=False for YOLO compatibility"""
    if "weights_only" not in kwargs:
        kwargs["weights_only"] = False
    return _original_torch_load(*args, **kwargs)


torch.load = _patched_torch_load

from ultralytics import YOLO

try:
    from ultralytics.nn.tasks import DetectionModel

    if hasattr(torch.serialization, "add_safe_globals"):
        torch.serialization.add_safe_globals([DetectionModel])
except (ImportError, AttributeError):
    pass

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.config_manager import ConfigManager


# Class: ObjectDetector
class ObjectDetector:
    """YOLOv8-based object detector for road infrastructure"""

    # Function: __init__
    def __init__(self, config: ConfigManager):
        self.config = config
        self.model_path = config.get("models.detection.yolo_model", "yolov8n.pt")
        self.confidence_threshold = config.get(
            "models.detection.confidence_threshold", 0.5
        )
        self.iou_threshold = config.get("models.detection.iou_threshold", 0.45)
        self.input_size = config.get("models.detection.input_size", [640, 640])

        self.model = self._load_model()

        self.class_mapping = self._get_class_mapping()

    # Function: _load_model
    def _load_model(self) -> YOLO:
        """Load YOLOv8 model"""
        model_path = Path(self.model_path)

        if not model_path.exists():
            models_dir = Path(self.config.get("storage.models_dir", "models"))
            models_dir.mkdir(parents=True, exist_ok=True)
            model_path = models_dir / self.model_path

        try:
            model = YOLO(str(model_path))
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            try:
                return YOLO(self.model_path)
            except Exception as e2:
                print(f"Error loading fallback model: {e2}")
                raise

    # Function: _get_class_mapping
    def _get_class_mapping(self) -> Dict[int, str]:
        """Map YOLO class IDs to road infrastructure elements"""
        return {
            0: "pavement_crack",  # person -> pavement_crack (example mapping)
            1: "faded_marking",  # bicycle -> faded_marking
            2: "missing_stud",  # car -> missing_stud
            3: "damaged_sign",  # motorcycle -> damaged_sign
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
        results = self.model.predict(
            frame,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            imgsz=self.input_size,
            verbose=False,
        )

        detections = []

        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for box in boxes:
                try:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                except Exception:
                    try:
                        coords = box.xywh[0].cpu().numpy()  # x, y, w, h
                        cx, cy, w, h = coords
                        x1, y1 = cx - w / 2, cy - h / 2
                        x2, y2 = cx + w / 2, cy + h / 2
                    except Exception:
                        x1 = y1 = x2 = y2 = 0.0
                    try:
                        confidence = float(getattr(box, "conf", [0])[0])
                    except Exception:
                        confidence = 0.0
                    try:
                        class_id = int(getattr(box, "cls", [0])[0])
                    except Exception:
                        class_id = 0

                element_type = self.class_mapping.get(class_id, f"unknown_{class_id}")

                try:
                    bbox = [float(x1), float(y1), float(x2), float(y2)]
                    width = max(0.0, bbox[2] - bbox[0])
                    height = max(0.0, bbox[3] - bbox[1])
                    area = float(width * height)
                except Exception:
                    bbox = [0.0, 0.0, 0.0, 0.0]
                    area = 0.0

                detection = {
                    "element_type": element_type,
                    "bbox": bbox,
                    "confidence": confidence,
                    "class_id": class_id,
                    "area": area,
                }

                detections.append(detection)

        return detections

    # Function: classify_severity
    def classify_severity(self, detection: Dict, frame: np.ndarray) -> str:
        """
        Classify severity of detected issue

        Args:
            detection: Detection dictionary
            frame: Image frame for context

        Returns:
            Severity level: "minor", "moderate", or "severe"
        """

        confidence = detection.get("confidence", 0.5)
        area = detection.get("area", 0)

        normalized_area = area / (1280 * 720)

        severity_score = confidence * 0.6 + normalized_area * 0.4

        if severity_score > 0.7:
            return "severe"
        elif severity_score > 0.4:
            return "moderate"
        else:
            return "minor"


# Class: RoadInfrastructureDetector
class RoadInfrastructureDetector(ObjectDetector):
    """Custom trained detector for road infrastructure elements"""

    # Function: __init__
    def __init__(self, config: ConfigManager, model_path: str):
        self.config = config
        self.model_path = model_path
        self.confidence_threshold = config.get(
            "models.detection.confidence_threshold", 0.5
        )
        self.iou_threshold = config.get("models.detection.iou_threshold", 0.45)

        self.model = YOLO(model_path)

        self.class_names = [
            "pavement_crack",
            "faded_marking",
            "missing_stud",
            "damaged_sign",
            "roadside_furniture_damage",
            "vru_path_obstruction",
        ]

    # Function: _get_class_mapping
    def _get_class_mapping(self) -> Dict[int, str]:
        """Map class IDs to road infrastructure elements"""
        return {i: name for i, name in enumerate(self.class_names)}
