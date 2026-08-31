from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.deps import get_current_user, get_db
from app.core.scopes import farm_scope
from app.core.audit import write_audit_log
from app.models.farm import Farm
from app.models.identity import User
from app.schemas.farm import FarmCreate, FarmOut, FarmUpdate

router = APIRouter(prefix="/farms", tags=["Farms"])

@router.get("", response_model=list[FarmOut])
async def list_farms(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    stmt = select(Farm).where(farm_scope(current_user)).order_by(Farm.created_at.desc()).offset(offset).limit(limit)
    return (await db.execute(stmt)).scalars().all()

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
    await db.flush()
    await write_audit_log(db, actor_user_id=current_user.id, action="farm.created", entity_type="farm", entity_id=farm.id)
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

@router.patch("/{farm_id}", response_model=FarmOut)
async def update_farm(farm_id: str, payload: FarmUpdate, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    farm = (await db.execute(select(Farm).where(Farm.id == farm_id, farm_scope(current_user)))).scalar_one_or_none()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(farm, key, value)
    await write_audit_log(db, actor_user_id=current_user.id, action="farm.updated", entity_type="farm", entity_id=farm.id)
    await db.commit()
    await db.refresh(farm)
    return farm
