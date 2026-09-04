from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import write_audit_log
from app.core.deps import get_db
from app.core.security import get_password_hash
from app.models.billing import Plan
from app.models.identity import AccountStatus, OnboardingApplication, User, UserRole
from app.schemas.onboarding import ApplicationCreate, ApplicationReceipt, PublicPlanOut

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


def application_reference(application_id: str) -> str:
    return f"APL-{application_id.replace('-', '')[-8:].upper()}"


@router.get("/plans", response_model=list[PublicPlanOut])
async def list_public_plans(db: Annotated[AsyncSession, Depends(get_db)]):
    """Public catalogue only. Subscription state and internal identifiers stay private."""
    return (
        await db.execute(
            select(Plan)
            .where(Plan.is_public.is_(True), Plan.is_active.is_(True))
            .order_by(Plan.monthly_price_paise.asc().nulls_last(), Plan.name.asc())
        )
    ).scalars().all()


@router.post("/applications", response_model=ApplicationReceipt, status_code=status.HTTP_202_ACCEPTED)
async def create_application(payload: ApplicationCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    conditions = []
    if payload.email:
        conditions.append(User.email == payload.email)
    if payload.phone:
        conditions.append(User.phone == payload.phone)
    existing = (await db.execute(select(User).where(or_(*conditions)))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="An account or application already exists for these details")

    applicant = User(
        email=payload.email,
        phone=payload.phone,
        password_hash=get_password_hash(payload.access_phrase),
        role=UserRole.agronomist if payload.application_type == "agronomist" else UserRole.enterprise,
        display_name=payload.display_name,
        account_status=AccountStatus.pending.value,
        consent_accepted_at=datetime.now(timezone.utc),
    )
    db.add(applicant)
    await db.flush()
    application = OnboardingApplication(
        applicant_user_id=applicant.id,
        application_type=payload.application_type,
        organization_name=payload.organization_name,
        requested_org_type=payload.organization_type.value if payload.organization_type else None,
        requested_plan_code=payload.requested_plan_code,
    )
    db.add(application)
    await db.flush()
    await write_audit_log(
        db,
        actor_user_id=applicant.id,
        action="onboarding.application_submitted",
        entity_type="onboarding_application",
        entity_id=application.id,
        metadata={"application_type": payload.application_type},
    )
    await db.commit()
    return ApplicationReceipt(
        reference=application_reference(application.id),
        status="pending",
        message="Your application is pending platform review. You can sign in after it is approved.",
    )
