# Multimodal Attendance & Engagement Agent

A privacy-preserving, offline-capable classroom intelligence platform that calculates sustained participant presence and multimodal engagement proxies using local computer vision and audio processing.

Built for submission to **Skill Wallet**.

---

## 1. Core Architectural Pillars

- **Privacy-Preserving Attendance**: Tracks anonymous visual IDs over time instead of single-frame marking. Strictly **NO** facial recognition, facial landmark biometric extraction, or emotion inference.
- **Multimodal Fusion Engine**: Transparent weighted fusion combining optical movement indices, orientation stability proxies, and acoustic energy / speaking-turn estimates.
- **Pedagogical AI Advisory**: Local, offline rule-based recommendation engine offering constructive suggestions for classroom pacing without punitive evaluation.
- **Zero Cloud Dependence**: Runs entirely on local CPU/GPU hardware with local SQLite persistence and local audio/video decoders.

---

## 2. Technology Stack

- **Backend**: FastAPI, Uvicorn, SQLAlchemy, SQLite, Pydantic, OpenCV (BackgroundSubtractorMOG2 & optical flow), SoundFile, SciPy, NumPy, Pytest.
- **Frontend**: React 19, Vite, Tailwind CSS v4, Lucide React, Recharts, Axios, React Router v7.

---

## 3. Directory Structure

```text
├── backend/
│   ├── app/
│   │   ├── api/            # REST API endpoints (participants, sessions, attendance, reports)
│   │   ├── core/           # Configuration, thresholds, and weights
│   │   ├── database/       # SQLAlchemy engine and local SQLite session
│   │   ├── models/         # Database models (Participant, Session, Attendance, Metrics)
│   │   ├── schemas/        # Pydantic request & response models
│   │   ├── services/       # Computer vision, audio analysis, multimodal fusion, advisory engine
│   │   └── workers/        # Asynchronous background processing jobs
│   └── tests/              # Pytest backend validation suite
├── frontend/
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── layouts/        # Application layout & navigation sidebar
│   │   ├── pages/          # Overview, Participants, Sessions, Attendance, Engagement, Suggestions, Reports
│   │   └── services/       # Axios API client
├── data/                   # Local SQLite database
├── uploads/                # Temporary processing directory for classroom recordings
├── reports/                # Generated CSV & JSON reports
└── README.md
```

---

## 4. Quickstart Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### Step 1: Backend Setup
```bash
# In project root:
# 1. Activate virtual environment
.\venv\Scripts\activate      # Windows
# source venv/bin/activate    # Linux / macOS

# 2. Run backend tests to verify environment
$env:PYTHONPATH="backend"
python -m pytest backend/tests/test_backend.py -v

# 3. Start FastAPI server
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
API Documentation and Swagger UI are accessible at: `http://localhost:8000/docs`

### Step 2: Frontend Setup
```bash
cd frontend

# Install dependencies (already completed)
npm install

# Start Vite development server
npm run dev
```
Open your browser at: `http://localhost:5173`

---

## 5. End-to-End Workflow

1. **Roster Setup**: Navigate to `Participants` and register classroom students with roll numbers.
2. **Session Creation**: Go to `Sessions` and click **Create Session**. Specify course title, expected count, and optional custom attendance thresholds.
3. **Upload Media**: Click the cloud upload button on any session card. Upload an MP4 classroom video and/or WAV audio file (a synthetic demo video is provided under `uploads/samples/sample_classroom.mp4`).
4. **Trigger Processing**: Click the play icon. The background worker processes frames, generates anonymous tracks, computes audio activity, fuses proxies, and generates pedagogical advice.
5. **View Attendance**: In `Attendance`, review observed durations and coverage percentages. Associate anonymous tracks with registered students.
6. **Analyze Engagement**: Open `Engagement Analytics` to inspect the temporal composite score and individual modality graphs.
7. **Export Reports**: Go to `Session Reports` to download comprehensive attendance and analytics in CSV or JSON format.

---

## 6. Privacy & Ethical Boundaries

- **No Emotion Recognition**: The system explicitly avoids inferring student emotions, attention, or comprehension from facial expressions.
- **No Biometrics**: Does not store face crops, face embeddings, or voiceprints.
- **Advisory Only**: Recommendations are pedagogical aids for educators and must never be used for punitive student grading.
