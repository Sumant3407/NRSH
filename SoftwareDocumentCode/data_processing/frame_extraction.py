"""
Video frame extraction module
"""

import cv2
import numpy as np
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import asyncio
from dataclasses import dataclass

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.config_manager import ConfigManager


@dataclass
class FrameMetadata:
    """Metadata for extracted frame"""
    frame_number: int
    timestamp: float
    gps_coords: Optional[Tuple[float, float]] = None  # (lat, lon)


class FrameExtractor:
    """Extract frames from video files"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.fps = config.get("video_processing.frame_extraction.fps", 1)
        self.max_frames = config.get("video_processing.frame_extraction.max_frames", 1000)
    
    async def extract_frames(
        self,
        video_path: Path,
        output_dir: Optional[Path] = None
    ) -> List[Tuple[np.ndarray, FrameMetadata]]:
        """
        Extract frames from video
        
        Args:
            video_path: Path to video file
            output_dir: Optional directory to save frames
        
        Returns:
            List of (frame, metadata) tuples
        """
        frames = []
        
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Get video properties
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_interval = max(1, int(video_fps / self.fps))
        
        frame_count = 0
        extracted_count = 0
        
        while cap.isOpened() and extracted_count < self.max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Extract frame at specified interval
            if frame_count % frame_interval == 0:
                # Preprocess frame
                processed_frame = await self._preprocess_frame(frame)
                
                # Create metadata
                timestamp = frame_count / video_fps
                metadata = FrameMetadata(
                    frame_number=frame_count,
                    timestamp=timestamp
                )
                
                frames.append((processed_frame, metadata))
                
                # Save frame if output directory provided
                if output_dir:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    frame_path = output_dir / f"frame_{frame_count:06d}.jpg"
                    cv2.imwrite(str(frame_path), frame)
                
                extracted_count += 1
            
            frame_count += 1
        
        cap.release()
        return frames
    
    async def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess frame for analysis"""
        config = self.config.get("video_processing.preprocessing", {})
        
        # Resize if specified
        if "resize_width" in config and "resize_height" in config:
            width = config["resize_width"]
            height = config["resize_height"]
            frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)
        
        # Normalize if specified
        if config.get("normalize", False):
            frame = cv2.normalize(
                frame, None, 0, 255, cv2.NORM_MINMAX
            )
        
        return frame
    
    def extract_frames_sync(
        self,
        video_path: Path,
        output_dir: Optional[Path] = None
    ) -> List[Tuple[np.ndarray, FrameMetadata]]:
        """Synchronous version of extract_frames"""
        return asyncio.run(self.extract_frames(video_path, output_dir))

