from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field as PydanticField
from ..models.prediction import ConfidenceBand, DecisionAuthorityStatus
from ..models.verification import CorrectionType

class DiagnosisEvidence(BaseModel):
    frames_analyzed: int
    supporting_frames: int
    leaf_regions_analyzed: int
    quality_score: float | None = None
    frames: list[dict[str, Any]] = []

class DiagnosisRecommendation(BaseModel):
    action: str
    agronomist_review: bool
    inspection_priority: str
    next_steps: list[str] = []

class DiagnosisOut(BaseModel):
    id: str
    video_id: str
    crop: str = "soybean"
    disease: str
    is_unknown: bool = False
    confidence: float
    confidence_band: ConfidenceBand
    severity: str
    severity_level: int | None = None
    affected_plant_estimate: float | None = None
    evidence: DiagnosisEvidence
    recommendation: DiagnosisRecommendation
    explanation: str
    decision_authority: DecisionAuthorityStatus = DecisionAuthorityStatus.advisory_only
    disclaimer: str = "AI indication, not a confirmed diagnosis."
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FeedbackCreate(BaseModel):
    correction_type: CorrectionType = CorrectionType.other
    note: str | None = None

class FeedbackOut(BaseModel):
    id: str
    video_diagnosis_id: str
    correction_type: CorrectionType
    note: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
