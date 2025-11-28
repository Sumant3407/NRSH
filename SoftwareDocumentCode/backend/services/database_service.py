"""
Supabase database service for Road Safety Infrastructure Analysis System
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.models.database import (
    VideoModel,
    AnalysisModel,
    DetectionModel,
    ReportModel,
    RoadSegmentModel,
    VideoType,
    AnalysisStatus,
    Severity,
    ElementType,
    TABLES
)

# Load environment variables
load_dotenv()


class DatabaseService:
    """Service for interacting with Supabase database"""
    
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
            )
        
        self.client: Client = create_client(supabase_url, supabase_key)
        self._verify_connection()
    
    def _verify_connection(self):
        """Verify database connection"""
        try:
            # Try a simple query to verify connection
            self.client.table(TABLES["videos"]).select("id").limit(1).execute()
        except Exception as e:
            print(f"Warning: Could not verify Supabase connection: {e}")
            print("Make sure your Supabase credentials are correct and tables are created.")
    
    # Video operations
    async def create_video(
        self,
        video_id: str,
        filename: str,
        video_type: VideoType,
        file_path: str,
        file_size: int,
        gps_data: Optional[Dict] = None
    ) -> VideoModel:
        """Create a new video record"""
        data = {
            "id": video_id,
            "filename": filename,
            "video_type": video_type.value,
            "file_path": file_path,
            "file_size": file_size,
            "upload_date": datetime.now().isoformat(),
            "gps_data": gps_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        result = self.client.table(TABLES["videos"]).insert(data).execute()
        return VideoModel(**result.data[0])
    
    async def get_video(self, video_id: str) -> Optional[VideoModel]:
        """Get video by ID"""
        result = self.client.table(TABLES["videos"]).select("*").eq("id", video_id).execute()
        
        if result.data:
            return VideoModel(**result.data[0])
        return None
    
    async def list_videos(self, video_type: Optional[VideoType] = None) -> List[VideoModel]:
        """List all videos, optionally filtered by type"""
        query = self.client.table(TABLES["videos"]).select("*")
        
        if video_type:
            query = query.eq("video_type", video_type.value)
        
        result = query.order("created_at", desc=True).execute()
        return [VideoModel(**item) for item in result.data]
    
    async def delete_video(self, video_id: str) -> bool:
        """Delete a video record"""
        result = self.client.table(TABLES["videos"]).delete().eq("id", video_id).execute()
        return len(result.data) > 0
    
    # Analysis operations
    async def create_analysis(
        self,
        analysis_id: str,
        base_video_id: str,
        present_video_id: str
    ) -> AnalysisModel:
        """Create a new analysis record"""
        data = {
            "id": analysis_id,
            "base_video_id": base_video_id,
            "present_video_id": present_video_id,
            "status": AnalysisStatus.PENDING.value,
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        result = self.client.table(TABLES["analyses"]).insert(data).execute()
        return AnalysisModel(**result.data[0])
    
    async def update_analysis_status(
        self,
        analysis_id: str,
        status: AnalysisStatus,
        progress: int = 0,
        error: Optional[str] = None,
        summary: Optional[Dict] = None
    ) -> AnalysisModel:
        """Update analysis status"""
        update_data = {
            "status": status.value,
            "progress": progress,
            "updated_at": datetime.now().isoformat()
        }
        
        if error:
            update_data["error"] = error
        
        if summary:
            update_data["summary"] = summary
        
        if status == AnalysisStatus.COMPLETED:
            update_data["completed_at"] = datetime.now().isoformat()
        
        result = self.client.table(TABLES["analyses"]).update(update_data).eq("id", analysis_id).execute()
        
        if result.data:
            return AnalysisModel(**result.data[0])
        raise ValueError(f"Analysis {analysis_id} not found")
    
    async def get_analysis(self, analysis_id: str) -> Optional[AnalysisModel]:
        """Get analysis by ID"""
        result = self.client.table(TABLES["analyses"]).select("*").eq("id", analysis_id).execute()
        
        if result.data:
            return AnalysisModel(**result.data[0])
        return None
    
    async def list_analyses(
        self,
        status: Optional[AnalysisStatus] = None,
        limit: int = 100
    ) -> List[AnalysisModel]:
        """List analyses, optionally filtered by status"""
        query = self.client.table(TABLES["analyses"]).select("*")
        
        if status:
            query = query.eq("status", status.value)
        
        result = query.order("created_at", desc=True).limit(limit).execute()
        return [AnalysisModel(**item) for item in result.data]
    
    # Detection operations
    async def create_detection(
        self,
        detection_id: str,
        analysis_id: str,
        element_type: ElementType,
        bbox: List[float],
        confidence: float,
        severity: Severity,
        severity_score: float = 0.0,
        gps_coords: Optional[List[float]] = None,
        frame_number: Optional[int] = None
    ) -> DetectionModel:
        """Create a new detection record"""
        data = {
            "id": detection_id,
            "analysis_id": analysis_id,
            "element_type": element_type.value,
            "bbox": bbox,
            "confidence": confidence,
            "severity": severity.value,
            "severity_score": severity_score,
            "gps_coords": gps_coords,
            "frame_number": frame_number,
            "created_at": datetime.now().isoformat()
        }
        
        result = self.client.table(TABLES["detections"]).insert(data).execute()
        return DetectionModel(**result.data[0])
    
    async def bulk_create_detections(
        self,
        detections: List[Dict[str, Any]]
    ) -> List[DetectionModel]:
        """Bulk create detection records"""
        if not detections:
            return []
        
        result = self.client.table(TABLES["detections"]).insert(detections).execute()
        return [DetectionModel(**item) for item in result.data]
    
    async def get_detections(
        self,
        analysis_id: str,
        element_type: Optional[ElementType] = None,
        severity: Optional[Severity] = None
    ) -> List[DetectionModel]:
        """Get detections for an analysis"""
        query = self.client.table(TABLES["detections"]).select("*").eq("analysis_id", analysis_id)
        
        if element_type:
            query = query.eq("element_type", element_type.value)
        
        if severity:
            query = query.eq("severity", severity.value)
        
        result = query.execute()
        return [DetectionModel(**item) for item in result.data]
    
    # Report operations
    async def create_report(
        self,
        report_id: str,
        analysis_id: str,
        file_path: str,
        file_size: int
    ) -> ReportModel:
        """Create a new report record"""
        data = {
            "id": report_id,
            "analysis_id": analysis_id,
            "file_path": file_path,
            "file_size": file_size,
            "generated_at": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        result = self.client.table(TABLES["reports"]).insert(data).execute()
        return ReportModel(**result.data[0])
    
    async def get_report(self, report_id: str) -> Optional[ReportModel]:
        """Get report by ID"""
        result = self.client.table(TABLES["reports"]).select("*").eq("id", report_id).execute()
        
        if result.data:
            return ReportModel(**result.data[0])
        return None
    
    async def get_reports_for_analysis(self, analysis_id: str) -> List[ReportModel]:
        """Get all reports for an analysis"""
        result = self.client.table(TABLES["reports"]).select("*").eq("analysis_id", analysis_id).execute()
        return [ReportModel(**item) for item in result.data]
    
    # Road segment operations
    async def create_road_segment(
        self,
        segment_id: str,
        name: Optional[str],
        gps_coords: List[List[float]]
    ) -> RoadSegmentModel:
        """Create a new road segment"""
        data = {
            "id": segment_id,
            "name": name,
            "gps_coords": gps_coords,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        result = self.client.table(TABLES["road_segments"]).insert(data).execute()
        return RoadSegmentModel(**result.data[0])
    
    async def get_road_segment(self, segment_id: str) -> Optional[RoadSegmentModel]:
        """Get road segment by ID"""
        result = self.client.table(TABLES["road_segments"]).select("*").eq("id", segment_id).execute()
        
        if result.data:
            return RoadSegmentModel(**result.data[0])
        return None
    
    async def list_road_segments(self) -> List[RoadSegmentModel]:
        """List all road segments"""
        result = self.client.table(TABLES["road_segments"]).select("*").execute()
        return [RoadSegmentModel(**item) for item in result.data]


# Singleton instance
_db_service: Optional[DatabaseService] = None


def get_database_service() -> Optional[DatabaseService]:
    """Get or create database service instance"""
    global _db_service
    
    if _db_service is None:
        try:
            _db_service = DatabaseService()
        except Exception as e:
            print(f"Warning: Could not initialize database service: {e}")
            print("Falling back to file-based storage.")
            return None
    
    return _db_service

