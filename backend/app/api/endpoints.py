import os
import shutil
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.config import settings
from app.models.models import (
    Participant as ParticipantModel,
    Session as SessionModel,
    SessionConfiguration as SessionConfigModel,
    ProcessingJob as ProcessingJobModel,
    AttendanceRecord as AttendanceRecordModel,
    EngagementMetric as EngagementMetricModel,
    Recommendation as RecommendationModel
)
from app.schemas.schemas import (
    ParticipantCreate, ParticipantUpdate, ParticipantResponse,
    SessionCreate, SessionUpdate, SessionResponse,
    AttendanceUpdate, AttendanceRecordResponse,
    EngagementMetricResponse, RecommendationResponse,
    ProcessingJobResponse, DashboardSummary
)
from app.services.report_service import ReportService
from app.workers.task_runner import process_session_job

router = APIRouter()

# --- Health Check ---
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

# --- Dashboard Summary ---
@router.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_participants = db.query(ParticipantModel).count()
    total_sessions = db.query(SessionModel).count()
    recent_sessions_count = db.query(SessionModel).filter(
        SessionModel.created_at >= datetime.datetime.utcnow() - datetime.timedelta(days=7)
    ).count()

    attendance_records = db.query(AttendanceRecordModel).all()
    if attendance_records:
        present_count = sum(1 for r in attendance_records if r.status == "PRESENT")
        avg_att = round((present_count / len(attendance_records)) * 100.0, 1)
    else:
        avg_att = 0.0

    eng_metrics = db.query(EngagementMetricModel).filter(EngagementMetricModel.composite_engagement_proxy.isnot(None)).all()
    if eng_metrics:
        avg_eng = round(sum(m.composite_engagement_proxy for m in eng_metrics) / len(eng_metrics), 1)
    else:
        avg_eng = 0.0

    latest_recs = db.query(RecommendationModel).order_by(RecommendationModel.id.desc()).limit(5).all()

    return {
        "total_participants": total_participants,
        "total_sessions": total_sessions,
        "recent_sessions_count": recent_sessions_count,
        "average_attendance_pct": avg_att,
        "average_engagement_proxy": avg_eng,
        "latest_recommendations": latest_recs
    }

# --- Participants CRUD ---
@router.get("/participants", response_model=List[ParticipantResponse])
def get_participants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ParticipantModel).offset(skip).limit(limit).all()

@router.post("/participants", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
def create_participant(data: ParticipantCreate, db: Session = Depends(get_db)):
    existing = db.query(ParticipantModel).filter(ParticipantModel.roll_number == data.roll_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Participant with this roll number already exists.")
    participant = ParticipantModel(**data.dict())
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant

@router.get("/participants/{participant_id}", response_model=ParticipantResponse)
def get_participant(participant_id: int, db: Session = Depends(get_db)):
    participant = db.query(ParticipantModel).filter(ParticipantModel.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found.")
    return participant

@router.put("/participants/{participant_id}", response_model=ParticipantResponse)
def update_participant(participant_id: int, data: ParticipantUpdate, db: Session = Depends(get_db)):
    participant = db.query(ParticipantModel).filter(ParticipantModel.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found.")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(participant, key, value)
    db.commit()
    db.refresh(participant)
    return participant

@router.delete("/participants/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_participant(participant_id: int, db: Session = Depends(get_db)):
    participant = db.query(ParticipantModel).filter(ParticipantModel.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found.")
    db.delete(participant)
    db.commit()
    return None

# --- Sessions CRUD ---
@router.get("/sessions", response_model=List[SessionResponse])
def get_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(SessionModel).order_by(SessionModel.id.desc()).offset(skip).limit(limit).all()

@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(data: SessionCreate, db: Session = Depends(get_db)):
    session_data = data.dict(exclude={"config"})
    if not session_data.get("start_time"):
        session_data["start_time"] = datetime.datetime.utcnow()
    
    session_obj = SessionModel(**session_data)
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)

    config_data = data.config.dict() if data.config else {}
    config_obj = SessionConfigModel(session_id=session_obj.id, **config_data)
    db.add(config_obj)
    db.commit()

    return session_obj

@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session_obj = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session_obj

@router.put("/sessions/{session_id}", response_model=SessionResponse)
def update_session(session_id: int, data: SessionUpdate, db: Session = Depends(get_db)):
    session_obj = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found.")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(session_obj, key, value)
    db.commit()
    db.refresh(session_obj)
    return session_obj

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session_obj = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    # Clean up uploaded files if present
    if session_obj.video_path and os.path.exists(session_obj.video_path):
        try:
            os.remove(session_obj.video_path)
        except Exception:
            pass
    if session_obj.audio_path and os.path.exists(session_obj.audio_path):
        try:
            os.remove(session_obj.audio_path)
        except Exception:
            pass

    db.delete(session_obj)
    db.commit()
    return None

# --- Media Upload & Processing ---
@router.post("/sessions/{session_id}/upload")
async def upload_session_media(
    session_id: int,
    video: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    session_obj = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found.")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    if video:
        safe_v_name = f"session_{session_id}_video_{video.filename}"
        v_dest = os.path.join(settings.UPLOAD_DIR, safe_v_name)
        with open(v_dest, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        session_obj.video_path = v_dest

    if audio:
        safe_a_name = f"session_{session_id}_audio_{audio.filename}"
        a_dest = os.path.join(settings.UPLOAD_DIR, safe_a_name)
        with open(a_dest, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        session_obj.audio_path = a_dest

    session_obj.status = "UPLOADED"
    db.commit()

    return {
        "message": "Media uploaded successfully.",
        "video_path": session_obj.video_path,
        "audio_path": session_obj.audio_path
    }

@router.post("/sessions/{session_id}/process")
def trigger_session_processing(
    session_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    session_obj = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found.")

    if not session_obj.video_path and not session_obj.audio_path:
        raise HTTPException(status_code=400, detail="No media file available to process for this session.")

    # Create job entry
    job = ProcessingJobModel(
        session_id=session_id,
        status="QUEUED",
        progress=0.0,
        current_step="Queued for analysis"
    )
    db.add(job)
    session_obj.status = "QUEUED"
    db.commit()

    # Launch background task
    background_tasks.add_task(process_session_job, session_id)

    return {"message": "Processing job queued successfully.", "job_id": job.id}

@router.get("/sessions/{session_id}/status", response_model=Optional[ProcessingJobResponse])
def get_session_processing_status(session_id: int, db: Session = Depends(get_db)):
    job = db.query(ProcessingJobModel).filter(
        ProcessingJobModel.session_id == session_id
    ).order_by(ProcessingJobModel.id.desc()).first()
    return job

# --- Attendance Endpoints ---
@router.get("/sessions/{session_id}/attendance", response_model=List[AttendanceRecordResponse])
def get_session_attendance(session_id: int, db: Session = Depends(get_db)):
    return db.query(AttendanceRecordModel).filter(AttendanceRecordModel.session_id == session_id).all()

@router.patch("/sessions/{session_id}/attendance/{record_id}", response_model=AttendanceRecordResponse)
def update_attendance_record(
    session_id: int,
    record_id: int,
    data: AttendanceUpdate,
    db: Session = Depends(get_db)
):
    record = db.query(AttendanceRecordModel).filter(
        AttendanceRecordModel.id == record_id,
        AttendanceRecordModel.session_id == session_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found.")

    if data.participant_id is not None:
        participant = db.query(ParticipantModel).filter(ParticipantModel.id == data.participant_id).first()
        if not participant:
            raise HTTPException(status_code=400, detail="Participant does not exist.")
        record.participant_id = data.participant_id

    if data.status is not None:
        record.status = data.status
        record.is_manual_override = True
        record.override_timestamp = datetime.datetime.utcnow()

    if data.override_notes is not None:
        record.override_notes = data.override_notes

    db.commit()
    db.refresh(record)
    return record

# --- Engagement & Recommendations ---
@router.get("/sessions/{session_id}/engagement", response_model=List[EngagementMetricResponse])
def get_session_engagement(session_id: int, db: Session = Depends(get_db)):
    return db.query(EngagementMetricModel).filter(
        EngagementMetricModel.session_id == session_id
    ).order_by(EngagementMetricModel.timestamp_sec.asc()).all()

@router.get("/sessions/{session_id}/recommendations", response_model=List[RecommendationResponse])
def get_session_recommendations(session_id: int, db: Session = Depends(get_db)):
    return db.query(RecommendationModel).filter(RecommendationModel.session_id == session_id).all()

# --- Reports & Exports ---
@router.get("/sessions/{session_id}/report")
def get_full_session_report(session_id: int, db: Session = Depends(get_db)):
    session_obj = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found.")

    attendance = db.query(AttendanceRecordModel).filter(AttendanceRecordModel.session_id == session_id).all()
    engagement = db.query(EngagementMetricModel).filter(EngagementMetricModel.session_id == session_id).all()
    recommendations = db.query(RecommendationModel).filter(RecommendationModel.session_id == session_id).all()

    present_count = sum(1 for a in attendance if a.status == "PRESENT")
    total_tracks = len(attendance)
    attendance_rate = (present_count / total_tracks * 100.0) if total_tracks > 0 else 0.0

    report_payload = {
        "session": {
            "id": session_obj.id,
            "title": session_obj.title,
            "course_name": session_obj.course_name,
            "instructor_name": session_obj.instructor_name,
            "start_time": session_obj.start_time,
            "media_duration_sec": session_obj.media_duration_sec,
            "status": session_obj.status
        },
        "summary": {
            "total_observed_tracks": total_tracks,
            "present_count": present_count,
            "attendance_rate_pct": round(attendance_rate, 1),
            "recommendations_count": len(recommendations)
        },
        "attendance": [
            {
                "id": a.id,
                "anonymous_track_id": a.anonymous_track_id,
                "participant_name": a.participant.name if a.participant else "Unassigned",
                "roll_number": a.participant.roll_number if a.participant else None,
                "status": a.status,
                "observed_pct": a.observed_pct,
                "total_observed_sec": a.total_observed_sec,
                "evidence_quality": a.evidence_quality,
                "is_manual_override": a.is_manual_override
            } for a in attendance
        ],
        "recommendations": [
            {
                "title": r.title,
                "explanation": r.explanation,
                "supporting_metric": r.supporting_metric,
                "timestamp_interval": r.timestamp_interval,
                "suggested_action": r.suggested_action,
                "severity": r.severity,
                "caveat": r.caveat
            } for r in recommendations
        ],
        "engagement_timeline_sample": [
            {
                "timestamp_sec": e.timestamp_sec,
                "visual_activity_index": e.visual_activity_index,
                "audio_activity_level": e.audio_activity_level,
                "composite_engagement_proxy": e.composite_engagement_proxy
            } for e in engagement[:50]
        ]
    }
    return report_payload

@router.get("/sessions/{session_id}/export/csv")
def export_attendance_csv(session_id: int, db: Session = Depends(get_db)):
    attendance = db.query(AttendanceRecordModel).filter(AttendanceRecordModel.session_id == session_id).all()
    records_data = []
    for a in attendance:
        records_data.append({
            "anonymous_track_id": a.anonymous_track_id,
            "participant_name": a.participant.name if a.participant else "Unassigned",
            "roll_number": a.participant.roll_number if a.participant else "N/A",
            "status": a.status,
            "observed_pct": a.observed_pct,
            "total_observed_sec": a.total_observed_sec,
            "evidence_quality": a.evidence_quality,
            "is_manual_override": a.is_manual_override,
            "override_notes": a.override_notes
        })
    csv_content = ReportService.generate_csv_attendance(records_data)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=attendance_session_{session_id}.csv"}
    )

@router.get("/sessions/{session_id}/export/json")
def export_session_json(session_id: int, db: Session = Depends(get_db)):
    report_data = get_full_session_report(session_id, db)
    json_content = ReportService.generate_json_report(report_data)
    return Response(
        content=json_content,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=session_report_{session_id}.json"}
    )
