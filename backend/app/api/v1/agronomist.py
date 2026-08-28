"""
agronomist.py — Agronomist Verification Queue & Case Inspection API
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, require_role, get_db
from app.core.scopes import diagnosis_scope
from app.models.farm import Field
from app.models.identity import User, UserRole
from app.models.prediction import VideoDiagnosis
from app.models.video import Video

router = APIRouter(prefix="/agronomist", tags=["Agronomist"])


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
        .options(selectinload(VideoDiagnosis.video))
        .join(VideoDiagnosis.video).join(Video.field).join(Field.farm)
        .where(diagnosis_scope(current_user))
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
            "disease": c.disease_id or ("unknown_other" if c.is_unknown else "soybean_rust"),
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
        "disease": diag.disease_id or ("unknown_other" if diag.is_unknown else "soybean_rust"),
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
