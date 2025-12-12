import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles
from fastapi import UploadFile

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.models.database import VideoType
from backend.services.config_manager import ConfigManager
from backend.services.database_service import get_database_service


# Class: VideoService
class VideoService:
    """Service for managing video uploads and metadata"""

    # Function: __init__
    def __init__(self, config: ConfigManager):
        self.config = config
        self.upload_dir = Path(config.get("storage.upload_dir", "uploads"))
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.upload_dir / "metadata.json"
        self.db_service = get_database_service()
        self._init_metadata()

    # Function: _init_metadata
    def _init_metadata(self):
        """Initialize metadata file if it doesn't exist (fallback)"""
        if not self.metadata_file.exists():
            with open(self.metadata_file, "w") as f:
                json.dump({"videos": {}}, f)

    async def save_video(
        self,
        file: UploadFile,
        video_id: str,
        video_type: str,
        gps_data: Optional[str] = None,
    ) -> Dict:
        """Save uploaded video file and metadata"""
        video_dir = self.upload_dir / video_id
        video_dir.mkdir(exist_ok=True)

        video_path = video_dir / file.filename
        async with aiofiles.open(video_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        gps_json = None
        if gps_data:
            try:
                gps_json = json.loads(gps_data)
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                print(f"Warning: Could not parse GPS data: {e}")
                gps_json = None

        file_size = os.path.getsize(video_path)

        if self.db_service:
            try:
                video_type_enum = (
                    VideoType.BASE if video_type == "base" else VideoType.PRESENT
                )
                video_model = await self.db_service.create_video(
                    video_id=video_id,
                    filename=file.filename,
                    video_type=video_type_enum,
                    file_path=str(video_path),
                    file_size=file_size,
                    gps_data=gps_json,
                )
                return {
                    "video_id": video_model.id,
                    "filename": video_model.filename,
                    "video_type": video_model.video_type,
                    "file_path": video_model.file_path,
                    "file_size": video_model.file_size,
                    "upload_date": video_model.upload_date.isoformat(),
                    "gps_data": video_model.gps_data,
                }
            except Exception as e:
                print(
                    f"Warning: Could not save to database: {e}. Using file-based storage."
                )

        metadata = {
            "video_id": video_id,
            "filename": file.filename,
            "video_type": video_type,
            "file_path": str(video_path),
            "file_size": file_size,
            "upload_date": datetime.now().isoformat(),
            "gps_data": gps_json,
        }

        with open(self.metadata_file, "r") as f:
            all_metadata = json.load(f)

        all_metadata["videos"][video_id] = metadata

        with open(self.metadata_file, "w") as f:
            json.dump(all_metadata, f, indent=2)

        return metadata

    async def get_video_info(self, video_id: str) -> Dict:
        """Get video information"""
        if self.db_service:
            try:
                video_model = await self.db_service.get_video(video_id)
                if video_model:
                    return {
                        "video_id": video_model.id,
                        "filename": video_model.filename,
                        "video_type": video_model.video_type,
                        "file_path": video_model.file_path,
                        "file_size": video_model.file_size,
                        "upload_date": video_model.upload_date.isoformat(),
                        "gps_data": video_model.gps_data,
                    }
            except Exception as e:
                print(
                    f"Warning: Could not fetch from database: {e}. Using file-based storage."
                )

        with open(self.metadata_file, "r") as f:
            all_metadata = json.load(f)

        if video_id not in all_metadata["videos"]:
            raise FileNotFoundError(f"Video {video_id} not found")

        return all_metadata["videos"][video_id]

    async def delete_video(self, video_id: str):
        """Delete video file and metadata"""
        video_info = await self.get_video_info(video_id)
        video_path = Path(video_info["file_path"])

        if video_path.exists():
            video_path.unlink()

        video_dir = video_path.parent
        if video_dir.exists() and video_dir.is_dir():
            video_dir.rmdir()

        if self.db_service:
            try:
                await self.db_service.delete_video(video_id)
                return
            except Exception as e:
                print(f"Warning: Could not delete from database: {e}.")

        with open(self.metadata_file, "r") as f:
            all_metadata = json.load(f)

        if video_id in all_metadata["videos"]:
            del all_metadata["videos"][video_id]

        with open(self.metadata_file, "w") as f:
            json.dump(all_metadata, f, indent=2)

    async def list_videos(self, video_type: Optional[str] = None) -> List[Dict]:
        """List all videos, optionally filtered by type"""
        if self.db_service:
            try:
                video_type_enum = None
                if video_type:
                    video_type_enum = (
                        VideoType.BASE if video_type == "base" else VideoType.PRESENT
                    )

                video_models = await self.db_service.list_videos(video_type_enum)
                return [
                    {
                        "video_id": v.id,
                        "filename": v.filename,
                        "video_type": v.video_type,
                        "file_path": v.file_path,
                        "file_size": v.file_size,
                        "upload_date": v.upload_date.isoformat(),
                        "gps_data": v.gps_data,
                    }
                    for v in video_models
                ]
            except Exception as e:
                print(
                    f"Warning: Could not fetch from database: {e}. Using file-based storage."
                )

        with open(self.metadata_file, "r") as f:
            all_metadata = json.load(f)

        videos = list(all_metadata["videos"].values())

        if video_type:
            videos = [v for v in videos if v.get("video_type") == video_type]

        return videos
