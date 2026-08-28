from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user, get_db
from app.core.scopes import field_scope
from app.models.farm import Farm, Field
from app.models.identity import User
from app.schemas.farm import FieldCreate, FieldHealthScoreOut, FieldOut

router = APIRouter(tags=["Fields"])

@router.get("/fields", response_model=list[FieldOut])
async def list_fields(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Field).join(Field.farm).where(field_scope(current_user))
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/farms/{farm_id}/fields", response_model=FieldOut, status_code=status.HTTP_201_CREATED)
async def create_field(
    farm_id: str,
    payload: FieldCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Farm).where(Farm.id == farm_id)
    result = await db.execute(stmt)
    farm = result.scalar_one_or_none()

    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    if farm.owner_user_id != current_user.id and current_user.role.value not in ("admin", "enterprise"):
        raise HTTPException(status_code=403, detail="Forbidden: Cannot add field to this farm")

    field = Field(
        farm_id=farm_id,
        name=payload.name,
        crop_id=payload.crop_id,
        area_hectares=payload.area_hectares,
    )
    db.add(field)
    await db.commit()
    await db.refresh(field)
    return field

@router.get("/fields/{field_id}", response_model=FieldOut)
async def get_field(
    field_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Field).join(Field.farm).where(Field.id == field_id, field_scope(current_user))
    result = await db.execute(stmt)
    field = result.scalar_one_or_none()

    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    return field

@router.get("/fields/{field_id}/health", response_model=FieldHealthScoreOut)
async def get_field_health(
    field_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Field).join(Field.farm).where(Field.id == field_id, field_scope(current_user))
    result = await db.execute(stmt)
    field = result.scalar_one_or_none()

    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    return FieldHealthScoreOut(
        field_id=field_id,
        fasal_health_score=78,
        components={
            "disease_prevalence": 25,
            "severity": 20,
            "healthy_ratio": 25,
            "visual_stress": 4,
            "confidence": 4,
        },
        zones=[
            {"zone_label": "North Plot", "status": "healthy"},
            {"zone_label": "South Plot", "status": "early_disease"},
        ],
    )
