"""
Video management service
"""

import os
import json
import sys
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
import aiofiles
from fastapi import UploadFile

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.config_manager import ConfigManager


class VideoService:
    """Service for managing video uploads and metadata"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.upload_dir = Path(config.get("storage.upload_dir", "uploads"))
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.upload_dir / "metadata.json"
        self._init_metadata()
    
    def _init_metadata(self):
        """Initialize metadata file if it doesn't exist"""
        if not self.metadata_file.exists():
            with open(self.metadata_file, 'w') as f:
                json.dump({"videos": {}}, f)
    
    async def save_video(
        self,
        file: UploadFile,
        video_id: str,
        video_type: str,
        gps_data: Optional[str] = None
    ) -> Dict:
        """Save uploaded video file and metadata"""
        # Create video directory
        video_dir = self.upload_dir / video_id
        video_dir.mkdir(exist_ok=True)
        
        # Save video file
        video_path = video_dir / file.filename
        async with aiofiles.open(video_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Parse GPS data if provided
        gps_json = None
        if gps_data:
            try:
                gps_json = json.loads(gps_data)
            except:
                pass
        
        # Save metadata
        metadata = {
            "video_id": video_id,
            "filename": file.filename,
            "video_type": video_type,
            "file_path": str(video_path),
            "file_size": os.path.getsize(video_path),
            "upload_date": datetime.now().isoformat(),
            "gps_data": gps_json
        }
        
        # Update metadata file
        with open(self.metadata_file, 'r') as f:
            all_metadata = json.load(f)
        
        all_metadata["videos"][video_id] = metadata
        
        with open(self.metadata_file, 'w') as f:
            json.dump(all_metadata, f, indent=2)
        
        return metadata
    
    async def get_video_info(self, video_id: str) -> Dict:
        """Get video information"""
        with open(self.metadata_file, 'r') as f:
            all_metadata = json.load(f)
        
        if video_id not in all_metadata["videos"]:
            raise FileNotFoundError(f"Video {video_id} not found")
        
        return all_metadata["videos"][video_id]
    
    async def delete_video(self, video_id: str):
        """Delete video file and metadata"""
        video_info = await self.get_video_info(video_id)
        video_path = Path(video_info["file_path"])
        
        # Delete video file
        if video_path.exists():
            video_path.unlink()
        
        # Delete video directory
        video_dir = video_path.parent
        if video_dir.exists() and video_dir.is_dir():
            video_dir.rmdir()
        
        # Remove from metadata
        with open(self.metadata_file, 'r') as f:
            all_metadata = json.load(f)
        
        if video_id in all_metadata["videos"]:
            del all_metadata["videos"][video_id]
        
        with open(self.metadata_file, 'w') as f:
            json.dump(all_metadata, f, indent=2)
    
    async def list_videos(self, video_type: Optional[str] = None) -> List[Dict]:
        """List all videos, optionally filtered by type"""
        with open(self.metadata_file, 'r') as f:
            all_metadata = json.load(f)
        
        videos = list(all_metadata["videos"].values())
        
        if video_type:
            videos = [v for v in videos if v.get("video_type") == video_type]
        
        return videos

