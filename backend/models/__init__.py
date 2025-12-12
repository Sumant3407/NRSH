from backend.models.database import (
    AnalysisModel,
    DetectionModel,
    ReportModel,
    RoadSegmentModel,
    VideoModel,
)

Video = VideoModel
Analysis = AnalysisModel
Detection = DetectionModel
Report = ReportModel
RoadSegment = RoadSegmentModel

__all__ = [
    "VideoModel",
    "AnalysisModel",
    "DetectionModel",
    "ReportModel",
    "RoadSegmentModel",
    "Video",
    "Analysis",
    "Detection",
    "Report",
    "RoadSegment",
]
