# Fasal Rakshak — Agentic Phase Backlog

Converts the Implementation Plan's phase-by-phase "Build tasks" into atomic,
agent-executable tickets. Ticket IDs are stable (`FR-P<phase>-<seq>`) and are
referenced from `Fasal_Rakshak_06_Task_Backlog.yaml`, commit messages, and
PR titles. `Guardrail ref` points to the Loopholes document's `[L#]` list
where applicable, or to the relevant PRD/Backend-Plan section otherwise.

**Sequencing:** Phases run mostly in order. The one explicit parallelism is
Phase 2 (Backend/Infra) and Phase 3 (ML cold-start), which run
concurrently — for a solo builder/agent this means alternating focus within
a week, not literal simultaneity. Phase 10 is standing infrastructure that
starts at Phase 3 and never "completes."

Every ticket's Definition of Done implicitly includes: tests added per the
Testing & Eval Strategy doc, `CLAUDE.md` conventions followed, and the
relevant Architecture Reference §4 rule(s) not violated.

---

## Phase 0 — Prototype Spike

| ID | Title | Track | Depends on | Guardrail ref | Acceptance criteria |
|---|---|---|---|---|---|
| FR-P0-01 | Colab/Kaggle end-to-end spike notebook: video → frames → pretrained detector → pretrained classifier → naive majority vote → printed report | ML | — | PRD §8 | Notebook runs top-to-bottom on a sample video and prints a disease name + rough confidence |
| FR-P0-02 | Thin local FFmpeg frame-extraction script (fixed FPS, CPU-only, no GPU dependency) | ML | — | — | Given a video file, produces a folder of JPEG frames locally |
| FR-P0-03 | Assemble 10–20 sample soybean videos (recorded or stitched from public sets) | ML | — | — | Video set stored in a shared location (not committed to git), referenced by path in FR-P0-01 |
| FR-P0-04 | Written breakage log: where frame extraction, detection, and classification visibly fail on field-like footage | ML | FR-P0-01 | — | Markdown doc listing concrete failure modes (blur, no-leaf, wrong-crop, etc.), becomes the requirements input for Phase 2's quality pipeline |

**Exit criteria:** a video reliably produces *some* disease name + confidence out the other end, and the failure-mode list from FR-P0-04 exists.

---

## Phase 1 — Foundations & Scaffolding

| ID | Title | Track | Depends on | Guardrail ref | Acceptance criteria |
|---|---|---|---|---|---|
| FR-P1-01 | Repo scaffolding per `Fasal_Rakshak_02_Repo_Structure.md` | Infra | — | — | `backend/app/modules/{ingestion,processing,inference,aggregation,reporting,agronomist}` exist as empty packages; imports resolve |
| FR-P1-02 | docker-compose (OrbStack-targeted) + managed-cloud Postgres/Redis wiring per Environment Setup doc | Infra | FR-P1-01 | Hardware Reality Check | `docker-compose up` brings up FastAPI locally, pointed at managed cloud Postgres/Redis via `.env` |
| FR-P1-03 | Alembic init + first migration: `organizations`, `users`, `farms`, `fields`, `crops`, `diseases` | BE | FR-P1-01 | — | `alembic upgrade head` succeeds against a clean DB; tables match Data Model Schema doc exactly |
| FR-P1-04 | JWT auth + RBAC skeleton (farmer/agronomist/admin/enterprise) | BE | FR-P1-03 | PRD §32 | `require_role()` dependency exists; a protected endpoint returns 401/403 correctly for each role combination (test-covered) |
| FR-P1-05 | Structured JSON logging w/ request IDs + `/healthz` endpoint | Infra | FR-P1-01 | — | Every log line is JSON with a `request_id`; `/healthz` returns 200 |
| FR-P1-06 | Migration: `videos`, `frames`, `detections`, `frame_diagnoses`, `video_diagnoses`, `verified_labels`, `feedback`, `model_versions`, `golden_set_items`, `dataset_splits`, `audit_logs` | BE | FR-P1-03 | `[L13]`, Arch §4 rules 4–7 | All `*_model_version` columns non-nullable; `decision_authority` defaults to `advisory_only`; matches Data Model Schema doc exactly |

**Exit criteria:** `docker-compose up` gives a working FastAPI app + Postgres + Redis + object storage locally, migrations applied, RBAC-gated endpoints return correct 401/403.

---

## Phase 2 — Ingestion & Video Processing Pipeline *(parallel with Phase 3)*

| ID | Title | Track | Depends on | Guardrail ref | Acceptance criteria |
|---|---|---|---|---|---|
| FR-P2-01 | `videos.status` state machine + status endpoint | BE | FR-P1-06 | Arch §4 rule 2 | Every transition (`uploaded→...→ready\|failed\|insufficient_evidence`) is a persisted, queryable state; no stage is a bare synchronous call |
| FR-P2-02 | Resumable/chunked upload (tus protocol or S3 multipart) | BE | FR-P2-01 | PRD §7, Backend Plan §4 P1 | An upload interrupted mid-transfer and resumed completes successfully (integration test simulates this) |
| FR-P2-03 | FFmpeg scene-change-aware extraction service (CPU worker) | BE | FR-P1-01 | Backend Plan §4 P1 | Given a video, extraction uses scene-change sampling, not fixed FPS; more diverse frames than uniform sampling on a walking-through-field test video |
| FR-P2-04 | Quality scoring: blur (variance-of-Laplacian), exposure histogram, near-dup removal (pHash/embedding clustering), composite score — server-side | BE | FR-P2-03 | Arch §4 rule (never trust client-only) | Server-side score computed independent of any client-supplied score; near-dup frames are demonstrably clustered and pruned |
| FR-P2-05 | Celery + Redis wiring, two named queues: `cpu_processing`, `gpu_inference` | Infra | FR-P1-02 | Arch §4 rule 3 | Queue names exist and are used even though `gpu_inference` has no consumer yet |
| FR-P2-06 | Minimum-usable-frame threshold (default 5) → `insufficient_evidence` path | BE | FR-P2-04 | Backend Plan §8 | A video with <5 usable frames resolves to `insufficient_evidence`, not a diagnosis |
| FR-P2-07 | Object storage integration (R2/B2) + lifecycle policy | Infra | FR-P1-02 | Hardware Reality Check | Uploaded video/frames land in cloud object storage, never accumulate on local disk; lifecycle policy auto-archives after N days |

**Exit criteria:** a video uploaded over a throttled/interrupted connection completes; a visibly bad video (dark/shaky/no plant) routes to `insufficient_evidence`; status is queryable at every stage.

---

## Phase 3 — Cold-Start ML Baseline *(parallel with Phase 2)*

| ID | Title | Track | Depends on | Guardrail ref | Acceptance criteria |
|---|---|---|---|---|---|
| FR-P3-01 | Video-level train/val/test split enforcement (`dataset_splits` table + `stratified_split.py`) | ML | FR-P1-06 | `[L7]` | Automated check fails the build if any two frames from the same `video_id` land in different splits within a `split_version` |
| FR-P3-02 | Stratified sampling utility (crop/disease/severity/region/phone/lighting) | ML | FR-P3-01 | Eval Framework §1 | Given a candidate split, utility reports per-stratum counts; flags strata below a minimum-count threshold |
| FR-P3-03 | Crop classifier: EfficientNet-B0/MobileNetV3 transfer learning on public crop-ID data (Colab) | ML | FR-P0-01 | Backend Plan §5.1 | Trained checkpoint + eval metrics logged to W&B/MLflow; low-priority, verification-only role (crop is user-selected) |
| FR-P3-04 | Seed annotation sprint: 300–500 boxed images (CVAT/Label Studio), agronomist-reviewed lesion boundaries | ML | — | Backend Plan §5.2 | Annotated set stored in DVC/LakeFS; inter-annotator spot-check documented |
| FR-P3-05 | Plant/leaf/lesion detector: YOLOv8/YOLO11 fine-tuned on PlantDoc (not PlantVillage) + seed annotations (Colab) | ML | FR-P3-04 | Backend Plan §5.2 | Per-class recall reported, especially lesion class (Eval Framework §2) |
| FR-P3-06 | Disease classifier Stage 0: PlantVillage+PlantDoc+ICAR/Kaggle soybean, aggressive field-condition augmentation, class-weighted/focal loss (Colab) | ML | FR-P0-04, FR-P3-01 | Backend Plan §5.3 | AUPRC per class + confusion matrix logged; augmentation pipeline includes motion blur, lighting jitter, background-clutter compositing, JPEG artifacts |
| FR-P3-07 | Post-hoc calibration (temperature scaling) + ECE measurement | ML | FR-P3-06 | Arch §4 rule 9, Eval Framework §2 | ECE computed and acceptable for at least the High confidence band; raw softmax never exposed downstream |
| FR-P3-08 | Class taxonomy lock: Rust, Bacterial Blight, Frogeye Leaf Spot, Septoria Brown Spot, Healthy, Other/Unknown — validated against agronomist/ICAR reference | ML | — | Backend Plan §5.3 | `diseases` table populated with the validated launch taxonomy; sign-off documented in `docs/adr/` |
| FR-P3-09 | Experiment tracking (W&B/MLflow) + dataset versioning (DVC/LakeFS) wired from first run | ML | — | Backend Plan §6 | Every training run in FR-P3-03/05/06 is logged; dataset version is a citable identifier, not "latest" |
| FR-P3-10 | Golden test set v0 + first `model_versions` row | ML | FR-P3-06, FR-P3-07 | Backend Plan §6, `[L12]` | `golden_set_items` populated (small, real); `model_versions` has ≥1 row with recorded `eval_metrics` |

**Exit criteria:** frozen versioned golden test set exists; ECE measured and acceptable for High band; train/val/test split is provably video-level (automated check, not manual claim).

---

## Phase 4 — GPU Inference Integration *(tracks converge here)*

| ID | Title | Track | Depends on | Guardrail ref | Acceptance criteria |
|---|---|---|---|---|---|
| FR-P4-01 | GPU worker service wired to `gpu_inference` queue, calling a rented/serverless GPU endpoint (RunPod/Vast.ai/Modal/HF Inference) | Infra | FR-P2-05, FR-P3-10 | Hardware Reality Check | A queued `gpu_inference` task invokes the remote endpoint and returns a result; no model weights loaded on the Mac |
| FR-P4-02 | Inference chain: crop classifier → detector → disease classifier per frame, storing full probability distributions as JSONB | BE+ML | FR-P4-01 | Arch §4 rule 7 | `frame_diagnoses.probability_distribution` contains the full per-class distribution, not just top-1, for every processed frame |
| FR-P4-03 | Model-version stamping on every prediction row | BE | FR-P4-02 | Arch §4 rule 4 | `detector_model_version` / `classifier_model_version` populated and non-null on 100% of rows (DB constraint + test) |
| FR-P4-04 | GPU failure handling (simulate OOM/timeout) → recoverable `failed` state with clear `error_detail` | BE | FR-P4-01 | Backend Plan §8 scenario table | Simulated GPU failure leaves the job in `failed`, not stuck/silent; retry policy documented |
| FR-P4-05 | End-to-end smoke test: upload → `ready` → `frame_diagnoses` populated, no manual intervention | BE | FR-P2-*, FR-P4-02 | — | `scripts/smoke_test_pipeline.py` passes against a fresh environment |

**Exit criteria:** a video uploaded through Phase 2 → Phase 4 produces stored per-frame distributions end-to-end; simulated GPU OOM leaves a recoverable failed job.

---

## Phase 5 — Aggregation, Severity & Confidence

| ID | Title | Track | Depends on | Guardrail ref | Acceptance criteria |
|---|---|---|---|---|---|
| FR-P5-01 | Bayesian/log-odds temporal aggregation (weighted by detector confidence × frame quality) | BE+ML | FR-P4-02 | Backend Plan §5.4 | Aggregation ablation test shows this beats naive majority vote on a held-out set (Eval Framework §3) |
| FR-P5-02 | Severity heuristic: detection-stat-based, 4 ordinal levels, explicitly presented as an estimate | BE+ML | FR-P5-01 | Backend Plan §5.5 | Severity level derivable and explainable from stored detection statistics; UI copy marks it "estimate" |
| FR-P5-03 | Open-set/OOD "Unknown" routing (entropy or energy-based score) | ML | FR-P3-07 | Arch §4 rule 13 | A held-out genuinely-different plant/leaf image routes to `is_unknown = true`, not a confident wrong class |
| FR-P5-04 | Cost-weighted threshold selection + alert-dismissal-rate instrumentation | BE+ML | FR-P5-01 | `[L10]` | Threshold chosen via explicit FN/FP cost weights, not blind recall maximization; dismissal-rate metric exists and is queryable from day one |
| FR-P5-05 | Confidence bands computed strictly from calibrated probabilities | BE | FR-P3-07 | Arch §4 rule 9 | Band boundaries (High ≥90%, Medium 70–89%, Low <70%) applied only to temperature-scaled output |
| FR-P5-06 | Repeat-scan test-retest reliability test suite | ML | FR-P5-01 | Eval Framework §3 | Same (unchanging) sample field scanned twice; output agreement measured and passes before Phase 6 |

**Exit criteria:** repeat-scan test passes; a genuinely different plant/leaf image correctly routes to Unknown.

---

## Phase 6 — Explanation Layer & Farmer Report

| ID | Title | Track | Depends on | Guardrail ref | Acceptance criteria |
|---|---|---|---|---|---|
| FR-P6-01 | LLM/VLM call fed only structured JSON (crop, disease, confidence, severity, evidence counts) — never raw video/images | BE | FR-P5-02 | Arch §4 rule 10 | Code path has no way to attach raw media to the LLM request (enforced by the request-builder's type signature, not just convention) |
| FR-P6-02 | Strict output JSON schema + validation before rendering | BE | FR-P6-01 | Backend Plan §5.6 | Invalid LLM output is rejected pre-render, 100% of the time (test-covered) |
| FR-P6-03 | Guardrail regex/classifier filter (rejects "definitely," "100%," "guaranteed," "cured by X" etc.) + canned-template fallback | BE | FR-P6-02 | Backend Plan §5.6 | Any validation/guardrail failure falls back to the template, never a raw unfiltered LLM string |
| FR-P6-04 | Red-team test set + automated guardrail pass-rate check | BE | FR-P6-03 | Eval Framework §6 | Guardrail pass rate ≥ ~100% on the red-team suite in CI; any failure blocks the release, not a soft warning |
| FR-P6-05 | Farmer report screen data contract + static "what to do now" recommendation content | BE | FR-P6-03 | PRD §16, §30 | `GET /diagnosis/{id}` returns the exact PRD §30 shape; no autonomous pesticide prescriptions anywhere in the content |
| FR-P6-06 | Recurring human-review process doc: periodic small-panel review of generated reports for overstated certainty | Process | FR-P6-04 | Eval Framework §6 | Process documented with a cadence (not one-time); first review executed and logged |

**Exit criteria:** guardrail red-team suite passes at ~100%; a human reviewer confirms 10 sampled reports never imply certainty beyond the stated confidence band.

---

## Phase 7 — Agronomist Dashboard & Verified-Label Loop

| ID | Title | Track | Depends on | Guardrail ref | Acceptance criteria |
|---|---|---|---|---|---|
| FR-P7-01 | `verified_labels` write endpoint, structurally separate from `video_diagnoses` | BE | FR-P1-06 | Arch §4 rule 5 | `POST /diagnosis/{id}/verify` never writes to or mutates `video_diagnoses` |
| FR-P7-02 | Case queue prioritized by low-confidence-first | BE | FR-P5-05 | Backend Plan §4 P4 | `GET /agronomist/queue` orders by ascending confidence |
| FR-P7-03 | AI-assisted pre-labeling (VLM draft) gated on anchoring-bias mitigation being live first | BE+ML | FR-P7-04 | `[L2]` | Pre-labeling feature flag stays off until FR-P7-04 ships; PR description records the ordering |
| FR-P7-04 | Blind re-labeling scheduled job + agreement-rate metric | BE | FR-P7-01 | `[L2]` | Recurring job periodically hides the AI suggestion for a sample and compares to anchored labels; agreement rate is a queryable metric |
| FR-P7-05 | 2+ agronomist consensus rule for "gold" labels; single-review = operational only | BE | FR-P7-01 | Backend Plan §4 P4 | `is_gold` flips true only once `consensus_group_id` has 2 agreeing reviews; single reviews never feed training export |
| FR-P7-06 | Independent severity ground-truth field (agronomist visual % estimate, not detector-derived) | BE | FR-P7-01 | `[L8]` | `affected_plant_estimate_independent` is a required field on verification, never pre-filled from AI output |
| FR-P7-07 | Nightly export job → DVC/LakeFS hierarchical structure (Crop→Disease→Severity→Region→Crop Stage→Image/Video) | BE | FR-P7-05 | Backend Plan §4 P4 | One full cycle (case flagged → verified → exported → dataset repo updated) runs without manual intervention |

**Exit criteria:** one full verify→export cycle works unattended; first blind-relabeling run executed and its agreement rate documented.

---

## Phase 8 — Pilot Program & Real Field Data Collection

| ID | Title | Track | Depends on | Guardrail ref | Acceptance criteria |
|---|---|---|---|---|---|
| FR-P8-01 | Pilot partner recruitment criteria doc, including a deliberate worst-case-site quota | Process | — | `[L1]` | Doc explicitly requires ≥1–2 "hard" sites (poor lighting, older phones, weedy fields), not just convenient ones |
| FR-P8-02 | Multi-region pilot site tracking + per-region metric dashboard | BE | FR-P8-01 | `[L5]` | Per-region performance is a first-class pre-launch dashboard, not a post-launch discovery |
| FR-P8-03 | Quarterly physical/lab ground-truth verification workflow | Process | FR-P7-05 | `[L3]` | Scheduled recurring task exists; first round produces an independent-of-video ground-truth data point |
| FR-P8-04 | `source_channel` tagging enforced before any commercially-linked party's data enters the pipeline | BE | FR-P3-08's taxonomy in place | `[L4]` | No insurer/input-company verification can be written without a non-default `source_channel` value |
| FR-P8-05 | Fine-tune Stage-0 model on pilot data (domain adaptation) | ML | FR-P3-06, pilot data collected | Backend Plan §5.3 Stage 1 | New `model_versions` row registered, evaluated against golden set before any promotion decision |

**Exit criteria:** pilot dataset spans ≥2 regions and ≥1 deliberately hard site; per-region breakdown reviewed before any go/no-go decision; ≥1 round of independent physical verification exists.

---

## Phase 9 — Field/B2B Analytics & Scale Hardening

| ID | Title | Track | Depends on | Guardrail ref | Acceptance criteria |
|---|---|---|---|---|---|
| FR-P9-01 | Field Health Score rollup + Field Health Map | BE | FR-P5-02 | PRD §17–18 | `GET /fields/{id}/health` returns score + zone map matching PRD shape |
| FR-P9-02 | B2B dashboard APIs w/ District→FPO→Farm→Field→Video drill-down | BE | FR-P9-01 | PRD §31 | `GET /b2b/dashboard` and `/b2b/drilldown` match the API spec doc |
| FR-P9-03 | OLAP/read-replica evaluation (ClickHouse/DuckDB) — build only once volume justifies | Infra | FR-P9-02 | Backend Plan §4 P5 | Decision documented with a volume threshold; not built speculatively at pilot scale |
| FR-P9-04 | Enforce `decision_authority` in workflow for financial-decision-linked B2B cases | BE | FR-P1-06 | `[L13]` | A simulated financial-decision case is provably blocked from proceeding without a recorded agronomist sign-off (`human_confirmed` transition) |
| FR-P9-05 | Metadata integrity checks (timestamp/GPS consistency) + screen-replay/moiré fraud-detection | BE+ML | FR-P2-01 | Backend Plan §8 scenario table | A screen-replay test video is flagged; a GPS/timestamp-inconsistent upload is flagged |
| FR-P9-06 | Tenant-scoped RBAC / row-level security for multi-tenant B2B data | BE | FR-P9-02 | Backend Plan §8 scenario table | Postgres RLS (or equivalent app-layer enforcement) proven to block cross-tenant reads in a test |
| FR-P9-07 | GPU autoscaling policy + cost-per-analysis dashboard | Infra | FR-P4-01 | Backend Plan §4 P5 | Cost-per-analysis is a named, queryable business metric, instrumented before scale pressure hits |

**Exit criteria:** B2B demo drills from district aggregate to a specific video's evidence, correctly tenant-scoped; simulated financial-decision case is provably blocked without sign-off.

---

## Phase 10 — Evaluation Gate, MLOps & Governance *(standing, starts at Phase 3, never "completes")*

| ID | Title | Track | Depends on | Guardrail ref | Acceptance criteria |
|---|---|---|---|---|---|
| FR-P10-01 | Golden set governance: frozen regression subset (never regresses) + periodically refreshed subset, versioned changelog | ML | FR-P3-10 | `[L12]` | Two distinct, separately-tracked subsets exist; changelog records every refresh |
| FR-P10-02 | Shadow-mode harness with a defined minimum sample size, reserved for major model changes only | BE+ML | FR-P4-03 | `[L11]` | Minor retrains gate on the golden set alone; shadow mode is explicitly not run for every retrain |
| FR-P10-03 | Drift monitoring dashboard sliced by region/season/phone-model | BE | FR-P4-03 | Backend Plan §6 | Metrics are queryable per-slice, not just in aggregate |
| FR-P10-04 | Release-gate checklist automated in CI, blocking `deployment_status → production` | Infra | FR-P3-10, FR-P6-04, FR-P5-06 | Eval Framework §10 | `PATCH /admin/model-versions/{id}/deployment-status` to `production` fails without a passing release-gate record (see FR-P4 API spec) |
| FR-P10-05 | Error-attribution / oracle-detection ablation tooling | ML | FR-P4-02 | `[L6]` | Given ground-truth detections substituted in, tool reports the error-rate gap attributable to detection vs. classification vs. aggregation |
| FR-P10-06 | Standing metrics dashboard: FN/FP paired, agronomist override rate (top-1 vs top-2), cost per verified diagnosis, Other-bucket composition, blind-vs-anchored agreement, source-channel comparison | BE | FR-P7-04, FR-P8-04 | Eval Framework §9, `[L4]`, `[L9]` | All six metrics are live and queryable; "Other" bucket composition is periodically manually sampled, not just tracked as a number |

**Exit criteria for "governance is live":** a new model cannot reach production without passing through FR-P10-04's automated gate.

---

## Cross-cutting (build alongside Phase 1, enforced by Phase 9)

| ID | Title | Track | Depends on | Guardrail ref | Acceptance criteria |
|---|---|---|---|---|---|
| FR-PX-01 | Encryption in transit and at rest | Infra | FR-P1-02 | PRD §32 | TLS everywhere; `raw_gps_encrypted` and other sensitive columns encrypted at the app or column level |
| FR-PX-02 | Consent-based data collection flow + audit logs + data retention controls | BE | FR-P1-06 | PRD §32 | Every mutating request writes to `audit_logs`; retention policy enforced via S3 lifecycle rules from FR-P2-07 |