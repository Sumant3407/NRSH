"""
Video upload and management endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
import sys
from pathlib import Path
import uuid
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.video_service import VideoService
from backend.services.config_manager import ConfigManager

router = APIRouter()

# Initialize services
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
config_path = project_root / "config" / "config.yaml"
config = ConfigManager(config_path)
video_service = VideoService(config)


class VideoUploadResponse(BaseModel):
    video_id: str
    filename: str
    status: str
    message: str


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    video_type: str = "present",  # "base" or "present"
    gps_data: Optional[str] = None
):
    """
    Upload a video file for analysis
    
    - **file**: Video file (mp4, avi, mov, mkv)
    - **video_type**: Type of video - "base" (reference) or "present" (current)
    - **gps_data**: Optional GPS metadata (JSON string)
    """
    # Validate file extension
    allowed_exts = config.get("api.allowed_extensions", [".mp4", ".avi", ".mov", ".mkv"])
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_exts)}"
        )
    
    # Validate video type
    if video_type not in ["base", "present"]:
        raise HTTPException(
            status_code=400,
            detail="video_type must be 'base' or 'present'"
        )
    
    try:
        # Save video file
        video_id = str(uuid.uuid4())
        result = await video_service.save_video(
            file=file,
            video_id=video_id,
            video_type=video_type,
            gps_data=gps_data
        )
        
        return VideoUploadResponse(
            video_id=video_id,
            filename=file.filename,
            status="success",
            message="Video uploaded successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}")
async def get_video_info(video_id: str):
    """Get video metadata and information"""
    try:
        info = await video_service.get_video_info(video_id)
        return JSONResponse(content=info)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Video not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{video_id}")
async def delete_video(video_id: str):
    """Delete a video file"""
    try:
        await video_service.delete_video(video_id)
        return {"status": "success", "message": "Video deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Video not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_videos(video_type: Optional[str] = None):
    """List all uploaded videos, optionally filtered by type"""
    try:
        videos = await video_service.list_videos(video_type)
        return {"videos": videos, "count": len(videos)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

