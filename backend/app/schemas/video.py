from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict
from ..models.video import VideoStatus

class VideoUploadResponse(BaseModel):
    video_id: str
    field_id: str
    status: VideoStatus
    filename: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class VideoStatusResponse(BaseModel):
    video_id: str
    status: VideoStatus
    quality_score: float | None = None
    usable_frames_count: int | None = None
    total_frames_extracted: int | None = None
    error_detail: str | None = None

    model_config = ConfigDict(from_attributes=True)

class VideoAnalysisEvidence(BaseModel):
    frames_analyzed: int
    supporting_frames: int
    quality_score: float | None = None

class VideoAnalysisDiagnosis(BaseModel):
    disease: str
    is_unknown: bool
    confidence: float
    confidence_band: str
    severity: str
    affected_plant_estimate: float

class VideoAnalysisResponse(BaseModel):
    video_id: str
    diagnosis_id: str | None = None
    crop: str
    result_state: Literal["ready", "healthy", "unknown", "insufficient_evidence", "failed"]
    diagnosis: VideoAnalysisDiagnosis | None = None
    evidence: VideoAnalysisEvidence
    model_versions: dict[str, str] = {}
    retake_guidance: str | None = None
    action_items: str | None = None
    explanation: str | None = None
