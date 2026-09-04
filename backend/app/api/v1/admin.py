"""
admin.py — Model Governance & Admin Management API
"""

from datetime import datetime, timezone
from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_role, get_db
from app.models.governance import AuditLog, DeploymentStatus, GoldenSetItem, ModelVersion
from app.models.identity import AccountStatus, OnboardingApplication, Organization, OrgType, User, UserRole
from app.models.billing import OrganizationSubscription, Plan, SubscriptionStatus
from app.core.audit import write_audit_log
from app.schemas.onboarding import ApplicationDecision
from app.db.demo_data import initialize_demo_data

router = APIRouter(prefix="/admin", tags=["Admin & Governance"])

@router.get("/demo-data")
async def demo_data_status(current_user: Annotated[User, Depends(require_role(UserRole.admin))], db: Annotated[AsyncSession, Depends(get_db)]):
    from app.db.demo_data import DEMO_ORG
    org = (await db.execute(select(Organization).where(Organization.name == DEMO_ORG))).scalar_one_or_none()
    return {"available": bool(org), "videos": 0, "message": "Demo data never includes videos, diagnoses, or generated reports."}

@router.post("/demo-data/initialize", status_code=201)
async def initialize_demo_data_endpoint(current_user: Annotated[User, Depends(require_role(UserRole.admin))], db: Annotated[AsyncSession, Depends(get_db)]):
    result = await initialize_demo_data(db)
    await write_audit_log(db, actor_user_id=current_user.id, action="demo_data.initialized", entity_type="demo_data", metadata={"videos": 0})
    await db.commit()
    return result


class ModelVersionCreate(BaseModel):
    model_name: str
    version_hash: str
    training_dataset_version: str = "v1.0"
    eval_metrics: dict = Field(default_factory=dict)


class DeploymentStatusUpdate(BaseModel):
    deployment_status: DeploymentStatus
    release_gate_record_id: str | None = None


class PlanCreate(BaseModel):
    code: str = Field(min_length=2, max_length=50, pattern=r"^[a-z0-9_-]+$")
    name: str = Field(min_length=2, max_length=100)
    monthly_price_paise: int | None = Field(default=None, ge=0)
    annual_price_paise: int | None = Field(default=None, ge=0)
    farm_limit: int | None = Field(default=None, ge=1)
    scan_limit: int | None = Field(default=None, ge=1)
    is_public: bool = True


class SubscriptionAssign(BaseModel):
    plan_id: str
    status: SubscriptionStatus = SubscriptionStatus.trial
    billing_interval: str = Field(default="monthly", pattern=r"^(monthly|annual)$")


def application_reference(application_id: str) -> str:
    return f"APL-{application_id.replace('-', '')[-8:].upper()}"


@router.get("/onboarding-applications")
async def list_onboarding_applications(
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
    application_status: Literal["pending", "approved", "rejected"] | None = None,
):
    statement = select(OnboardingApplication, User).join(User, OnboardingApplication.applicant_user_id == User.id)
    if application_status:
        statement = statement.where(OnboardingApplication.status == application_status)
    rows = (await db.execute(statement.order_by(OnboardingApplication.created_at.desc()))).all()
    return [
        {
            "reference": application_reference(application.id),
            "application_type": application.application_type,
            "status": application.status,
            "applicant_name": applicant.display_name,
            "contact": applicant.email or applicant.phone,
            "organization_name": application.organization_name,
            "organization_type": application.requested_org_type,
            "requested_plan_code": application.requested_plan_code,
            "review_note": application.review_note,
            "created_at": application.created_at,
            "reviewed_at": application.reviewed_at,
        }
        for application, applicant in rows
    ]


@router.patch("/onboarding-applications/{application_reference_id}")
async def decide_onboarding_application(
    application_reference_id: str,
    payload: ApplicationDecision,
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    reference = application_reference_id.strip().upper()
    if not reference.startswith("APL-") or len(reference) != 12:
        raise HTTPException(status_code=404, detail="Onboarding application not found")
    suffix = reference[4:].lower()
    application = (await db.execute(select(OnboardingApplication).where(OnboardingApplication.id.ilike(f"%{suffix}")))).scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Onboarding application not found")
    if application.status != AccountStatus.pending.value:
        raise HTTPException(status_code=409, detail="This application has already been decided")
    applicant = (await db.execute(select(User).where(User.id == application.applicant_user_id))).scalar_one()

    if payload.decision == "approved":
        applicant.account_status = AccountStatus.active.value
        if application.application_type == "organization":
            if not application.organization_name or not application.requested_org_type:
                raise HTTPException(status_code=422, detail="Organization application is incomplete")
            organization = Organization(name=application.organization_name, org_type=OrgType(application.requested_org_type))
            db.add(organization)
            await db.flush()
            applicant.org_id = organization.id
            applicant.role = UserRole.enterprise
            if application.requested_plan_code:
                plan = (await db.execute(select(Plan).where(Plan.code == application.requested_plan_code, Plan.is_active.is_(True)))).scalar_one_or_none()
                if plan:
                    db.add(OrganizationSubscription(organization_id=organization.id, plan_id=plan.id, status=SubscriptionStatus.trial.value))
        else:
            applicant.role = UserRole.agronomist
    else:
        applicant.account_status = AccountStatus.rejected.value

    application.status = payload.decision
    application.review_note = payload.review_note
    application.reviewer_user_id = current_user.id
    application.reviewed_at = datetime.now(timezone.utc)
    await write_audit_log(
        db,
        actor_user_id=current_user.id,
        action=f"onboarding.application_{payload.decision}",
        entity_type="onboarding_application",
        entity_id=application.id,
        metadata={"application_type": application.application_type},
    )
    await db.commit()
    return {"reference": application_reference(application.id), "status": application.status, "message": "Application decision recorded"}


@router.get("/onboarding-audit-history")
async def onboarding_audit_history(
    current_user: Annotated[User, Depends(require_role(UserRole.admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    applications = (await db.execute(select(OnboardingApplication.id))).scalars().all()
    if not applications:
        return []
    records = (await db.execute(
        select(AuditLog).where(
            AuditLog.entity_type == "onboarding_application",
            AuditLog.entity_id.in_(applications),
        ).order_by(AuditLog.created_at.desc()).limit(100)
    )).scalars().all()
    return [
        {
            "action": record.action,
            "created_at": record.created_at,
            "application_reference": application_reference(record.entity_id or ""),
            "application_type": (record.metadata_json or {}).get("application_type"),
        }
        for record in records
    ]


@router.get("/plans")
async def list_plans(current_user: Annotated[User, Depends(require_role(UserRole.admin))], db: Annotated[AsyncSession, Depends(get_db)]):
    return (await db.execute(select(Plan).order_by(Plan.created_at.desc()))).scalars().all()


@router.post("/plans", status_code=201)
async def create_plan(payload: PlanCreate, current_user: Annotated[User, Depends(require_role(UserRole.admin))], db: Annotated[AsyncSession, Depends(get_db)]):
    plan = Plan(**payload.model_dump())
    db.add(plan)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="A plan with this code already exists")
    await write_audit_log(db, actor_user_id=current_user.id, action="plan.created", entity_type="plan", entity_id=plan.id)
    await db.commit(); await db.refresh(plan)
    return plan


@router.put("/organizations/{organization_id}/subscription")
async def assign_subscription(organization_id: str, payload: SubscriptionAssign, current_user: Annotated[User, Depends(require_role(UserRole.admin))], db: Annotated[AsyncSession, Depends(get_db)]):
    organization = (await db.execute(select(Organization).where(Organization.id == organization_id))).scalar_one_or_none()
    plan = (await db.execute(select(Plan).where(Plan.id == payload.plan_id, Plan.is_active.is_(True)))).scalar_one_or_none()
    if not organization or not plan:
        raise HTTPException(status_code=404, detail="Organization or active plan not found")
    subscription = (await db.execute(select(OrganizationSubscription).where(OrganizationSubscription.organization_id == organization_id))).scalar_one_or_none()
    if subscription is None:
        subscription = OrganizationSubscription(organization_id=organization_id, plan_id=plan.id, status=payload.status.value, billing_interval=payload.billing_interval)
        db.add(subscription)
    else:
        subscription.plan_id, subscription.status, subscription.billing_interval = plan.id, payload.status.value, payload.billing_interval
    await write_audit_log(db, actor_user_id=current_user.id, action="organization.subscription_assigned", entity_type="organization", entity_id=organization_id, metadata={"plan_id": plan.id, "status": payload.status.value})
    await db.commit(); await db.refresh(subscription)
    return subscription


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
