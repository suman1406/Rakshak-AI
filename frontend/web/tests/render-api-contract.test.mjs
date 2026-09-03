import assert from 'node:assert/strict';
import test from 'node:test';

const baseUrl = (process.env.RAKSHAK_API_BASE_URL || 'https://rakshak-backend-7qx2.onrender.com').replace(/\/$/, '');
const requiredPaths = [
  '/api/v1/farms',
  '/api/v1/fields',
  '/api/v1/videos',
  '/api/v1/videos/{video_id}',
  '/api/v1/videos/{video_id}/analysis',
  '/api/v1/agronomist/queue',
  '/api/v1/agronomist/cases/{video_diagnosis_id}/claim',
  '/api/v1/diagnosis/{video_diagnosis_id}/verify',
  '/api/v1/b2b/dashboard',
];

test('deployed API exposes every frontend integration contract', async () => {
  const health = await fetch(`${baseUrl}/healthz`);
  assert.equal(health.status, 200);
  const spec = await fetch(`${baseUrl}/openapi.json`);
  assert.equal(spec.status, 200);
  const document = await spec.json();
  for (const path of requiredPaths) assert.ok(document.paths[path], `missing deployed API route: ${path}`);
  assert.ok(document.paths['/api/v1/farms'].get, 'farm listing must be deployed');
  assert.ok(document.paths['/api/v1/videos'].get, 'video history listing must be deployed');
});
