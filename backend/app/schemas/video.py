from datetime import datetime
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
    leaf_regions_analyzed: int
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
    crop: str
    crop_confidence: float
    diagnosis: VideoAnalysisDiagnosis
    evidence: VideoAnalysisEvidence
    model_versions: dict[str, str]
