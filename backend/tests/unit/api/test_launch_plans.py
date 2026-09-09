import pytest
from fastapi import HTTPException
from sqlalchemy import select
from app.core.entitlements import require_capacity, organization_usage
from app.core.security import create_access_token
from app.db.plans import ensure_launch_plans
from app.models.billing import Plan, OrganizationSubscription
from app.models.identity import Organization, OrgType, User, UserRole
from app.models.farm import Farm


@pytest.mark.asyncio
async def test_catalog_restart_preserves_administrator_changes(test_db):
    await ensure_launch_plans(test_db)
    plan = (await test_db.execute(select(Plan).where(Plan.code == 'fpo-starter'))).scalar_one()
    plan.monthly_price_paise = 123400
    plan.is_public = False
    await test_db.commit()
    await ensure_launch_plans(test_db)
    await test_db.refresh(plan)
    assert plan.monthly_price_paise == 123400
    assert not plan.is_public
    assert len((await test_db.execute(select(Plan))).scalars().all()) == 3


@pytest.mark.asyncio
async def test_annual_request_survives_approval(client, test_db):
    await ensure_launch_plans(test_db)
    response = await client.post('/api/v1/onboarding/applications', json={
        'application_type': 'organization', 'email': 'annual@example.test',
        'display_name': 'Annual lead', 'access_phrase': 'AnnualTest2026!',
        'consent_to_data_processing': True, 'organization_name': 'Annual FPO',
        'organization_type': 'fpo', 'requested_plan_code': 'fpo-starter',
        'requested_billing_interval': 'annual',
    })
    assert response.status_code == 202, response.text
    admin = User(email='admin@example.test', password_hash='unused-test-hash', role=UserRole.admin)
    test_db.add(admin)
    await test_db.commit()
    headers = {'Authorization': f'Bearer {create_access_token(admin.id, "admin", None)}'}
    approved = await client.patch('/api/v1/admin/onboarding-applications/' + response.json()['reference'],
        headers=headers, json={'decision': 'approved', 'review_note': 'Approved annual pilot'})
    assert approved.status_code == 200, approved.text
    subscription = (await test_db.execute(select(OrganizationSubscription))).scalar_one()
    assert subscription.billing_interval == 'annual'
    usage = await organization_usage(test_db, subscription.organization_id)
    assert usage['farm_limit'] == 25
    assert usage['scan_limit'] == 250


@pytest.mark.asyncio
async def test_unpublished_plan_rejected_without_creating_account(client, test_db):
    response = await client.post('/api/v1/onboarding/applications', json={
        'application_type': 'organization', 'email': 'invalid@example.test',
        'display_name': 'Lead', 'access_phrase': 'AnnualTest2026!',
        'consent_to_data_processing': True, 'organization_name': 'FPO',
        'organization_type': 'fpo', 'requested_plan_code': 'not-published',
    })
    assert response.status_code == 422
    assert (await test_db.execute(select(User))).scalars().all() == []


@pytest.mark.asyncio
async def test_capacity_is_scoped_and_paused_records_stay_readable(test_db):
    org = Organization(name='Limited', org_type=OrgType.fpo)
    other = Organization(name='Other', org_type=OrgType.fpo)
    owner = User(email='owner@example.test', password_hash='unused-test-hash', role=UserRole.enterprise)
    plan = Plan(code='one', name='One farm', farm_limit=1, scan_limit=1)
    test_db.add_all([org, other, owner, plan])
    await test_db.flush()
    sub = OrganizationSubscription(organization_id=org.id, plan_id=plan.id, status='active')
    test_db.add_all([sub, Farm(name='Other farm', org_id=other.id, owner_user_id=owner.id)])
    await test_db.commit()
    await require_capacity(test_db, org.id, 'farms')
    test_db.add(Farm(name='Our farm', org_id=org.id, owner_user_id=owner.id))
    await test_db.commit()
    with pytest.raises(HTTPException) as error:
        await require_capacity(test_db, org.id, 'farms')
    assert error.value.status_code == 409
    await require_capacity(test_db, None, 'farms')
    sub.status = 'paused'
    await test_db.commit()
    with pytest.raises(HTTPException) as error:
        await require_capacity(test_db, org.id, 'scans')
    assert error.value.status_code == 403
    assert (await organization_usage(test_db, org.id))['farms_used'] == 1
