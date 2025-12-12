import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from geopy.distance import geodesic

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.services.config_manager import ConfigManager
from data_processing.frame_extraction import FrameMetadata


# Class: FrameAligner
class FrameAligner:
    """Align frames from base and present videos using GPS and temporal data"""

    # Function: __init__
    def __init__(self, config: ConfigManager):
        self.config = config
        self.gps_tolerance = config.get(
            "video_processing.alignment.gps_tolerance", 50
        )  # meters
        self.temporal_tolerance = config.get(
            "video_processing.alignment.temporal_tolerance", 5
        )  # seconds

    async def align_frames(
        self,
        base_frames: List[Tuple[np.ndarray, FrameMetadata]],
        present_frames: List[Tuple[np.ndarray, FrameMetadata]],
        base_gps_data: Optional[Dict] = None,
        present_gps_data: Optional[Dict] = None,
    ) -> List[Tuple[np.ndarray, np.ndarray, Dict]]:
        """
        Align frames from base and present videos

        Args:
            base_frames: List of (frame, metadata) tuples from base video
            present_frames: List of (frame, metadata) tuples from present video
            base_gps_data: Optional GPS data for base video
            present_gps_data: Optional GPS data for present video

        Returns:
            List of (base_frame, present_frame, alignment_metadata) tuples
        """
        aligned_pairs = []

        if base_gps_data and present_gps_data:
            aligned_pairs = await self._align_by_gps(
                base_frames, present_frames, base_gps_data, present_gps_data
            )
        else:
            aligned_pairs = await self._align_by_temporal(base_frames, present_frames)

        return aligned_pairs

    async def _align_by_gps(
        self,
        base_frames: List[Tuple[np.ndarray, FrameMetadata]],
        present_frames: List[Tuple[np.ndarray, FrameMetadata]],
        base_gps_data: Dict,
        present_gps_data: Dict,
    ) -> List[Tuple[np.ndarray, np.ndarray, Dict]]:
        """Align frames using GPS coordinates"""
        aligned_pairs = []

        base_coords = self._extract_gps_coords(base_frames, base_gps_data)
        present_coords = self._extract_gps_coords(present_frames, present_gps_data)

        for i, (base_frame, base_meta) in enumerate(base_frames):
            base_coord = base_coords[i] if i < len(base_coords) else None

            if base_coord is None:
                continue

            best_match_idx = None
            min_distance = float("inf")

            for j, (present_frame, present_meta) in enumerate(present_frames):
                present_coord = present_coords[j] if j < len(present_coords) else None

                if present_coord is None:
                    continue

                distance = geodesic(base_coord, present_coord).meters

                if distance < min_distance and distance <= self.gps_tolerance:
                    min_distance = distance
                    best_match_idx = j

            if best_match_idx is not None:
                present_frame, present_meta = present_frames[best_match_idx]
                alignment_meta = {
                    "base_frame_number": base_meta.frame_number,
                    "present_frame_number": present_meta.frame_number,
                    "gps_distance_m": min_distance,
                    "alignment_method": "gps",
                }
                aligned_pairs.append((base_frame, present_frame, alignment_meta))

        return aligned_pairs

    async def _align_by_temporal(
        self,
        base_frames: List[Tuple[np.ndarray, FrameMetadata]],
        present_frames: List[Tuple[np.ndarray, FrameMetadata]],
    ) -> List[Tuple[np.ndarray, np.ndarray, Dict]]:
        """Align frames using temporal matching"""
        aligned_pairs = []

        min_len = min(len(base_frames), len(present_frames))

        for i in range(min_len):
            base_frame, base_meta = base_frames[i]
            present_frame, present_meta = present_frames[i]

            time_diff = abs(base_meta.timestamp - present_meta.timestamp)

            if time_diff <= self.temporal_tolerance:
                alignment_meta = {
                    "base_frame_number": base_meta.frame_number,
                    "present_frame_number": present_meta.frame_number,
                    "time_difference_s": time_diff,
                    "alignment_method": "temporal",
                }
                aligned_pairs.append((base_frame, present_frame, alignment_meta))

        return aligned_pairs

    # Function: _extract_gps_coords
    def _extract_gps_coords(
        self,
        frames: List[Tuple[np.ndarray, FrameMetadata]],
        gps_data: Optional[Dict] = None,
    ) -> List[Optional[Tuple[float, float]]]:
        """Extract GPS coordinates from frames or provided data"""
        coords = []

        for frame, metadata in frames:
            coord = None

            if metadata.gps_coords:
                coord = metadata.gps_coords
            elif gps_data:
                frame_num = metadata.frame_number
                if isinstance(gps_data, dict):
                    if frame_num in gps_data:
                        coord_data = gps_data[frame_num]
                        if (
                            isinstance(coord_data, (list, tuple))
                            and len(coord_data) >= 2
                        ):
                            coord = (float(coord_data[0]), float(coord_data[1]))

            coords.append(coord)

        return coords
