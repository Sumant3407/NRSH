"""
Supabase database models and schemas
"""

from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class VideoType(str, Enum):
    """Video type enumeration"""
    BASE = "base"
    PRESENT = "present"


class AnalysisStatus(str, Enum):
    """Analysis status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Severity(str, Enum):
    """Severity level enumeration"""
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"


class ElementType(str, Enum):
    """Road infrastructure element types"""
    PAVEMENT_CRACK = "pavement_crack"
    FADED_MARKING = "faded_marking"
    MISSING_STUD = "missing_stud"
    DAMAGED_SIGN = "damaged_sign"
    ROADSIDE_FURNITURE_DAMAGE = "roadside_furniture_damage"
    VRU_PATH_OBSTRUCTION = "vru_path_obstruction"


# Pydantic models for API and database operations

class VideoModel(BaseModel):
    """Video model"""
    id: str
    filename: str
    video_type: VideoType
    file_path: str
    file_size: int
    upload_date: datetime
    gps_data: Optional[Dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnalysisModel(BaseModel):
    """Analysis model"""
    id: str
    base_video_id: str
    present_video_id: str
    status: AnalysisStatus
    progress: int = Field(default=0, ge=0, le=100)
    error: Optional[str] = None
    summary: Optional[Dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DetectionModel(BaseModel):
    """Detection model"""
    id: str
    analysis_id: str
    element_type: ElementType
    bbox: List[float]  # [x1, y1, x2, y2]
    confidence: float = Field(ge=0.0, le=1.0)
    severity: Severity
    severity_score: float = Field(default=0.0, ge=0.0, le=10.0)
    gps_coords: Optional[List[float]] = None  # [lat, lon]
    frame_number: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReportModel(BaseModel):
    """Report model"""
    id: str
    analysis_id: str
    file_path: str
    file_size: int
    generated_at: datetime
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoadSegmentModel(BaseModel):
    """Road segment model"""
    id: str
    name: Optional[str] = None
    gps_coords: List[List[float]]  # Polygon coordinates [[lat, lon], ...]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Database table names (for Supabase)
TABLES = {
    "videos": "videos",
    "analyses": "analyses",
    "detections": "detections",
    "reports": "reports",
    "road_segments": "road_segments"
}

