"""
Dashboard data service
"""

import os
import json
import sys
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.config_manager import ConfigManager
from backend.services.analysis_service import AnalysisService
from backend.services.video_service import VideoService


class DashboardService:
    """Service for providing dashboard data"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.analysis_service = AnalysisService(config)
        self.video_service = VideoService(config)
    
    async def get_summary(self) -> Dict:
        """Get overall dashboard summary statistics"""
        # This is a simplified summary - in production, aggregate from all analyses
        return {
            "total_analyses": 0,
            "total_videos": 0,
            "total_issues": 0,
            "severe_issues": 0,
            "last_analysis": None
        }
    
    async def get_map_data(self, analysis_id: str) -> Dict:
        """Get geospatial data for map visualization"""
        # Get heatmap data from analysis service
        heatmap_data = await self.analysis_service.get_heatmap_data(analysis_id)
        
        # Add markers for each detection
        detections = await self.analysis_service.get_detections(analysis_id)
        
        markers = []
        for i, detection in enumerate(detections[:100]):  # Limit to first 100 for performance
            if "gps_coords" in detection:
                markers.append({
                    "id": i,
                    "lat": detection["gps_coords"][0],
                    "lon": detection["gps_coords"][1],
                    "element_type": detection.get("element_type", "unknown"),
                    "severity": detection.get("severity", "minor"),
                    "confidence": detection.get("confidence", 0.5)
                })
        
        return {
            "heatmap": heatmap_data,
            "markers": markers,
            "bounds": heatmap_data.get("bounds")
        }
    
    async def get_timeline(self, analysis_id: str) -> Dict:
        """Get temporal analysis data for timeline visualization"""
        results = await self.analysis_service.get_analysis_results(analysis_id)
        detections = results.get("detections", [])
        
        # Group by time (if available) or frame number
        timeline_data = []
        for i, detection in enumerate(detections):
            timeline_data.append({
                "frame_index": i,
                "timestamp": detection.get("timestamp", i),
                "element_type": detection.get("element_type", "unknown"),
                "severity": detection.get("severity", "minor"),
                "change_type": detection.get("change_type", "new_issue")
            })
        
        return {
            "timeline": timeline_data,
            "total_frames": len(timeline_data)
        }
    
    async def get_comparison_frames(
        self,
        analysis_id: str,
        frame_index: Optional[int] = None
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
                "severity": detection.get("severity", "minor")
            }
        else:
            return {
                "frame_index": frame_index,
                "detection": None,
                "message": "Frame index out of range"
            }
