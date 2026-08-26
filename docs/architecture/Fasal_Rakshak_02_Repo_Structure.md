# Fasal Rakshak — Repository Structure

Canonical monorepo layout. Every ticket in the phase backlog references
paths from this tree. If a ticket needs a path not listed here, add it in
the same place the pattern below implies, and note the addition in the PR.

```
fasal-rakshak/
├── CLAUDE.md                          # = Fasal_Rakshak_07_CLAUDE_Agent_Instructions.md, copied to repo root
├── README.md
├── docs/
│   ├── source-plans/                  # the four original planning docs, unmodified
│   ├── architecture/                  # this doc set (01, 02, 03, 04, 08, 09)
│   ├── backlog/                       # 05 (md) + 06 (yaml), kept in sync with actual issue tracker
│   └── adr/                           # Architecture Decision Records — one short .md per non-trivial
│                                       #   deviation from docs/architecture, numbered ADR-0001, ADR-0002...
│
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app factory, router registration
│   │   ├── core/
│   │   │   ├── config.py              # pydantic-settings, reads .env
│   │   │   ├── security.py            # JWT, password hashing, RBAC dependency
│   │   │   ├── logging.py             # structured JSON logging w/ request IDs
│   │   │   └── deps.py                # shared FastAPI dependencies (db session, current_user, require_role)
│   │   ├── db/
│   │   │   ├── base.py                # SQLAlchemy declarative base, import hub for Alembic autogenerate
│   │   │   └── session.py             # engine + session factory
│   │   ├── models/                    # SQLAlchemy ORM models — one file per table cluster
│   │   │   ├── identity.py            # users, organizations
│   │   │   ├── farm.py                # farms, fields, crops, diseases
│   │   │   ├── video.py               # videos, frames
│   │   │   ├── prediction.py          # detections, frame_diagnoses, video_diagnoses
│   │   │   ├── verification.py        # verified_labels, feedback
│   │   │   └── governance.py          # model_versions, golden_set_items, dataset_splits, audit_logs
│   │   ├── schemas/                   # Pydantic request/response models, mirrors models/ 1:1
│   │   ├── modules/                   # business logic, one subpackage per architectural module
│   │   │   ├── auth/
│   │   │   ├── ingestion/             # upload handling, state-machine transitions
│   │   │   ├── processing/            # FFmpeg, quality scoring, near-dup removal (CPU-worker logic)
│   │   │   ├── inference/             # model-calling logic (GPU-worker logic; models themselves live in ml/)
│   │   │   ├── aggregation/           # temporal voting, severity heuristic, OOD routing
│   │   │   ├── reporting/             # explanation service: JSON contract, guardrail filter, templates
│   │   │   ├── agronomist/            # verification queue, verify endpoint, consensus logic
│   │   │   ├── field_intelligence/    # Field Health Score, Field Health Map, B2B drill-down
│   │   │   └── admin/                 # model_versions registry, golden-set management
│   │   ├── workers/
│   │   │   ├── celery_app.py          # Celery app, queue definitions (cpu_processing, gpu_inference)
│   │   │   ├── cpu_tasks.py
│   │   │   └── gpu_tasks.py           # calls out to rented/serverless GPU endpoint; no local model load
│   │   └── guardrails/                # LLM output JSON-schema validation + regex/classifier certainty filter
│   ├── alembic/
│   │   ├── versions/                  # one file per migration; never edit an applied migration, only add new ones
│   │   └── env.py
│   ├── tests/
│   │   ├── unit/                      # mirrors app/ 1:1, e.g. tests/unit/modules/ingestion/test_quality_score.py
│   │   ├── integration/               # full pipeline runs against a test DB + sample fixture videos
│   │   ├── guardrail_redteam/         # the adversarial JSON input suite from the eval framework
│   │   └── fixtures/                  # small sample videos/frames checked in (or fetched from a fixtures bucket)
│   ├── pyproject.toml
│   └── Dockerfile
│
├── ml/
│   ├── notebooks/                     # Colab/Kaggle notebooks; treat as source, sync final .py/.ipynb here
│   ├── training/
│   │   ├── crop_classifier/
│   │   ├── detector/
│   │   ├── disease_classifier/
│   │   └── aggregation_heuristic/     # Bayesian/log-odds weighting logic + later meta-model experiments
│   ├── eval/
│   │   ├── golden_set/                # manifest files (video IDs + subset + version), not the videos themselves
│   │   ├── metrics/                   # component + end-to-end metric computation scripts
│   │   └── red_team/                  # adversarial structured-JSON test cases for the guardrail filter
│   ├── data_pipeline/
│   │   ├── stratified_split.py        # enforces video-level, stratified splitting — see [L7]
│   │   └── export_to_dvc.py           # nightly export job: verified_labels -> DVC/LakeFS hierarchical structure
│   └── requirements.txt
│
├── infra/
│   ├── docker-compose.yml             # local dev only; see Environment Setup doc for what's local vs. managed
│   ├── terraform/                     # infra-as-code, introduced Phase 1, expanded Phase 9
│   └── ci/                            # CI pipeline definitions (see Testing & Eval Strategy doc)
│
├── mobile/                            # Flutter app — out of scope for backend-focused tickets in this backlog
│
└── scripts/
    ├── seed_dev_db.py
    └── smoke_test_pipeline.py         # scripted upload -> poll status -> assert ready, for local sanity checks
```

## Module boundary rules

- `app/modules/<name>/` may depend on `app/models`, `app/schemas`,
  `app/core`, and `app/db`. It should **not** import another module's
  internals directly (`modules/aggregation` should not reach into
  `modules/inference`'s private helpers) — go through a public function or
  a shared service in `app/core` if cross-module coordination is needed.
- `app/workers/*_tasks.py` are thin: they resolve queue plumbing and call
  into `app/modules/*` functions. Business logic does not live in the task
  file itself, so it stays unit-testable without Celery running.
- Vision model weights and training code live in `ml/`, never in `backend/`.
  `backend/app/workers/gpu_tasks.py` calls a rented/serverless inference
  endpoint (or, later, an internal Triton endpoint) — it does not load model
  weights in-process.
- `ml/notebooks/` is allowed to be messy (that's what Colab/Kaggle is for);
  anything that needs to be reproducible or reused gets promoted into
  `ml/training/<model>/` as a script before a ticket is marked done.

## Naming conventions

- Python: `snake_case` files/functions, `PascalCase` classes, one
  SQLAlchemy model class per file section in `models/`.
- Tests mirror source paths: `app/modules/ingestion/quality_score.py` →
  `tests/unit/modules/ingestion/test_quality_score.py`.
- Migrations: `alembic/versions/<timestamp>_<short_description>.py`,
  auto-generated then hand-reviewed — never hand-write a migration that
  drifts from what `models/` declares.
- Ticket IDs (from the backlog) referenced in commit messages and PR titles:
  `FR-P<phase>-<seq>`, e.g. `FR-P2-04`.