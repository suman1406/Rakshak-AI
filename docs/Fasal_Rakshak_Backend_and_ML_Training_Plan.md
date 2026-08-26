# Fasal Rakshak: Backend + ML Training Plan

## 1. Architecture Philosophy

Two decisions shape everything else:

- **Modular monolith, not microservices, at MVP.** A single FastAPI codebase with clearly separated internal modules (ingestion, processing, inference, aggregation, reporting, agronomist-review) is faster to build and debug with a small team. Split into separate *deployable* services only where there's a real scaling mismatch — which is exactly one place: **GPU inference must be its own scalable worker pool**, decoupled from the CPU-bound API and video-processing layers.
- **The pipeline must be a durable state machine, not a single request.** Video → report can take 30–60s+ and multiple stages can fail independently (bad video, GPU OOM, LLM API timeout). Every video gets a persistent job with an explicit status enum, not a synchronous HTTP call.

## 2. Backend Component Breakdown

```
Client (Flutter)
   │  resumable/multipart upload
   ▼
FastAPI (API layer: auth, RBAC, CRUD, status polling)
   │
   ▼
Redis (broker) → Celery/RQ task queue
   │
   ├─► CPU Worker Pool (autoscale on CPU)
   │     - FFmpeg frame extraction
   │     - Blur / exposure / motion quality scoring
   │     - Near-duplicate removal
   │     - Best-frame selection
   │
   ├─► GPU Worker Pool (autoscale on GPU, separate node group)
   │     - Crop classifier
   │     - Plant/leaf/lesion detector (YOLO)
   │     - Disease classifier (per leaf-region crop)
   │
   ├─► Aggregation Service (CPU, lightweight)
   │     - Temporal voting / probability aggregation
   │     - Severity estimation
   │     - Field Health Score rollup
   │
   └─► Explanation Service
         - Calls LLM/VLM API with structured JSON (never raw video)
         - Schema validation + guardrail filter
         - Template fallback on failure

PostgreSQL (system of record) ── Object Storage (S3-compatible, videos/frames)
Redis (cache + job status) ── DVC/LakeFS (versioned training datasets, separate from prod DB)
```

**Why GPU inference is isolated:** CPU processing and GPU inference have completely different cost profiles, scaling triggers, and failure modes. If they share a worker pool, you either overprovision expensive GPU nodes to handle FFmpeg jobs, or starve inference during upload spikes. Route via separate Celery queues (`cpu_processing`, `gpu_inference`) from day one even before you formally split deployments — it's a one-line change now vs. a painful migration later.

**Production-scale note (not MVP-day-1, but design for it):** plain PyTorch-in-a-worker inference doesn't batch efficiently. Plan a migration path to **NVIDIA Triton Inference Server** or **TorchServe** once volume justifies it — it gives you dynamic batching (critical for GPU cost control) and clean model versioning/hot-swapping.

## 3. Data Model (Postgres) — Key Tables

Beyond the obvious `users`, `farms`, `fields`, design these deliberately:

| Table | Key columns / notes |
|---|---|
| `videos` | status enum (`uploaded→validating→processing→analyzing→aggregating→ready→failed`), quality_score, gps_geohash (truncated), raw_gps (encrypted, restricted access) |
| `frames` | video_id, storage_path, blur_score, exposure_score, is_selected, sequence_index |
| `detections` | frame_id, bbox, class (plant/leaf/lesion/stem/pod), detector_confidence, **detector_model_version** |
| `frame_diagnoses` | detection_id, **full probability distribution as JSONB** (not just top-1), classifier_model_version |
| `video_diagnoses` | video_id, aggregated disease, confidence, confidence_band (H/M/L), severity_level, affected_plant_estimate, supporting_frames/total_frames, **aggregation_model_version** |
| `diseases` / `crops` | taxonomy tables, versioned (don't hardcode enums in code) |
| `verified_labels` | separate from `video_diagnoses` — agronomist ground truth, distinct from AI prediction, this is what feeds training, never mix the two |
| `feedback` | farmer-reported correction, lower trust weight than agronomist verification |
| `model_versions` | registry: model name, version hash, training dataset version, eval metrics, deployment status (shadow/canary/production) |

The `*_model_version` fields on every prediction table are not optional — without them you cannot debug regressions, run shadow comparisons, or explain to an agronomist/insurer why a diagnosis changed between two model releases.

## 4. Phased Backend Build Plan

**Phase 0 — Foundations (before Sprint 1)**
Repo + CI/CD, Terraform for infra-as-code, Docker skeleton for FastAPI, Alembic migrations, S3 bucket + lifecycle policies (auto-archive/delete raw video after N days per retention policy), JWT auth + RBAC skeleton (farmer/agronomist/admin/enterprise roles from day one — retrofitting RBAC is painful), structured logging + Sentry + Prometheus/Grafana.

**Phase 1 — Ingestion & Processing (Sprints 1–2)**
- Resumable/chunked upload (tus protocol or S3 multipart) — mandatory given rural/low-bandwidth connectivity, not a nice-to-have.
- FFmpeg extraction using **scene-change-aware sampling** (`select='gt(scene,0.02)'` or similar), not fixed FPS — gets more diverse frames from a walking-through-field video than uniform sampling.
- Blur detection: variance-of-Laplacian threshold (classic, fast, no model needed).
- Exposure: histogram-based over/underexposure check.
- Near-duplicate removal: perceptual hashing (pHash) or cheap embedding similarity (MobileNet features) + clustering, keep best-scoring frame per cluster.
- Composite quality score = weighted(blur, exposure, motion, coarse plant-coverage) → drives the on-device-mirrored "82/100" score. **Never trust only client-side quality checks** — re-validate server-side as defense in depth.

**Phase 2 — Inference (Sprints 3–4)**
Stand up GPU workers, wire crop classifier → detector → disease classifier → store full distributions per frame.

**Phase 3 — Aggregation, Explanation, Farmer Report (Sprint 5)**
Temporal voting service, severity heuristic, LLM explanation service with strict JSON-in/JSON-out contract, feedback endpoint.

**Phase 4 — Agronomist Dashboard (Sprint 6)**
Verification endpoint writing to `verified_labels` (kept separate from raw predictions), case queue **prioritized by low confidence first** (that's where verification adds the most value), nightly export job pushing verified samples into a DVC/LakeFS-tracked dataset using the hierarchical structure (Crop → Disease → Severity → Region → Crop Stage → Image/Video).

**Phase 5 — Field/B2B Analytics + Hardening (Sprints 7–8)**
Field Health Score rollups, B2B dashboard APIs. Watch out: aggregate queries over millions of `frame_diagnoses` rows will get slow on OLTP Postgres — plan for a read replica or a lightweight OLAP layer (ClickHouse/DuckDB) once B2B volume grows; not needed at pilot scale. Load testing, GPU autoscaling policies, cost-per-analysis dashboard (this is a named business metric — instrument it early).

## 5. Model Training Strategy — Per Model

The biggest unstated risk in the product is the **cold-start problem**: the whole product thesis (the moat is verified Indian field data) assumes you have zero real field data at launch. The plan has to explicitly bridge that gap.

### 5.1 Crop Classifier
- Transfer learning: EfficientNet-B0/MobileNetV3 backbone, fine-tuned on public crop-ID datasets + your own pilot images.
- Low risk area — for MVP, crop selection is already mandatory for the user, so this model's job is verification, not sole authority. Don't over-invest here initially.

### 5.2 Plant/Leaf/Lesion Detector
- YOLOv8/YOLO11, COCO-pretrained, fine-tuned.
- **Cold start:** PlantDoc (real field-condition images) is a better base than PlantVillage for this stage since PlantVillage is lab-condition and won't transfer well to messy field video frames.
- Requires a **seed annotation sprint**: 300–500 manually boxed images across varied lighting/angle/phone conditions, using CVAT or Label Studio, ideally with an agronomist reviewing lesion boundaries.

### 5.3 Disease Classifier (the core model)
- Backbone: EfficientNet or ViT-B/16, fine-tuned per-crop, starting with soybean only.
- **Stage 0 (cold start):** PlantVillage soybean subset + PlantDoc soybean subset + any ICAR/Kaggle Indian soybean disease datasets available, combined with aggressive augmentation (motion blur simulation, lighting jitter, background-clutter compositing, JPEG compression artifacts) specifically to close the lab→field domain gap.
- **Stage 1 (pilot):** Partner with 5–10 real farms/an FPO or an agri university trial plot for supervised video collection with agronomist ground truth. This produces the first *real* Indian-field-labeled dataset, disproportionately valuable for domain adaptation via fine-tuning on top of the Stage 0 model.
- **Speed up annotation with AI-assisted pre-labeling:** run a strong general-purpose VLM over newly collected field images to draft candidate labels/descriptions, then have agronomists correct rather than label from scratch — roughly halves annotation time.
- **Class taxonomy:** lock a small, well-validated set for launch (e.g., Rust, Bacterial Blight, Frogeye Leaf Spot, Septoria Brown Spot, Healthy, Other/Unknown) — validate this list with an actual agronomist/ICAR reference before training.
- **Loss/calibration:** class-weighted or focal loss (Healthy will dominate the data), and **post-hoc calibration (temperature scaling)** is mandatory — raw softmax is overconfident, and High/Medium/Low confidence bands are meaningless without calibration.
- **Threshold tuning:** explicitly optimize decision thresholds to minimize false-negative rate, not maximize accuracy — this usually means accepting more "possible disease" false positives in exchange for near-zero missed real disease.

### 5.4 Temporal Aggregation Engine
- **Don't jump straight to a learned model** — you won't have enough video-level ground truth at launch. Start with a principled **Bayesian/log-odds aggregation**: combine per-frame predictions weighted by (detector confidence × frame quality score), more defensible than naive majority voting and handles the "one bad frame" problem.
- Once enough agronomist-verified video-level outcomes accumulate (post-pilot), train a small meta-model (gradient-boosted trees over frame-level summary features: count above threshold, mean/variance, quality-weighted mean) and A/B it against the heuristic before switching.

### 5.5 Severity Estimation
- **MVP:** proxy heuristic from detection statistics (% leaf-regions classified diseased, lesion bounding-box density) mapped to the 4 severity levels — cheap, explainable, presented as an estimate, not a precise measurement.
- **V2:** move to actual lesion-area segmentation (U-Net/DeepLabV3) to get a defensible affected-area percentage, and treat severity as **ordinal regression** (not plain multiclass) since Level 0→3 has inherent order — ordinal loss (e.g., CORAL) will outperform standard cross-entropy here.

### 5.6 LLM/VLM Explanation Layer
- **Do not fine-tune an LLM at MVP.** Use a strong instruction-following model via API, fed only the *structured JSON* output of the vision pipeline (crop, disease, confidence, severity, evidence counts) — never raw video/images — so the LLM cannot independently "diagnose" something different from what the vision pipeline determined.
- Enforce **strict output schema** (JSON), validate before rendering, and run a lightweight guardrail filter (regex/classifier) that rejects disallowed certainty language ("definitely," "100%," "guaranteed," "cured by X") and falls back to a canned template if validation fails.

## 6. MLOps / Training Infra

- **Experiment tracking:** Weights & Biases or MLflow from the first training run — don't retrofit this.
- **Dataset versioning:** DVC or LakeFS, completely separate from the production Postgres DB. The nightly export job is the bridge between "verified diagnosis in prod" and "training sample in dataset repo."
- **Frameworks:** PyTorch + Ultralytics (YOLO), timm/torchvision (classification backbones).
- **Compute:** spot/preemptible GPU instances for training (cost-sensitive startup budget); mixed precision + gradient accumulation given likely small batch sizes early on.
- **Retraining cadence:** trigger retraining either on a fixed cadence (e.g., monthly) or when N new verified samples cross a threshold — whichever comes first. Never auto-promote: every retrained model must beat the current production model on a **frozen, agronomist-curated golden test set** stratified across crop/disease/severity/region before deployment.
- **Deployment safety:** new models go through **shadow mode** first — run in parallel on live traffic, log predictions, compare against production model + agronomist verifications, only promote after a defined evaluation window.
- **Drift monitoring:** track model performance broken out by region, season, and phone-model metadata — domain shift is nearly guaranteed given India's regional and seasonal diversity, and averaged metrics will hide it.

## 7. Guardrail Implementation Details

- Confidence bands are computed **after** calibration, not from raw softmax.
- Low-confidence and out-of-taxonomy cases: add an explicit **open-set/"Unknown" handling** mechanism — softmax entropy or an energy-based OOD score — so a genuinely novel symptom pattern routes to "Unable to confidently classify" and mandatory agronomist review, rather than being force-classified into the nearest known disease class.
- GPS: store precise coordinates encrypted at rest with restricted field-level access; expose only geohash-truncated (~1km) or district-level location by default in analytics/B2B dashboards, with explicit consent flow for anything more precise.

## 8. Scenarios to Design For Explicitly

| Scenario | Mitigation |
|---|---|
| No training data at launch | Public datasets (PlantDoc > PlantVillage for domain realism) + heavy field-condition augmentation + VLM-assisted pre-labeling + pilot-farm partnership |
| Poor rural connectivity | Resumable/chunked upload, client-side background queue, server accepts partial uploads |
| Multiple diseases co-occurring in one leaf | Multi-label output per leaf region instead of forced single softmax; report top-2 if both exceed threshold |
| Genuinely novel/unlisted disease | Open-set detection → "Unknown," mandatory agronomist routing, never force-fit to nearest class |
| Insurance-fraud risk (crop insurers are a named B2B customer — real financial stakes) | Metadata integrity checks (timestamp/GPS consistency), screen-replay/moiré detection, immutable audit trail, and a hard rule that AI output alone **never** authorizes a payout — always requires agronomist sign-off |
| Class imbalance (mostly healthy frames) | Focal/weighted loss, oversampling minority disease classes, false-negative-rate-optimized thresholds |
| Regional/seasonal distribution shift | Per-region/season performance monitoring, staged shadow-mode rollout of retrained models |
| Low-end device video (compression artifacts, low res) | Server-side quality gating mirrors client checks; degrade to "insufficient evidence" rather than force a diagnosis |
| Demand spike (e.g., outbreak season) | GPU worker autoscaling, queue backpressure, honest "high demand" messaging via status endpoint |
| GPU cost control at scale | Model quantization/distillation, batched inference (Triton), tiered pipeline — cheap triage model first, full pipeline only if triage is uncertain |
| B2B/FPO multi-tenancy | Tenant-scoped RBAC / row-level security in Postgres, strict cross-tenant data isolation |
| Agronomist label disagreement | Inter-annotator agreement tracking; require 2+ agronomist consensus for "gold" labels used in retraining, single-review labels used operationally only |
| Video yields almost no usable frames | Minimum accepted-frame threshold (e.g., ≥5); below it, return "insufficient evidence, please re-record" rather than a low-quality diagnosis |
| Model version confusion / trust erosion | Every prediction record stores exact model version; shadow-mode evaluation before any promotion |

## 9. Summary Timeline

Backend Phases 0–5 map roughly onto MVP Sprints 1–8. ML Stage 0 (cold-start baseline models) should run **in parallel** with Backend Phase 1–2, not after — you need a working (even if mediocre) model to test the pipeline end-to-end before real pilot data arrives. ML Stage 1 (pilot data + domain adaptation) starts once Phase 4 (agronomist dashboard) is live, since that's the mechanism that actually produces verified labels. Everything after that is the flywheel operating on its own cadence (monthly-ish retraining, gated by shadow evaluation).

The biggest technical risk in this whole plan isn't the model architecture — it's the domain gap between whatever public data you bootstrap with and real Indian field video, plus the cold-start chicken-and-egg (need data to be good, need to be good to get farmers, need farmers for data). The pilot-partner-farm step and VLM-assisted labeling are the two levers that most directly address that.
