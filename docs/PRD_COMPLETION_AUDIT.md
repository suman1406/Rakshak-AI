# PRD implementation and acceptance record

Date: 2026-09-09 · Release: 0.2.0 · Branch: `codex/prd-completion`.
Source of truth: `docs/source-plans/Fasal_Rakshak_AI_PRD.md`.

## Scope decisions

The owner approved a practical, accessible redesign and explicitly chose to use the available models/scripts now, with model improvement deferred. This release implements the MVP engineering and supporting account, history, review, organization and operations flows. PRD Phase 2/3 features remain later product work. A successful engineering test is not evidence of model accuracy or a real-farm pilot.

## Repository audit

| Branch | Finding |
| --- | --- |
| `main` at `7edbfc3` | Existing web, Flutter, API, schema and partial role workflows |
| `mvp-completion` at `51022fb` | Four unique commits with EfficientNet classifier, generic YOLO weights, scripts and report persistence; merged into the implementation branch |
| `pipeline` | Already an ancestor of main after fetching; no unique integration required |
| `backend-model` | Already an ancestor of main after fetching; no unique integration required |

## Implemented MVP engineering

| PRD area | Implementation and evidence |
| --- | --- |
| Farmer journey, capture (§6–7) | Farmer web and Flutter field creation, field selection, upload consent, 10–30 second / 100 MB validation, capture instructions, actual server progress, retry and retake states |
| Video engine (§8) | FFmpeg/OpenCV validation, independent frame sampling, blur/exposure filtering, selected evidence persistence, Celery worker state transitions and idempotent derived-row replacement |
| Crop/detection (§9–10) | Soybean selection is explicit. Generic COCO classes are not relabeled leaves. Whole-frame fallback is recorded as `frame_region` with provenance; crop verification and trained leaf detection remain deferred model work |
| Disease classifier (§11) | Supplied five-class EfficientNet loads with strict checkpoint compatibility; bacterial blight taxonomy corrected; inference failures do not masquerade as ordinary uncertainty |
| Aggregation/confidence (§12,14) | Quality-weighted temporal mean, unknown evidence retained, winning-class support counts, 90/70 confidence bands, stored full probability distribution and actual version provenance |
| Severity (§13) | Supplied heuristic pipeline integrated; visual severity and affected-area signals are explicitly unvalidated, not farm-wide plant measurements |
| Advice/safety (§15–16,33) | Guarded generated advice when a provider is configured; deterministic conservative templates otherwise; uncertainty/retake/healthy states and no autonomous pesticide prescription |
| Farmer report (§30) | Saved assessment, explanation, next steps, protected evidence frames and web original-video playback; feedback and expert-review request; completed human assessment returned to the farmer |
| Expert review (§22) | Authorized queue, case evidence, claim protection, correction/severity/notes persistence, completed review history and CSV, separate AI and human records |
| Dataset pipeline (§21,23–26) | Consent-filtered expert-label manifest exporter, field-disjoint splits, private media references and provenance; existing training scripts retained. Retraining, calibration and field evaluation deferred by owner |
| Organization dashboard (§31) | Scoped farms/fields/scans, latest indications, filter-consistent counts and chart, evidence drilldown, CSV export and organization capture route; unvalidated health scores removed |
| Account lifecycle | Farmer registration, reviewed expert/organization applications, serialized approval, token refresh, password change, global session revocation, profile editing and optional training consent |
| Privacy/storage (§32) | Private S3-compatible storage across API/worker hosts, authorized media routes, automatic expiry, per-host cache pruning, audit records, dry-run legacy local-media migration |
| Operations | Rootless container, PostgreSQL migrations, Redis queue, worker time limits and stale-work recovery, one retention scheduler, readiness checks, shared deployment environment, locked runtime and repeatable CI |
| Public/support workflows | Refreshed landing/about/guide/pricing/privacy/onboarding pages; published plan selection retained into application; contact form persists to a protected administrator inbox |

## Redesign

Shared olive, warm stone and sunflower identity; bundled Public Sans on web; consistent mobile theme and typography; responsive role navigation; Radix navigation dialog, accordion and button primitives; clear forms, focus states, errors and empty states; actual private images in report viewers; accessible field-indication bars and record tables. Marketing imagery is explicitly illustrative and separate from scan evidence. See `DESIGN.md`.

## Validation evidence

- Backend: final full unit/integration suite passed 86 tests, including legacy media migration and production-secret regression cases. The release validation record is in `RELEASE_0_2_0.md`.
- Actual model smoke: synthetic 11-second video → 28 extracted frames → 15 selected observations → stored unknown assessment with five-class probabilities and model provenance. Original media retrieval succeeded across separate API/worker filesystems; unauthenticated retrieval returned 401.
- PostgreSQL role smoke: pending expert login denied; simultaneous approval returned one 200 and one 409; requested case became accessible to the assigned expert; review appeared in farmer and expert reports; separate organization could not access private farmer video (404).
- Web: TypeScript and optimized Next.js builds passed; no-mock integration contract passed. Browser checks covered public rendering at narrow width, contact submission/receipt, administrator inbox/close, protected farmer evidence, and organization field creation/selection.
- Mobile: analyzer passed; four tests passed including narrow-screen large-text login validation and required registration consent. Android debug APK builds passed; final artifact version is tracked in the release record.

## Explicitly not established by these checks

Production deployment, paid infrastructure capacity, cloud backup restore, email/SMS/WhatsApp providers, mobile store signing, physical camera behavior, iOS builds, GPU performance, field-model accuracy/calibration and pilot outcomes require their own validation. No Android device or emulator was connected during these checks; Windows cannot establish an iOS build.

PRD Phase 2/3 items—regional languages, real-time camera guidance, multiple crops/diseases, validated health score, progression, agronomist marketplace, spatial/weather intelligence—are not represented as complete. Basic saved history is implemented ahead of the broader Phase 2 history features.
