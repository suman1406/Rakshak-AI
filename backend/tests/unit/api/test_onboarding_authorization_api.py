import pytest
from sqlalchemy import select

from app.core.security import create_access_token, get_password_hash
from app.models.governance import AuditLog
from app.models.identity import AccountStatus, Organization, OnboardingApplication, User, UserRole


@pytest.mark.asyncio
async def test_farmer_registration_requires_consent_and_creates_active_account(client):
    no_consent = await client.post(
        "/api/v1/auth/register",
        json={"email": "farmer-no-consent@test.local", "password": "Password123!", "display_name": "Farmer"},
    )
    assert no_consent.status_code == 422

    registered = await client.post(
        "/api/v1/auth/register",
        json={"email": "farmer@test.local", "password": "Password123!", "display_name": "Farmer", "consent_to_data_processing": True},
    )
    assert registered.status_code == 201
    assert registered.json()["account_status"] == "active"


@pytest.mark.asyncio
async def test_pending_application_cannot_sign_in_until_admin_approval_and_is_audited(client, test_db):
    application_response = await client.post(
        "/api/v1/onboarding/applications",
        json={
            "application_type": "organization",
            "email": "lead@fpo.test",
            "display_name": "FPO Lead",
            "access_phrase": "A personal phrase 123",
            "consent_to_data_processing": True,
            "organization_name": "Test FPO",
            "organization_type": "fpo",
        },
    )
    assert application_response.status_code == 202
    reference = application_response.json()["reference"]
    assert reference.startswith("APL-")

    denied_login = await client.post("/api/v1/auth/login", json={"email_or_phone": "lead@fpo.test", "password": "A personal phrase 123"})
    assert denied_login.status_code == 403
    assert "awaiting" in denied_login.json()["message"].lower()

    admin = User(email="admin@test.local", password_hash=get_password_hash("AdminPassword123!"), role=UserRole.admin, account_status=AccountStatus.active.value)
    test_db.add(admin)
    await test_db.commit()
    token = create_access_token(admin.id, admin.role.value, None)
    headers = {"Authorization": f"Bearer {token}"}

    listing = await client.get("/api/v1/admin/onboarding-applications?application_status=pending", headers=headers)
    assert listing.status_code == 200
    item = listing.json()[0]
    assert item["reference"] == reference
    assert "id" not in item
    assert item["contact"] == "lead@fpo.test"

    approved = await client.patch(
        f"/api/v1/admin/onboarding-applications/{reference}",
        headers=headers,
        json={"decision": "approved", "review_note": "Verified for pilot"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    login = await client.post("/api/v1/auth/login", json={"email_or_phone": "lead@fpo.test", "password": "A personal phrase 123"})
    assert login.status_code == 200
    assert login.json()["role"] == "enterprise"
    application = (await test_db.execute(select(OnboardingApplication))).scalar_one()
    applicant = (await test_db.execute(select(User).where(User.id == application.applicant_user_id))).scalar_one()
    assert applicant.account_status == "active"
    assert applicant.org_id is not None
    assert (await test_db.execute(select(Organization))).scalar_one().name == "Test FPO"
    actions = (await test_db.execute(select(AuditLog.action))).scalars().all()
    assert "onboarding.application_submitted" in actions
    assert "onboarding.application_approved" in actions
    history = await client.get("/api/v1/admin/onboarding-audit-history", headers=headers)
    assert history.status_code == 200
    assert {item["action"] for item in history.json()} >= {"onboarding.application_submitted", "onboarding.application_approved"}
    assert all("id" not in item for item in history.json())


@pytest.mark.asyncio
async def test_non_admin_cannot_read_or_decide_pending_applications(client, test_db):
    farmer = User(email="farmer-authz@test.local", password_hash=get_password_hash("Password123!"), role=UserRole.farmer)
    test_db.add(farmer)
    await test_db.commit()
    headers = {"Authorization": f"Bearer {create_access_token(farmer.id, farmer.role.value, None)}"}
    assert (await client.get("/api/v1/admin/onboarding-applications", headers=headers)).status_code == 403
    assert (await client.patch("/api/v1/admin/onboarding-applications/APL-AAAAAAAA", headers=headers, json={"decision": "approved"})).status_code == 403
