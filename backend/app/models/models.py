import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    roll_number = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    group_name = Column(String(100), nullable=True) # class or section
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    attendance_records = relationship("AttendanceRecord", back_populates="participant", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    course_name = Column(String(100), nullable=False)
    instructor_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    expected_participant_count = Column(Integer, default=0)
    
    start_time = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(50), default="CREATED")  # CREATED, UPLOADING, PROCESSING, COMPLETED, FAILED
    
    video_path = Column(String(255), nullable=True)
    audio_path = Column(String(255), nullable=True)
    media_duration_sec = Column(Float, nullable=True, default=0.0)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    jobs = relationship("ProcessingJob", back_populates="session", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", back_populates="session", cascade="all, delete-orphan")
    engagement_metrics = relationship("EngagementMetric", back_populates="session", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="session", cascade="all, delete-orphan")
    configuration = relationship("SessionConfiguration", uselist=False, back_populates="session", cascade="all, delete-orphan")

class SessionConfiguration(Base):
    __tablename__ = "session_configurations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), unique=True)
    
    min_attendance_pct = Column(Float, default=60.0)
    min_observed_duration_sec = Column(Float, default=30.0)
    frame_sample_interval_sec = Column(Float, default=1.0)
    
    weight_visual = Column(Float, default=0.35)
    weight_orientation = Column(Float, default=0.35)
    weight_audio = Column(Float, default=0.30)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    session = relationship("Session", back_populates="configuration")

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    job_type = Column(String(50), default="MULTIMODAL_ANALYSIS")
    status = Column(String(50), default="QUEUED") # QUEUED, RUNNING, COMPLETED, FAILED
    progress = Column(Float, default=0.0) # 0 to 100
    current_step = Column(String(100), default="Initialized")
    error_message = Column(Text, nullable=True)
    
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    session = relationship("Session", back_populates="jobs")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    participant_id = Column(Integer, ForeignKey("participants.id", ondelete="SET NULL"), nullable=True)
    anonymous_track_id = Column(String(50), nullable=False) # e.g. Track_1, Track_2
    
    first_detected_sec = Column(Float, default=0.0)
    last_detected_sec = Column(Float, default=0.0)
    total_observed_sec = Column(Float, default=0.0)
    observed_pct = Column(Float, default=0.0)
    
    status = Column(String(50), default="NEEDS_REVIEW") # PRESENT, PARTIAL, ABSENT, NEEDS_REVIEW
    evidence_quality = Column(String(50), default="MEDIUM") # HIGH, MEDIUM, LOW
    is_manual_override = Column(Boolean, default=False)
    override_notes = Column(Text, nullable=True)
    override_timestamp = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    session = relationship("Session", back_populates="attendance_records")
    participant = relationship("Participant", back_populates="attendance_records")

class EngagementMetric(Base):
    __tablename__ = "engagement_metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    timestamp_sec = Column(Float, nullable=False) # Offset from session start
    window_duration_sec = Column(Float, default=5.0)
    
    visual_activity_index = Column(Float, nullable=True) # 0 to 100
    head_pose_orientation_score = Column(Float, nullable=True) # 0 to 100
    audio_activity_level = Column(Float, nullable=True) # 0 to 100
    speaking_turn_detected = Column(Boolean, default=False)
    
    composite_engagement_proxy = Column(Float, nullable=True) # 0 to 100
    signal_confidence = Column(Float, default=1.0) # 0 to 1
    modalities_available = Column(String(50), default="VIDEO_AUDIO") # VIDEO_ONLY, AUDIO_ONLY, MULTIMODAL
    
    session = relationship("Session", back_populates="engagement_metrics")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    
    title = Column(String(200), nullable=False)
    explanation = Column(Text, nullable=False)
    supporting_metric = Column(String(100), nullable=False)
    timestamp_interval = Column(String(100), nullable=True) # e.g. "12:00 - 15:30"
    suggested_action = Column(Text, nullable=False)
    severity = Column(String(20), default="MEDIUM") # HIGH, MEDIUM, LOW, INFO
    caveat = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    session = relationship("Session", back_populates="recommendations")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
