import pytest

@pytest.mark.asyncio
async def test_logout_all_revokes_access_and_refresh_tokens(client):
    await client.post('/api/v1/auth/register', json={'email':'session@test.local','password':'Password123!', 'consent_to_data_processing':True})
    login = (await client.post('/api/v1/auth/login', json={'email_or_phone':'session@test.local','password':'Password123!'})).json()
    headers = {'Authorization': 'Bearer ' + login['access_token']}
    assert (await client.post('/api/v1/auth/logout-all', headers=headers)).status_code == 200
    assert (await client.get('/api/v1/auth/me', headers=headers)).status_code == 401
    assert (await client.post('/api/v1/auth/refresh', json={'refresh_token':login['refresh_token']})).status_code == 401
    login2 = (await client.post('/api/v1/auth/login', json={'email_or_phone':'session@test.local','password':'Password123!'})).json()
    assert (await client.get('/api/v1/auth/me', headers={'Authorization':'Bearer ' + login2['access_token']})).status_code == 200

@pytest.mark.asyncio
async def test_password_change_requires_current_password_and_revokes_sessions(client):
    await client.post('/api/v1/auth/register', json={'email':'password@test.local','password':'Password123!', 'consent_to_data_processing':True})
    login = (await client.post('/api/v1/auth/login', json={'email_or_phone':'password@test.local','password':'Password123!'})).json()
    headers = {'Authorization': 'Bearer ' + login['access_token']}
    assert (await client.post('/api/v1/auth/password', headers=headers, json={'current_password':'wrong','new_password':'NewPassword123!'})).status_code == 403
    assert (await client.post('/api/v1/auth/password', headers=headers, json={'current_password':'Password123!','new_password':'NewPassword123!'})).status_code == 200
    assert (await client.get('/api/v1/auth/me', headers=headers)).status_code == 401
    assert (await client.post('/api/v1/auth/login', json={'email_or_phone':'password@test.local','password':'Password123!'})).status_code == 401
    assert (await client.post('/api/v1/auth/login', json={'email_or_phone':'password@test.local','password':'NewPassword123!'})).status_code == 200
