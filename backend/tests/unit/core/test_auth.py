import pytest
from app.core.security import create_refresh_token
from app.core.security import create_access_token, decode_token, get_password_hash, verify_password

def test_password_hashing():
    raw = "secretPassword123"
    hashed = get_password_hash(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("wrongPassword", hashed) is False

def test_jwt_token_creation_and_decoding():
    user_id = "test-user-uuid"
    role = "farmer"
    token = create_access_token(subject=user_id, role=role)
    payload = decode_token(token)
    assert payload["sub"] == user_id
    assert payload["role"] == role
    assert payload["type"] == "access"

@pytest.mark.asyncio
async def test_auth_register_and_login_flow(client):
    # 1. Register new user
    register_payload = {
        "email": "testfarmer@rakshak.ai",
        "password": "Password123!",
        "display_name": "Test Farmer",
        "consent_to_data_processing": True,
    }
    reg_response = await client.post("/api/v1/auth/register", json=register_payload)
    assert reg_response.status_code == 201
    user_data = reg_response.json()
    assert user_data["email"] == "testfarmer@rakshak.ai"
    assert user_data["role"] == "farmer"

    # 2. Login with registered user
    login_payload = {
        "email_or_phone": "testfarmer@rakshak.ai",
        "password": "Password123!",
    }
    login_response = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["role"] == "farmer"

    # 3. Access /me endpoint with token
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_response = await client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "testfarmer@rakshak.ai"


@pytest.mark.asyncio
async def test_public_registration_cannot_assign_a_privileged_role(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "admin-attempt@rakshak.ai", "password": "Password123!", "role": "admin"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_public_registration_rejects_short_password(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "short-password@rakshak.ai", "password": "short"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_refresh_token_cannot_access_protected_routes(client):
    registration = await client.post(
        "/api/v1/auth/register",
        json={"email": "refresh-misuse@rakshak.ai", "password": "Password123!", "consent_to_data_processing": True},
    )
    user_id = registration.json()["id"]
    refresh_token = create_refresh_token(user_id)

    response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {refresh_token}"})

    assert response.status_code == 401
