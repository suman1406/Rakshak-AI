# Fasal Rakshak — Environment Setup

Written for the Phase 0/1 bootstrap under the Hardware Reality Check (Mac
M2 Air, 8GB, no dedicated GPU). Service names below are the ones named in
the Implementation Plan; **check each provider's current free-tier limits
before relying on them** — those change over time and aren't verified here.

## 1. Accounts to create before Phase 1

| Purpose | Suggested provider(s) | Used from |
|---|---|---|
| Managed Postgres | Neon or Supabase (or equivalent managed free-tier Postgres) | Phase 1 |
| Managed Redis | Upstash (or equivalent managed free-tier Redis) | Phase 1 |
| Object storage | Cloudflare R2 or Backblaze B2 | Phase 2 |
| GPU training | Google Colab or Kaggle Notebooks (free GPU quota) | Phase 3 |
| GPU inference (rented/serverless) | RunPod or Vast.ai (spot) — or Modal / Replicate / HF Inference Endpoints (serverless) | Phase 4 |
| Experiment tracking | Weights & Biases or MLflow | Phase 3 |
| Dataset versioning | DVC (with a remote, e.g. the same object storage bucket) or LakeFS | Phase 3, 7 |
| Annotation tooling | CVAT or Label Studio | Phase 3 |
| LLM/VLM API | Any strong instruction-following model API | Phase 3 (pre-labeling), Phase 6 (explanation layer) |
| Error tracking | Sentry | Phase 8 (per Implementation Plan; logging shape from Phase 1) |
| Container runtime | OrbStack (Mac) | Phase 1 |

## 2. `.env.example`

```
# --- Environment ---
ENVIRONMENT=local            # local | pilot | production

# --- Database (managed cloud Postgres) ---
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>/<db>

# --- Redis (managed cloud, broker + cache) ---
REDIS_URL=rediss://<user>:<password>@<host>:<port>

# --- Auth ---
JWT_SECRET_KEY=<generate-a-strong-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# --- Object storage (R2/B2, S3-compatible) ---
S3_ENDPOINT_URL=<provider-endpoint>
S3_ACCESS_KEY=<key>
S3_SECRET_KEY=<secret>
S3_BUCKET_NAME=fasal-rakshak-videos
S3_REGION=auto

# --- GPU inference endpoint (rented/serverless) ---
GPU_INFERENCE_ENDPOINT_URL=<runpod-or-modal-endpoint>
GPU_INFERENCE_API_KEY=<key>

# --- LLM/VLM explanation layer ---
LLM_API_BASE_URL=<provider-base-url>
LLM_API_KEY=<key>

# --- MLOps ---
WANDB_API_KEY=<key>
DVC_REMOTE_URL=<same-bucket-or-separate>

# --- Observability ---
SENTRY_DSN=<dsn>            # can stay empty until Phase 8
```

Never commit a populated `.env`. `.env.example` (with placeholders only) is
the file that lives in git.

## 3. Local dev bootstrap (Mac-safe)

1. Install OrbStack (not Docker Desktop).
2. Create accounts + free-tier instances for managed Postgres and Redis;
   copy connection strings into `.env`.
3. Create an R2/B2 bucket; copy credentials into `.env`.
4. `cd backend && python -m venv .venv && source .venv/bin/activate`
5. `pip install -r requirements.txt` (or `poetry install` if using Poetry).
6. `alembic upgrade head` — applies the schema in
   `Fasal_Rakshak_03_Data_Model_Schema.md`.
7. `docker compose up` (OrbStack) — brings up just the FastAPI app +
   Celery worker locally; Postgres/Redis are the managed cloud instances
   from step 2, not local containers. A minimal local MinIO container is
   acceptable for a handful of throwaway test videos during early dev, but
   should never hold real/pilot footage.
8. `curl localhost:8000/healthz` should return `200`.

### Minimal `docker-compose.yml` shape

```yaml
services:
  api:
    build: ./backend
    env_file: .env
    ports: ["8000:8000"]
  worker-cpu:
    build: ./backend
    command: celery -A app.workers.celery_app worker -Q cpu_processing --loglevel=info
    env_file: .env
  worker-gpu:
    build: ./backend
    command: celery -A app.workers.celery_app worker -Q gpu_inference --loglevel=info
    env_file: .env
    # this worker's tasks call out to GPU_INFERENCE_ENDPOINT_URL — it does not
    # load any model weights itself, so it's fine to run locally
```
No `postgres:` or `redis:` service is defined here on purpose — see the
Hardware Reality Check rationale in the Architecture Reference doc. Add them
back locally only for fully offline development, and never let them hold
data that matters.

## 4. ML training workflow (Colab/Kaggle)

1. Push the relevant script/notebook from `ml/training/<model>/` (or work
   directly in `ml/notebooks/` during early iteration).
2. Open in Colab/Kaggle, select a free GPU runtime.
3. Point the notebook's dataset-loading cell at DVC/LakeFS (not local
   disk) for anything beyond a tiny sanity-check sample.
4. Log the run to W&B/MLflow (`WANDB_API_KEY` from `.env`, entered as a
   Colab secret, not committed anywhere).
5. Sync only the final weights (tens–hundreds of MB) back to a location the
   backend's `GPU_INFERENCE_ENDPOINT_URL` deployment can load from — not
   into the git repo directly unless the file is small and versioned
   deliberately.
6. Register the trained model via `POST /admin/model-versions` (see API
   Specification doc) so it gets a `model_versions` row before anything
   downstream references it.

## 5. Mobile (Flutter) testing

Test on a physical Android or iOS device over USB/wireless debugging.
Avoid running an emulator simultaneously with the rest of the local stack —
emulators alone can consume several GB of the machine's 8GB RAM.

## 6. Secrets management

`.env` locally, never committed. For pilot/production, move to a proper
secrets manager (cloud provider's native one, or a lightweight option like
Doppler/1Password Secrets Automation) — this is a Phase 8/9-era upgrade, not
required for local dev.