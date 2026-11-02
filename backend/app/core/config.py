import os
from typing import List

class Settings:
    PROJECT_NAME: str = "Multimodal Attendance & Engagement Agent"
    API_V1_STR: str = "/api"
    
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "..", "data")
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "..", "uploads")
    REPORT_DIR: str = os.path.join(BASE_DIR, "..", "reports")
    
    # SQLite local DB
    DATABASE_URL: str = f"sqlite:///{os.path.join(DATA_DIR, 'attendance_engagement.db')}"
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]
    
    # Video & Audio Config defaults
    FRAME_SAMPLE_INTERVAL_SEC: float = 1.0  # sample 1 frame per second
    MIN_ATTENDANCE_PCT: float = 60.0        # 60% of observed session duration for present
    MIN_OBSERVED_DURATION_SEC: float = 30.0 # at least 30s of observation
    MIN_CONSECUTIVE_FRAMES: int = 3         # never mark from a single frame
    
    # Engagement weights
    WEIGHT_VISUAL_ACTIVITY: float = 0.35
    WEIGHT_HEAD_ORIENTATION: float = 0.35
    WEIGHT_AUDIO_INTERACTION: float = 0.30
    
    MAX_FILE_SIZE_MB: int = 500

settings = Settings()

# Ensure directories exist
os.makedirs(os.path.abspath(settings.DATA_DIR), exist_ok=True)
os.makedirs(os.path.abspath(settings.UPLOAD_DIR), exist_ok=True)
os.makedirs(os.path.abspath(settings.REPORT_DIR), exist_ok=True)
