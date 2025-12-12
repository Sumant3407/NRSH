import sys
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.config_manager import ConfigManager


# Class: ChangeDetector
class ChangeDetector:
    """Detect changes between base and present detections

    Notes:
    - Detections are expected to be dicts with at least `bbox`, `confidence`,
      and optionally `area` and `element_type` keys.
    - Matching is performed per-element-type using IoU. Unmatched present
      detections are treated as "new issues" and unmatched base detections
      as "fixed".
    - Deterioration is computed using both confidence and area changes with
      safe numeric coercion to avoid exceptions on malformed model output.
    """

    # Function: __init__
    def __init__(self, config: ConfigManager):
        self.config = config
        self.similarity_threshold = config.get(
            "models.change_detection.similarity_threshold", 0.85
        )
        self.change_threshold = config.get(
            "models.change_detection.change_threshold", 0.3
        )

    async def detect_changes(
        self, base_detections: List[Dict], present_detections: List[Dict]
    ) -> List[Dict]:
        """
        Detect changes between base and present detections

        Args:
            base_detections: Detections from base (reference) frame
            present_detections: Detections from present (current) frame

        Returns:
            List of change detections with severity classification
        """
        changes = []

        base_by_type = self._group_by_type(base_detections)
        present_by_type = self._group_by_type(present_detections)

        for element_type, present_dets in present_by_type.items():
            base_dets = base_by_type.get(element_type, [])

            matched_pairs = self._match_detections(base_dets, present_dets)
            unmatched_present = self._get_unmatched(
                present_dets, matched_pairs, "present"
            )

            for det in unmatched_present:
                change = {
                    "element_type": element_type,
                    "bbox": det["bbox"],
                    "confidence": det["confidence"],
                    "change_type": "new_issue",
                    "severity": self._classify_severity(det),
                    "base_detection": None,
                    "present_detection": det,
                }
                changes.append(change)

            for base_det, present_det in matched_pairs:
                if self._is_deteriorated(base_det, present_det):
                    change = {
                        "element_type": element_type,
                        "bbox": present_det["bbox"],
                        "confidence": present_det["confidence"],
                        "change_type": "deteriorated",
                        "severity": self._classify_severity(present_det),
                        "base_detection": base_det,
                        "present_detection": present_det,
                        "deterioration_score": self._calculate_deterioration(
                            base_det, present_det
                        ),
                    }
                    changes.append(change)

        for element_type, base_dets in base_by_type.items():
            present_dets = present_by_type.get(element_type, [])
            matched_pairs = self._match_detections(base_dets, present_dets)
            unmatched_base = self._get_unmatched(base_dets, matched_pairs, "base")

            for det in unmatched_base:
                change = {
                    "element_type": element_type,
                    "bbox": det["bbox"],
                    "confidence": det["confidence"],
                    "change_type": "fixed",
                    "severity": "minor",  # Fixed issues are less critical
                    "base_detection": det,
                    "present_detection": None,
                }
                changes.append(change)

        return changes

    # Function: _group_by_type
    def _group_by_type(self, detections: List[Dict]) -> Dict[str, List[Dict]]:
        """Group detections by element type"""
        grouped = {}
        for det in detections:
            element_type = det.get("element_type", "unknown")
            if element_type not in grouped:
                grouped[element_type] = []
            grouped[element_type].append(det)
        return grouped

    # Function: _match_detections
    def _match_detections(
        self,
        base_dets: List[Dict],
        present_dets: List[Dict],
        iou_threshold: float = 0.3,
    ) -> List[Tuple[Dict, Dict]]:
        """Match detections between base and present using IoU"""
        matched_pairs = []
        used_present = set()

        for base_det in base_dets:
            best_match = None
            best_iou = 0

            for i, present_det in enumerate(present_dets):
                if i in used_present:
                    continue

                iou = self._calculate_iou(base_det["bbox"], present_det["bbox"])

                if iou > best_iou and iou >= iou_threshold:
                    best_iou = iou
                    best_match = (base_det, present_det, i)

            if best_match:
                matched_pairs.append((best_match[0], best_match[1]))
                used_present.add(best_match[2])

        return matched_pairs

    # Function: _calculate_iou
    def _calculate_iou(self, bbox1: List[float], bbox2: List[float]) -> float:
        """Calculate Intersection over Union (IoU) between two bounding boxes"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2

        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)

        if x2_i < x1_i or y2_i < y1_i:
            return 0.0

        intersection = (x2_i - x1_i) * (y2_i - y1_i)

        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection

        if union == 0:
            return 0.0

        return intersection / union

    # Function: _get_unmatched
    def _get_unmatched(
        self, detections: List[Dict], matched_pairs: List[Tuple[Dict, Dict]], side: str
    ) -> List[Dict]:
        """Get unmatched detections"""
        matched_dets = set()
        if side == "base":
            matched_dets = {id(base) for base, _ in matched_pairs}
        else:
            matched_dets = {id(present) for _, present in matched_pairs}

        return [det for det in detections if id(det) not in matched_dets]

    # Function: _is_deteriorated
    def _is_deteriorated(self, base_det: Dict, present_det: Dict) -> bool:
        """Check if issue has deteriorated"""

        # Function: _safe_float
        def _safe_float(value):
            try:
                return float(value) if value is not None else 0.0
            except Exception:
                return 0.0

        base_conf = _safe_float(base_det.get("confidence", 0))
        present_conf = _safe_float(present_det.get("confidence", 0))

        base_area = max(0.0, _safe_float(base_det.get("area", 0)))
        present_area = max(0.0, _safe_float(present_det.get("area", 0)))

        conf_increase = present_conf - base_conf

        denom = base_area if base_area > 1e-6 else 1.0
        area_increase = (present_area - base_area) / denom

        return (conf_increase > self.change_threshold) or (area_increase > 0.3)

    # Function: _calculate_deterioration
    def _calculate_deterioration(self, base_det: Dict, present_det: Dict) -> float:
        """Calculate deterioration score"""

        # Function: _safe_float
        def _safe_float(value):
            try:
                return float(value) if value is not None else 0.0
            except Exception:
                return 0.0

        base_conf = _safe_float(base_det.get("confidence", 0))
        present_conf = _safe_float(present_det.get("confidence", 0))

        base_area = max(0.0, _safe_float(base_det.get("area", 0)))
        present_area = max(0.0, _safe_float(present_det.get("area", 0)))

        conf_score = max(0.0, present_conf - base_conf)

        denom = base_area if base_area > 1e-6 else 1.0
        raw_area_score = max(0.0, (present_area - base_area) / denom)
        area_score = min(raw_area_score, 1.0)

        return conf_score * 0.6 + area_score * 0.4

    # Function: _classify_severity
    def _classify_severity(self, detection: Dict) -> str:
        """Classify severity based on detection characteristics"""
        confidence = detection.get("confidence", 0.5)
        area = detection.get("area", 0)

        normalized_area = min(1.0, area / (1280 * 720))

        severity_score = confidence * 0.6 + normalized_area * 0.4

        if severity_score > 0.7:
            return "severe"
        elif severity_score > 0.4:
            return "moderate"
        else:
            return "minor"
