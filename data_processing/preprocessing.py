from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np


# Class: ImagePreprocessor
class ImagePreprocessor:
    """Preprocessing utilities for video frames"""

    # Function: __init__
    def __init__(self, target_size: Optional[Tuple[int, int]] = None):
        self.target_size = target_size or (1280, 720)

    # Function: resize
    def resize(
        self, image: np.ndarray, size: Optional[Tuple[int, int]] = None
    ) -> np.ndarray:
        """Resize image to target size"""
        size = size or self.target_size
        return cv2.resize(image, size, interpolation=cv2.INTER_LINEAR)

    # Function: normalize
    def normalize(self, image: np.ndarray) -> np.ndarray:
        """Normalize image pixel values"""
        return cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)

    # Function: stabilize
    def stabilize(
        self, image: np.ndarray, previous_image: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Basic image stabilization (placeholder for more advanced stabilization)"""
        if previous_image is None:
            return image

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        prev_gray = cv2.cvtColor(previous_image, cv2.COLOR_BGR2GRAY)

        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(prev_gray, None)
        kp2, des2 = orb.detectAndCompute(gray, None)

        if des1 is None or des2 is None:
            return image

        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = matcher.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)

        if len(matches) < 4:
            return image

        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)

        if M is None:
            return image

        h, w = image.shape[:2]
        stabilized = cv2.warpPerspective(image, M, (w, h))

        return stabilized

    # Function: preprocess
    def preprocess(
        self,
        image: np.ndarray,
        resize: bool = True,
        normalize: bool = True,
        stabilize: bool = False,
        previous_image: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Apply all preprocessing steps"""
        processed = image.copy()

        if stabilize and previous_image is not None:
            processed = self.stabilize(processed, previous_image)

        if resize:
            processed = self.resize(processed)

        if normalize:
            processed = self.normalize(processed)

        return processed
