from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Header
from fastapi.middleware.cors import CORSMiddleware
from .models import Diagnosis, Feedback, Field, FieldCreate, Role, User
from .pipeline import analyze_video, to_diagnosis

app = FastAPI(title="Rakshak AI API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
fields: dict[str, Field] = {}
videos: dict[str, dict] = {}
diagnoses: dict[str, dict] = {}

def current_user(x_role: str | None) -> User:
    role = Role(x_role or "farmer")
    return User(id="demo-user", email="demo@rakshak.ai", role=role, organization_id="demo-org")

@app.get("/health")
def health(): return {"status": "ok", "service": "rakshak-api"}

@app.post("/api/v1/auth/login")
def login(): return {"access_token": "demo-token", "token_type": "bearer", "user": current_user(None).model_dump()}

@app.get("/api/v1/me")
def me(x_role: str | None = Header(default=None)): return current_user(x_role)

@app.post("/api/v1/fields", response_model=Field)
def create_field(payload: FieldCreate):
    field = Field(id=str(uuid4()), owner_id="demo-user", **payload.model_dump())
    fields[field.id] = field
    return field

@app.get("/api/v1/fields")
def list_fields(): return list(fields.values())

@app.post("/api/v1/videos")
async def upload_video(field_id: str = Form(...), consent: bool = Form(...), file: UploadFile = File(...)):
    if field_id not in fields: raise HTTPException(404, "Field not found")
    if not consent: raise HTTPException(400, "Consent is required")
    video_id = str(uuid4())
    suffix = Path(file.filename or "video.mp4").suffix or ".mp4"
    with NamedTemporaryFile(delete=False, suffix=suffix) as target:
        target.write(await file.read())
        path = target.name
    result = analyze_video(path)
    diagnosis_id = str(uuid4())
    diagnosis = to_diagnosis(result)
    diagnosis["id"] = diagnosis_id
    diagnosis["video_id"] = video_id
    diagnoses[diagnosis_id] = diagnosis
    videos[video_id] = {"id": video_id, "field_id": field_id, "filename": file.filename, "status": "completed", "diagnosis_id": diagnosis_id, "created_at": datetime.now(timezone.utc).isoformat()}
    return videos[video_id]

@app.get("/api/v1/videos/{video_id}/status")
def video_status(video_id: str):
    if video_id not in videos: raise HTTPException(404, "Video not found")
    return {"video_id": video_id, "status": videos[video_id]["status"]}

@app.get("/api/v1/videos/{video_id}/analysis")
def video_analysis(video_id: str):
    if video_id not in videos: raise HTTPException(404, "Video not found")
    return diagnoses[videos[video_id]["diagnosis_id"]]

@app.get("/api/v1/diagnosis/{analysis_id}", response_model=Diagnosis)
def diagnosis(analysis_id: str):
    if analysis_id not in diagnoses: raise HTTPException(404, "Analysis not found")
    return diagnoses[analysis_id]

@app.post("/api/v1/diagnosis/{analysis_id}/feedback")
def feedback(analysis_id: str, payload: Feedback):
    if analysis_id not in diagnoses: raise HTTPException(404, "Analysis not found")
    diagnoses[analysis_id]["feedback"] = payload.model_dump()
    return {"status": "recorded", "analysis_id": analysis_id}

@app.post("/api/v1/diagnosis/{analysis_id}/verify")
def verify(analysis_id: str, payload: Feedback, x_role: str | None = Header(default=None)):
    if current_user(x_role).role != Role.agronomist: raise HTTPException(403, "Agronomist role required")
    if analysis_id not in diagnoses: raise HTTPException(404, "Analysis not found")
    diagnoses[analysis_id]["expert_verification"] = payload.model_dump()
    return {"status": "verified", "analysis_id": analysis_id}

@app.get("/api/v1/fields/{field_id}/health")
def field_health(field_id: str):
    if field_id not in fields: raise HTTPException(404, "Field not found")
    return {"field_id": field_id, "health_score": 72, "status": "at_risk", "analyses": 1}

@app.get("/api/v1/dashboard/summary")
def dashboard_summary(): return {"total_farms": 1, "healthy": 62, "at_risk": 23, "disease_detected": 15, "top_diseases": [{"name": "Soybean Rust", "share": 42}], "high_risk_farms": 1}

