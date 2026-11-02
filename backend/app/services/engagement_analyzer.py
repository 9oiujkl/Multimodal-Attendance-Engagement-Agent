from typing import List, Dict, Any, Optional

class EngagementAnalyzer:
    """
    Multimodal fusion engine.
    Fuses visual movement, head/pose orientation indicators, and audio activity
    into transparent, observable behavioral indicators (0-100 scale).
    Renormalizes weights if one modality is unavailable.
    Does NOT infer emotions, comprehension, or attention.
    """
    def __init__(self, weight_visual: float = 0.35, weight_orientation: float = 0.35, weight_audio: float = 0.30):
        self.w_visual = weight_visual
        self.w_orient = weight_orientation
        self.w_audio = weight_audio

    def fuse_signals(
        self,
        visual_timeline: List[Dict[str, Any]],
        audio_timeline: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        # Map audio timestamps for fast lookup
        audio_map = {}
        if audio_timeline:
            for item in audio_timeline:
                # Key by rounded 1-second interval
                t_sec = int(round(item["timestamp_sec"]))
                audio_map[t_sec] = item

        fused_timeline = []

        for v_point in visual_timeline:
            t = v_point["timestamp_sec"]
            t_int = int(round(t))
            
            motion = v_point.get("motion_index")
            orient = v_point.get("orientation_score")
            
            a_point = audio_map.get(t_int)
            audio_act = a_point.get("audio_activity_level") if a_point else None
            speaking_turn = a_point.get("speaking_turn_detected", False) if a_point else False

            # Modality availability & weight renormalization
            available_weights = []
            values = []

            if motion is not None:
                available_weights.append(self.w_visual)
                values.append(motion)

            if orient is not None:
                available_weights.append(self.w_orient)
                values.append(orient)

            if audio_act is not None:
                available_weights.append(self.w_audio)
                values.append(audio_act)

            if len(values) == 0:
                proxy_score = None
                confidence = 0.0
                modality_label = "NONE"
            else:
                total_w = sum(available_weights)
                norm_weights = [w / total_w for w in available_weights]
                proxy_score = sum(val * weight for val, weight in zip(values, norm_weights))
                proxy_score = round(float(proxy_score), 2)
                confidence = round(total_w / (self.w_visual + self.w_orient + self.w_audio), 2)
                
                if len(values) >= 3:
                    modality_label = "MULTIMODAL"
                elif audio_act is not None:
                    modality_label = "AUDIO_FUSED"
                else:
                    modality_label = "VIDEO_ONLY"

            fused_timeline.append({
                "timestamp_sec": t,
                "visual_activity_index": motion,
                "head_pose_orientation_score": orient,
                "audio_activity_level": audio_act,
                "speaking_turn_detected": speaking_turn,
                "composite_engagement_proxy": proxy_score,
                "signal_confidence": confidence,
                "modalities_available": modality_label
            })

        return fused_timeline
