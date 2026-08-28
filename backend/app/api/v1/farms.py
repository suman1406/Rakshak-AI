from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.deps import get_current_user, get_db
from app.core.scopes import farm_scope
from app.models.farm import Farm
from app.models.identity import User
from app.schemas.farm import FarmCreate, FarmOut

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
    stmt = select(Farm).options(selectinload(Farm.fields)).where(Farm.id == farm_id, farm_scope(current_user))
    result = await db.execute(stmt)
    farm = result.scalar_one_or_none()

    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    return farm
