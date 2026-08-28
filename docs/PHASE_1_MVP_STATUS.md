# Rakshak AI Phase 1 MVP status

Updated: 2026-08-28  
Scope: non-model P0/P1 pilot hardening. Model training, calibration, and model-quality evaluation remain with the ML owner.

## Completed in this sprint

- [x] Shared tenant-scope helpers are applied to farm, field, video, diagnosis, agronomist, and B2B reads.
- [x] Protected evidence access uses an authenticated backend route and never returns raw storage paths to clients.
- [x] Login and refresh-token flows are available to web and Flutter clients.
- [x] Flutter stores access and refresh tokens in `flutter_secure_storage` and can restore/refresh a session.
- [x] Web stores the access and refresh tokens separately and clears both on logout.
- [x] Video extension and maximum-size validation are enforced before processing.
- [x] Video processing records retry count, start time, completion time, last failure time, and failure detail.
- [x] Celery is routed to the named `cpu_processing` queue; the worker is subscribed to both `cpu_processing` and `gpu_inference` so the future model worker can be isolated without changing the API.
- [x] Key mutation paths write audit records: registration, login, farm creation, field creation, video upload, feedback, and agronomist verification.
- [x] API errors expose a consistent `error_code`, `message`, and `request_id` envelope.
- [x] Docker configuration includes the API, PostgreSQL, Redis, MinIO, and a queue-aware worker.

## Still required before a credible pilot

- [x] Add committed Alembic migration history and run it before seed on Docker startup. A clean-database migration test is still required before production use.
- [ ] Complete S3/MinIO object storage integration for uploaded videos and extracted frames, including lifecycle/retention policy. The current authenticated local file route is a safe development fallback, not cloud storage.
- [ ] Add real evidence-frame fixtures to the seed dataset or label seeded evidence as unavailable. Synthetic database paths must not look like downloadable production evidence.
- [ ] Add two-organization cross-tenant tests covering farms, fields, videos, diagnoses, feedback, and frame access.
- [ ] Add end-to-end API contract tests for Flutter and web upload/status/analysis/feedback flows.
- [ ] Add worker retry/idempotency integration tests, including permanent failure and timeout behavior.
- [ ] Reconcile `API.md` and `backend/SEED_ACCOUNTS.md` with the live response schemas and canonical seed accounts.
- [ ] Add structured audit assertions for every remaining mutating admin endpoint.
- [ ] Add an explicit contract for resumable uploads; the current MVP remains multipart upload.
- [ ] Keep confidence wording explicitly uncalibrated until the ML owner supplies calibration evidence.

## Deliberately out of scope for this sprint

- Training or retraining YOLO/PyTorch models.
- Model calibration, golden-set creation, drift monitoring, and release-gate evaluation.
- Scientific field/laboratory validation and PRD accuracy targets.
- GPU infrastructure provisioning. The queue boundary is ready, but model-worker deployment depends on the ML environment.

## Validation performed

- Python syntax compilation for the backend source.
- Backend unit and integration tests where local dependencies are available.
- Web TypeScript build/lint.
- Flutter source/static validation only; no device, emulator, or Flutter runtime was launched.

## Release note

This is a controlled pilot hardening pass, not a claim of production compliance. Before external pilot traffic, complete the unchecked storage, migration, cross-tenant, contract, and worker integration items above and configure secrets outside the repository.
