"""Exercise an isolated stack with real workers and checkpoints, not model accuracy.

Run inside the validation API container. Creates identifiable synthetic test records.
"""
import json
import time
from uuid import uuid4
import httpx
import tempfile
from pathlib import Path
import cv2
import numpy as np


def create_synthetic_mp4(count):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'synthetic.mp4'
        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*'mp4v'), 5, (128, 128))
        for index in range(count):
            rng = np.random.default_rng(index)
            writer.write(cv2.resize(rng.integers(30, 220, (16, 16, 3), dtype=np.uint8), (128, 128), interpolation=cv2.INTER_NEAREST))
        writer.release()
        return path.read_bytes()


def main():
    with httpx.Client(base_url='http://api:8000', timeout=60) as client:
        def call(method, path, **kwargs):
            response = client.request(method, '/api/v1' + path, **kwargs)
            response.raise_for_status()
            return response.json()

        email = f'validation-{uuid4().hex[:8]}@example.test'
        password = 'ValidationFarmer2026!'
        call('POST', '/auth/register', json={'email': email, 'password': password,
             'display_name': 'Validation Farmer', 'consent_to_data_processing': True})
        session = call('POST', '/auth/login', json={'email_or_phone': email, 'password': password})
        client.headers['Authorization'] = 'Bearer ' + session['access_token']
        farm = call('POST', '/farms', json={'name': 'Validation farm'})
        field = call('POST', f"/farms/{farm['id']}/fields", json={'name': 'Validation soybean plot', 'area_hectares': 1.2})
        upload = call('POST', '/videos', data={'field_id': field['id'], 'consent': 'true'},
                      files={'file': ('synthetic.mp4', create_synthetic_mp4(55), 'video/mp4')})
        video_id = upload['video_id']
        print(json.dumps({'email': email, 'video_id': video_id}), flush=True)
        deadline = time.monotonic() + 240
        previous = None
        while time.monotonic() < deadline:
            state = call('GET', f'/videos/{video_id}/status')
            if state['status'] != previous:
                print(json.dumps(state), flush=True)
                previous = state['status']
            if state['status'] in ('ready', 'failed', 'insufficient_evidence'):
                break
            time.sleep(3)
        assert state['status'] == 'ready', state
        analysis = call('GET', f'/videos/{video_id}/analysis')
        assert analysis['model_status'] == 'baseline_unvalidated'
        assert analysis['evidence']['frames_analyzed'] >= 5
        assert analysis['model_versions']['classifier'].startswith('effnet-')
        assert analysis['model_versions']['detector'] == 'whole-frame-observation-v1'
        assert abs(sum(analysis['probability_distribution'].values()) - 1) < .001
        frames = call('GET', f'/videos/{video_id}/frames')
        print(json.dumps({'analysis': analysis, 'frame_count': len(frames)}), flush=True)
        media = client.get(f'/api/v1/videos/{video_id}/content')
        assert media.status_code == 200 and len(media.content) > 100
        # A different, unauthenticated client must never receive private evidence.
        assert httpx.get(f'http://api:8000/api/v1/videos/{video_id}/content').status_code == 401
        # Exercise reviewed onboarding and the human-feedback loop on PostgreSQL.
        from app.core.config import settings
        assert settings.ENVIRONMENT == 'validation', 'Role smoke test is for the isolated validation environment only'
        admin_session = call('POST', '/auth/login', json={'email_or_phone': settings.INITIAL_ADMIN_EMAIL, 'password': settings.INITIAL_ADMIN_PASSPHRASE})
        admin_headers = {'Authorization': 'Bearer ' + admin_session['access_token']}
        expert_email = f'expert-{uuid4().hex[:8]}@example.test'
        application = call('POST', '/onboarding/applications', json={'application_type': 'agronomist', 'email': expert_email, 'access_phrase': password, 'display_name': 'Validation Agronomist', 'consent_to_data_processing': True})
        assert client.post('/api/v1/auth/login', json={'email_or_phone': expert_email, 'password': password}).status_code == 403
        from concurrent.futures import ThreadPoolExecutor
        def approve(_):
            return client.patch('/api/v1/admin/onboarding-applications/' + application['reference'], headers=admin_headers, json={'decision': 'approved', 'review_note': 'Isolated test account'}).status_code
        with ThreadPoolExecutor(max_workers=2) as pool:
            assert sorted(pool.map(approve, range(2))) == [200, 409]
        expert_session = call('POST', '/auth/login', json={'email_or_phone': expert_email, 'password': password})
        expert_headers = {'Authorization': 'Bearer ' + expert_session['access_token']}
        case_path = '/agronomist/cases/' + analysis['diagnosis_id']
        assert client.get('/api/v1' + case_path, headers=expert_headers).status_code == 404
        call('POST', '/diagnosis/' + analysis['diagnosis_id'] + '/review-requests')
        case = call('GET', case_path, headers=expert_headers)
        assert case['probability_distribution'] == analysis['probability_distribution']
        assert case['is_unknown'] is True
        call('POST', case_path + '/claim', headers=expert_headers)
        call('POST', '/diagnosis/' + analysis['diagnosis_id'] + '/verify', headers=expert_headers, json={'is_healthy_override': False, 'severity_level': 0, 'affected_plant_estimate_independent': 0, 'notes': 'Synthetic validation footage; no crop diagnosis can be established.'})
        reviewed = call('GET', f'/videos/{video_id}/analysis')
        assert reviewed['expert_review']['status'] == 'completed'
        assert reviewed['expert_review']['disease'] == 'Uncertain'
        assert call('GET', case_path, headers=expert_headers)['expert_review']['status'] == 'completed'
        org_email = f'org-{uuid4().hex[:8]}@example.test'
        org_application = call('POST', '/onboarding/applications', json={'application_type': 'organization', 'email': org_email, 'access_phrase': password, 'display_name': 'Validation Organization', 'organization_name': 'Validation Cooperative', 'organization_type': 'fpo', 'consent_to_data_processing': True})
        call('PATCH', '/admin/onboarding-applications/' + org_application['reference'], headers=admin_headers, json={'decision': 'approved'})
        org_session = call('POST', '/auth/login', json={'email_or_phone': org_email, 'password': password})
        org_headers = {'Authorization': 'Bearer ' + org_session['access_token']}
        org_farm = call('POST', '/farms', headers=org_headers, json={'name': 'Cooperative farm'})
        call('POST', f"/farms/{org_farm['id']}/fields", headers=org_headers, json={'name': 'Cooperative soybean field'})
        dashboard = call('GET', '/b2b/dashboard', headers=org_headers)
        assert dashboard['total_fields'] == 1 and dashboard['total_farms'] == 1
        assert client.get(f'/api/v1/videos/{video_id}/content', headers=org_headers).status_code == 404
        print(json.dumps({'expert_email': expert_email, 'organization_email': org_email}), flush=True)
        print('PASS: real checkpoint -> PostgreSQL report -> separate-host private evidence', flush=True)
        print('PASS: concurrent approval -> scoped review -> farmer feedback -> organization isolation', flush=True)


if __name__ == '__main__':
    main()
