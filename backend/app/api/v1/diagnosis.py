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
from app.models.farm import Field, Disease
from app.models.video import Video
from app.models.identity import User, UserRole
from app.models.prediction import VideoDiagnosis
from app.models.verification import Feedback, ReviewStatus, ReviewWorkItem, VerifiedLabel
from app.modules.reporting.templates import get_canned_report
from app.modules.reporting.reviews import review_summary
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
        .where(VideoDiagnosis.id == video_diagnosis_id, diagnosis_scope(current_user)).with_for_update(of=VideoDiagnosis)
    )
    result = await db.execute(stmt)
    diag = result.scalar_one_or_none()
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnosis record not found")

    slug = disease_slug(diag)
    canned = get_canned_report(slug)

    return DiagnosisReportResponse(
        video_diagnosis_id=diag.id,
        expert_review=await review_summary(db, diag.id),
        probability_distribution=diag.probability_distribution,
        model_versions=diag.model_versions or {'aggregation': diag.aggregation_model_version},
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
        action_items=diag.action_items or canned["action_items"],
        created_at=diag.created_at,
    )


@router.post("/{video_diagnosis_id}/feedback", response_model=FarmerFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_farmer_feedback(
    video_diagnosis_id: str,
    payload: FarmerFeedbackCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(VideoDiagnosis).join(VideoDiagnosis.video).join(Video.field).join(Field.farm).where(VideoDiagnosis.id == video_diagnosis_id, diagnosis_scope(current_user)).with_for_update(of=VideoDiagnosis)
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


@router.post("/{video_diagnosis_id}/review-requests", status_code=status.HTTP_201_CREATED)
async def request_agronomist_review(
    video_diagnosis_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    diag = (await db.execute(select(VideoDiagnosis).join(VideoDiagnosis.video).join(Video.field).join(Field.farm).where(VideoDiagnosis.id == video_diagnosis_id, diagnosis_scope(current_user)).with_for_update(of=VideoDiagnosis))).scalar_one_or_none()
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnosis record not found")
    work_item = (await db.execute(select(ReviewWorkItem).where(ReviewWorkItem.video_diagnosis_id == video_diagnosis_id))).scalar_one_or_none()
    if work_item is None:
        work_item = ReviewWorkItem(video_diagnosis_id=video_diagnosis_id, status=ReviewStatus.pending)
        db.add(work_item)
        await write_audit_log(db, actor_user_id=current_user.id, action="diagnosis.review_requested", entity_type="diagnosis", entity_id=video_diagnosis_id)
        await db.commit()
        await db.refresh(work_item)
    return {"review_work_item_id": work_item.id, "status": work_item.status, "already_requested": work_item.status != ReviewStatus.pending}


@router.post("/{video_diagnosis_id}/verify", response_model=AgronomistVerifyResponse, status_code=status.HTTP_201_CREATED)
async def submit_agronomist_verification(
    video_diagnosis_id: str,
    payload: AgronomistVerifyCreate,
    current_user: Annotated[User, Depends(require_role(UserRole.agronomist, UserRole.admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(VideoDiagnosis).join(VideoDiagnosis.video).join(Video.field).join(Field.farm).where(VideoDiagnosis.id == video_diagnosis_id, diagnosis_scope(current_user)).with_for_update(of=VideoDiagnosis)
    result = await db.execute(stmt)
    diag = result.scalar_one_or_none()
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnosis record not found")

    vl = VerifiedLabel(
        video_diagnosis_id=video_diagnosis_id,
        agronomist_id=current_user.id,
        disease_id=await resolve_verified_disease(payload, db),
        is_healthy_override=payload.is_healthy_override,
        severity_level=payload.severity_level,
        affected_plant_estimate_independent=payload.affected_plant_estimate_independent,
        is_blind_relabel=payload.is_blind_relabel,
        notes=payload.notes,
    )
    work_item = (await db.execute(select(ReviewWorkItem).where(ReviewWorkItem.video_diagnosis_id == video_diagnosis_id))).scalar_one_or_none()
    if work_item:
        if work_item.status == ReviewStatus.completed:
            raise HTTPException(status_code=409, detail="This review has already been completed")
        if work_item.assigned_agronomist_id and work_item.assigned_agronomist_id != current_user.id:
            raise HTTPException(status_code=409, detail="Case is assigned to another reviewer")
        work_item.status = ReviewStatus.completed
        work_item.completed_at = datetime.now(timezone.utc)
    else:
        db.add(ReviewWorkItem(video_diagnosis_id=video_diagnosis_id, status=ReviewStatus.completed, assigned_agronomist_id=current_user.id, completed_at=datetime.now(timezone.utc)))
    db.add(vl)
    await db.flush()
    await write_audit_log(db, actor_user_id=current_user.id, action="diagnosis.verified", entity_type="diagnosis", entity_id=video_diagnosis_id, metadata={"decision": vl.disease_id or ("healthy" if vl.is_healthy_override else "uncertain")})
    await db.commit()
    await db.refresh(vl)
    return AgronomistVerifyResponse(
        verified_label_id=vl.id,
        video_diagnosis_id=video_diagnosis_id,
        is_gold=vl.is_gold,
        created_at=vl.created_at,
    )

async def resolve_verified_disease(payload: AgronomistVerifyCreate, db: AsyncSession) -> str | None:
    if payload.is_healthy_override:
        if payload.disease_id or payload.disease_slug:
            raise HTTPException(status_code=422, detail="Healthy review cannot also name a disease")
        if payload.severity_level != 0:
            raise HTTPException(status_code=422, detail="Healthy review must have severity zero")
        return None
    if payload.disease_slug:
        names = {"soybean_rust": "Soybean Rust", "soybean_bacterial_blight": "Bacterial Blight", "bacterial_blight": "Bacterial Blight", "soybean_frogeye_leaf_spot": "Frogeye Leaf Spot", "frogeye_leaf_spot": "Frogeye Leaf Spot"}
        name = names.get(payload.disease_slug)
        if name is None:
            raise HTTPException(status_code=422, detail="Unsupported disease classification")
        disease = (await db.execute(select(Disease).where(Disease.name == name, Disease.active.is_(True)))).scalars().first()
        if disease is None:
            raise HTTPException(status_code=422, detail="Disease is not in the active catalog")
        return disease.id
    if payload.disease_id:
        disease = await db.get(Disease, payload.disease_id)
        if disease is None or not disease.active:
            raise HTTPException(status_code=422, detail="Disease is not in the active catalog")
        return disease.id
    # Neither healthy nor a named disease means the expert could not classify.
    return None
