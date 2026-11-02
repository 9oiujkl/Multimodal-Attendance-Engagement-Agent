from typing import List, Dict, Any

class RecommendationEngine:
    """
    Offline, rule-based pedagogical advisory system.
    Generates actionable suggestions derived strictly from empirical temporal metrics.
    Contains mandatory caveats and never grades or punishes students.
    """
    @staticmethod
    def generate_recommendations(
        fused_timeline: List[Dict[str, Any]],
        attendance_records: List[Dict[str, Any]],
        session_duration_sec: float
    ) -> List[Dict[str, Any]]:
        recommendations = []

        if not fused_timeline:
            recommendations.append({
                "title": "Insufficient Observational Data",
                "explanation": "No valid temporal metrics were detected in the provided session recording.",
                "supporting_metric": "Observations = 0 frames",
                "timestamp_interval": "00:00 - End",
                "suggested_action": "Verify video and audio stream encoding, file integrity, and camera coverage.",
                "severity": "HIGH",
                "caveat": "System functions strictly as an advisory proxy and requires valid sensor signals."
            })
            return recommendations

        # 1. Analyze Visual Activity Trajectory (last 10 min or second half)
        motion_indices = [p["visual_activity_index"] for p in fused_timeline if p.get("visual_activity_index") is not None]
        if motion_indices:
            midpoint = len(motion_indices) // 2
            first_half_avg = sum(motion_indices[:midpoint]) / max(1, midpoint)
            second_half_avg = sum(motion_indices[midpoint:]) / max(1, len(motion_indices) - midpoint)

            if first_half_avg > 0 and (second_half_avg / first_half_avg) < 0.6:
                recommendations.append({
                    "title": "Sustained Reduction in Movement Indicators",
                    "explanation": f"Visual activity indicators declined significantly in the second half of the session ({round(second_half_avg, 1)} vs {round(first_half_avg, 1)}).",
                    "supporting_metric": f"Relative activity drop: {round((1 - second_half_avg/first_half_avg)*100, 1)}%",
                    "timestamp_interval": f"{int(session_duration_sec/120)}m - {int(session_duration_sec/60)}m",
                    "suggested_action": "Consider incorporating interactive polling, structured Q&A, or short group discussion to stimulate classroom dynamics.",
                    "severity": "MEDIUM",
                    "caveat": "Low movement does not establish inattention; quiet focus can also exhibit low movement."
                })

        # 2. Analyze Audio Activity & Speaking Turns
        audio_levels = [p["audio_activity_level"] for p in fused_timeline if p.get("audio_activity_level") is not None]
        speaking_turns = sum(1 for p in fused_timeline if p.get("speaking_turn_detected", False))

        if audio_levels:
            avg_audio = sum(audio_levels) / len(audio_levels)
            if avg_audio < 20.0 or speaking_turns < 3:
                recommendations.append({
                    "title": "Low Verbal Interaction Identified",
                    "explanation": f"Classroom audio levels averaged {round(avg_audio, 1)}/100 with only {speaking_turns} speaking turns identified.",
                    "supporting_metric": f"Audio Activity = {round(avg_audio, 1)}, Turns = {speaking_turns}",
                    "timestamp_interval": "Full Session",
                    "suggested_action": "Incorporate structured think-pair-share or invite questions to promote verbal participation.",
                    "severity": "LOW",
                    "caveat": "Audio activity reflects sound energy, not semantic understanding or private note-taking."
                })

        # 3. Analyze Attendance & Detection Continuity
        needs_review_count = sum(1 for r in attendance_records if r.get("status") == "NEEDS_REVIEW")
        if needs_review_count > 0:
            recommendations.append({
                "title": "Intermittent Participant Tracking Detected",
                "explanation": f"{needs_review_count} participant track(s) exhibited brief or intermittent detection requiring instructor verification.",
                "supporting_metric": f"Uncertain Tracks = {needs_review_count}",
                "timestamp_interval": "Attendance Timeline",
                "suggested_action": "Check camera angle, occlusion zones, and lighting to reduce visual blind spots across desks.",
                "severity": "MEDIUM",
                "caveat": "Never mark unobserved students absent without manual verification and sufficient camera coverage."
            })

        # Ensure at least one positive pedagogical note if session ran smoothly
        if not recommendations:
            recommendations.append({
                "title": "Balanced Observable Engagement Pattern",
                "explanation": "Observed visual activity, head orientation proxies, and interaction intervals maintained consistent levels throughout the session.",
                "supporting_metric": "Consistent temporal metrics across recorded duration",
                "timestamp_interval": "Session Duration",
                "suggested_action": "Continue current instructional pacing and classroom structure.",
                "severity": "INFO",
                "caveat": "Metrics represent behavioral proxies and do not replace holistic teacher assessment."
            })

        return recommendations
