import pytest
from app.core.security import create_access_token, get_password_hash
from app.models.farm import Farm
from app.models.identity import Organization, OrgType, User, UserRole

@pytest.mark.asyncio
async def test_farms_and_fields_api_flow(client):
    registration = await client.post(
        "/api/v1/auth/register",
        json={"email": "farm-owner@rakshak.ai", "password": "Password123!"},
    )
    assert registration.status_code == 201
    login = await client.post(
        "/api/v1/auth/login",
        json={"email_or_phone": "farm-owner@rakshak.ai", "password": "Password123!"},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    # 1. Create a Farm
    farm_payload = {
        "name": "Indore Soybean Farm",
        "state": "Madhya Pradesh",
        "district": "Indore",
    }
    farm_res = await client.post("/api/v1/farms", json=farm_payload, headers=headers)
    assert farm_res.status_code == 201
    farm_data = farm_res.json()
    assert farm_data["name"] == "Indore Soybean Farm"
    farm_id = farm_data["id"]

    # 2. Create a Field under the Farm
    field_payload = {
        "name": "North Plot A",
        "area_hectares": 3.2,
    }
    field_res = await client.post(f"/api/v1/farms/{farm_id}/fields", json=field_payload, headers=headers)
    assert field_res.status_code == 201
    field_data = field_res.json()
    assert field_data["name"] == "North Plot A"
    field_id = field_data["id"]

    # 3. List Fields
    list_res = await client.get("/api/v1/fields", headers=headers)
    assert list_res.status_code == 200
    fields = list_res.json()
    assert len(fields) >= 1
    assert any(f["id"] == field_id for f in fields)

    # 4. Get Field Health (returns 501 - methodology not yet validated)
    health_res = await client.get(f"/api/v1/fields/{field_id}/health", headers=headers)
    # Field health scoring is intentionally not yet implemented
    assert health_res.status_code in (200, 501)
    if health_res.status_code == 200:
        health_data = health_res.json()
        assert health_data["field_id"] == field_id
        assert "fasal_health_score" in health_data
        assert "components" in health_data
        assert "zones" in health_data


@pytest.mark.asyncio
async def test_organization_user_cannot_create_field_on_another_organization_farm(client, test_db):
    org_a = Organization(name="Organization A", org_type=OrgType.fpo)
    org_b = Organization(name="Organization B", org_type=OrgType.fpo)
    test_db.add_all([org_a, org_b])
    await test_db.flush()
    enterprise_user = User(
        email="operator@orga.test",
        password_hash=get_password_hash("Password123!"),
        role=UserRole.enterprise,
        org_id=org_a.id,
    )
    farm_owner = User(
        email="owner@orgb.test",
        password_hash=get_password_hash("Password123!"),
        role=UserRole.farmer,
        org_id=org_b.id,
    )
    test_db.add_all([enterprise_user, farm_owner])
    await test_db.flush()
    other_org_farm = Farm(owner_user_id=farm_owner.id, org_id=org_b.id, name="Other organization farm")
    test_db.add(other_org_farm)
    await test_db.commit()

    token = create_access_token(enterprise_user.id, enterprise_user.role.value, enterprise_user.org_id)
    response = await client.post(
        f"/api/v1/farms/{other_org_farm.id}/fields",
        json={"name": "Unauthorized field"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
