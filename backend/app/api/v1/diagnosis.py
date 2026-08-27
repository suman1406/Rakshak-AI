"""
diagnosis.py — Diagnosis Report & Feedback API Endpoints
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, require_role
from app.models.identity import User, UserRole
from app.models.prediction import VideoDiagnosis
from app.models.verification import Feedback, VerifiedLabel
from app.modules.reporting.templates import get_canned_report
from app.schemas.diagnosis import (
    AgronomistVerifyCreate,
    AgronomistVerifyResponse,
    DiagnosisReportResponse,
    FarmerFeedbackCreate,
    FarmerFeedbackResponse,
)

router = APIRouter(prefix="/diagnosis", tags=["Diagnosis"])


@router.get("/{video_diagnosis_id}", response_model=DiagnosisReportResponse)
async def get_diagnosis_report(
    video_diagnosis_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(VideoDiagnosis).where(VideoDiagnosis.id == video_diagnosis_id)
    result = await db.execute(stmt)
    diag = result.scalar_one_or_none()
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnosis record not found")

    disease_slug = diag.disease_id or ("unknown_other" if diag.is_unknown else "soybean_rust")
    canned = get_canned_report(disease_slug)

    severity_names = {0: "None", 1: "Mild", 2: "Moderate", 3: "Severe"}
    severity_name = severity_names.get(diag.severity_level or 0, "None")

    return DiagnosisReportResponse(
        video_diagnosis_id=diag.id,
        video_id=diag.video_id,
        crop="soybean",
        disease=disease_slug,
        headline=canned["headline"],
        is_unknown=diag.is_unknown,
        confidence=diag.confidence,
        confidence_band=diag.confidence_band,
        severity_level=diag.severity_level or 0,
        severity_name=severity_name,
        affected_plant_estimate=diag.affected_plant_estimate or 0.0,
        supporting_frames=diag.supporting_frames or 0,
        total_frames=diag.total_frames or 0,
        decision_authority=diag.decision_authority,
        explanation=diag.explanation or canned["explanation"],
        action_items=canned["action_items"],
        created_at=diag.created_at,
    )


@router.post("/{video_diagnosis_id}/feedback", response_model=FarmerFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_farmer_feedback(
    video_diagnosis_id: str,
    payload: FarmerFeedbackCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(VideoDiagnosis).where(VideoDiagnosis.id == video_diagnosis_id)
    result = await db.execute(stmt)
    diag = result.scalar_one_or_none()
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnosis record not found")

    fb = Feedback(
        video_diagnosis_id=video_diagnosis_id,
        user_id=current_user.id,
        correction_type=payload.correction_type,
        note=payload.note,
    )
    db.add(fb)
    await db.commit()
    await db.refresh(fb)
    return FarmerFeedbackResponse(
        feedback_id=fb.id,
        video_diagnosis_id=video_diagnosis_id,
        created_at=fb.created_at,
    )


@router.post("/{video_diagnosis_id}/verify", response_model=AgronomistVerifyResponse, status_code=status.HTTP_201_CREATED)
async def submit_agronomist_verification(
    video_diagnosis_id: str,
    payload: AgronomistVerifyCreate,
    current_user: Annotated[User, Depends(require_role(UserRole.agronomist, UserRole.admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(VideoDiagnosis).where(VideoDiagnosis.id == video_diagnosis_id)
    result = await db.execute(stmt)
    diag = result.scalar_one_or_none()
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnosis record not found")

    vl = VerifiedLabel(
        video_diagnosis_id=video_diagnosis_id,
        agronomist_user_id=current_user.id,
        disease_id=payload.disease_id,
        is_healthy_override=payload.is_healthy_override,
        severity_level=payload.severity_level,
        affected_plant_estimate_independent=payload.affected_plant_estimate_independent,
        is_blind_relabel=payload.is_blind_relabel,
        notes=payload.notes,
    )
    db.add(vl)
    await db.commit()
    await db.refresh(vl)
    return AgronomistVerifyResponse(
        verified_label_id=vl.id,
        video_diagnosis_id=video_diagnosis_id,
        is_gold=vl.is_gold,
        created_at=vl.created_at,
    )
