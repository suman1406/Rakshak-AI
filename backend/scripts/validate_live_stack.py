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
        print('PASS: real checkpoint -> PostgreSQL report -> separate-host private evidence', flush=True)


if __name__ == '__main__':
    main()
