"""
b2b.py — Enterprise & B2B Field Intelligence Analytics API
"""

from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, require_role, get_db
from app.core.scopes import farm_scope
from app.models.farm import Farm, Field
from app.models.identity import User, UserRole
from app.models.prediction import VideoDiagnosis
from app.models.video import Video
from app.modules.reporting.result_contract import disease_slug

router = APIRouter(prefix="/b2b", tags=["B2B / Enterprise"])


@router.get("/dashboard")
async def get_b2b_dashboard(
    current_user: Annotated[User, Depends(require_role(UserRole.enterprise, UserRole.admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    scope = farm_scope(current_user)
    farms_count_stmt = select(func.count(Farm.id)).where(scope)
    farms_count = (await db.execute(farms_count_stmt)).scalar() or 0

    fields_count_stmt = select(func.count(Field.id)).join(Field.farm).where(scope)
    fields_count = (await db.execute(fields_count_stmt)).scalar() or 0

    videos_count_stmt = select(func.count(Video.id)).join(Video.field).join(Field.farm).where(scope)
    videos_count = (await db.execute(videos_count_stmt)).scalar() or 0

    diag_count_stmt = select(func.count(VideoDiagnosis.id)).join(VideoDiagnosis.video).join(Video.field).join(Field.farm).where(scope)
    total_diagnoses = (await db.execute(diag_count_stmt)).scalar() or 0

    diagnoses = (
        await db.execute(
            select(VideoDiagnosis)
            .options(selectinload(VideoDiagnosis.video), selectinload(VideoDiagnosis.disease))
            .join(VideoDiagnosis.video).join(Video.field).join(Field.farm)
            .join(VideoDiagnosis.disease, isouter=True)
            .where(scope)
        )
    ).scalars().all()
    by_disease: dict[str, int] = {}
    healthy_fields: set[str] = set()
    at_risk_fields: set[str] = set()
    for diagnosis in diagnoses:
        slug = disease_slug(diagnosis)
        by_disease[slug] = by_disease.get(slug, 0) + 1
        if slug == "healthy":
            healthy_fields.add(diagnosis.video.field_id)
        elif slug != "unknown_other":
            at_risk_fields.add(diagnosis.video.field_id)

    return {
        "total_farms": farms_count,
        "total_fields": fields_count,
        "scans_processed": videos_count,
        "total_diagnoses": total_diagnoses,
        "healthy_fields_count": len(healthy_fields),
        "at_risk_fields_count": len(at_risk_fields),
        "top_diseases": [{"disease": disease, "count": count} for disease, count in sorted(by_disease.items(), key=lambda item: (-item[1], item[0]))],
        "fasal_health_index": None,
        "health_index_status": "unavailable_until_validated",
    }


@router.get("/drilldown")
async def get_b2b_drilldown(
    current_user: Annotated[User, Depends(require_role(UserRole.enterprise, UserRole.admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
    district: str | None = Query(None),
    farm_id: str | None = Query(None),
    field_id: str | None = Query(None),
):
    scope = farm_scope(current_user)
    stmt = select(VideoDiagnosis).options(selectinload(VideoDiagnosis.video), selectinload(VideoDiagnosis.disease)).join(VideoDiagnosis.video).join(Video.field).join(Field.farm).join(VideoDiagnosis.disease, isouter=True).where(scope)
    if district:
        stmt = stmt.where(Farm.district == district)
    if farm_id:
        stmt = stmt.where(Farm.id == farm_id)
    if field_id:
        stmt = stmt.where(Field.id == field_id)
    diagnoses = (await db.execute(stmt)).scalars().all()
    affected_fields = {diagnosis.video.field_id for diagnosis in diagnoses if disease_slug(diagnosis) not in ("healthy", "unknown_other")}
    diagnosed_fields = {diagnosis.video.field_id for diagnosis in diagnoses}
    severities = [diagnosis.severity_level for diagnosis in diagnoses if diagnosis.severity_level is not None]
    return {
        "filters": {"district": district, "farm_id": farm_id, "field_id": field_id},
        "metrics": {
            "disease_prevalence_percentage": round((len(affected_fields) / len(diagnosed_fields)) * 100, 2) if diagnosed_fields else 0.0,
            "high_risk_farms": None,
            "average_severity_level": round(sum(severities) / len(severities), 2) if severities else None,
            "fasal_health_score": None,
            "health_score_status": "unavailable_until_validated",
        },
    }
