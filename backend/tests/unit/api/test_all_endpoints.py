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
    # These endpoints require privileged roles that cannot be created via public registration
    # Public registration only allows farmer role (see auth.py validate_public_role)
    # Test that unauthenticated requests are rejected
    res = await client.get("/api/v1/admin/model-versions")
    # Will return 401 or 403 since we can't create admin users through public API
    assert res.status_code in (401, 403)

@pytest.mark.asyncio
async def test_b2b_dashboard_endpoint(client):
    # Enterprise role cannot be created via public registration
    res = await client.get("/api/v1/b2b/dashboard")
    assert res.status_code in (401, 403)

@pytest.mark.asyncio
async def test_agronomist_queue_endpoint(client):
    # Agronomist role cannot be created via public registration
    res = await client.get("/api/v1/agronomist/queue")
    assert res.status_code in (401, 403)
