"""
diagnosis.py — Pydantic Schemas for Farmer Report (PRD §30) and Agronomist Verification
"""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field
from ..models.prediction import ConfidenceBand, DecisionAuthorityStatus
from ..models.verification import CorrectionType

class DiagnosisEvidence(BaseModel):
    frames_analyzed: int
    supporting_frames: int
    leaf_regions_analyzed: int
    quality_score: float = 80.0


class DiagnosisRecommendation(BaseModel):
    title: str
    description: str


class DiagnosisOut(BaseModel):
    video_diagnosis_id: str
    video_id: str
    crop: str = "soybean"
    result_state: str
    disease: str
    headline: str
    is_unknown: bool
    confidence: float
    confidence_band: ConfidenceBand
    severity_level: int
    severity_name: str
    affected_plant_estimate: float
    supporting_frames: int
    total_frames: int
    decision_authority: DecisionAuthorityStatus
    explanation: str
    action_items: str
    disclaimer: str = "AI estimate, not a confirmed diagnosis"
    created_at: datetime

    class Config:
        from_attributes = True


DiagnosisReportResponse = DiagnosisOut


class FeedbackCreate(BaseModel):
    correction_type: CorrectionType
    note: str | None = Field(default=None, max_length=2000)


FarmerFeedbackCreate = FeedbackCreate


class FeedbackOut(BaseModel):
    feedback_id: str
    video_diagnosis_id: str
    created_at: datetime


FarmerFeedbackResponse = FeedbackOut


class VerifyCreate(BaseModel):
    disease_id: str | None = None
    disease_slug: str | None = None
    is_healthy_override: bool = False
    severity_level: int = Field(..., ge=0, le=3)
    affected_plant_estimate_independent: float = Field(..., ge=0.0, le=1.0)
    is_blind_relabel: bool = False
    notes: str | None = Field(default=None, max_length=2000)


AgronomistVerifyCreate = VerifyCreate


class VerifiedLabelOut(BaseModel):
    verified_label_id: str
    video_diagnosis_id: str
    is_gold: bool = False
    created_at: datetime


AgronomistVerifyResponse = VerifiedLabelOut


class AgronomistQueueItem(BaseModel):
    video_diagnosis_id: str
    video_id: str
    disease: str
    confidence: float
    confidence_band: str
    severity_level: int | None
    is_unknown: bool
    created_at: datetime
