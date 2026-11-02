import os
import numpy as np
import soundfile as sf
from typing import Dict, Any, List, Optional

class AudioProcessor:
    """
    Real local audio processing using soundfile and numpy/scipy.
    Calculates RMS energy, short-time energy, audio activity intervals, and speaking-turn proxies.
    Gracefully handles silence, missing audio, and missing codecs.
    Never identifies voiceprints, biometric speaker profiles, or transcripts.
    """
    def __init__(self, window_size_sec: float = 1.0, silence_threshold_db: float = -40.0):
        self.window_size_sec = window_size_sec
        self.silence_threshold_db = silence_threshold_db

    def process_audio(self, audio_path: str, progress_callback=None) -> Dict[str, Any]:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            data, sample_rate = sf.read(audio_path)
        except Exception as e:
            raise ValueError(f"Unable to read audio file format: {str(e)}")

        # Convert stereo to mono if needed
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)

        total_samples = len(data)
        duration_sec = total_samples / float(sample_rate) if sample_rate > 0 else 0.0

        if duration_sec == 0 or total_samples == 0:
            return {
                "duration_sec": 0.0,
                "is_silent": True,
                "timeline_metrics": []
            }

        window_samples = int(sample_rate * self.window_size_sec)
        num_windows = int(np.ceil(total_samples / float(window_samples)))

        timeline_metrics = []
        speaking_turns = 0
        was_active = False

        for i in range(num_windows):
            start_idx = i * window_samples
            end_idx = min(start_idx + window_samples, total_samples)
            chunk = data[start_idx:end_idx]

            # RMS energy
            rms = np.sqrt(np.mean(chunk**2)) if len(chunk) > 0 else 0.0
            
            # Convert to dB relative to 1.0
            if rms > 1e-7:
                db = 20 * np.log10(rms)
            else:
                db = -100.0

            # Activity determination
            is_active = bool(db > self.silence_threshold_db)
            
            # Normalized activity index (0-100)
            # Map [-60dB, -10dB] to [0, 100]
            normalized_activity = float(np.clip((db + 60.0) * (100.0 / 50.0), 0.0, 100.0))

            # Approximate speaking turn transition
            speaking_turn_detected = False
            if is_active and not was_active:
                speaking_turns += 1
                speaking_turn_detected = True
            was_active = is_active

            timestamp_sec = i * self.window_size_sec
            timeline_metrics.append({
                "timestamp_sec": round(timestamp_sec, 2),
                "rms_energy": float(rms),
                "energy_db": float(round(db, 2)),
                "audio_activity_level": float(round(normalized_activity, 2)),
                "is_active": is_active,
                "speaking_turn_detected": speaking_turn_detected
            })

            if progress_callback and num_windows > 0:
                pct = 50.0 + (i / float(num_windows)) * 30.0 # 50-80% for audio
                progress_callback(pct, f"Analyzing audio timeline at {round(timestamp_sec, 1)}s")

        return {
            "duration_sec": round(duration_sec, 2),
            "sample_rate": sample_rate,
            "total_speaking_turns": speaking_turns,
            "timeline_metrics": timeline_metrics
        }
