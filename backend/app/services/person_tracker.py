import os
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple

class PersonTracker:
    """
    Robust, privacy-preserving classroom participant tracking using OpenCV.
    Uses Background Subtraction (createBackgroundSubtractorMOG2) and contour-based centroid tracking.
    Never extracts biometric facial landmarks, emotion, or face crops.
    """
    def __init__(self, max_disappeared: int = 15, max_distance: float = 120.0):
        self.next_track_id = 1
        self.tracks = {}        # track_id -> centroid (x, y)
        self.disappeared = {}   # track_id -> consecutive frames absent
        self.track_history = {} # track_id -> list of detection timestamps
        self.track_boxes = {}   # track_id -> (x, y, w, h)
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        
        # Fast, adaptive background subtractor
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=300,
            varThreshold=32,
            detectShadows=False
        )

    def register(self, centroid: Tuple[int, int], box: Tuple[int, int, int, int], timestamp_sec: float) -> str:
        track_id = f"Track_{self.next_track_id}"
        self.next_track_id += 1
        self.tracks[track_id] = centroid
        self.disappeared[track_id] = 0
        self.track_boxes[track_id] = box
        self.track_history[track_id] = [timestamp_sec]
        return track_id

    def deregister(self, track_id: str):
        if track_id in self.tracks:
            del self.tracks[track_id]
        if track_id in self.disappeared:
            del self.disappeared[track_id]
        if track_id in self.track_boxes:
            del self.track_boxes[track_id]

    def detect_people(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect person regions using background subtraction + contour filtering.
        """
        h, w = frame.shape[:2]
        # Pre-process frame with slight Gaussian blur
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        fg_mask = self.bg_subtractor.apply(blurred)

        # Morphology to remove speckle noise and bridge small gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.dilate(fg_mask, kernel, iterations=2)

        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        candidate_boxes = []
        min_area = (w * h) * 0.005  # At least 0.5% of frame area

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > min_area:
                x, y, bw, bh = cv2.boundingRect(cnt)
                # Aspect ratio check for person/upper-body presence
                aspect_ratio = bh / float(bw)
                if aspect_ratio > 0.6:  # Upright or seated human profile
                    candidate_boxes.append((x, y, bw, bh))

        return candidate_boxes

    def update(self, frame: np.ndarray, timestamp_sec: float) -> Dict[str, Dict[str, Any]]:
        rects = self.detect_people(frame)
        
        input_centroids = []
        for (x, y, w, h) in rects:
            cX = int(x + w / 2.0)
            cY = int(y + h / 2.0)
            input_centroids.append((cX, cY))

        if len(self.tracks) == 0:
            for i, centroid in enumerate(input_centroids):
                self.register(centroid, rects[i], timestamp_sec)
        else:
            track_ids = list(self.tracks.keys())
            track_centroids = list(self.tracks.values())

            if len(input_centroids) == 0:
                for track_id in track_ids:
                    self.disappeared[track_id] += 1
                    if self.disappeared[track_id] > self.max_disappeared:
                        self.deregister(track_id)
            else:
                D = np.zeros((len(track_centroids), len(input_centroids)), dtype="float")
                for i in range(len(track_centroids)):
                    for j in range(len(input_centroids)):
                        D[i, j] = np.linalg.norm(np.array(track_centroids[i]) - np.array(input_centroids[j]))

                rows = D.min(axis=1).argsort()
                cols = D.argmin(axis=1)[rows]

                used_rows = set()
                used_cols = set()

                for (row, col) in zip(rows, cols):
                    if row in used_rows or col in used_cols:
                        continue
                    if D[row, col] > self.max_distance:
                        continue

                    track_id = track_ids[row]
                    self.tracks[track_id] = input_centroids[col]
                    self.track_boxes[track_id] = rects[col]
                    self.disappeared[track_id] = 0
                    self.track_history[track_id].append(timestamp_sec)

                    used_rows.add(row)
                    used_cols.add(col)

                unused_rows = set(range(0, D.shape[0])).difference(used_rows)
                unused_cols = set(range(0, D.shape[1])).difference(used_cols)

                for row in unused_rows:
                    track_id = track_ids[row]
                    self.disappeared[track_id] += 1
                    if self.disappeared[track_id] > self.max_disappeared:
                        self.deregister(track_id)

                for col in unused_cols:
                    self.register(input_centroids[col], rects[col], timestamp_sec)

        active_snapshot = {}
        for track_id in self.tracks:
            active_snapshot[track_id] = {
                "centroid": self.tracks[track_id],
                "box": self.track_boxes[track_id],
                "history_count": len(self.track_history[track_id])
            }
        return active_snapshot
