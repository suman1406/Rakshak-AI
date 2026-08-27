"""
admin.py — Model Governance & Admin Management API
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.deps import get_current_user, require_role, get_db
from ...models.identity import User, UserRole
from ...modules.inference.classifier import CLASSIFIER_MODEL_VERSION
from ...modules.inference.detector import DETECTOR_MODEL_VERSION

router = APIRouter(prefix="/admin", tags=["Admin & Governance"])


class ModelVersionCreate(BaseModel):
    model_name: str
    version_hash: str
    training_dataset_version: str = "v1.0"
    eval_metrics: dict = Field(default_factory=dict)


class DeploymentStatusUpdate(BaseModel):
    deployment_status: str = Field(..., description="canary | production | retired")
    release_gate_record_id: str | None = None


@router.get("/model-versions")
async def list_model_versions(
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return [
        {
            "id": "mv-detector-001",
            "model_name": "FasterRCNN-ResNet50-Detector",
            "version_hash": DETECTOR_MODEL_VERSION,
            "deployment_status": "production",
            "created_at": "2026-08-27T00:00:00Z",
        },
        {
            "id": "mv-classifier-001",
            "model_name": "EfficientNet-B0-Soybean-Classifier",
            "version_hash": CLASSIFIER_MODEL_VERSION,
            "deployment_status": "production",
            "created_at": "2026-08-27T00:00:00Z",
        },
    ]


@router.post("/model-versions", status_code=201)
async def register_model_version(
    payload: ModelVersionCreate,
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return {
        "id": "mv-new-002",
        "model_name": payload.model_name,
        "version_hash": payload.version_hash,
        "deployment_status": "shadow",
        "message": "Model version registered in shadow deployment mode",
    }


@router.patch("/model-versions/{model_version_id}/deployment-status")
async def update_deployment_status(
    model_version_id: str,
    payload: DeploymentStatusUpdate,
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if payload.deployment_status == "production" and not payload.release_gate_record_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot promote to production without passing release_gate_record_id",
        )
    return {
        "id": model_version_id,
        "deployment_status": payload.deployment_status,
        "release_gate_record_id": payload.release_gate_record_id,
    }


@router.get("/golden-set")
async def get_golden_set(
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return [
        {
            "id": "gs-001",
            "subset": "frozen_regression",
            "set_version": "v1.0",
            "item_count": 10,
        }
    ]
