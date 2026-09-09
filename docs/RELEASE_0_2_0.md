# Release 0.2.0 — deployment and operations

This is an integrated soybean MVP engineering release with unvalidated supplied model assets. Read `PRD_COMPLETION_AUDIT.md` for the acceptance boundary and evidence.

## Services and configuration

Run the API, one or more model workers, PostgreSQL, Redis and exactly one Celery beat scheduler. API and workers must share `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, S3 bucket/region/credentials and storage backend. Every service uses the same application revision. Private evidence is durable in S3-compatible object storage; local cache files are disposable.

API startup runs `alembic upgrade head`. Production forbids SQLite, local-only storage, development JWT secrets and bootstrapped demo accounts. `/healthz` is liveness; `/readyz` tests database, Redis and bucket access. Readiness does not establish that a worker is alive or that model accuracy is acceptable; run the real scan smoke flow after deployment.

`render.yaml` defines the API, model worker, scheduler and Redis. The plans carry cost and are not deployed by this source change. Before applying, configure the `rakshak-runtime` environment group with the production database URL, S3 endpoint/access/secret and exact web `CORS_ORIGINS`. Review bucket/region, resource plans and backup policy. Configure initial admin credentials on the API only. Keep all populated secrets out of Git.

On Vercel or another web host, set `NEXT_PUBLIC_API_URL` to the deployed API HTTPS origin and rebuild the web app. Do not deploy a web build pointed at localhost. Reuse the same origin in the Flutter release `API_BASE_URL` define.

## Upgrade existing installations

1. Back up the database and existing evidence volume/bucket. Preserve the current deployed revision for rollback.
2. Check `docs/LOCAL_PILOT_STORAGE.md`. If old records contain local file paths, run the migration on the host that still owns those files before retiring its disk.
3. Apply schema migrations through `0013_report_provenance`. Older reports intentionally do not receive invented model distributions or versions.
4. Deploy API and worker from the same revision and start one beat scheduler. Confirm shared environment values.
5. Check readiness, login/refresh, upload-to-report, private media, expert review and organization isolation on deployment-specific test records.
6. Deploy the web build and signed mobile distribution only after its configured API is reachable.

Do not downgrade migrations against production data as an automatic rollback. Restore from a reviewed backup or roll forward with a compatible application migration.

## Scheduled operations

- Stale nonterminal scans older than 15 minutes become retryable failed scans; model tasks have 600/660 second soft/hard limits.
- Evidence older than `EVIDENCE_RETENTION_DAYS` (180 by default) expires daily for terminal scans. Review metadata remains.
- API caches are pruned hourly for objects older than 24 hours; worker retention also prunes its cache.
- Dry-run retention and media migration are available through `python -m app.retention` and `python -m app.migrate_media`.
- `python -m app.dataset_export --help` describes optional consent-filtered expert training exports.

## Mobile distribution

The Android debug artifact is under `frontend/mobile/build/app/outputs/flutter-apk/app-debug.apk`. It targets the local emulator validation API only when built with the documented debug define. A physical phone needs a reachable host address; `10.0.2.2` is emulator-specific.

For release signing, create a private `frontend/mobile/android/key.properties` from the checked-in example and provide the keystore outside Git. Release no longer silently uses the debug key. iOS distribution requires macOS/Xcode, signing and device testing. Confirm camera permission, video selection, upload on poor connectivity, resume/history, image evidence and account logout on a real device before pilot rollout.

## External prerequisites still required

- Production PostgreSQL, private object storage, shared secrets, CORS/domain configuration and infrastructure cost review.
- A deployment-specific smoke run and monitored worker/queue behavior, including backup restoration and representative-video resource limits.
- Owner-approved Android/iOS signing and physical device tests.
- Optional advisory provider credentials/model. Without them, conservative templates are intentional and functional.
- Email/SMS/WhatsApp delivery is not enabled. Account-recovery requests are stored through the support form for verified manual handling; the app does not pretend to send a reset email.
- Real field datasets and a crop/leaf-specific detector, calibration and severity evaluation when the owner resumes model work. The generic detector baseline does not establish crop identity.

## Validation record

Validated locally on 2026-09-09:

- Backend: 82 unit/integration tests passed; four additional production-secret regression cases passed. The actual CPU checkpoint/PostgreSQL/Redis/private-storage smoke completed, including concurrent access approvals and farmer-to-expert review.
- Web: `pnpm lint`, `pnpm test:contracts` and `pnpm build` passed. Browser validation covered public/contact/admin, farmer evidence, organization field creation, valid expert submission dates and completed human review alongside saved model probabilities.
- Mobile: `flutter analyze --no-pub` reported no issues; `flutter test --no-pub` passed all four tests; `flutter build apk --debug --dart-define=API_BASE_URL=http://10.0.2.2:8001` produced the version 0.2.0+2 artifact.
- Git: implementation is grouped on `codex/prd-completion`; mobile workflows are in `55099a2`, mobile identity/signing in `50f509b`, and final review/history/job-state corrections in `02fb0d4`. Earlier focused commits cover model integration, private storage, account controls, contact persistence and web redesign.

The dependency lock records the successfully exercised Python 3.12 CPU runtime. A fresh build of that lock and the remote GitHub workflow must also pass before release approval. No production deployment has been performed in this session.
