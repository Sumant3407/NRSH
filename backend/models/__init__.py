"""Database models for Road Safety Infrastructure Analysis System

This module re-exports the concrete model classes defined in
``backend.models.database``. It also provides short-name aliases for
backwards compatibility.
"""

from backend.models.database import (
    VideoModel,
    AnalysisModel,
    DetectionModel,
    ReportModel,
    RoadSegmentModel,
)

# Backwards-compatible short names
Video = VideoModel
Analysis = AnalysisModel
Detection = DetectionModel
Report = ReportModel
RoadSegment = RoadSegmentModel

__all__ = [
    # Primary (suffixed) names
    "VideoModel",
    "AnalysisModel",
    "DetectionModel",
    "ReportModel",
    "RoadSegmentModel",
    # Backwards-compatible short names
    "Video",
    "Analysis",
    "Detection",
    "Report",
    "RoadSegment",
]

