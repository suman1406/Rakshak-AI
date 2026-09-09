import pytest
from app.core.security import create_access_token
from app.models.identity import User, UserRole
from app.models.contact import ContactInquiry


@pytest.mark.asyncio
async def test_contact_is_persisted_private_and_can_be_closed(client, test_db):
    payload = {'name': ' Field team ', 'email': 'field@example.test', 'message': 'Please help with workspace access.', 'consent': True}
    response = await client.post('/api/v1/contact', json=payload)
    assert response.status_code == 201
    inquiry = await test_db.get(ContactInquiry, response.json()['reference'])
    assert inquiry.name == 'Field team'
    assert inquiry.request_key and '127.0.0.1' not in inquiry.request_key
    assert (await client.get('/api/v1/admin/inquiries')).status_code == 401
    farmer = User(email='farmer@contact.test', password_hash='unused', role=UserRole.farmer)
    admin = User(email='admin@contact.test', password_hash='unused', role=UserRole.admin)
    test_db.add_all([farmer, admin])
    await test_db.commit()
    farmer_headers = {'Authorization': 'Bearer ' + create_access_token(farmer.id, 'farmer')}
    admin_headers = {'Authorization': 'Bearer ' + create_access_token(admin.id, 'admin')}
    assert (await client.get('/api/v1/admin/inquiries', headers=farmer_headers)).status_code == 403
    listed = await client.get('/api/v1/admin/inquiries', headers=admin_headers)
    assert listed.json()[0]['id'] == inquiry.id
    assert (await client.post(f'/api/v1/admin/inquiries/{inquiry.id}/close', headers=admin_headers)).status_code == 200
    assert (await client.get('/api/v1/admin/inquiries', headers=admin_headers)).json()[0]['status'] == 'closed'


@pytest.mark.asyncio
async def test_contact_requires_consent_and_limits_repeated_submissions(client):
    payload = {'name': 'Field team', 'email': 'field@example.test', 'message': 'Please help with workspace access.', 'consent': False}
    assert (await client.post('/api/v1/contact', json=payload)).status_code == 422
    payload['consent'] = True
    for _ in range(10):
        assert (await client.post('/api/v1/contact', json=payload)).status_code == 201
    assert (await client.post('/api/v1/contact', json=payload)).status_code == 429
