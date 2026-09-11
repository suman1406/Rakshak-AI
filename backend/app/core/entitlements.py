from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import func, select
from app.models.billing import OrganizationSubscription, Plan
from app.models.identity import Organization
from app.models.farm import Farm, Field
from app.models.video import Video

async def organization_usage(db, org_id):
    month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    row = (await db.execute(select(OrganizationSubscription, Plan).join(Plan,
        OrganizationSubscription.plan_id == Plan.id).where(
        OrganizationSubscription.organization_id == org_id))).first()
    farms = (await db.execute(select(func.count(Farm.id)).where(Farm.org_id == org_id))).scalar_one()
    scans = (await db.execute(select(func.count(Video.id)).join(Field, Video.field_id == Field.id)
        .join(Farm, Field.farm_id == Farm.id).where(Farm.org_id == org_id, Video.created_at >= month))).scalar_one()
    subscription, plan = row if row else (None, None)
    return {'plan': plan.name if plan else 'Unassigned pilot', 'plan_code': plan.code if plan else None,
        'status': subscription.status if subscription else 'unassigned',
        'billing_interval': subscription.billing_interval if subscription else None,
        'farms_used': farms, 'farm_limit': plan.farm_limit if plan else None,
        'scans_used': scans, 'scan_limit': plan.scan_limit if plan else None,
        'period_start': month, 'billing_managed_manually': True}

async def require_capacity(db, org_id, resource):
    if not org_id:
        return
    # The organization row serializes all capacity checks until insertion commits.
    await db.execute(select(Organization.id).where(Organization.id == org_id).with_for_update())
    usage = await organization_usage(db, org_id)
    if usage['status'] in ('paused', 'cancelled'):
        raise HTTPException(403, 'Your organization plan is paused. Contact support to resume new uploads or farms. Existing records remain available.')
    limit = usage['farm_limit' if resource == 'farms' else 'scan_limit']
    if limit is not None and usage[f'{resource}_used'] >= limit:
        raise HTTPException(409, f'Your organization has reached its {resource} allowance. Contact support to adjust your plan.')
