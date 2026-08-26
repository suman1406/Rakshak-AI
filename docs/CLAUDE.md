# CLAUDE.md — Fasal Rakshak Agent Instructions

Place this file at the repo root as `CLAUDE.md`. It is the operating manual
for any agent (or human) writing code here. Read this before touching any
ticket.

## What this project is

Fasal Rakshak turns a farmer's short crop video into a disease diagnosis +
severity estimate + farmer-readable report, backed by a versioned,
agronomist-verified Indian field dataset that improves over time. Soybean
only at MVP. Full context: `docs/source-plans/` (PRD, Backend/ML Plan,
Loopholes/Evaluation Framework, Implementation Plan) and
`docs/architecture/` (this doc set).

## Hardware/environment reality

The primary dev machine is a **Mac M2 Air, 8GB unified memory, no dedicated
GPU**. This is binding, not incidental:
- Never propose training a real model on the local machine's MPS backend
  beyond a tiny sanity check. Training happens on Colab/Kaggle (free GPU
  tiers) or a rented cloud GPU. Only final weights sync back locally.
- Never propose running a "GPU worker pool" as a local process. GPU
  inference calls out to a rented/serverless endpoint (RunPod, Vast.ai,
  Modal, Replicate, HF Inference Endpoints).
- Never let raw video/frames accumulate on local disk. Object storage is
  cloud (R2/B2) from Phase 2 onward; local disk is scratch only.
- Prefer managed cloud Postgres/Redis free tiers over running both as local
  containers alongside everything else.
- Prefer OrbStack over Docker Desktop if a container runtime is needed.
- If a task needs a GPU for more than a few seconds, or needs to store more
  than a few hundred MB, it belongs in the cloud — the laptop only
  orchestrates. See `Fasal_Rakshak_08_Environment_Setup.md`.

## Standing rules — never violate these

These come from `Fasal_Rakshak_01_Architecture_Reference.md` §4 and the
Loopholes document. They are permanent invariants, not one-time tasks, so
they apply to *every* ticket, not just the ticket that first introduces
them.

1. Never make GPU inference share infra/autoscaling with CPU processing.
   Always route through the `gpu_inference` / `cpu_processing` queue split.
2. Never treat the video→report pipeline as a synchronous request. Every
   stage transition is a persisted `videos.status` change.
3. Never add a prediction table or column without a `*_model_version` field.
4. Never write agronomist ground truth into `video_diagnoses`. It belongs in
   `verified_labels`, always.
5. Never let an AI diagnosis alone gate a financial action. Any
   B2B/financial-decision-linked case must go through the
   `decision_authority` flag (`advisory_only` → `human_confirmed`), enforced
   in the backend, not just UI copy.
6. Never store only a top-1 prediction where a full distribution is
   available. `frame_diagnoses.probability_distribution` is always the full
   distribution.
7. Never split train/val/test at the frame level. Always split at the video
   level via `dataset_splits`, and never disable the automated leakage
   check to make a deadline.
8. Never expose a confidence band computed from raw/uncalibrated softmax.
   Calibration (temperature scaling) happens first.
9. Never let the LLM/VLM explanation layer receive raw video or images.
   JSON in, JSON out, always. Never skip schema validation or the guardrail
   filter "just this once" — fall back to the canned template instead.
10. Never force-classify a low-confidence or out-of-taxonomy case into the
    nearest known disease. Route to "Unknown" + mandatory agronomist review.
11. Never expose precise GPS by default. Geohash/district-level only,
    unless an explicit consent flow says otherwise.
12. Never let a model auto-promote to production. It must pass the release
    gate (frozen regression set, slice checks, calibration, guardrail
    red-team, repeat-scan consistency) first — see
    `Fasal_Rakshak_09_Testing_Eval_Strategy.md`.
13. Never enable AI-assisted pre-labeling for agronomists before the blind
    re-labeling / anchoring-bias check (`FR-P7-04`) is live. Sequencing
    matters here, not just the individual features.
14. Never merge commercially-linked (insurer/input-company) verified labels
    into the core training set without a `source_channel` tag and a
    separate skew audit.

If a ticket seems to require breaking one of these, stop and flag it (as a
comment in the PR or an ADR) rather than silently working around it. These
rules exist because of documented failure modes in the Loopholes document —
they are the point of the project's risk mitigation, not friction to route
around.

## Coding conventions

- Python: type hints everywhere in `backend/app`; format with `black`, lint
  with `ruff`. FastAPI routers stay thin — business logic lives in
  `app/modules/*`, not in route handler bodies.
- SQLAlchemy models in `app/models/`, Pydantic schemas in `app/schemas/`,
  mirrored 1:1 with the tables in `Fasal_Rakshak_03_Data_Model_Schema.md`.
  If a migration is needed, generate it with Alembic autogenerate, then
  hand-review the diff before committing — never hand-write a migration that
  drifts from what the ORM models declare.
- Never edit an already-applied Alembic migration. Add a new one.
- Tests mirror source paths (see Repo Structure doc). Every new
  endpoint/module function needs a corresponding test in `backend/tests/`.
  No ticket is done without test coverage for its acceptance criteria.
- ML code: training scripts belong in `ml/training/<model>/`, promoted from
  notebooks once they're reproducible. Every training run logs to
  W&B/MLflow and records a dataset version — no "trained on whatever CSV was
  lying around."
- Commit messages and PR titles reference the ticket ID, e.g.
  `FR-P2-04: server-side quality scoring`.
- When a ticket's acceptance criteria is ambiguous, state the assumption
  you're making inline in the PR description and proceed — don't block on
  it unless it changes the architecture.

## Working through the backlog

- The authoritative backlog is `Fasal_Rakshak_05_Agentic_Phase_Backlog.md`
  (human-readable, full detail) and `Fasal_Rakshak_06_Task_Backlog.yaml`
  (machine-readable — update `status` as you work).
- Respect `depends_on`. Don't start a ticket whose dependencies are still
  `todo` unless explicitly asked to work out of order.
- Phases 2 and 3 are the one explicitly parallel pair — feel free to
  alternate between them, but don't start Phase 4 until both have met their
  exit criteria in the backlog doc.
- Phase 10 tickets are standing infrastructure, not a one-time checklist —
  once "done," they still run continuously (drift monitoring, golden-set
  refresh, etc.). Treat their completion as "the mechanism exists and is
  scheduled," not "the mechanism ran once."

## Definition of Done (apply to every ticket)

1. Acceptance criteria in the backlog doc are met and verifiable (a test,
   not just a claim).
2. No standing rule (above) is violated.
3. Tests added per the Testing & Eval Strategy doc; existing tests still
   pass.
4. Relevant doc updated in the same PR if behavior diverges from what's
   written (Architecture Reference, Data Model, API Spec) — these docs
   should never silently go stale.
5. `Fasal_Rakshak_06_Task_Backlog.yaml` status updated for the ticket.

## When something is genuinely ambiguous

Pick the most reasonable interpretation consistent with the four source
planning docs and the standing rules above, state the assumption, and
proceed. Only stop and ask when the ambiguity is architectural (would
require violating a standing rule, or picking between two incompatible
directions for a component) rather than a small implementation detail.