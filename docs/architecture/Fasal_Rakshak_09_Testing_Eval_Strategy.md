# Fasal Rakshak — Testing & Evaluation Strategy

This translates the Loopholes & Evaluation Framework document into things
that actually run in CI/CD and gate merges/releases, rather than living only
as prose intent. It's the doc referenced by every ticket's "tests added"
requirement and by `Fasal_Rakshak_07_CLAUDE_Agent_Instructions.md`'s
Definition of Done.

## 1. Test pyramid

| Layer | Location | Runs on | Purpose |
|---|---|---|---|
| Unit | `backend/tests/unit/`, mirrors `app/` 1:1 | Every PR | Individual functions/modules in isolation (quality scoring, aggregation math, guardrail regex, RBAC dependency) |
| Integration | `backend/tests/integration/` | Every PR | Full pipeline against a test DB + small fixture videos — upload through to a stored diagnosis, without hitting real GPU/LLM providers (mocked) |
| Guardrail red-team | `backend/tests/guardrail_redteam/` | Every PR touching `app/guardrails` or `app/modules/reporting`, and nightly | Adversarial structured-JSON inputs run through the explanation layer's guardrail filter |
| Data-integrity checks | `ml/data_pipeline/` (invoked via CI) | Every PR touching training data or split logic, and before every training run | Video-level split enforcement, stratification coverage |
| Component ML eval | `ml/eval/metrics/` | Every training run | Per-model metrics (below) |
| End-to-end / pipeline eval | `ml/eval/metrics/` + integration tests | Before every shadow/production promotion | Video-level diagnosis accuracy, error attribution, repeat-scan reliability |
| Release gate | CI job gating `PATCH /admin/model-versions/{id}/deployment-status` | Before shadow, and again before production | All of the above, combined into one pass/fail |

## 2. Data integrity checks (run before any model eval is trusted)

- **Video-level split assertion** (`[L7]`): a CI job (and a pre-training
  hook) queries `dataset_splits` joined to `frames.video_id` and fails if
  any video's frames appear across more than one `split` value within a
  `split_version`. This is the automated enforcement of Architecture
  Reference §4 rule 8 — never a manual claim.
- **Stratification coverage check**: for a given `split_version`, assert
  every stratum (crop × disease × severity × region × phone-model ×
  lighting bucket) present in the full dataset has a non-zero representative
  in each of train/val/test, or explicitly flag the gap if the stratum is
  too small to split (acceptable at cold-start scale, must shrink over
  time).
- **Golden set versioning check**: `golden_set_items` for `subset =
  'frozen_regression'` must be a strict superset across `set_version`
  bumps (nothing removed) — a CI job diffs consecutive versions and fails on
  an unexplained removal (an explained removal needs an ADR).

## 3. Component-level metrics (per training run, logged to W&B/MLflow)

| Component | Metrics | Script location |
|---|---|---|
| Plant/leaf/lesion detector | mAP@0.5, mAP@0.5:0.95, per-class recall (lesion class especially) | `ml/eval/metrics/detector_eval.py` |
| Crop classifier | Accuracy, confusion matrix vs. visually-similar crops, calibration curve | `ml/eval/metrics/crop_classifier_eval.py` |
| Disease classifier | Precision/recall/F1 per class, AUPRC per class, confusion matrix | `ml/eval/metrics/disease_classifier_eval.py` |
| Confidence calibration | ECE + reliability diagram, per confidence band | `ml/eval/metrics/calibration_eval.py` |
| Severity model | Quadratic Weighted Kappa, Macro F1, MAE vs. independently-collected % affected | `ml/eval/metrics/severity_eval.py` |

A training run's registered `model_versions.eval_metrics` JSONB must include
all of the metrics relevant to that model type — the `POST
/admin/model-versions` endpoint should reject a registration missing the
required keys for its `model_name` category.

## 4. End-to-end / pipeline eval

- **Video-level diagnosis accuracy** against `verified_labels` (gold only) —
  the real product metric, computed on full-pipeline output.
- **Error attribution**: `ml/eval/metrics/error_attribution.py`
  (`FR-P10-05`) re-runs classifier+aggregation with oracle detections
  substituted in and reports the gap vs. full-pipeline error, split by
  stage.
- **Aggregation ablation**: naive majority vote vs. Bayesian/log-odds vs.
  (later) learned meta-model, all against the same ground truth, before
  adopting a more complex method — required before `FR-P5-01` is marked
  done.
- **Repeat-scan / test-retest reliability**: same unchanging sample field
  scanned twice; output agreement measured. Required to pass before Phase 6
  ships (a jittery signal undermines the farmer report regardless of how
  well it's written).

## 5. Threshold & operating-point tests

- Cost-weighted confusion matrix test: given configured relative FN/FP
  costs, the chosen operating point must sit on the PR curve at (or
  documented-close-to) the cost-minimizing point — not an arbitrary
  round-number threshold.
- Alert-dismissal / override-to-Healthy rate: instrumented as a live query
  (`FR-P5-04`), reviewed on a recurring cadence, with a rising-trend alert
  wired into the standing metrics dashboard (`FR-P10-06`).

## 6. Open-set / novel-condition tests

- OOD detection AUROC: a held-out class (or a genuinely unseen
  disease/crop) is used as a proxy "unknown" set; the OOD score's
  separation from in-distribution predictions is measured and must clear a
  documented minimum before `FR-P5-03` is marked done.
- "Other" bucket precision/recall tracked explicitly; a recurring manual
  sampling task (not just an automated metric) is scheduled as part of
  `FR-P10-06`.

## 7. Guardrail / explanation-layer eval (`backend/tests/guardrail_redteam/`)

- Test cases: contradictory confidence/severity combinations, boundary
  confidence values (exactly 90%, exactly 70%), disallowed-certainty-language
  triggers ("definitely," "100%," "guaranteed," "cured by X"), malformed
  JSON, missing required fields.
- Target: **~100% pass rate**. Any failure is release-blocking for
  `app/modules/reporting` changes — not a soft warning, not a follow-up
  ticket.
- Separately, a recurring human-panel review (`FR-P6-06`) samples generated
  reports for overstated certainty the automated filter might miss — this
  is a process task, not a CI job, and its cadence is documented in
  `docs/adr/` or a runbook.

## 8. Fairness / robustness slices

Every metric in §3–§6 above is additionally reported **sliced by** region,
phone model/OS, lighting condition, and video length — not just in
aggregate. This is what the drift-monitoring dashboard (`FR-P10-03`)
surfaces continuously post-launch, and what the per-region pilot dashboard
(`FR-P8-02`) surfaces pre-launch.

Stress test fixtures (kept in `backend/tests/fixtures/`): deliberately
blurry/dark/very-short/wrong-crop/non-crop videos, and a screen-replay
recording as a proxy for the fraud-detection concern (`FR-P9-05`).

## 9. Release gate (CI-enforced)

Before `deployment_status` can move `shadow → canary` or `canary →
production` via `PATCH /admin/model-versions/{id}/deployment-status`, the
referenced `release_gate_record_id` must show all of:

1. Beats current production model on the frozen regression subset of the
   golden set.
2. No slice-level regression beyond a defined threshold (region, phone,
   lighting, video length).
3. Passes calibration/ECE checks.
4. Passes the guardrail red-team suite at ~100% (if the change touches the
   explanation layer at all).
5. Acceptable repeat-scan consistency.

If any of these is missing or failing, the API call is rejected — this is
the concrete enforcement of Architecture Reference §4 rule 12 ("no model
auto-promotes") and closes Loophole `[L12]`. Minor retrains that don't
trigger shadow mode (per `[L11]`, `FR-P10-02`) still must pass items 1–3 and
5 against the golden set before promotion; shadow mode (item-by-item
production-traffic comparison) is reserved for major model changes given
its cost at low pilot volume.

## 10. Test data & fixtures management

- Small sample videos/frames for unit and integration tests live in
  `backend/tests/fixtures/` (checked in if small enough, otherwise fetched
  from a dedicated fixtures bucket referenced by a manifest file — never the
  production/pilot video bucket).
- Golden set videos themselves are **not** duplicated into the repo; only
  `golden_set_items` manifest rows (video ID + subset + version) are
  version-controlled, pointing at the real object-storage videos.
- Red-team JSON cases for the guardrail suite are checked into
  `backend/tests/guardrail_redteam/cases/` as plain JSON fixtures, so new
  cases are easy to add as new failure modes are discovered in production.

## 11. CI pipeline stages (suggested order)

1. Lint + type-check (`ruff`, `mypy` if adopted).
2. Unit tests.
3. Data-integrity checks (§2) — only runs when training-data or split code
   changed.
4. Integration tests (mocked GPU/LLM providers).
5. Guardrail red-team suite — only runs when `app/guardrails` or
   `app/modules/reporting` changed, plus nightly on `main`.
6. (Separately, not on every PR) Release gate job, triggered manually or by
   the admin promotion endpoint's pre-check.

A PR cannot merge with any of stages 1–5 failing. Stage 6 is not a PR gate —
it's a deployment gate, invoked at promotion time.
