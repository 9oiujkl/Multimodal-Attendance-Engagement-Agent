import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.session import Base, get_db, engine
from app.services.attendance_service import AttendanceService
from app.services.engagement_analyzer import EngagementAnalyzer
from app.services.recommendation_engine import RecommendationEngine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up data between tests
    with engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_participant_crud():
    # 1. Create participant
    payload = {
        "roll_number": "CS-101",
        "name": "Alice Johnson",
        "group_name": "Section A",
        "notes": "Lab representative"
    }
    res = client.post("/api/participants", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Alice Johnson"
    participant_id = data["id"]

    # 2. Get participant
    res_get = client.get(f"/api/participants/{participant_id}")
    assert res_get.status_code == 200
    assert res_get.json()["roll_number"] == "CS-101"

    # 3. Update participant
    res_up = client.put(f"/api/participants/{participant_id}", json={"name": "Alice M. Johnson"})
    assert res_up.status_code == 200
    assert res_up.json()["name"] == "Alice M. Johnson"

    # 4. Delete participant
    res_del = client.delete(f"/api/participants/{participant_id}")
    assert res_del.status_code == 204

def test_session_crud():
    payload = {
        "title": "Computer Vision Lecture 1",
        "course_name": "CS402",
        "instructor_name": "Dr. Smith",
        "description": "Introduction to optical flow and feature tracking",
        "expected_participant_count": 35
    }
    res = client.post("/api/sessions", json=payload)
    assert res.status_code == 201
    session_id = res.json()["id"]

    # Verify session retrieval
    res_get = client.get(f"/api/sessions/{session_id}")
    assert res_get.status_code == 200
    assert res_get.json()["title"] == "Computer Vision Lecture 1"

def test_attendance_calculation_rules():
    track_stats = [
        # Present: observed 70% of 100s, 30 frames
        {
            "track_id": "Track_1",
            "first_detected_sec": 5.0,
            "last_detected_sec": 95.0,
            "total_observed_sec": 70.0,
            "observed_pct": 70.0,
            "detection_count": 30
        },
        # Needs Review: single frame detection
        {
            "track_id": "Track_2",
            "first_detected_sec": 10.0,
            "last_detected_sec": 10.0,
            "total_observed_sec": 1.0,
            "observed_pct": 1.0,
            "detection_count": 1
        },
        # Partial: observed 40s (40%)
        {
            "track_id": "Track_3",
            "first_detected_sec": 10.0,
            "last_detected_sec": 80.0,
            "total_observed_sec": 40.0,
            "observed_pct": 40.0,
            "detection_count": 20
        }
    ]

    records = AttendanceService.calculate_attendance_records(
        track_stats=track_stats,
        session_duration_sec=100.0,
        min_attendance_pct=60.0,
        min_observed_duration_sec=30.0,
        min_consecutive_frames=3
    )

    assert len(records) == 3
    assert records[0]["status"] == "PRESENT"
    assert records[0]["evidence_quality"] == "HIGH"

    assert records[1]["status"] == "NEEDS_REVIEW"
    assert records[1]["evidence_quality"] == "LOW"

    assert records[2]["status"] == "PARTIAL"
    assert records[2]["evidence_quality"] == "MEDIUM"

def test_multimodal_fusion_normalization():
    fusion = EngagementAnalyzer(weight_visual=0.35, weight_orientation=0.35, weight_audio=0.30)
    
    # Case 1: All modalities present
    v_timeline = [{"timestamp_sec": 1.0, "motion_index": 50.0, "orientation_score": 80.0}]
    a_timeline = [{"timestamp_sec": 1.0, "audio_activity_level": 40.0, "speaking_turn_detected": True}]
    fused = fusion.fuse_signals(v_timeline, a_timeline)
    
    assert len(fused) == 1
    # 50*0.35 + 80*0.35 + 40*0.30 = 17.5 + 28.0 + 12.0 = 57.5
    assert fused[0]["composite_engagement_proxy"] == 57.5
    assert fused[0]["modalities_available"] == "MULTIMODAL"

    # Case 2: Missing audio modality (renormalize visual weights)
    fused_video_only = fusion.fuse_signals(v_timeline, None)
    # (50*0.35 + 80*0.35) / 0.70 = 65.0
    assert fused_video_only[0]["composite_engagement_proxy"] == 65.0
    assert fused_video_only[0]["modalities_available"] == "VIDEO_ONLY"

def test_recommendation_engine_generation():
    fused_timeline = [
        {"timestamp_sec": float(i), "visual_activity_index": 80.0 if i < 10 else 20.0, "audio_activity_level": 5.0, "speaking_turn_detected": False}
        for i in range(20)
    ]
    attendance = [{"status": "NEEDS_REVIEW"}]
    
    recs = RecommendationEngine.generate_recommendations(fused_timeline, attendance, 20.0)
    assert len(recs) >= 2
    titles = [r["title"] for r in recs]
    assert any("Reduction in Movement" in t for t in titles)
    assert any("Low Verbal Interaction" in t for t in titles)
