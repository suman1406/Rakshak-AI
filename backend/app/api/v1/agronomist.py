"""
agronomist.py — Agronomist Verification Queue & Case Inspection API
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timezone
from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, require_role, get_db
from app.core.scopes import diagnosis_scope
from app.models.farm import Field
from app.models.identity import User, UserRole
from app.models.prediction import VideoDiagnosis
from app.models.verification import ReviewStatus, ReviewWorkItem, VerifiedLabel
from app.models.video import Video
from app.modules.reporting.result_contract import disease_slug

router = APIRouter(prefix="/agronomist", tags=["Agronomist"])

@router.post("/cases/{video_diagnosis_id}/claim")
async def claim_case(video_diagnosis_id: str, current_user: Annotated[User, Depends(require_role(UserRole.agronomist, UserRole.admin))], db: Annotated[AsyncSession, Depends(get_db)]):
    diag = (await db.execute(select(VideoDiagnosis).join(VideoDiagnosis.video).join(Video.field).join(Field.farm).where(VideoDiagnosis.id == video_diagnosis_id, diagnosis_scope(current_user)))).scalar_one_or_none()
    if not diag: raise HTTPException(status_code=404, detail="Case not found")
    item = (await db.execute(select(ReviewWorkItem).where(ReviewWorkItem.video_diagnosis_id == video_diagnosis_id))).scalar_one_or_none()
    if item is None:
        item = ReviewWorkItem(video_diagnosis_id=video_diagnosis_id, status=ReviewStatus.in_review, assigned_agronomist_id=current_user.id)
        db.add(item)
    elif item.status == ReviewStatus.pending:
        claimed = await db.execute(update(ReviewWorkItem).where(ReviewWorkItem.id == item.id, ReviewWorkItem.status == ReviewStatus.pending).values(status=ReviewStatus.in_review, assigned_agronomist_id=current_user.id))
        if claimed.rowcount != 1: raise HTTPException(status_code=409, detail="Case was claimed by another reviewer")
    elif item.assigned_agronomist_id != current_user.id:
        raise HTTPException(status_code=409, detail="Case is assigned to another reviewer")
    await db.commit(); await db.refresh(item)
    return {"review_work_item_id": item.id, "status": item.status, "assigned_agronomist_id": item.assigned_agronomist_id}

@router.get("/cases/{video_diagnosis_id}/history")
async def review_history(video_diagnosis_id: str, current_user: Annotated[User, Depends(require_role(UserRole.agronomist, UserRole.admin))], db: Annotated[AsyncSession, Depends(get_db)]):
    item = (await db.execute(select(ReviewWorkItem).where(ReviewWorkItem.video_diagnosis_id == video_diagnosis_id))).scalar_one_or_none()
    labels = (await db.execute(select(VerifiedLabel).where(VerifiedLabel.video_diagnosis_id == video_diagnosis_id).order_by(VerifiedLabel.created_at))).scalars().all()
    return {"workflow": None if not item else {"status": item.status, "assigned_agronomist_id": item.assigned_agronomist_id, "completed_at": item.completed_at}, "verifications": [{"id": label.id, "agronomist_id": label.agronomist_id, "created_at": label.created_at, "notes": label.notes} for label in labels]}


@router.get("/queue")
async def get_agronomist_queue(
    current_user: Annotated[User, Depends(require_role(UserRole.agronomist, UserRole.admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Returns cases sorted by lowest AI confidence first for agronomist review."""
    stmt = (
        select(VideoDiagnosis)
        .options(selectinload(VideoDiagnosis.video), selectinload(VideoDiagnosis.disease))
        .join(VideoDiagnosis.video).join(Video.field).join(Field.farm)
        .where(diagnosis_scope(current_user), ~exists(select(VerifiedLabel.id).where(VerifiedLabel.video_diagnosis_id == VideoDiagnosis.id)))
        .order_by(VideoDiagnosis.confidence.asc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    cases = result.scalars().all()

    return [
        {
            "video_diagnosis_id": c.id,
            "video_id": c.video_id,
            "disease": disease_slug(c),
            "confidence": c.confidence,
            "confidence_band": c.confidence_band.value,
            "severity_level": c.severity_level,
            "is_unknown": c.is_unknown,
            "created_at": c.created_at,
        }
        for c in cases
    ]


@router.get("/cases/{video_diagnosis_id}")
async def get_agronomist_case(
    video_diagnosis_id: str,
    current_user: Annotated[User, Depends(require_role(UserRole.agronomist, UserRole.admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = (
        select(VideoDiagnosis)
        .options(
            selectinload(VideoDiagnosis.video).selectinload(Video.frames),
            selectinload(VideoDiagnosis.verified_labels),
            selectinload(VideoDiagnosis.disease),
        )
        .join(VideoDiagnosis.video).join(Video.field).join(Field.farm)
        .where(VideoDiagnosis.id == video_diagnosis_id, diagnosis_scope(current_user))
    )
    result = await db.execute(stmt)
    diag = result.scalar_one_or_none()
    if not diag:
        raise HTTPException(status_code=404, detail="Case not found")

    return {
        "video_diagnosis_id": diag.id,
        "video_id": diag.video_id,
        "disease": disease_slug(diag),
        "confidence": diag.confidence,
        "confidence_band": diag.confidence_band.value,
        "severity_level": diag.severity_level,
        "affected_plant_estimate": diag.affected_plant_estimate,
        "supporting_frames": diag.supporting_frames,
        "total_frames": diag.total_frames,
        "explanation": diag.explanation,
        "frames": [
            {
                "frame_id": f.id,
                "sequence_index": f.sequence_index,
                "blur_score": f.blur_score,
                "exposure_score": f.exposure_score,
                "is_selected": f.is_selected,
                "evidence_url": f"/api/v1/videos/{diag.video_id}/frames/{f.id}/content",
            }
            for f in (diag.video.frames if diag.video else [])
        ],
        "verifications_count": len(diag.verified_labels),
    }
