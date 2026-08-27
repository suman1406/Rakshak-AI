from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.deps import get_current_user, get_db
from ...models.farm import Field
from ...models.identity import User
from ...schemas.farm import FieldCreate, FieldHealthScoreOut, FieldOut

router = APIRouter(prefix="/fields", tags=["Fields"])

@router.get("", response_model=list[FieldOut])
async def list_fields(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Field)
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.get("/{field_id}", response_model=FieldOut)
async def get_field(
    field_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Field).where(Field.id == field_id)
    result = await db.execute(stmt)
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field

@router.get("/{field_id}/health", response_model=FieldHealthScoreOut)
async def get_field_health(
    field_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Field).where(Field.id == field_id)
    result = await db.execute(stmt)
    field = result.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    return FieldHealthScoreOut(
        field_id=field_id,
        fasal_health_score=78,
        components={
            "disease_prevalence": 25.0,
            "severity": 20.0,
            "healthy_ratio": 35.0,
            "visual_stress": 8.0,
            "confidence": 10.0,
        },
        zones=[
            {"zone_label": "Zone A (North)", "status": "healthy", "score": 88},
            {"zone_label": "Zone B (South)", "status": "early_rust_indication", "score": 68},
        ],
        latest_diagnosis_summary={
            "disease": "soybean_rust",
            "confidence_band": "medium",
            "severity": "moderate",
            "disclaimer": "AI indication, not a confirmed diagnosis.",
        },
    )
