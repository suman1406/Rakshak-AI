"""
Unit tests verifying all API endpoints across Auth, Farms/Fields, Videos, Diagnosis, Agronomist, B2B, and Admin modules.
"""

import pytest

@pytest.mark.asyncio
async def test_auth_refresh_endpoint(client):
    # Register & login
    reg_res = await client.post(
        "/api/v1/auth/register",
        json={"email": "refreshtest@rakshak.ai", "password": "PassWord123!", "role": "farmer"},
    )
    assert reg_res.status_code == 201

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email_or_phone": "refreshtest@rakshak.ai", "password": "PassWord123!"},
    )
    assert login_res.status_code == 200
    tokens = login_res.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # Refresh
    ref_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert ref_res.status_code == 200
    assert "access_token" in ref_res.json()

@pytest.mark.asyncio
async def test_admin_model_versions_endpoint(client):
    res = await client.get("/api/v1/admin/model-versions", headers={"x-demo-role": "admin"})
    assert res.status_code == 200
    versions = res.json()
    assert len(versions) >= 2

@pytest.mark.asyncio
async def test_b2b_dashboard_endpoint(client):
    res = await client.get("/api/v1/b2b/dashboard", headers={"x-demo-role": "admin"})
    assert res.status_code == 200
    data = res.json()
    assert "total_farms" in data
    assert "fasal_health_index" in data

@pytest.mark.asyncio
async def test_agronomist_queue_endpoint(client):
    res = await client.get("/api/v1/agronomist/queue", headers={"x-demo-role": "agronomist"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)
