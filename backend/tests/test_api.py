from fastapi.testclient import TestClient
from app.main import app, fields, diagnoses, videos

client = TestClient(app)

def setup_function():
    fields.clear(); diagnoses.clear(); videos.clear()

def test_health_and_field_flow():
    assert client.get('/health').json()['status'] == 'ok'
    field = client.post('/api/v1/fields', json={'name': 'North plot', 'crop': 'soybean'}).json()
    assert field['crop'] == 'soybean'
    assert client.get('/api/v1/fields').status_code == 200

def test_consent_required():
    field = client.post('/api/v1/fields', json={'name': 'Plot', 'crop': 'soybean'}).json()
    response = client.post('/api/v1/videos', data={'field_id': field['id'], 'consent': 'false'}, files={'file': ('x.mp4', b'video')})
    assert response.status_code == 400

def test_upload_returns_guarded_diagnosis():
    field = client.post('/api/v1/fields', json={'name': 'Plot', 'crop': 'soybean'}).json()
    response = client.post('/api/v1/videos', data={'field_id': field['id'], 'consent': 'true'}, files={'file': ('x.mp4', b'video')})
    assert response.status_code == 200
    analysis = client.get('/api/v1/videos/' + response.json()['id'] + '/analysis').json()
    assert analysis['confidence_band'] == 'low'
    assert 'confidently classify' in analysis['explanation']
