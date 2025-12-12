import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.config_manager import ConfigManager
from backend.services.video_service import VideoService

router = APIRouter()

from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
config_path = project_root / "config" / "config.yaml"
config = ConfigManager(config_path)
video_service = VideoService(config)


# Class: VideoUploadResponse
class VideoUploadResponse(BaseModel):
    video_id: str
    filename: str
    status: str
    message: str


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    video_type: str = "present",  # "base" or "present"
    gps_data: Optional[str] = None,
):
    """
    Upload a media file (video or image) for analysis

    - **file**: Video or image file (see allowed extensions)
    - **video_type**: "base" (reference) or "present" (current)
    - **gps_data**: Optional GPS metadata (JSON string)
    """
    allowed_exts = config.get(
        "api.allowed_extensions",
        [
            ".mp4",
            ".avi",
            ".mov",
            ".mkv",
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".tif",
            ".tiff",
        ],
    )
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_exts)}",
        )

    if video_type not in ["base", "present"]:
        raise HTTPException(
            status_code=400, detail="video_type must be 'base' or 'present'"
        )

    try:
        video_id = str(uuid.uuid4())
        result = await video_service.save_video(
            file=file, video_id=video_id, video_type=video_type, gps_data=gps_data
        )

        return VideoUploadResponse(
            video_id=video_id,
            filename=file.filename,
            status="success",
            message="Media uploaded successfully",
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
