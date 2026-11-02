import os
import cv2
import numpy as np
import soundfile as sf
from app.services.video_processor import VideoProcessor
from app.services.audio_processor import AudioProcessor
from app.services.engagement_analyzer import EngagementAnalyzer
from app.services.attendance_service import AttendanceService
from app.services.recommendation_engine import RecommendationEngine

def generate_sample_media():
    os.makedirs("uploads/samples", exist_ok=True)
    video_path = "uploads/samples/sample_classroom.mp4"
    audio_path = "uploads/samples/sample_audio.wav"

    # 1. Generate 5-second sample video with synthetic moving participant boxes
    width, height = 640, 480
    fps = 20
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    for frame_idx in range(fps * 5):
        frame = np.ones((height, width, 3), dtype=np.uint8) * 240
        # Draw background classroom whiteboard
        cv2.rectangle(frame, (100, 30), (540, 160), (220, 220, 220), -1)
        cv2.putText(frame, "CS402 Lecture", (180, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (80, 80, 80), 2)

        # Draw participant 1: sitting at (180, 320)
        p1_x = int(180 + np.sin(frame_idx * 0.1) * 8)
        cv2.rectangle(frame, (p1_x, 260), (p1_x + 80, 420), (60, 120, 200), -1)
        cv2.circle(frame, (p1_x + 40, 230), 25, (200, 160, 120), -1)

        # Draw participant 2: sitting at (400, 320)
        p2_x = 400
        cv2.rectangle(frame, (p2_x, 260), (p2_x + 80, 420), (80, 160, 100), -1)
        cv2.circle(frame, (p2_x + 40, 230), 25, (190, 150, 110), -1)

        out.write(frame)

    out.release()
    print("Sample video generated:", video_path)

    # 2. Generate 5-second sample audio with active pulses
    sample_rate = 16000
    t = np.linspace(0, 5, sample_rate * 5)
    # 2 seconds active tone, 1 sec silence, 2 sec active speech tone
    audio_signal = np.sin(2 * np.pi * 440 * t) * 0.3
    audio_signal[sample_rate * 2 : sample_rate * 3] = 0.0  # silence interval

    sf.write(audio_path, audio_signal, sample_rate)
    print("Sample audio generated:", audio_path)

    # 3. Test video pipeline
    v_proc = VideoProcessor(sample_interval_sec=1.0)
    v_res = v_proc.process_video(video_path)
    print("Video processed successfully! Metadata:", v_res["metadata"])
    print("Visual timeline metrics count:", len(v_res["timeline_metrics"]))

    # 4. Test audio pipeline
    a_proc = AudioProcessor(window_size_sec=1.0)
    a_res = a_proc.process_audio(audio_path)
    print("Audio processed successfully! Duration:", a_res["duration_sec"], "Speaking turns:", a_res["total_speaking_turns"])

    # 5. Multimodal fusion
    fusion = EngagementAnalyzer()
    fused = fusion.fuse_signals(v_res["timeline_metrics"], a_res["timeline_metrics"])
    print("Fused metrics count:", len(fused))

    # 6. Recommendation generation
    recs = RecommendationEngine.generate_recommendations(fused, v_res["track_attendance_stats"], 5.0)
    print("Generated recommendations count:", len(recs))
    for r in recs:
        print(f" -> [{r['severity']}] {r['title']}: {r['suggested_action']}")

if __name__ == "__main__":
    generate_sample_media()
