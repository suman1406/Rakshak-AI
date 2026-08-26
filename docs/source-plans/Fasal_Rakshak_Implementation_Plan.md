# Fasal Rakshak — Phase-Wise Implementation Plan
### From Prototype to Pilot-Ready Product

**Purpose of this document:** turn the PRD, the Backend/ML Training Plan, and the Loopholes/Evaluation Framework into a single sequenced build plan — what to build, in what order, with which guardrails baked in *at the phase they're relevant*, not bolted on afterward.

**Assumptions made** (state these back if any are wrong, and the plan can be re-sequenced):
- **Solo builder on a Mac M2 Air, 8GB unified memory / 512GB disk, no dedicated GPU.** This is the binding constraint on the whole plan — see the "Hardware Reality Check" section immediately below. "Two parallel tracks" throughout this document means alternating focus as one person, not literal simultaneous work.
- Goal is a **real working prototype first** (thin vertical slice, soybean only, one geography), then hardening toward the full architecture described in the backend plan — not a big-bang production build.
- No real field data exists on day one. This drives Phase 2's sequencing.
- "Avoid production-level disaster" means: every loophole from the evaluation-framework document is mapped to the phase where it must be addressed, not treated as a post-launch afterthought.
- Budget is bootstrap-scale: the plan leans on free/cheap cloud tiers rather than assuming dedicated infra budget, since the laptop can't absorb the heavy workloads itself.

---

## Hardware Reality Check — Mac M2 Air (8GB / 512GB)

This machine is a fine **orchestration and coding** machine and a poor **training/heavy-inference** machine. Two numbers drive every substitution below: 8GB is *unified* memory (CPU and GPU share it, so Docker + a browser + an IDE + a model already leaves little headroom), and 512GB total disk means real field video cannot be allowed to accumulate locally. Treat the laptop as the place code gets written and orchestration gets tested at small scale — not the place training or bulk storage happens.

| Task | Don't do this on the Mac | Do this instead |
|---|---|---|
| Model training (YOLO fine-tuning, EfficientNet/ViT fine-tuning — Phase 3) | Train locally via the M2's integrated GPU (MPS backend) | Run training on Google Colab or Kaggle notebooks (both offer a free GPU quota) for anything beyond a toy sanity check. Only the final trained weights (tens–hundreds of MB) need to come back to the laptop. |
| GPU inference at any real volume (Phase 4) | Run a local "GPU worker pool" | Rent a small cloud GPU on demand (RunPod/Vast.ai spot pricing) or use a serverless inference option (Modal, Replicate, HF Inference Endpoints) that spins up only when called. The Celery/queue *orchestration* logic can still live wherever the rest of the backend runs — only the actual model forward-pass needs real GPU compute. |
| Full local stack — Postgres + Redis + MinIO + Celery + FastAPI running at once (Phase 1) | Run all of it in Docker Desktop while also coding and browsing | Prefer OrbStack over Docker Desktop (noticeably lighter on Mac). Better still, offload Postgres and Redis to free-tier managed cloud services (e.g., Neon/Supabase-style Postgres, Upstash-style Redis) — check current free-tier limits since they change — so the laptop only runs what it's actively testing, not a full always-on stack. |
| Raw video/frame storage (Phase 2 onward) | Let uploaded videos and extracted frames pile up on local disk | Point object storage at a real cloud provider (Cloudflare R2 or Backblaze B2 are cost-friendly at prototype volume) from day one. Local disk should only ever hold a small scratch cache that gets cleaned up, never the accumulating archive — this matters even more once Phase 8's real pilot footage starts arriving. |
| Mobile app testing (Flutter) | Run an Android emulator + Docker + Xcode simultaneously | Test on a physical Android or iOS device over USB/wireless debugging instead of an emulator — emulators alone can consume several GB of RAM that the rest of the stack needs. |

**One practical rule that covers most of the above:** if a task needs a GPU for more than a few seconds, or needs to store more than a few hundred MB of data, it doesn't belong on the laptop — it belongs in the cloud, with the laptop just calling out to it. This is also *cheaper* than it sounds: nano/small model variants (YOLOv8n, EfficientNet-B0, MobileNetV3 — already what the backend/ML plan recommends) keep both training and inference costs low on rented compute, which is one more reason the smaller-model choices in Phase 3 aren't just a good MLOps decision, they're the right call for this hardware too.

The phase-by-phase notes below flag exactly where this substitution applies.

---

## How This Plan Is Organized

Two tracks run in parallel from Phase 2 onward, exactly as the backend plan recommends: a **Backend/Infra track** and an **ML track**. They converge at Phase 4 (Inference Integration). Each phase below has:
- **Goal**
- **Build tasks**
- **Guardrails baked in** (mapped to specific loopholes from the evaluation document, cited as `[L#]`)
- **Exit criteria** — what must be true before moving on
- **Common failure mode if skipped**

---

## Phase 0 — Prototype Spike (Week 0–2)
**Goal:** Prove the end-to-end concept works at all, before investing in real infrastructure. This phase deliberately cuts corners that later phases will fix — the point is a demo-able vertical slice, not a scalable system.

**Build tasks**
- One script/notebook, not a service: take a video file → FFmpeg frame extraction (fixed FPS is fine here) → run an off-the-shelf pretrained plant/leaf detector (YOLOv8 COCO or a public plant-disease model) → run a pretrained PlantVillage-style disease classifier → naive majority vote across frames → print a report.
- **Run this as a Colab or Kaggle notebook, not a local script on the Mac.** Free GPU quota makes iteration faster, and it sidesteps loading two vision models into 8GB of unified memory alongside a browser and IDE. Keep only a thin local script for the FFmpeg step, which is CPU-bound and fine locally.
- No database, no queue, no auth. A single Python process is enough.
- Use 10–20 sample soybean videos (can be recorded by the team walking through any accessible soybean/similar-leaf plants, or public disease video/image sets stitched into short clips).
- Manually inspect: does frame extraction produce usable frames? Does the detector find leaves at all in field-like footage (not lab close-ups)? Does the classifier output something plausible?

**Guardrails baked in**
- None yet by design — this phase is intentionally throwaway code. Its only job is to surface *whether the pretrained models are even remotely usable on field-like video* before committing to the full architecture.

**Exit criteria**
- You can point to a video and get a disease name + rough confidence out the other end, even if accuracy is bad.
- You have a documented list of where it clearly breaks (blurry frames, no leaves detected, wrong crop, etc.) — this becomes the requirements list for Phase 1's quality pipeline.

**Common failure mode if skipped:** teams build the full Celery/Postgres/GPU-worker architecture from the backend plan before ever confirming a pretrained model produces sane output on real field video — and discover in month 3 that the core detection problem is harder than expected, with a lot of now-wasted infra work.

---

## Phase 1 — Foundations & Scaffolding (Week 2–4)
Maps to Backend Plan §4 "Phase 0."

**Goal:** Lay down the skeleton so every later phase has somewhere to plug in, without over-building for scale you don't need yet.

**Build tasks**
- Repo structure: modular monolith (FastAPI) with clearly separated internal modules — `ingestion/`, `processing/`, `inference/`, `aggregation/`, `reporting/`, `agronomist/` — even before any of them do real work.
- Docker skeleton, docker-compose for local dev — but see the Hardware Reality Check above: prefer **OrbStack over Docker Desktop** on 8GB RAM, and lean toward **managed cloud Postgres/Redis free tiers** instead of running both as local containers alongside everything else you're doing. Local MinIO is fine for a handful of test videos during early dev, but shouldn't hold anything beyond that.
- Alembic migrations set up from commit #1.
- **RBAC skeleton from day one** (farmer / agronomist / admin / enterprise roles) — even if only 2 roles are used at first. Retrofitting RBAC later is the single most annoying migration to defer.
- Structured logging + a basic health-check endpoint. Sentry/Prometheus can wait for Phase 8, but the *logging shape* (structured JSON logs with request IDs) should exist now — retrofitting log structure is nearly as painful as retrofitting RBAC.
- Core DB tables stubbed out per the backend plan's schema: `users`, `farms`, `fields`, `videos`, `frames`, `detections`, `frame_diagnoses`, `video_diagnoses`, `diseases`/`crops` (taxonomy tables, not hardcoded enums), `verified_labels` (kept structurally separate from `video_diagnoses` from the start), `feedback`, `model_versions`.
- **Add `*_model_version` columns to every prediction table now**, even while there's only one model version. Adding this after you have production rows is a painful backfill.
- Add a `decision_authority` flag field on cases/diagnoses tied to any B2B/financial context, defaulting to "advisory-only." `[L13]` — this is cheap to add now and expensive to retrofit once B2B pilots start.

**Guardrails baked in**
- `[L13]` Liability surface: `decision_authority` flag exists in the schema from day one, not added reactively when the first insurer pilot signs.
- `[L7]` (preventing, not yet enforcing) — because `videos` is the unit of upload, video-level identity is preserved end-to-end, which is the precondition for correct train/val splitting later.

**Exit criteria**
- `docker-compose up` gives you a working FastAPI app, Postgres, Redis, and object storage locally, with migrations applied and RBAC-gated endpoints returning 401/403 correctly.

**Common failure mode if skipped:** RBAC and model-version columns get added after there's real user data, forcing painful migrations and backfills exactly when the team can least afford the distraction.

---

## Phase 2 — Ingestion & Video Processing Pipeline (Week 4–7)
Maps to Backend Plan §4 "Phase 1." Runs **in parallel** with Phase 3 (ML cold start) — this is the one place the two tracks should explicitly overlap, per the backend plan's own timeline note.

**Goal:** A real video goes in, quality-checked frames come out — as a durable, resumable pipeline, not a single synchronous request.

**Build tasks**
- Video job as a **state machine**, not an HTTP call: `uploaded → validating → processing → analyzing → aggregating → ready → failed`, persisted in `videos.status`.
- Resumable/chunked upload (tus protocol or S3 multipart) — treat this as mandatory, not a nice-to-have, given rural/low-bandwidth use.
- FFmpeg extraction using scene-change-aware sampling, not fixed FPS.
- Blur detection (variance-of-Laplacian), exposure histogram check, near-duplicate removal (pHash or MobileNet-embedding clustering), best-frame selection.
- Composite quality score, computed **server-side even though the client also computes one** — never trust only the on-device check.
- Wire this into Redis + Celery/RQ with two named queues from day one: `cpu_processing` and `gpu_inference` — even before GPU workers exist, the queue separation is a one-line decision now vs. a painful migration later.
- **Minimum accepted-frame threshold** (e.g., ≥5 usable frames): below it, the job returns "insufficient evidence, please re-record" instead of limping forward with 1–2 frames.
- Point object storage at a real cloud provider (Cloudflare R2 / Backblaze B2) from the start rather than local MinIO — video files add up fast against a 512GB drive, and it means Phase 8's real pilot footage never has to touch the laptop's disk at all.

**Guardrails baked in**
- Scenario table (Backend Plan §8): poor connectivity → resumable upload; low-end device video → server-side quality gating degrades to "insufficient evidence" rather than forcing a diagnosis; video yields almost no usable frames → explicit minimum-frame threshold.

**Exit criteria**
- A video uploaded over a throttled/interrupted connection completes successfully.
- A visibly bad video (dark, shaky, no plant) is correctly routed to "insufficient evidence" rather than silently proceeding.
- Job status is queryable at every stage via the status endpoint.

**Common failure mode if skipped:** the pipeline works fine on the team's Wi-Fi and fails silently or times out for the exact rural users it's built for.

---

## Phase 3 — Cold-Start ML Baseline (Week 4–9, parallel to Phase 2)
Maps to Backend Plan §5.1–§5.4, run against Phase 0's learnings.

**Goal:** Real (if imperfect) crop, detection, and disease models trained on public data, with the leakage and calibration traps from the evaluation framework closed from the first training run — not retrofitted after a bad result ships.

**Build tasks**
- **Crop classifier:** EfficientNet-B0/MobileNetV3 transfer learning on public crop-ID data. Low priority — crop is already user-selected and AI only verifies it.
- **Plant/leaf/lesion detector:** YOLOv8/YOLO11, COCO-pretrained, fine-tuned starting from **PlantDoc** (real field-condition images), not PlantVillage (lab-condition, won't transfer). Run the **seed annotation sprint**: 300–500 manually boxed images across varied lighting/angle/phone conditions (CVAT/Label Studio), agronomist-reviewed lesion boundaries.
- **Disease classifier:** EfficientNet or ViT-B/16, soybean-only for launch. Stage 0 data = PlantVillage soybean + PlantDoc soybean + any ICAR/Kaggle Indian soybean sets, combined with aggressive field-condition augmentation (motion blur, lighting jitter, background clutter compositing, JPEG artifacts) specifically to close the lab→field gap surfaced in Phase 0.
- Lock the class taxonomy for launch (e.g., Rust, Bacterial Blight, Frogeye Leaf Spot, Septoria Brown Spot, Healthy, Other/Unknown) and **validate it with an actual agronomist/ICAR reference before training starts**, not after.
- Class-weighted or focal loss (Healthy will dominate).
- **Post-hoc calibration (temperature scaling) is mandatory before any confidence band is shown to a user** — raw softmax is overconfident and the High/Medium/Low system is meaningless without it.
- Explicitly tune decision thresholds toward minimizing false negatives, but see Phase 5 for why this can't be the *only* consideration.
- Experiment tracking (W&B/MLflow) and dataset versioning (DVC/LakeFS) from the very first training run.
- **All real training runs happen on Colab/Kaggle (free GPU tiers) or a rented cloud GPU (hourly/spot), not the M2's integrated GPU.** The Mac's MPS backend can handle quick sanity-check experiments on tiny batches, but isn't a realistic engine for fine-tuning YOLO or a ViT/EfficientNet backbone in reasonable time on 8GB unified memory. Only the final weights need to sync back locally.

**Guardrails baked in**
- `[L7]` **Video-level (not frame-level) train/val/test splits, enforced automatically before every training run** — the single most common and easy-to-miss leakage bug in exactly this kind of frame-extraction pipeline. This must be a pipeline assertion, not a one-time manual check.
- Stratified sampling across crop/disease/severity/region/phone/lighting in every split, even at cold-start scale where "region" only has one or two real values — build the stratification logic now so it scales later.
- Calibration (temperature scaling) built in from the first model, not added when confidence numbers turn out to be wrong in production.

**Exit criteria**
- A frozen, versioned **golden test set** exists (small at this stage, but real) — `model_versions` table has at least one entry with recorded eval metrics.
- ECE (Expected Calibration Error) is measured and acceptable for at least the High confidence band.
- Train/val/test split is provably video-level (automated check, not a manual claim).

**Common failure mode if skipped:** the model reports 92% validation accuracy (inflated by near-duplicate frame leakage) and then performs dramatically worse on the first real pilot video, destroying team and stakeholder trust in the whole approach.

---

## Phase 4 — GPU Inference Integration (Week 8–11)
Maps to Backend Plan §4 "Phase 2" and §2 (GPU worker isolation).

**Goal:** Wire the Phase 3 models into the Phase 2 pipeline as an isolated, autoscaling worker pool — this is the one place the backend plan insists on a real architectural split, not a monolith shortcut.

**Build tasks**
- Stand up GPU workers as a separate node group / deployable service from the CPU workers, consuming the `gpu_inference` queue.
- Crop classifier → detector → disease classifier chain, storing **full probability distributions as JSONB** in `frame_diagnoses`, not just top-1 — this is what later enables re-thresholding, calibration analysis, and multi-label handling without re-running inference.
- Every prediction row writes its `detector_model_version` / `classifier_model_version`.
- Plain PyTorch-in-a-worker inference is fine at this stage — defer Triton/TorchServe until volume justifies it (flagged explicitly for Phase 9, not now).
- **On this hardware, "GPU worker pool" means a small rented cloud GPU (RunPod/Vast.ai spot pricing) or a serverless option (Modal, Replicate, HF Inference Endpoints) that the backend calls out to** — not a local process. Keep the Celery/job-state orchestration wherever the rest of the backend runs; only the actual forward-pass needs rented GPU compute, and it only needs to run when a job is actually queued.

**Guardrails baked in**
- `[L9]`-adjacent: because full distributions are stored (not just top-1), "Other/Unknown" composition can be mined later instead of being an unrecoverable black box.
- Model-version stamping on every row makes the shadow-mode evaluation in Phase 10 possible at all.

**Exit criteria**
- A video uploaded through the full pipeline (Phase 2 → Phase 4) produces stored per-frame probability distributions end-to-end, without manual intervention.
- GPU worker failure (simulate an OOM) leaves the job in a recoverable `failed` state with a clear error, not a stuck/silent job.

**Common failure mode if skipped:** GPU and CPU work share a pool, so either GPU nodes sit idle waiting for FFmpeg jobs (expensive) or inference gets starved during upload spikes (bad user experience) — exactly the failure mode the backend plan calls out.

---

## Phase 5 — Aggregation, Severity & Confidence (Week 11–13)
Maps to Backend Plan §5.4–§5.5 and §7; addresses evaluation-framework §4 and loophole 10.

**Goal:** Turn per-frame predictions into one trustworthy video-level diagnosis — and resolve the false-negative-vs-alarm-fatigue tension explicitly, rather than leaving it as an unstated tradeoff.

**Build tasks**
- **Temporal aggregation:** principled Bayesian/log-odds aggregation weighted by (detector confidence × frame quality score) — not naive majority voting, and not a learned meta-model yet (there isn't enough video-level ground truth for that until after Phase 8).
- **Severity:** MVP heuristic from detection statistics (% diseased leaf-regions, lesion density) mapped to 4 ordinal levels — cheap and explainable, explicitly presented to users as an estimate.
- **Open-set/"Unknown" handling:** softmax entropy or energy-based OOD score routes genuinely novel symptom patterns to "Unable to confidently classify" + mandatory agronomist review, instead of force-classifying into the nearest known disease.
- **Cost-weighted threshold selection**, not blind false-negative minimization: assign explicit relative costs to false negatives vs. false positives and pick the operating point on the PR curve deliberately. Instrument **alert-dismissal / override-to-Healthy rate** as a live metric from day one so alarm fatigue is visible before it does damage.
- Confidence bands (High ≥90% / Medium 70–89% / Low <70%) computed strictly from **calibrated** probabilities.

**Guardrails baked in**
- `[L10]` Threshold selection is cost-weighted from the start, with alert-dismissal rate tracked as a first-class live signal, not discovered as a problem after farmers have already learned to ignore the app.
- `[L9]` seed: routing genuinely novel cases to "Unknown" + agronomist review, rather than the nearest known class, is what keeps "Other" from becoming an unmonitored dumping ground later.

**Exit criteria**
- Repeat-scan test: scan the same (unchanging) sample field/plants twice in quick succession and confirm output agreement is high — this is the test-retest reliability check from the evaluation framework, and it should pass *before* Phase 6, since a jittery signal will make the farmer report look unstable and untrustworthy regardless of how well the report is written.
- A held-out "genuinely different" plant/leaf image correctly routes to "Unknown" rather than a confident wrong disease.

**Common failure mode if skipped:** thresholds get tuned once, purely for recall, at launch — and nobody notices six months later that dismissal rates have crept toward 80% because every "possible disease" alert has trained farmers to stop opening the app.

---

## Phase 6 — Explanation Layer & Farmer Report (Week 13–15)
Maps to Backend Plan §5.6 and evaluation-framework §6.

**Goal:** Turn structured diagnosis JSON into a farmer-readable report that cannot overstate certainty, even under adversarial or edge-case inputs.

**Build tasks**
- LLM/VLM API call fed **only the structured JSON** (crop, disease, confidence, severity, evidence counts) — never raw video/images — so the LLM cannot independently "diagnose" something the vision pipeline didn't determine.
- Strict output schema (JSON), validated before rendering.
- Guardrail filter (regex/classifier) that rejects disallowed certainty language ("definitely," "100%," "guaranteed," "cured by X") and falls back to a canned template on any validation failure.
- Farmer report screen: disease name, confidence band, severity, affected-plant estimate, "what we found," "what to do now" (inspect more plants / close-ups / consult agronomist) — explicitly no autonomous pesticide prescriptions at this stage.

**Guardrails baked in**
- Evaluation-framework §6: build the **red-team test set** now (contradictory confidence/severity combos, boundary confidence values, disallowed-language triggers) and run it against the guardrail filter before this phase is considered done. Target ~100% pass rate; treat any failure as blocking, not a soft warning.
- Periodic small-panel human review of generated reports for clarity and for overstated certainty the automated filter might miss — schedule this as a recurring task, not a one-time check.

**Exit criteria**
- Guardrail red-team suite passes at ~100%.
- A human reviewer reads 10 generated reports and confirms none imply certainty the underlying confidence band doesn't support.

**Common failure mode if skipped:** the LLM occasionally produces a fluent, confident-sounding sentence like "this is soybean rust" with no hedging, for a Medium- or Low-confidence case — and a farmer acts on it as if it were certain.

---

## Phase 7 — Agronomist Dashboard & Verified-Label Loop (Week 15–18)
Maps to Backend Plan §4 "Phase 4"; addresses loopholes 2, 8, and the dataset-architecture section.

**Goal:** Stand up the mechanism that actually produces trustworthy training labels — this is the hinge the entire data-flywheel strategy depends on, so it needs its own bias checks built in, not assumed away.

**Build tasks**
- Verification endpoint writing to `verified_labels`, structurally separate from `video_diagnoses` — never mixed.
- Case queue **prioritized by low confidence first** — that's where agronomist time adds the most value.
- **Speed up annotation with AI-assisted pre-labeling** (VLM drafts candidate labels, agronomist corrects) — but only after the anchoring-bias mitigation below is in place, not before.
- Nightly export job pushing verified samples into DVC/LakeFS using the hierarchical structure: Crop → Disease → Severity → Region → Crop Stage → Image/Video.
- Require **2+ agronomist consensus** for labels used as "gold" in retraining; single-review labels are used operationally only, not for training.

**Guardrails baked in**
- `[L2]` **Blind re-labeling program**: periodically re-label a sample with the AI suggestion hidden, and measure agreement rate against the anchored labels. Set this up as a recurring scheduled job from the moment AI-assisted pre-labeling goes live — if agreement is suspiciously high, it's a signal agronomists are rubber-stamping, not verifying.
- `[L8]` Severity ground truth: during any pilot activity in this phase, have agronomists also provide an **independent visual percentage-affected estimate**, separate from the detector's own output — this is what makes severity validation non-circular later.
- Inter-annotator agreement tracked explicitly, feeding the 2+ consensus rule above.

**Exit criteria**
- At least one full cycle of: case flagged → agronomist verifies → nightly export → dataset repo updated, works without manual intervention.
- First blind-relabeling run has been executed and agreement rate is documented (even if it's the first data point in a trend, not yet actionable).

**Common failure mode if skipped:** "verified" labels quietly become a mirror of the VLM's own blind spots, and the model appears to improve on paper while actually just converging toward its own pre-labeling biases.

---

## Phase 8 — Pilot Program & Real Field Data Collection (Week 18–24)
Maps to Backend Plan §5.3 "Stage 1" and directly addresses loopholes 1, 3, 4, 5 — the ones evaluation framework flags as the biggest strategic risk to the whole data-flywheel thesis.

**Goal:** Get real Indian field video with agronomist ground truth — deliberately structured to avoid making the model look better than it will actually perform in the wild.

**Build tasks**
- Partner with 5–10 real farms / an FPO / an agri university trial plot for supervised video collection.
- **Deliberately recruit at least a few "worst-case" sites**: poor lighting, older/cheaper phones, dense weedy fields — not just the most cooperative, well-maintained plots.
- **Deliberately spread pilot sites across more than one region/state** rather than letting geography be incidental to convenience — track per-region performance as a first-class pre-launch metric, not a post-launch discovery.
- Budget for **quarterly physical field visits or lab pathogen confirmation** on a small random sample, as a ground-truth check independent of the video pipeline itself (video-based agronomist review alone only confirms internal consistency, not real-world correctness).
- If any commercially-linked party (insurer, input company) is involved at this stage, **tag every verified label with its source channel** now — retrofitting this tag after data is mixed into the training set is not recoverable.
- Fine-tune the Stage 0 model on this newly collected pilot data (domain adaptation) — this is the update disproportionately valuable for closing the lab→field gap.

**Guardrails baked in**
- `[L1]` Worst-case site inclusion, by design, not convenience.
- `[L3]` Quarterly independent ground-truth check scheduled, not left implicit.
- `[L4]` Source-channel tagging live before any commercially-linked data enters the pipeline.
- `[L5]` Regional performance tracked and reported before launch decisions are made, with pilot effort deliberately weighted toward underrepresented regions.

**Exit criteria**
- Pilot dataset includes at least 2 distinct regions and at least one deliberately "hard" site.
- Per-region performance breakdown exists and is reviewed by the team before any go/no-go launch decision.
- At least one round of independent physical-verification data exists to sanity-check video-based agronomist labels.

**Common failure mode if skipped:** the golden test set is built entirely from clean, cooperative pilot farms; launch metrics look great; real users in messier conditions and other regions get a materially worse experience, and the team doesn't find out until complaints roll in.

---

## Phase 9 — Field/B2B Analytics & Scale Hardening (Week 24–30)
Maps to Backend Plan §4 "Phase 5."

**Goal:** Only build this once Phase 8 has produced enough real usage to justify it — this phase is explicitly about scale, not core product correctness.

**Build tasks**
- Field Health Score rollups, Field Health Map, B2B dashboard APIs with the Disease → District → FPO → Farm → Field → Video Evidence drill-down.
- Read replica or lightweight OLAP layer (ClickHouse/DuckDB) for aggregate queries over `frame_diagnoses` once volume makes OLTP Postgres slow — explicitly *not* needed at pilot scale, don't build it early.
- GPU autoscaling policies, load testing, cost-per-analysis dashboard (instrument this as a named business metric now, not later).
- Tenant-scoped RBAC / row-level security for multi-tenant B2B/FPO data isolation.
- Migration path to Triton/TorchServe if per-inference cost or latency now justifies dynamic batching.
- GPS handling: encrypted precise coordinates with restricted access; geohash-truncated (~1km) or district-level location exposed by default in analytics, with explicit consent flow for anything more precise.

**Guardrails baked in**
- `[L13]` Enforce `decision_authority` in the backend for any B2B case tied to a financial action (insurance payout, loan decision): the flag from Phase 1 now actually gates workflow — AI output alone cannot authorize a payout, agronomist sign-off is required and logged.
- Metadata integrity checks (timestamp/GPS consistency) and screen-replay/moiré detection for the insurance-fraud scenario, given crop insurers are a named B2B customer with real financial stakes.

**Exit criteria**
- A B2B dashboard demo can drill from district-level aggregate down to a specific video's evidence, correctly scoped to that tenant only.
- A simulated "financial decision" case is provably blocked from proceeding without an agronomist sign-off recorded.

**Common failure mode if skipped:** an insurer or bank pilot goes live, a false negative contributes to a bad downstream decision, and "AI indication ≠ confirmed diagnosis" UI copy turns out to be the only thing standing between the product and real liability exposure.

---

## Phase 10 — Evaluation Gate, MLOps & Governance (Ongoing from Phase 3 onward)
This isn't a phase that ends — it's the process that governs every model release from Phase 3 forward. Maps to evaluation-framework §2–§10 and Backend Plan §6.

**Standing infrastructure**
- **Golden set governance:** a frozen regression subset that must never regress, plus a periodically refreshed subset (quarterly, versioned, with a changelog) for measuring real progress.
- **Shadow mode**, used selectively: define a minimum sample size for conclusions up front, and reserve full shadow evaluation for major model changes only `[L11]` — smaller updates gate on the golden set alone, since shadow mode doubles GPU inference spend and is slow at low pilot volume.
- **Drift monitoring** broken out by region, season, and phone-model metadata — averaged metrics will hide exactly the regional inequity Phase 8 was built to prevent.
- **Release gate**, applied before shadow mode and again before full promotion — a model must: beat production on the frozen regression set, show no slice-level regression beyond a defined threshold, pass calibration/ECE checks, pass the guardrail red-team suite at ~100%, and show acceptable repeat-scan consistency.

**Standing metrics dashboard**
- False-negative rate, always paired with false-positive/alert-dismissal rate.
- Agronomist override rate, split by top-1 vs. top-2 match.
- Cost per correctly-verified diagnosis.
- "Other/Unknown" bucket volume and composition, periodically manually sampled.
- Blind vs. anchored labeling agreement rate.
- Source-channel comparison (commercially-linked vs. neutral verified data).

**Guardrails baked in**
- `[L12]` Golden set is versioned (frozen regression + refreshed subset), not a single static file that quietly goes stale or a constantly-changing one that makes release comparisons meaningless.
- `[L6]` End-to-end/error-attribution analysis run whenever a component metric improves but product-level accuracy doesn't move as expected — re-run classifier+aggregation with oracle detections substituted in to isolate which stage is actually responsible.

**Exit criteria for "governance is live":** a new model cannot reach production without passing through this gate — enforced as a checklist in the deployment process, not a document people are trusted to remember.

---

## Cross-Cutting: Security & Privacy (build alongside Phase 1, enforced by Phase 9)
- Encryption in transit and at rest from Phase 1.
- GPS: precise coordinates encrypted with restricted field-level access; geohash/district-level exposure by default (Phase 9).
- Consent-based data collection, audit logs, and data retention controls (S3 lifecycle policies set in Phase 1, enforced through the pipeline).

---

## Suggested Sequencing at a Glance

| Weeks | Backend/Infra Track | ML Track |
|---|---|---|
| 0–2 | — | Phase 0: Prototype spike |
| 2–4 | Phase 1: Foundations | — |
| 4–9 | Phase 2: Ingestion pipeline | Phase 3: Cold-start models (parallel) |
| 8–11 | Phase 4: GPU inference integration (both tracks converge) | |
| 11–13 | Phase 5: Aggregation, severity, confidence | |
| 13–15 | Phase 6: Explanation layer & farmer report | |
| 15–18 | Phase 7: Agronomist dashboard & verified-label loop | |
| 18–24 | Phase 8: Pilot program & real field data | |
| 24–30 | Phase 9: Field/B2B analytics & scale hardening | |
| Ongoing from wk 9 | Phase 10: Evaluation gate & governance | |

This is a realistic-effort estimate, not a hard commitment — the phases matter more than the week numbers. As a solo builder, "parallel tracks" in this table means alternating focus across a week, not literally running both at once, so budget roughly **1.5–2x** the week numbers above. Leaning on the cloud substitutions from the Hardware Reality Check keeps the laptop from being the bottleneck for training or storage, which is where solo timelines usually blow out hardest. If timeline pressure forces further compression, compress **within** a phase (smaller pilot, fewer disease classes, one region) rather than skipping a phase's guardrails outright — nearly every "production disaster" in the loopholes document comes from a guardrail that was skipped, not a feature that shipped late.

## Single Most Important Sequencing Rule

Do not let the **data-flywheel narrative** (more farmers → more data → better models) become an excuse to skip Phase 8's deliberate-hard-site and cross-region recruiting. That loophole compounds itself the longest and is the hardest to unwind after launch — every other loophole in this plan is a data-quality or process fix; that one is a structural one.
