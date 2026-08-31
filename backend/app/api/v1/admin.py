"""
admin.py — Model Governance & Admin Management API
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_role, get_db
from app.models.governance import DeploymentStatus, GoldenSetItem, ModelVersion
from app.models.identity import User, UserRole

router = APIRouter(prefix="/admin", tags=["Admin & Governance"])


class ModelVersionCreate(BaseModel):
    model_name: str
    version_hash: str
    training_dataset_version: str = "v1.0"
    eval_metrics: dict = Field(default_factory=dict)


class DeploymentStatusUpdate(BaseModel):
    deployment_status: DeploymentStatus
    release_gate_record_id: str | None = None


@router.get("/model-versions")
async def list_model_versions(
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return (await db.execute(select(ModelVersion).order_by(ModelVersion.created_at.desc()))).scalars().all()


@router.post("/model-versions", status_code=201)
async def register_model_version(
    payload: ModelVersionCreate,
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    model_version = ModelVersion(model_name=payload.model_name, version_hash=payload.version_hash, training_dataset_version=payload.training_dataset_version, eval_metrics=payload.eval_metrics)
    db.add(model_version)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Model version already exists")
    await db.refresh(model_version)
    return model_version


@router.patch("/model-versions/{model_version_id}/deployment-status")
async def update_deployment_status(
    model_version_id: str,
    payload: DeploymentStatusUpdate,
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if payload.deployment_status == DeploymentStatus.production and not payload.release_gate_record_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot promote to production without passing release_gate_record_id",
        )
    model_version = (await db.execute(select(ModelVersion).where(ModelVersion.id == model_version_id))).scalar_one_or_none()
    if not model_version:
        raise HTTPException(status_code=404, detail="Model version not found")
    model_version.deployment_status = payload.deployment_status
    await db.commit()
    await db.refresh(model_version)
    return model_version


@router.get("/golden-set")
async def get_golden_set(
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    rows = (await db.execute(select(GoldenSetItem.subset, GoldenSetItem.set_version, func.count(GoldenSetItem.id)).group_by(GoldenSetItem.subset, GoldenSetItem.set_version))).all()
    return [{"subset": subset, "set_version": version, "item_count": count} for subset, version, count in rows]
