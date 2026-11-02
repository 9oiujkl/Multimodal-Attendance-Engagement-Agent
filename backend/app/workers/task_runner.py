import os
import datetime
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.models import (
    Session as SessionModel,
    ProcessingJob,
    AttendanceRecord,
    EngagementMetric,
    Recommendation,
    SessionConfiguration
)
from app.services.video_processor import VideoProcessor
from app.services.audio_processor import AudioProcessor
from app.services.engagement_analyzer import EngagementAnalyzer
from app.services.attendance_service import AttendanceService
from app.services.recommendation_engine import RecommendationEngine

def process_session_job(session_id: int):
    """
    Background worker task to execute multimodal analysis pipeline on uploaded session media.
    """
    db: Session = SessionLocal()
    job = None
    try:
        session_obj = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session_obj:
            return

        job = db.query(ProcessingJob).filter(
            ProcessingJob.session_id == session_id
        ).order_by(ProcessingJob.id.desc()).first()

        if not job:
            job = ProcessingJob(session_id=session_id, status="RUNNING", started_at=datetime.datetime.utcnow())
            db.add(job)
            db.commit()
            db.refresh(job)
        else:
            job.status = "RUNNING"
            job.started_at = datetime.datetime.utcnow()
            job.progress = 5.0
            job.current_step = "Starting media analysis pipeline"
            db.commit()

        session_obj.status = "PROCESSING"
        db.commit()

        # Load configuration
        config = session_obj.configuration
        min_pct = config.min_attendance_pct if config else 60.0
        min_dur = config.min_observed_duration_sec if config else 30.0
        sample_interval = config.frame_sample_interval_sec if config else 1.0

        w_vis = config.weight_visual if config else 0.35
        w_ori = config.weight_orientation if config else 0.35
        w_aud = config.weight_audio if config else 0.30

        video_path = session_obj.video_path
        audio_path = session_obj.audio_path

        def update_job_progress(progress_pct: float, step_msg: str):
            if job:
                job.progress = round(progress_pct, 1)
                job.current_step = step_msg
                db.commit()

        # 1. Process Video
        visual_timeline = []
        track_attendance_stats = []
        total_duration_sec = 0.0

        if video_path and os.path.exists(video_path):
            update_job_progress(10.0, "Decoding and sampling video frames")
            video_proc = VideoProcessor(sample_interval_sec=sample_interval)
            video_results = video_proc.process_video(video_path, progress_callback=update_job_progress)
            visual_timeline = video_results["timeline_metrics"]
            track_attendance_stats = video_results["track_attendance_stats"]
            total_duration_sec = video_results["metadata"]["duration_sec"]
            session_obj.media_duration_sec = total_duration_sec
            db.commit()

        # 2. Process Audio
        audio_timeline = []
        if audio_path and os.path.exists(audio_path):
            update_job_progress(55.0, "Extracting audio energy and speaking turns")
            audio_proc = AudioProcessor()
            audio_results = audio_proc.process_audio(audio_path, progress_callback=update_job_progress)
            audio_timeline = audio_results["timeline_metrics"]
            if total_duration_sec == 0.0:
                total_duration_sec = audio_results["duration_sec"]
                session_obj.media_duration_sec = total_duration_sec
                db.commit()

        # 3. Multimodal Fusion
        update_job_progress(82.0, "Fusing multimodal behavioral proxies")
        fusion_engine = EngagementAnalyzer(weight_visual=w_vis, weight_orientation=w_ori, weight_audio=w_aud)
        fused_timeline = fusion_engine.fuse_signals(visual_timeline, audio_timeline)

        # 4. Calculate Attendance
        update_job_progress(88.0, "Applying attendance verification rules")
        attendance_calc = AttendanceService.calculate_attendance_records(
            track_stats=track_attendance_stats,
            session_duration_sec=total_duration_sec,
            min_attendance_pct=min_pct,
            min_observed_duration_sec=min_dur
        )

        # 5. Clear previous records and save new records
        db.query(AttendanceRecord).filter(AttendanceRecord.session_id == session_id).delete()
        db.query(EngagementMetric).filter(EngagementMetric.session_id == session_id).delete()
        db.query(Recommendation).filter(Recommendation.session_id == session_id).delete()

        for rec in attendance_calc:
            att_obj = AttendanceRecord(
                session_id=session_id,
                anonymous_track_id=rec["anonymous_track_id"],
                first_detected_sec=rec["first_detected_sec"],
                last_detected_sec=rec["last_detected_sec"],
                total_observed_sec=rec["total_observed_sec"],
                observed_pct=rec["observed_pct"],
                status=rec["status"],
                evidence_quality=rec["evidence_quality"]
            )
            db.add(att_obj)

        for met in fused_timeline:
            eng_obj = EngagementMetric(
                session_id=session_id,
                timestamp_sec=met["timestamp_sec"],
                window_duration_sec=sample_interval,
                visual_activity_index=met["visual_activity_index"],
                head_pose_orientation_score=met["head_pose_orientation_score"],
                audio_activity_level=met["audio_activity_level"],
                speaking_turn_detected=met["speaking_turn_detected"],
                composite_engagement_proxy=met["composite_engagement_proxy"],
                signal_confidence=met["signal_confidence"],
                modalities_available=met["modalities_available"]
            )
            db.add(eng_obj)

        # 6. Generate AI Teaching Suggestions
        update_job_progress(95.0, "Generating contextual pedagogical recommendations")
        recs = RecommendationEngine.generate_recommendations(
            fused_timeline=fused_timeline,
            attendance_records=attendance_calc,
            session_duration_sec=total_duration_sec
        )

        for r in recs:
            rec_obj = Recommendation(
                session_id=session_id,
                title=r["title"],
                explanation=r["explanation"],
                supporting_metric=r["supporting_metric"],
                timestamp_interval=r["timestamp_interval"],
                suggested_action=r["suggested_action"],
                severity=r["severity"],
                caveat=r["caveat"]
            )
            db.add(rec_obj)

        # Complete job
        job.status = "COMPLETED"
        job.progress = 100.0
        job.current_step = "Processing complete"
        job.completed_at = datetime.datetime.utcnow()
        session_obj.status = "COMPLETED"
        db.commit()

    except Exception as e:
        db.rollback()
        if job:
            job.status = "FAILED"
            job.error_message = str(e)
            job.completed_at = datetime.datetime.utcnow()
        if session_obj:
            session_obj.status = "FAILED"
        db.commit()
    finally:
        db.close()
