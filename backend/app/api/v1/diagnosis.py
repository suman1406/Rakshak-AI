"""
diagnosis.py — Diagnosis Report & Feedback API Endpoints
"""

from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, get_db, require_role
from app.core.scopes import diagnosis_scope
from app.core.audit import write_audit_log
from app.models.farm import Field
from app.models.video import Video
from app.models.identity import User, UserRole
from app.models.prediction import VideoDiagnosis
from app.models.verification import Feedback, ReviewStatus, ReviewWorkItem, VerifiedLabel
from app.modules.reporting.templates import get_canned_report
from app.modules.reporting.result_contract import disease_slug, result_state, severity_name
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
    stmt = (
        select(VideoDiagnosis)
        .join(VideoDiagnosis.video).join(Video.field).join(Field.farm)
        .options(selectinload(VideoDiagnosis.disease))
        .where(VideoDiagnosis.id == video_diagnosis_id, diagnosis_scope(current_user))
    )
    result = await db.execute(stmt)
    diag = result.scalar_one_or_none()
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnosis record not found")

    slug = disease_slug(diag)
    canned = get_canned_report(slug)

    return DiagnosisReportResponse(
        video_diagnosis_id=diag.id,
        video_id=diag.video_id,
        crop="soybean",
        result_state=result_state(diag),
        disease=slug,
        headline=canned["headline"],
        is_unknown=diag.is_unknown,
        confidence=diag.confidence,
        confidence_band=diag.confidence_band,
        severity_level=diag.severity_level or 0,
        severity_name=severity_name(diag.severity_level),
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
    stmt = select(VideoDiagnosis).join(VideoDiagnosis.video).join(Video.field).join(Field.farm).where(VideoDiagnosis.id == video_diagnosis_id, diagnosis_scope(current_user))
    result = await db.execute(stmt)
    diag = result.scalar_one_or_none()
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnosis record not found")

    fb = Feedback(
        video_diagnosis_id=video_diagnosis_id,
        farmer_user_id=current_user.id,
        correction_type=payload.correction_type,
        note=payload.note,
    )
    db.add(fb)
    await db.flush()
    await write_audit_log(db, actor_user_id=current_user.id, action="diagnosis.feedback_submitted", entity_type="diagnosis", entity_id=video_diagnosis_id)
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
    stmt = select(VideoDiagnosis).join(VideoDiagnosis.video).join(Video.field).join(Field.farm).where(VideoDiagnosis.id == video_diagnosis_id, diagnosis_scope(current_user))
    result = await db.execute(stmt)
    diag = result.scalar_one_or_none()
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnosis record not found")

    vl = VerifiedLabel(
        video_diagnosis_id=video_diagnosis_id,
        agronomist_id=current_user.id,
        disease_id=payload.disease_id,
        is_healthy_override=payload.is_healthy_override,
        severity_level=payload.severity_level,
        affected_plant_estimate_independent=payload.affected_plant_estimate_independent,
        is_blind_relabel=payload.is_blind_relabel,
        notes=payload.notes,
    )
    db.add(vl)
    work_item = (await db.execute(select(ReviewWorkItem).where(ReviewWorkItem.video_diagnosis_id == video_diagnosis_id))).scalar_one_or_none()
    if work_item:
        work_item.status = ReviewStatus.completed
        work_item.completed_at = datetime.now(timezone.utc)
    await db.flush()
    await write_audit_log(db, actor_user_id=current_user.id, action="diagnosis.verified", entity_type="diagnosis", entity_id=video_diagnosis_id, metadata={"decision": payload.disease_id or "healthy"})
    await db.commit()
    await db.refresh(vl)
    return AgronomistVerifyResponse(
        verified_label_id=vl.id,
        video_diagnosis_id=video_diagnosis_id,
        is_gold=vl.is_gold,
        created_at=vl.created_at,
    )
