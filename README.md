# Rakshak AI · 0.2.0

A soybean video-assessment pilot with one connected FastAPI API, background model worker, Next.js web workspace and Flutter farmer app. The supplied EfficientNet checkpoint is integrated; the generic YOLO checkpoint does not verify crop identity. All current model outputs remain an unvalidated baseline.

## Start locally

Requires Docker, Node 22 with pnpm 11.10, and Flutter 3.41.6 for mobile.

1. Copy `.env.example` to `.env`. Set a unique `JWT_SECRET_KEY` and your initial administrator email/passphrase. Keep the populated file private.
2. Run `docker compose up --build -d`. This starts PostgreSQL, Redis, private MinIO storage, API, worker and scheduler. The API runs at `http://localhost:8000`; `/readyz` checks the database, queue and evidence bucket.
3. In `frontend/web`, run `pnpm install --frozen-lockfile`. Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in its local environment, then `pnpm dev`.
4. Register a farmer account to add fields and upload 10–30 second videos. Organization and agronomist applications require approval in the initial administrator's workspace.
5. For Android emulator development, run `flutter pub get` in `frontend/mobile`, then `flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000`. Debug builds permit local HTTP; release builds use HTTPS and your signing configuration.

The initial administrator is created only if that email does not already exist. This mechanism does not reset an existing user's password or grant a public registration administrator rights.

## Validation

The isolated validation stack uses separate containers and database, with synthetic accounts and footage:

```sh
docker build -t rakshak-prd-validation backend
docker compose -f docker-compose.validation.yml up -d
# Wait for http://localhost:8001/readyz to return 200.
docker compose -f docker-compose.validation.yml exec -T api python -m pytest -q -p no:cacheprovider
docker compose -f docker-compose.validation.yml exec -T api python scripts/validate_live_stack.py
```

The live smoke test runs the real supplied checkpoint, retrieves private evidence across separate API/worker filesystems, tests simultaneous onboarding approval, completes a human review, and verifies organization isolation. It creates clearly synthetic local records. It does not measure crop accuracy.

Web: `pnpm lint`, `pnpm test:contracts`, `pnpm build`. Mobile: `flutter analyze`, `flutter test`, `flutter build apk --debug`. GitHub Actions repeats these checks and the isolated model smoke flow on pushes and pull requests.

## Repository and release records

- `backend`: API, migrations, worker, supplied weights, private storage, review and consent controls.
- `frontend/web`: public site, farmer capture, expert review, organization overview, administration and settings.
- `frontend/mobile`: farmer field setup, capture/upload, history, evidence, feedback and account controls.
- [PRD acceptance record](docs/PRD_COMPLETION_AUDIT.md)
- [Deployment and operations](docs/RELEASE_0_2_0.md)
- [Storage and migration](docs/LOCAL_PILOT_STORAGE.md)
- [Design system](DESIGN.md)

`VERSION`, web package version and API version are 0.2.0; mobile is 0.2.0+2. Web and Flutter dependencies are locked. The Docker build constrains Python packages using `backend/requirements.lock`, captured from the tested Python 3.12 CPU runtime. Model asset hashes are recorded in `backend/app/weights/manifest.json`.

Production deployment, external provider credentials, mobile store signing and physical-device verification are separate release operations. No deployment or field-accuracy claim follows from a successful source build.
