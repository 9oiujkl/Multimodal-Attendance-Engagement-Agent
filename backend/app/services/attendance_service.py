from typing import List, Dict, Any

class AttendanceService:
    """
    Applies strict attendance rules:
    - Never marks present from a single frame.
    - Requires sustained observation exceeding min_duration_sec and min_attendance_pct.
    - Classifies as PRESENT, PARTIAL, ABSENT, or NEEDS_REVIEW.
    """
    @staticmethod
    def calculate_attendance_records(
        track_stats: List[Dict[str, Any]],
        session_duration_sec: float,
        min_attendance_pct: float = 60.0,
        min_observed_duration_sec: float = 30.0,
        min_consecutive_frames: int = 3
    ) -> List[Dict[str, Any]]:
        results = []

        for stat in track_stats:
            track_id = stat["track_id"]
            observed_sec = stat["total_observed_sec"]
            detection_count = stat.get("detection_count", 0)
            obs_pct = stat["observed_pct"]

            # Rule: Never mark from single frame
            if detection_count < min_consecutive_frames:
                status = "NEEDS_REVIEW"
                evidence_quality = "LOW"
            elif observed_sec >= min_observed_duration_sec and obs_pct >= min_attendance_pct:
                status = "PRESENT"
                evidence_quality = "HIGH"
            elif observed_sec >= (min_observed_duration_sec * 0.5) or obs_pct >= (min_attendance_pct * 0.5):
                status = "PARTIAL"
                evidence_quality = "MEDIUM"
            else:
                status = "NEEDS_REVIEW"
                evidence_quality = "LOW"

            results.append({
                "anonymous_track_id": track_id,
                "first_detected_sec": stat["first_detected_sec"],
                "last_detected_sec": stat["last_detected_sec"],
                "total_observed_sec": observed_sec,
                "observed_pct": obs_pct,
                "status": status,
                "evidence_quality": evidence_quality,
                "is_manual_override": False,
                "override_notes": None
            })

        return results
