import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.analysis_service import AnalysisService
from backend.services.config_manager import ConfigManager
from backend.services.errors import ServiceError
from backend.services.video_service import VideoService


# Class: DashboardService
class DashboardService:
    """Service for providing dashboard data"""

    # Function: __init__
    def __init__(self, config: ConfigManager):
        self.config = config
        self.analysis_service = AnalysisService(config)
        self.video_service = VideoService(config)

    async def get_summary(self) -> Dict:
        """Get overall dashboard summary statistics"""
        return {
            "total_analyses": 0,
            "total_videos": 0,
            "total_issues": 0,
            "severe_issues": 0,
            "last_analysis": None,
        }

    async def get_map_data(self, analysis_id: str) -> Dict:
        """Get geospatial data for map visualization"""
        try:
            heatmap_data = await self.analysis_service.get_heatmap_data(analysis_id)

            detections = await self.analysis_service.get_detections(analysis_id)

            markers = []
            for i, detection in enumerate(
                detections[:100]
            ):  # Limit to first 100 for performance
                gps = detection.get("gps_coords")
                if not gps or not isinstance(gps, (list, tuple)) or len(gps) < 2:
                    continue

                lat, lon = gps[0], gps[1]

                try:
                    lat_f = float(lat)
                    lon_f = float(lon)
                except Exception:
                    continue

                if math.isnan(lat_f) or math.isnan(lon_f):
                    continue

                markers.append(
                    {
                        "id": i,
                        "lat": lat_f,
                        "lon": lon_f,
                        "element_type": detection.get("element_type", "unknown"),
                        "severity": detection.get("severity", "minor"),
                        "confidence": detection.get("confidence", 0.5),
                    }
                )

            return {
                "heatmap": heatmap_data,
                "markers": markers,
                "bounds": heatmap_data.get("bounds"),
            }
        except Exception as exc:
            raise ServiceError(
                "DASHBOARD_MAP_DATA_ERROR", "Failed to build map data", details=str(exc)
            )

    async def get_timeline(self, analysis_id: str) -> Dict:
        """Get temporal analysis data for timeline visualization"""
        results = await self.analysis_service.get_analysis_results(analysis_id)
        detections = results.get("detections", [])

        timeline_data = []
        for i, detection in enumerate(detections):
            timeline_data.append(
                {
                    "frame_index": i,
                    "timestamp": detection.get("timestamp", i),
                    "element_type": detection.get("element_type", "unknown"),
                    "severity": detection.get("severity", "minor"),
                    "change_type": detection.get("change_type", "new_issue"),
                }
            )

        return {"timeline": timeline_data, "total_frames": len(timeline_data)}

    async def get_comparison_frames(
        self, analysis_id: str, frame_index: Optional[int] = None
    ) -> Dict:
        """Get before-after comparison frames"""
        results = await self.analysis_service.get_analysis_results(analysis_id)
        detections = results.get("detections", [])

        if frame_index is None:
            frame_index = 0

        if frame_index < len(detections):
            detection = detections[frame_index]
            return {
                "frame_index": frame_index,
                "detection": detection,
                "base_detection": detection.get("base_detection"),
                "present_detection": detection.get("present_detection"),
                "change_type": detection.get("change_type", "new_issue"),
                "severity": detection.get("severity", "minor"),
            }
        else:
            return {
                "frame_index": frame_index,
                "detection": None,
                "message": "Frame index out of range",
            }
