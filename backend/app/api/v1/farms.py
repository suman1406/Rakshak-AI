from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.deps import get_current_user, get_db
from ...models.farm import Farm, Field
from ...models.identity import User
from ...schemas.farm import FarmCreate, FarmOut, FieldCreate, FieldOut

router = APIRouter(prefix="/farms", tags=["Farms"])

@router.post("", response_model=FarmOut, status_code=status.HTTP_201_CREATED)
async def create_farm(
    payload: FarmCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    farm = Farm(
        owner_user_id=current_user.id,
        org_id=current_user.org_id,
        name=payload.name,
        state=payload.state,
        district=payload.district,
    )
    db.add(farm)
    await db.commit()
    await db.refresh(farm)
    return farm

@router.get("/{farm_id}", response_model=FarmOut)
async def get_farm(
    farm_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(Farm).where(Farm.id == farm_id)
    result = await db.execute(stmt)
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm

@router.post("/{farm_id}/fields", response_model=FieldOut, status_code=status.HTTP_201_CREATED)
async def create_field_for_farm(
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
