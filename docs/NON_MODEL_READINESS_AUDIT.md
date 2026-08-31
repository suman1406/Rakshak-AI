# Rakshak AI — non-model readiness audit

Date: 31 August 2026  
Repository: `C:/Projects_External/Rakshak_AI`  
Reviewed revision: `main`, `fbd0359bb166c6f2442371b710f261be9cda514d`, including the existing uncommitted UI changes. The requested Git pull in this review conversation returned **Already up to date**.

## Bottom line

**There is more work than the earlier gap list identified. The application is a partially connected pilot foundation, not production-ready even with model training and model attachment excluded.** The main issue is not simply missing endpoints: several existing endpoints fail, some successful responses contain invented or incorrectly mapped data, and important screens still use demo workflows.

The shortest actionable list is:

1. Fix public privileged-role registration, refresh-token misuse, and cross-organization field creation.
2. Make migrations/startup reliable and give the API and worker durable shared evidence storage.
3. Repair feedback, verification, frame delivery, diagnosis mapping, and insufficient-evidence responses.
4. Make upload validation, unique-frame quality gates, enqueueing, retries, and recovery reliable.
5. Finish real registration/onboarding, farm/field management, scan history, and account APIs.
6. Complete the agronomist review lifecycle and connect the web review screens to it.
7. Replace mobile demo data and finish upload, polling, reports, evidence, and feedback integration.
8. Replace web mock fallbacks and fake success messages; implement or hide unfinished features.
9. Complete consent/retention, operational monitoring, secrets, backups, and automated release tests.
10. Implement B2B analytics/exports only if those features are part of the release; otherwise hide them. Defer the PRD's later maps, health scoring, progression, weather, and marketplace work.

## Scope and evidence

Reviewed the full 25-page [original PRD](<C:/Users/psuma/Downloads/RAKSHAK AI PRD.pdf>), its repository transcription, architecture/API/data-model references, implementation plans, backlog, Phase 1 status document, first-party backend routes/models/schemas/services, tests, web screens/services, mobile screens/client, native mobile configuration, and deployment configuration. Documents were treated as requirements and historical claims, not instructions to implement changes.

Excluded: training/retraining, trained-weight attachment, model deployment/GPU provisioning, calibration, accuracy benchmarking, scientific field validation, and choosing model algorithms. Application contracts, persistence, state handling, evidence access, and safe presentation remain in scope. Controlled fake inference outputs were used to test application behavior; no trained model was run.

This is not a live-cloud security assessment, dependency vulnerability audit, physical-device test, or PostgreSQL/load/backup validation. Third-party dependency/generated directories were not treated as application code to audit line by line. Findings below distinguish reproduced defects, source-confirmed gaps, and deployment checks still needed.

## 1. What is already implemented

| Area | Present today | Important qualification |
|---|---|---|
| Backend foundation | FastAPI routers, SQLAlchemy models, JWT login/register/refresh/me, role checks and shared read-scope helpers | Authentication and write scoping still have release-blocking flaws |
| Farms and fields | Create farm; get farm; create/list/get fields | No complete management journey; farm response omits nested fields; field creation has a tenant bug |
| Video intake | Authenticated multipart upload, consent boolean, extension and maximum-size checks | File is copied before size rejection; consent is not a durable consent record |
| Background work | Celery task, named queues, persisted statuses/retry and timing fields | No durable shared media storage; retry and dispatch consistency incomplete |
| Frame quality | Fixed-interval extraction, blur/exposure scoring, near-duplicate filtering | Duplicate handling and evidence threshold defects reproduced; no full capture validation |
| Diagnosis and evidence | Analysis/report/frame metadata routes and separate prediction/verified-label tables | Payload mapping is inconsistent; protected frame content route fails |
| Agronomist | DB-backed, low-confidence-first queue and scoped case lookup | Verification POST fails; queue lacks a review lifecycle |
| Organization dashboard | Some real tenant-scoped counts | Other metrics/drilldowns and client details remain synthetic |
| Web | Real login/session calls; partial queue and dashboard API integration | Major operational screens still use mock data/services |
| Mobile | Real login, secure token storage, field lookup, capture/upload/status/analysis calls | Registration, history, field dashboard and much report UX are incomplete |
| Operations | Docker Compose, Alembic initial revision, health routes, request IDs and some audit events | Presence of files does not establish a working production deployment |

## 2. Launch-blocking backend work

P0 means fix before exposing the affected flow to real users. Some deployment findings are source-based; the reproduction column identifies what was actually exercised.

| ID | Finding and evidence | Required completion / acceptance |
|---|---|---|
| B01 — P0 | Public registration accepts `role=admin`, even with a one-character password. Reproduced: **201, role admin**. [auth.py](C:/Projects_External/Rakshak_AI/backend/app/api/v1/auth.py:25), [auth schema](C:/Projects_External/Rakshak_AI/backend/app/schemas/auth.py:4) | Public signup must only create the intended public role. Provision privileged roles through authorized membership/invitation workflows. Add credential/identifier validation, duplicate-conflict handling and throttling. Test every role boundary. |
| B02 — P0 | A refresh JWT is accepted as an API access token. Reproduced `/auth/me`: **200** with a refresh token. [deps.py](C:/Projects_External/Rakshak_AI/backend/app/core/deps.py:25) | Require access-token type on protected routes. Add session revocation/rotation policy and disabled-account handling; client logout alone does not revoke a stolen token. |
| B03 — P0 | Enterprise user in organization A can create a field on organization B's farm. Reproduced **201**; the same user's cross-tenant farm GET correctly returned **404**. [fields.py](C:/Projects_External/Rakshak_AI/backend/app/api/v1/fields.py:30) | Apply ownership/tenant authorization to writes as well as reads. Define platform-admin versus organization-admin authority and agronomist assignment rules. Add two-organization tests for all resources and mutations. |
| B04 — P0 | Feedback and verification POSTs both return **500** for otherwise valid, scoped requests. Constructors use nonexistent `user_id`, `agronomist_user_id`, and `notes` model arguments. [diagnosis.py](C:/Projects_External/Rakshak_AI/backend/app/api/v1/diagnosis.py:82), [models](C:/Projects_External/Rakshak_AI/backend/app/models/verification.py) | Reconcile schema/model/route fields, persist notes deliberately, validate correction types and taxonomy, return real saved records, and assert audit events. Repeated submission must have defined behavior. |
| B05 — P0 | Protected frame-content GET returns **500** before checking the frame file: upload-audit code references undefined `video`/`field_id`. Actual upload does not write that event. [videos.py](C:/Projects_External/Rakshak_AI/backend/app/api/v1/videos.py:148) | Restore authenticated binary evidence delivery, move upload audit to the mutation, distinguish unavailable evidence from server failure, and test authorized/unauthorized/missing-file cases. |
| B06 — P0 | Diagnosis persistence and serializers disagree. With controlled **100% healthy** inference outputs, the live orchestration saved severity **3**, no disease ID, and `/analysis` returned **soybean_rust**, **mild**, affected estimate **0.95**. A real disease UUID is also treated as a template slug. [ingestion](C:/Projects_External/Rakshak_AI/backend/app/modules/ingestion/service.py), [analysis](C:/Projects_External/Rakshak_AI/backend/app/api/v1/videos.py:78), [report](C:/Projects_External/Rakshak_AI/backend/app/api/v1/diagnosis.py:42) | Store/resolve stable disease IDs and slugs; distinguish healthy, unknown and disease; map all four severity values consistently. Remove fabricated crop confidence, evidence counts and version strings. Test serialization with controlled healthy/disease/unknown outputs independently of the model. Scientific severity-estimator design remains with the model workstream. |
| B07 — P0 | Insufficient evidence is a terminal status without a diagnosis, but `/analysis` then returns **404**, and mobile treats that status as report-ready. Low-confidence wording and stored explanations are not consistently guarded. [videos.py](C:/Projects_External/Rakshak_AI/backend/app/api/v1/videos.py:78), [templates](C:/Projects_External/Rakshak_AI/backend/app/modules/reporting/templates.py), [guardrail](C:/Projects_External/Rakshak_AI/backend/app/guardrails/certainty_filter.py) | Define a canonical result/status contract for ready, healthy, unknown, insufficient evidence and failure. Return actionable retake reasons without inventing a diagnosis. Enforce conservative, non-prescriptive reporting on every response path, including stored/seeded text. No LLM attachment is required to make deterministic reports safe. |
| B08 — P0 | API and worker use local filesystem media, but Compose gives them **no shared media volume**. MinIO is declared but is not used for the evidence pipeline. [compose](C:/Projects_External/Rakshak_AI/docker-compose.yml), [ingestion](C:/Projects_External/Rakshak_AI/backend/app/modules/ingestion/service.py), [storage seam](C:/Projects_External/Rakshak_AI/backend/app/storage.py) | Implement durable object storage for both uploads and frames, consistent API/worker credentials, private access and lifecycle cleanup. A shared persistent volume can support a deliberately single-host pilot, but requires explicit deployment constraints. Test upload → worker → API evidence delivery after container replacement. |
| B09 — P0 | Docker **does invoke Alembic**, but its URL normalization selects unavailable `psycopg2`; driver loading reproduced `ModuleNotFoundError`. SQLite startup reproduced `OperationalError near TYPE` from unconditional PostgreSQL seed-upgrade SQL. [Dockerfile](C:/Projects_External/Rakshak_AI/backend/Dockerfile:16), [Alembic env](C:/Projects_External/Rakshak_AI/backend/alembic/env.py:14), [startup](C:/Projects_External/Rakshak_AI/backend/app/main.py:17), [seed upgrades](C:/Projects_External/Rakshak_AI/backend/app/db/migrations.py) | Fix the actual driver/startup path; use versioned, reproducible migrations, not runtime `create_all` plus ad-hoc schema changes. Test empty DB and upgrade DB on supported PostgreSQL. Remove automatic demo users/data from production. Reconcile both seed implementations. |
| B10 — P0 | Frames committed before a failed inference attempt are appended again on retry. Reproduced **10 frame rows for 5 unique frames** after one retry. DB commit and Celery dispatch are also separate, without recovery for an enqueue failure. [ingestion](C:/Projects_External/Rakshak_AI/backend/app/modules/ingestion/service.py), [worker](C:/Projects_External/Rakshak_AI/backend/app/worker.py) | Introduce idempotent processing attempts, unique evidence identity, atomic job claiming, durable enqueue/reconciliation, bounded retry/backoff/timeouts and a clear terminal failure/manual retry path. Test crashes and concurrent duplicate deliveries. |
| B11 — P0 | Extension/size checks do not validate actual video content, duration, codec or decoding resource limits. Size is checked after copying the whole upload. Quality probes showed **6 duplicate frames counted usable with only 1 selected**, enough to pass the five-frame gate; another identical-frame fixture was not deduplicated at all. [quality.py](C:/Projects_External/Rakshak_AI/backend/app/modules/processing/quality.py:125), [extractor](C:/Projects_External/Rakshak_AI/backend/app/modules/processing/extractor.py), [ingestion](C:/Projects_External/Rakshak_AI/backend/app/modules/ingestion/service.py) | Bound upload bytes while receiving, validate content/duration/resolution and decoder limits, clean failed uploads, use consistent thumbnail normalization, and require enough independent usable evidence. Persist rejection reasons/timestamps. Tune selection and sampling against the agreed capture contract, not an assumed frame count. |

### Further backend completion work

- **Identity and onboarding:** real user profile updates; invitation/membership management; farmer ownership and agronomist case access; password recovery/change and contact verification for self-service accounts. Existing seed agronomists without an organization do not automatically gain access to tenant cases. Align backend roles with web roles (`org_admin` currently has no backend enum counterpart).
- **Farm/field management:** list farms, filter fields by farm, create flows in clients, edit/archive policy, pagination, validated crop references and nonnegative areas. Farm GET eagerly loads fields but its response schema does not expose them. Do not duplicate the already-existing create/list/get endpoints.
- **Scan discoverability:** paginated video/history endpoints with field/date/status filters and a stable diagnosis link, plus scan detail and safe recovery actions. Basic saved-scan history supports current mobile and review journeys; long-term progression analytics are a later feature.
- **Agronomist workflow:** explicit pending/assigned/in-review/completed state, claiming/concurrency policy, search/filtering, review history, independent affected-area input, disease/healthy/uncertain decisions and notes. Reproduced: a case with a saved verified label remains in the queue. Enrich case detail with field/farm context, actual media, per-frame probabilities and detections where available.
- **Feedback versus review:** distinguish a satisfaction rating, a correction, and a review request. Mobile sends `agree`/`disagree`, while backend correction types are `disease_change`, `healthy_override`, `severity_change`, `other`. Neither a feedback write nor a success screen currently establishes a tracked agronomist review request.
- **Canonical API contracts:** unify disease ID/slug/name, severity enum, confidence range/band, percent-versus-fraction units, evidence counts, model-version provenance and result state. Generate typed clients or equivalent checked contracts. Preserve detailed structured evidence rather than returning fabricated counts.
- **Consent and privacy controls:** record actor/time/policy/purpose rather than only requiring a boolean; implement retention/deletion across database and media. Persist permitted device/capture/crop-stage metadata if needed. Do not introduce precise GPS collection unless required and consented; raw precise GPS is not currently being captured by this intake.
- **Verified-data provenance:** backend support for review author/source channel, revision history, blind-review enforcement, independent labels and consent-aware export remains incomplete. Two-reviewer consensus and gold-only export are required before using this as the claimed verified-data flywheel, not before a read-only demo. Training, golden-set scientific validation and model release metrics are excluded here.
- **Operations:** environment-specific secrets and CORS, rate limits/quotas, a safe 500 error envelope, durable queues, dependency readiness/worker heartbeat, stage latency/queue age/error/cost telemetry, alerting, backups with restore drills, deployment rollback and retention jobs. Health currently returns constants, not dependency checks. HTTP/validation errors have envelopes; reproduced unhandled errors return plain `Internal Server Error`.
- **Deployment/configuration:** reconcile `.env.example` names and driver/port assumptions with actual settings and Compose. The checked-in Render file only describes an API with `/tmp` SQLite, not the required durable DB/cache/worker/storage stack. Live hosting configuration was not inspected. Verify TLS, encryption at rest and secret management in the actual deployment; repository absence is not proof a cloud provider lacks them.
- **Maintainability/testing:** the initial migration creates tables from mutable current metadata rather than frozen DDL. Alternative pipeline/aggregation/guardrail/storage implementations are not all wired into the active execution path; consolidate or clearly mark them. Existing tests of a separate toy pipeline do not validate live ingestion.

## 3. Backend endpoint checklist for frontend work

All routes in this section use `/api/v1` unless stated otherwise. “Exists” means a registered implementation was found, **not** that it is production-ready. Proposed names below are recommendations, not claims that the PRD prescribes those exact paths.

### Existing endpoints: repair or complete these

| Existing routes | Current state / required work |
|---|---|
| `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me` | Real implementations. Fix B01/B02; complete onboarding, role policy and session lifecycle. Both client registration experiences are not connected to registration. |
| `POST /farms`, `GET /farms/{id}` | Present. Complete validation, ownership, nested field contract and client integration. |
| `GET /fields`, `POST /farms/{id}/fields`, `GET /fields/{id}` | Present. Fix B03, add filters/pagination/enriched field summaries. |
| `GET /fields/{id}/health` | Returns a fixed score/components/zones. Hide or label unavailable until a real, validated scoring capability is released. |
| `POST /videos` | Present multipart upload. Complete validation, durable storage, consent metadata and dispatch recovery. |
| `GET /videos/{id}/status` | Present. Expose useful stage/retry/failure/retake information with defined terminal states and safe errors. |
| `GET /videos/{id}/analysis`, `GET /diagnosis/{id}` | Present but inconsistent. Fix B06/B07 and establish one authoritative report contract. |
| `GET /videos/{id}/frames`, `GET /videos/{id}/frames/{frame_id}/content` | Metadata exists; binary route fails. Add real media rendering, timestamps/quality explanations and protected access. |
| `POST /diagnosis/{id}/feedback`, `POST /diagnosis/{id}/verify` | Both reproduced 500. Fix persistence and request/response contracts; wire clients to real calls. |
| `GET /agronomist/queue`, `GET /agronomist/cases/{id}` | Real queries with scoped data. Complete pending-state behavior, filters, assignments and evidence/review detail. Queue currently supports offset/limit rather than documented cursor pagination. |
| `GET /b2b/dashboard`, `GET /b2b/drilldown` | Partly live counts versus synthetic health/disease metrics and drilldowns. Required only if B2B ships; never show fixed data as a real user's analytics. |
| `GET/POST /admin/model-versions`, `PATCH /admin/model-versions/{id}/deployment-status`, `GET /admin/golden-set` | Placeholder governance responses, not durable administration. Defer with model operations; disable misleading promotion controls. A nonempty release-gate ID is not a validated gate. |
| `/health`, `/healthz` | Liveness-style constant responses. Add dependency readiness separately. |

### Missing capabilities: recommended API additions

| Priority / consumer | Suggested API capability | Purpose |
|---|---|---|
| Core onboarding: mobile/web | `GET /farms`; `GET /fields?farm_id=...` | Real owned farm/field selection. Extend existing fields route rather than duplicate it. |
| Core history: mobile/agronomist | `GET /videos?field_id=...&status=...&cursor=...`; `GET /videos/{id}` | Saved scan history, pending jobs, contextual details and report links. |
| Core forms/review | `GET /crops`; `GET /diseases?crop_id=...` | Shared launch taxonomy; alternatively serve a versioned, authoritative static catalogue. |
| Account management | `PATCH /auth/me`; password-change and forgot/reset-password routes; server-side logout/revoke capability | Make profile/recovery/logout promises real. Recovery is required for public self-service release or needs an explicit supported alternative. |
| Farm/field management | `PATCH /farms/{id}`, `PATCH /fields/{id}`; scoped archive/delete capability | Correct user-entered data and remove/archive it with a safe retention policy. Hard deletion is not automatically the right default. |
| Agronomist review | Review-request creation and status, e.g. `POST /diagnosis/{id}/review-requests`; case claim/assignment and review-history routes | Turn “request review” into tracked work; prevent conflicting edits. These can also be clean extensions of existing case resources. |
| Media/review | `GET /videos/{id}/content` with authenticated range delivery, or short-lived authorized media URLs | Actual video playback; preserve tenant isolation. |
| Job recovery | Authorized retry/cancel capability, e.g. `POST /videos/{id}/retry` | Explicit safe handling of failed/stuck scans after the underlying idempotency work. |
| Rural upload reliability | Resumable upload session/init/parts/complete/abort contract | Resume interrupted uploads. A separate quality-check/start API is only needed if keeping the current two-step UI; otherwise make the UI match automatic processing. |
| Organization release | Organization/member/invitation APIs; implemented filters on B2B summary/drilldown | Tenant onboarding and real organization administration. |
| Report/export release | Export creation/status/download, e.g. `POST /reports`, `GET /reports/{id}`, `GET /reports/{id}/download` | Replace simulated web report generation. If not shipping exports, disable those controls. |
| Optional visible settings | Notification-preference endpoints, notification delivery/status if promised; contact submission endpoint or supported external handler | Make settings/contact forms real or remove unsupported success messages. SMS/WhatsApp is not mandatory merely because a checkbox exists. |
| Privacy/operations | Consent records, authorized data-deletion/export requests; readiness/operational endpoints | Enforce the selected privacy/operations policy; some capabilities may be internal jobs rather than public APIs. |

For lists and mutations, define permissions, pagination/filter semantics, validation, concurrency/idempotency, error codes and audit behavior before client integration. A long list of newly named routes is not a substitute for fixing the existing ones.

## 4. Web frontend: remaining work

| Surface | Current evidence | Needed |
|---|---|---|
| Login/session/roles | Real API login/me/refresh; tokens in localStorage; frontend and backend role sets/access rules disagree | Align capabilities and routing; handle refresh races/timeouts/offline errors; choose and document browser-session protections |
| Registration/onboarding/recovery/contact | Registration navigates to contact; onboarding is instructional; recovery/contact show local success without delivery | Connect real workflows or honestly disable them; never confirm an operation that did not happen |
| Agronomist dashboard | Fetches live queue, but retains/merges demo data; filters/metrics are not consistently live | Use typed real queue data and real empty/error states; wire all filters and links |
| Agronomist case review | Uses mock lookup and mock verification; live queue UUID can lead to a case screen that stays loading | Fetch real case, render real evidence, submit independent estimate/notes/decision, show persisted review state |
| Evidence viewer | Video URL is not actually played; frame selection can retain a stale image; empty frame list can dereference an undefined frame | Real protected video/image rendering, loading/unavailable states, selected-frame sync, no decorative crop fallback posing as evidence |
| Organization dashboard | Some real counts overlaid on demo farms/scans and fixed metrics; errors can leave mock data visible | Real scoped lists/filters/details and explicit unavailable states; fix incompatible metric meanings |
| Farm/field details | Demo lookup/fallback and hardcoded case context | Use route IDs and backend responses; handle 404 properly, never substitute a different farm |
| Reports | Simulated creation and placeholder download links | Implement export APIs and downloads, or disable export UI |
| Profile/org/settings | Read-only identity plus static organization details and nonpersistent controls | Persist actual editable fields/team settings, or remove unsupported controls and retention/notification promises |
| Public pages/release quality | Public pages exist; support/privacy claims need reconciliation; no browser E2E validated here | Verify routes, forms, keyboard/accessibility, responsive/error states and public metadata. Server-rendered public content is a separate public-site improvement, not a reason to rewrite frameworks |

Main evidence: [AuthContext](C:/Projects_External/Rakshak_AI/frontend/web/src/context/AuthContext.tsx), [API client](C:/Projects_External/Rakshak_AI/frontend/web/src/services/apiClient.ts), [agronomist dashboard](C:/Projects_External/Rakshak_AI/frontend/web/src/screens/agronomist/AgronomistDashboard.tsx), [case review](C:/Projects_External/Rakshak_AI/frontend/web/src/screens/agronomist/AgronomistCaseReviewPage.tsx), [organization dashboard](C:/Projects_External/Rakshak_AI/frontend/web/src/screens/organization/OrgDashboard.tsx), [evidence viewer](C:/Projects_External/Rakshak_AI/frontend/web/src/components/shared/EvidenceViewer.tsx), [SafeImage](C:/Projects_External/Rakshak_AI/frontend/web/src/components/shared/SafeImage.tsx).

## 5. Mobile frontend: remaining work

The basic flow exists; this is **not** a recommendation to rebuild mobile from scratch.

| Surface | Current evidence | Needed |
|---|---|---|
| Registration/onboarding | Registration collects fields but does not create an account; no real new-user farm/field setup | Register with actual credentials; create/select farm and field; persist consent/onboarding completion |
| Dashboard/field/history/profile | Demo fields/scans/person; history items lack real video IDs; field detail is hardcoded | Fetch user/field/history data, carry real IDs through navigation and preserve selected field when scanning |
| New scan | Real field lookup but errors are swallowed; empty list falls back to fake field ID; crop input is not submitted | Explicit loading/error/no-fields flow; real field creation/selection and consistent soybean-only catalogue |
| Capture/quality | Native capture capped at 15 seconds; generic “good” quality checks; no actual quality preview | Enforce agreed duration and server validation; 15 seconds is within the PRD range, but full 10–30 support/minimum enforcement is incomplete. Show real quality feedback or only capture guidance |
| Upload/processing | Upload starts processing before “Start analysis”; no progress/resume/cancel; upload lacks refresh retry; polling makes only six short attempts and can silently stop | Match UI to server lifecycle, durable pending uploads/jobs, bounded background-safe retries, resume after relaunch, handle failed/insufficient states explicitly |
| Report | Calls analysis/frames, but not the richer diagnosis report; ignores major state/severity/explanation fields; evidence is text cards rather than images | Render canonical report, healthy/unknown/insufficient states, real media and actionable retake guidance |
| Feedback/review | Sends incompatible `agree`/`disagree`; star value is not persisted as a rating; successful flow claims review requested | Agree a feedback schema, distinguish rating/correction/review request, and show confirmation only for a persisted action |
| Session/settings | Secure token storage is present; offline restoration can clear session; profile/settings mostly static | Preserve offline session appropriately, enforce user-role routing, implement or disable settings, handle refresh/network failure consistently |
| Native release | Android/iOS projects exist. Android main manifest lacks explicit INTERNET permission; debug/profile manifests contain it. Android release signing uses debug keys | Check merged release manifest/connectivity, production signing, camera permissions on real devices, iOS provisioning/plugin setup, suspend/resume and low-bandwidth behavior |

Main evidence: [mobile API client](C:/Projects_External/Rakshak_AI/frontend/mobile/lib/api_client.dart), [authentication](C:/Projects_External/Rakshak_AI/frontend/mobile/lib/screens/authentication_screens.dart), [scanning](C:/Projects_External/Rakshak_AI/frontend/mobile/lib/screens/scan_screens.dart), [reports](C:/Projects_External/Rakshak_AI/frontend/mobile/lib/screens/report_screens.dart), [feedback](C:/Projects_External/Rakshak_AI/frontend/mobile/lib/screens/feedback_screens.dart), [history](C:/Projects_External/Rakshak_AI/frontend/mobile/lib/screens/history_screen.dart), [Android manifest](C:/Projects_External/Rakshak_AI/frontend/mobile/android/app/src/main/AndroidManifest.xml), [release signing](C:/Projects_External/Rakshak_AI/frontend/mobile/android/app/build.gradle.kts:34).

## 6. PRD/backlog coverage and what can wait

| Requirement group | Current assessment | Scope decision |
|---|---|---|
| PRD §§1–6: product/users/core soybean journey | Screens and partial APIs exist; new-user and expert-review journeys are incomplete | Core release work |
| §§7–8: capture and preprocessing | Basic capture/filtering exists; validation, unique evidence and reliable processing are partial | Core server-quality work now; advanced on-device real-time guidance can follow Phase 2 |
| §§9–14: inference/aggregation/confidence/severity | Model implementation and scientific quality not evaluated; application mapping defects are verified | Fix data contracts/state/persistence now; leave model methods, thresholds/calibration and attachment to teammate |
| §§15–16, §30: explanation, advisory guidance and farmer report | Templates/schema exist, but report paths and client rendering are inconsistent | Safe deterministic report is core; LLM attachment can remain deferred |
| §§17–20: health index/maps/progression/weather | Current scores/zones are placeholders; progression/weather not implemented | Later PRD work; do not display invented scores as real results |
| §§21–26: verified data/training/evaluation | Separate label tables exist, but review persistence/lifecycle/export incomplete | Operational review and provenance now/as needed for pilot; training/evaluation remain excluded |
| §§27–29: architecture/pipeline | Modular API/worker scaffolding exists; deployment, storage and consistency gaps remain | Core release blockers |
| §31: B2B dashboard/drilldown | Partially live totals; fabricated risk/health/disease summaries | Complete if launching B2B; otherwise disable and defer |
| §§32–33: privacy/security/safety | Some scoped reads, consent checks, audit helpers and disclaimers | Not complete; enforce behavior, not only UI copy |
| §34: success metrics | Operational/usage measurements and PRD latency/reliability targets not demonstrated | Instrument and validate; do not infer production readiness from syntax/type checks |
| §§35–36: phased roadmap | Wider crops, advanced history/progression, realtime assistance and marketplace not delivered | Explicit later scope; basic history for today's app still needed |
| §§37–38: long-term vision | Future ecosystem/outbreak/risk capabilities | Not launch blockers for soybean pilot |

Backlog reconciliation: `FR-P1` foundations and `FR-P2` ingestion are **partial**, not completed merely because modules exist. `FR-P6` guarded reporting and `FR-P7` verification still have substantive application work. `FR-P8` pilot provenance is partly a collection/operations process. `FR-P9` field/B2B intelligence is conditional later-release work. Cross-cutting security/privacy/testing remains incomplete. `FR-P3/P4/P5/P10` contain model-related work excluded here, except application-boundary correctness and safe presentation described above. YAML `todo` values and historical “completed” prose are not authoritative evidence of current behavior.

### Corrections to earlier high-priority/completion claims

- Alembic startup is **present but defective**, not wholly absent.
- Farm/field creation and field listing already exist; complete them instead of rebuilding them.
- Server-side blur/exposure/duplicate processing already exists; its correctness/integration needs repair.
- Web queue/dashboard integration is **partial**, not entirely mock and not fully connected.
- Authenticated frame access exists structurally but currently fails; calling it a safe working fallback is premature.
- Audit helpers exist, but upload audit is misplaced and feedback/verification fail before their audit writes.
- HTTP/validation error envelopes exist; a universal consistent 500 envelope does not.
- Named CPU/GPU queues do not establish an isolated model-worker deployment. That deployment remains out of scope.
- Mobile platform folders exist, and the capture limit is 15 seconds—not an absence of camera capture.
- Maps/field scores/weather/full progression and model-governance work should not be mixed into the immediate non-model blocker list without a release-scope decision.

## 7. Verification performed

| Check | Result | Meaning / limit |
|---|---|---|
| Git refresh | Already up to date in this review conversation | No merge or overwrite was needed |
| Backend application syntax | **61 Python files parsed** | Syntax only, not behavioral correctness |
| Selected non-model backend tests | **13 passed, 7 failed** | Seven failures are stale unauthenticated/demo-header fixtures: three role endpoint tests, one farm/field test, three ingestion tests. They do not establish working authenticated mutation flows |
| Isolated behavior probes | Reproduced B01–B07, B10, duplicate-quality defects, SQLite startup failure and migration driver-load failure | In-memory SQLite and controlled fake outputs; no user DB, trained model or external network used |
| Positive tenant control | Cross-organization farm GET returned **404** | Confirms that specific read is scoped; does not excuse the reproduced write bypass |
| Web TypeScript | **Passed** `tsc --noEmit --incremental false` | Not a browser, production build or end-to-end test |
| Flutter analysis | **1 warning, 4 infos**, exit 1 | Unused import, async-context/style and deprecated API notices; no compile errors reported by analysis |
| Flutter widget test | **0 passed, 1 failed** | Welcome text assertion found no widget after initial pump; test does not account for the session-gate flow. No device behavior proven |
| Production/staging integration | **Not verified** | No live DB, bucket, worker, reverse proxy, release mobile build, device or load test was exercised |

There is no checked-in `.github` CI workflow. Existing tests largely use SQLite and bypass application lifespan, so they did not catch startup/driver problems and do not prove PostgreSQL constraints/migrations. No claim is made that the whole suite is green.

Reproducible diagnostic helper: [non_model_probe.py](C:/Projects_External/Rakshak_AI/docs/audits/non_model_probe.py). It **observes defects, not fixes or release-test passes**. It requires the disposable container layout below and is not intended to run against a deployed app.

PowerShell commands used for isolated backend checks, with an already-existing local image (`rakshak_ai-backend:latest`, image ID prefix `1ef31bbbb329`):

```powershell
docker run --rm --network none --read-only --tmpfs /tmp -e PYTHONDONTWRITEBYTECODE=1 -e DATABASE_URL=sqlite+aiosqlite:////tmp/audit.db -e LOCAL_STORAGE_DIR=/tmp/storage --mount 'type=bind,source=C:\Projects_External\Rakshak_AI\backend,target=/audit,readonly' -w /audit --entrypoint python rakshak_ai-backend:latest -m pytest -q -p no:cacheprovider tests/unit/core tests/unit/api tests/integration tests/unit/modules/processing tests/test_pipeline.py --tb=short

docker run --rm --network none --read-only --tmpfs /tmp -e PYTHONDONTWRITEBYTECODE=1 -e DATABASE_URL=sqlite+aiosqlite:////tmp/audit.db -e LOCAL_STORAGE_DIR=/tmp/storage --mount 'type=bind,source=C:\Projects_External\Rakshak_AI\backend,target=/audit,readonly' --mount 'type=bind,source=C:\Projects_External\Rakshak_AI\docs\audits,target=/probes,readonly' -w /audit --entrypoint python rakshak_ai-backend:latest /probes/non_model_probe.py
```

## 8. Recommended implementation order and release gate

1. **Secure and boot:** B01–B03, migrations/seeding/configuration, durable storage and trustworthy readiness.
2. **Make the existing scan API correct:** evidence/feedback/verification failures, canonical output mapping, quality/insufficient-evidence behavior, safe reports and idempotent jobs.
3. **Finish one real farmer journey:** register → farm/field setup → upload → real status → report/evidence → saved history → feedback/review request. Handle no fields, offline, expired token, failed scan and retake.
4. **Finish one real agronomist journey:** scoped queue → real case/media → independent review → persisted result → queue/history update. No mock fallbacks.
5. **Complete the release's supporting surfaces:** profiles, recovery, consent/retention, exports/team/B2B only where promised; hide the rest.
6. **Prove it:** PostgreSQL migration and permission tests, API/client contract tests, crash/retry/storage tests, web E2E, Android/iOS release/device checks, bounded load tests and backup restore drill.

Non-model release gate: these core journeys work with deterministic test inference outputs, all role/tenant/state tests pass, evidence survives restart, retries do not duplicate records, no fake data is shown as a user's result, and operational recovery is documented. The separately owned model-readiness gate must still be satisfied before presenting real diagnostic capability to users.

No application fixes were made during this audit. Only this report and the diagnostic helper were added; the six preexisting web/mobile UI modifications were preserved.
