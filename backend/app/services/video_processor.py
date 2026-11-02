import os
import cv2
import numpy as np
from typing import Dict, Any, List, Optional
from app.services.person_tracker import PersonTracker
from app.services.pose_analyzer import PoseAnalyzer

class VideoProcessor:
    """
    Safely opens, validates, and decodes local classroom video recordings.
    Processes frames sequentially with configurable sampling interval.
    Tracks participants anonymously and computes visual activity metrics.
    """
    def __init__(self, sample_interval_sec: float = 1.0):
        self.sample_interval_sec = sample_interval_sec
        self.tracker = PersonTracker()
        self.pose_analyzer = PoseAnalyzer()

    @staticmethod
    def get_video_metadata(video_path: str) -> Dict[str, Any]:
        """
        Validates decoding and reads video FPS, frame count, dimensions, and duration.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Unable to decode video format at {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration_sec = frame_count / fps if fps > 0 else 0.0

        cap.release()
        return {
            "fps": fps,
            "frame_count": frame_count,
            "width": width,
            "height": height,
            "duration_sec": duration_sec,
            "is_valid": True
        }

    def process_video(self, video_path: str, progress_callback=None) -> Dict[str, Any]:
        """
        Extracts temporal visual features and anonymous participant trajectories.
        """
        meta = self.get_video_metadata(video_path)
        duration_sec = meta["duration_sec"]
        fps = meta["fps"]

        cap = cv2.VideoCapture(video_path)
        frame_interval = max(1, int(fps * self.sample_interval_sec))
        
        current_frame_idx = 0
        timeline_metrics = []

        total_frames = meta["frame_count"]

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if current_frame_idx % frame_interval == 0:
                timestamp_sec = current_frame_idx / fps
                
                # Anonymous tracking
                active_tracks = self.tracker.update(frame, timestamp_sec)
                
                # Visual movement index
                motion_index = self.pose_analyzer.calculate_frame_motion(frame)
                
                # Orientation proxy
                boxes = [track_info["box"] for track_info in active_tracks.values()]
                orientation_score = self.pose_analyzer.estimate_orientation_proxy(frame, boxes)

                timeline_metrics.append({
                    "timestamp_sec": round(timestamp_sec, 2),
                    "active_tracks_count": len(active_tracks),
                    "motion_index": motion_index,
                    "orientation_score": orientation_score
                })

                if progress_callback and total_frames > 0:
                    pct = min(100.0, (current_frame_idx / float(total_frames)) * 50.0) # 0-50% for visual
                    progress_callback(pct, f"Processing video frame at {round(timestamp_sec, 1)}s")

            current_frame_idx += 1

        cap.release()

        # Compute attendance stats from anonymous track histories
        track_attendance_stats = []
        for track_id, timestamps in self.tracker.track_history.items():
            if not timestamps:
                continue
            first_seen = min(timestamps)
            last_seen = max(timestamps)
            # Duration approximated by count of sampled intervals
            observed_sec = len(timestamps) * self.sample_interval_sec
            obs_pct = (observed_sec / duration_sec * 100.0) if duration_sec > 0 else 0.0

            track_attendance_stats.append({
                "track_id": track_id,
                "first_detected_sec": round(first_seen, 2),
                "last_detected_sec": round(last_seen, 2),
                "total_observed_sec": round(observed_sec, 2),
                "observed_pct": round(min(100.0, obs_pct), 2),
                "detection_count": len(timestamps)
            })

        return {
            "metadata": meta,
            "timeline_metrics": timeline_metrics,
            "track_attendance_stats": track_attendance_stats
        }
