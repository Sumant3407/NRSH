import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.config_manager import ConfigManager


@dataclass
# Class: FrameMetadata
class FrameMetadata:
    """Metadata for extracted frame"""

    frame_number: int
    timestamp: float
    gps_coords: Optional[Tuple[float, float]] = None  # (lat, lon)


# Class: FrameExtractor
class FrameExtractor:
    """Extract frames from video files"""

    # Function: __init__
    def __init__(self, config: ConfigManager):
        self.config = config
        self.fps = config.get("video_processing.frame_extraction.fps", 1)
        self.max_frames = config.get(
            "video_processing.frame_extraction.max_frames", 1000
        )
        self.image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

    async def extract_frames(
        self, video_path: Path, output_dir: Optional[Path] = None
    ) -> List[Tuple[np.ndarray, FrameMetadata]]:
        """
        Extract frames from video, or wrap an image as a single frame

        Args:
            video_path: Path to video file
            output_dir: Optional directory to save frames

        Returns:
            List of (frame, metadata) tuples
        """
        frames = []

        if video_path.suffix.lower() in self.image_extensions:
            image = cv2.imread(str(video_path))
            if image is None:
                raise ValueError(f"Could not open image: {video_path}")

            processed_image = self._preprocess_frame(image)
            metadata = FrameMetadata(frame_number=0, timestamp=0.0)
            frames.append((processed_image, metadata))

            if output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                frame_path = output_dir / "frame_000000.jpg"
                cv2.imwrite(str(frame_path), image)

            return frames

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_interval = max(1, int(video_fps / self.fps))

        frame_count = 0
        extracted_count = 0

        while cap.isOpened() and extracted_count < self.max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                processed_frame = self._preprocess_frame(frame)

                timestamp = frame_count / video_fps
                metadata = FrameMetadata(frame_number=frame_count, timestamp=timestamp)

                frames.append((processed_frame, metadata))

                if output_dir:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    frame_path = output_dir / f"frame_{frame_count:06d}.jpg"
                    cv2.imwrite(str(frame_path), frame)

                extracted_count += 1

            frame_count += 1

        cap.release()
        return frames

    # Function: _preprocess_frame
    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess frame for analysis (synchronous).

        This function performs CPU-bound image operations and does not
        perform any asynchronous I/O, so it is implemented synchronously
        to simplify callers.
        """
        config = self.config.get("video_processing.preprocessing", {})

        if "resize_width" in config and "resize_height" in config:
            width = config["resize_width"]
            height = config["resize_height"]
            frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)

        if config.get("normalize", False):
            frame = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX)

        return frame

    # Function: extract_frames_sync
    def extract_frames_sync(
        self, video_path: Path, output_dir: Optional[Path] = None
    ) -> List[Tuple[np.ndarray, FrameMetadata]]:
        """Synchronous version of extract_frames"""
        return asyncio.run(self.extract_frames(video_path, output_dir))
