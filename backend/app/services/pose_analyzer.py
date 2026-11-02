import cv2
import numpy as np
from typing import Dict, Any, Optional

class PoseAnalyzer:
    """
    Analyzes visual activity and observable head/body orientation proxy.
    Calculates optical flow, frame-diff movement indicators, and upper-body orientation proxy.
    Explicitly does NOT infer emotions, personality, or internal attention states.
    """
    def __init__(self):
        self.prev_gray = None

    def calculate_frame_motion(self, frame: np.ndarray) -> float:
        """
        Calculates normalized visual movement indicator (0-100) using frame differencing.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.prev_gray is None:
            self.prev_gray = gray
            return 20.0  # Baseline initialization

        frame_delta = cv2.absdiff(self.prev_gray, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        self.prev_gray = gray

        # Motion intensity = percentage of changed pixels normalized
        non_zero_ratio = np.count_nonzero(thresh) / float(thresh.size)
        # Scaled to 0-100 scale: 10% change is very high classroom activity
        motion_index = float(np.clip(non_zero_ratio * 1000.0, 0.0, 100.0))
        return round(motion_index, 2)

    def estimate_orientation_proxy(self, frame: np.ndarray, person_boxes: list) -> Optional[float]:
        """
        Estimates observable orientation score toward teaching area (assumed centered-forward).
        Uses face/upper body horizontal symmetry proxy when people are detected.
        Returns 0-100 or None if no detections.
        """
        if not person_boxes:
            return None

        scores = []
        frame_center_x = frame.shape[1] / 2.0

        for (x, y, w, h) in person_boxes:
            box_center_x = x + (w / 2.0)
            # Deviation of person orientation/position relative to frontal viewpoint
            offset_ratio = abs(box_center_x - frame_center_x) / frame_center_x
            # Orientation proxy score: centered alignment gives higher frontal proxy
            score = 100.0 * (1.0 - min(offset_ratio * 0.4, 0.8))
            scores.append(score)

        return round(float(np.mean(scores)), 2)
