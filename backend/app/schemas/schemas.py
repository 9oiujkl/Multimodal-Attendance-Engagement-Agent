from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Participant Schemas ---
class ParticipantBase(BaseModel):
    roll_number: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    group_name: Optional[str] = None
    notes: Optional[str] = None

class ParticipantCreate(ParticipantBase):
    pass

class ParticipantUpdate(BaseModel):
    name: Optional[str] = None
    group_name: Optional[str] = None
    notes: Optional[str] = None

class ParticipantResponse(ParticipantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Session Config Schemas ---
class SessionConfigBase(BaseModel):
    min_attendance_pct: float = 60.0
    min_observed_duration_sec: float = 30.0
    frame_sample_interval_sec: float = 1.0
    weight_visual: float = 0.35
    weight_orientation: float = 0.35
    weight_audio: float = 0.30

class SessionConfigResponse(SessionConfigBase):
    id: int
    session_id: int

    class Config:
        from_attributes = True

# --- Session Schemas ---
class SessionBase(BaseModel):
    title: str = Field(..., max_length=150)
    course_name: str = Field(..., max_length=100)
    instructor_name: str = Field(..., max_length=100)
    description: Optional[str] = None
    expected_participant_count: Optional[int] = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class SessionCreate(SessionBase):
    config: Optional[SessionConfigBase] = None

class SessionUpdate(BaseModel):
    title: Optional[str] = None
    course_name: Optional[str] = None
    instructor_name: Optional[str] = None
    description: Optional[str] = None
    expected_participant_count: Optional[int] = None
    status: Optional[str] = None

class SessionResponse(SessionBase):
    id: int
    status: str
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    media_duration_sec: Optional[float] = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Attendance Schemas ---
class AttendanceRecordBase(BaseModel):
    anonymous_track_id: str
    first_detected_sec: float
    last_detected_sec: float
    total_observed_sec: float
    observed_pct: float
    status: str
    evidence_quality: str
    is_manual_override: bool = False
    override_notes: Optional[str] = None
    participant_id: Optional[int] = None

class AttendanceUpdate(BaseModel):
    participant_id: Optional[int] = None
    status: Optional[str] = None
    override_notes: Optional[str] = None

class AttendanceRecordResponse(AttendanceRecordBase):
    id: int
    session_id: int
    participant: Optional[ParticipantResponse] = None
    override_timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Engagement Schemas ---
class EngagementMetricResponse(BaseModel):
    id: int
    session_id: int
    timestamp_sec: float
    window_duration_sec: float
    visual_activity_index: Optional[float] = None
    head_pose_orientation_score: Optional[float] = None
    audio_activity_level: Optional[float] = None
    speaking_turn_detected: bool
    composite_engagement_proxy: Optional[float] = None
    signal_confidence: float
    modalities_available: str

    class Config:
        from_attributes = True

# --- Recommendation Schemas ---
class RecommendationResponse(BaseModel):
    id: int
    session_id: int
    title: str
    explanation: str
    supporting_metric: str
    timestamp_interval: Optional[str] = None
    suggested_action: str
    severity: str
    caveat: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Processing Job Schemas ---
class ProcessingJobResponse(BaseModel):
    id: int
    session_id: int
    job_type: str
    status: str
    progress: float
    current_step: str
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Dashboard & Reports ---
class DashboardSummary(BaseModel):
    total_participants: int
    total_sessions: int
    recent_sessions_count: int
    average_attendance_pct: float
    average_engagement_proxy: float
    latest_recommendations: List[RecommendationResponse]
