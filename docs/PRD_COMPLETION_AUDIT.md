# PRD completion audit and implementation record

Date: 2026-09-09. Source: `docs/source-plans/Fasal_Rakshak_AI_PRD.md`.

## Branch inventory

- Main baseline: `7edbfc3`; web, Flutter, FastAPI, review workflow and deployment foundation.
- `pipeline` and `backend-model`: already ancestors of main; no unique commits to integrate after fetching origin.
- `mvp-completion`: `51022fb`; four additional commits add YOLO and EfficientNet weights, disease catalog and action-item persistence. Integrated with a merge commit into `codex/prd-completion`.

## Baseline evidence

Full backend suite: 65 passed in an isolated Docker container, including the newly integrated branch tests. These tests do not establish model accuracy or a working farmer journey.

## Confirmed gaps under remediation

- Generic YOLO detections are mislabeled as leaves; empty detections synthesize a leaf.
- Aggregation multiplies correlated frame evidence into inflated confidence and counts all usable frames as supporting the winning disease.
- Bacterial blight is incorrectly mapped to Sudden Death Syndrome.
- Processing retry deletes parent frame rows before dependent predictions.
- Model errors are swallowed as ordinary unknown predictions.
- Website lacks a farmer workspace; mobile field setup tells users to use the backend.
- Upload dispatch, storage, recovery, consent and full client journeys require integration verification.

## Acceptance boundary

Complete the PRD MVP and supporting basic history, field management, expert review and organization analytics. Phase 2/3 features explicitly deferred by the PRD remain later work. Scientific accuracy, trained plant detector suitability, field calibration, physical mobile testing and production infrastructure must be backed by real evidence; code tests cannot substitute for these.

This is an in-progress record, not a release certification.

## Integration checkpoint

- User approved the practical accessible design direction and use of existing models, with model improvement deferred.
- Added the farmer web journey and mobile field setup/profile editing; fixed mobile registration compilation and Android internet permission.
- Whole-frame classifier observations are now explicitly recorded as `frame_region` with `whole-frame-observation-v1` provenance. Generic COCO objects are not renamed leaves.
- Replaced confidence inflation with a conservative quality-weighted mean; unknown observations remain part of aggregation; supporting counts reflect the winning class.
- Corrected bacterial blight identity, independent-frame gating, dependency deletion order on retry, advisory action checks and swallowed model failures.
- Added authorized video playback and retries; replaced placeholder expert evidence with protected media delivery.
- Connected expert correction labels and independent severity input; scoped review history and independent-farmer review requests.
- Removed fabricated settings statistics and the unused file-size-based diagnosis adapter.
- Full backend suite reached 69 passing before two additional scope/migration tests passed; retiring two tests of the obsolete adapter leaves the suite count unchanged. Re-run at final release.
- Web TypeScript passed. A production build passed before the latest expert/settings edits; rebuild at final release. Flutter analysis and existing mobile test passed.
- Actual EfficientNet checkpoint loaded offline with all five expected classes. This is compatibility proof, not an accuracy evaluation.

## Remaining work

Durable cloud storage, session/retention controls, organization record accuracy and exports, full integration/browser/device/build tests, operational release configuration and final commits remain in progress.
