# Fasal Rakshak — API Specification

Base path: `/api/v1`. Auth: JWT bearer token (`Authorization: Bearer
<token>`) except `auth/*`. Roles: `farmer`, `agronomist`, `admin`,
`enterprise` (per RBAC skeleton, Architecture Reference §4 rule 1 / PRD §32).
Every mutating endpoint writes an `audit_logs` row.

This expands PRD §28/§29 into full request/response contracts. Treat this
as the source of truth for `app/schemas/*` — Pydantic models should mirror
these shapes exactly; if a schema needs to diverge, update this doc in the
same PR.

## Auth

### `POST /auth/register`
Roles: public. Body: `{ "email": str, "phone": str|null, "password": str, "role": "farmer"|null }`
(default `farmer`; `agronomist`/`admin`/`enterprise` creation is
admin-invite-only — see `POST /admin/users`).
Response `201`: `{ "user_id": uuid }`

### `POST /auth/login`
Roles: public. Body: `{ "email_or_phone": str, "password": str }`
Response `200`: `{ "access_token": str, "refresh_token": str, "role": str }`
Response `401`: invalid credentials.

### `POST /auth/refresh`
Body: `{ "refresh_token": str }` → `200`: `{ "access_token": str }`

## Farms & fields

### `POST /farms`
Roles: farmer, admin, enterprise. Body: `{ "name": str, "state": str|null, "district": str|null }`
Response `201`: `{ "farm_id": uuid }`

### `GET /farms/{farm_id}`
Roles: owner, admin, or same-org enterprise. `200`: farm object + field list.

### `POST /farms/{farm_id}/fields`
Body: `{ "name": str, "crop_id": uuid, "area_hectares": number|null }`
Response `201`: `{ "field_id": uuid }`

### `GET /fields/{field_id}`
`200`: field object.

### `GET /fields/{field_id}/health`
Roles: owner, agronomist, admin, same-org enterprise. Returns the Field
Health Score + latest video_diagnoses summary per zone (PRD §17/§18).
`200`:
```json
{
  "field_id": "uuid",
  "fasal_health_score": 72,
  "components": { "disease_prevalence": 30, "severity": 25, "healthy_ratio": 25, "visual_stress": 10, "confidence": 10 },
  "zones": [ { "zone_label": "A", "status": "healthy" }, { "zone_label": "B", "status": "early_disease" } ]
}
```

## Video ingestion & status

### `POST /videos`
Roles: farmer, agronomist, enterprise. Initiates a resumable upload session
(tus protocol handshake, or S3 multipart init depending on chosen
transport — see Environment Setup doc). Body: `{ "field_id": uuid,
"duration_seconds": number, "device_metadata": object }`
Response `201`: `{ "video_id": uuid, "upload_url": str, "status": "uploaded" }`
*Note: chunk upload itself happens against `upload_url` per the tus/S3
multipart protocol, not as additional plain REST calls on this resource.*

### `GET /videos/{video_id}/status`
Roles: uploader, agronomist, admin. `200`:
```json
{ "video_id": "uuid", "status": "processing", "quality_score": 82, "usable_frames_count": 14, "error_detail": null }
```

### `GET /videos/{video_id}/analysis`
Roles: uploader, agronomist, admin. Returns the vision-pipeline output
(pre-explanation-layer), matching PRD §29's example shape:
```json
{
  "crop": "soybean",
  "crop_confidence": 0.94,
  "diagnosis": {
    "disease": "soybean_rust",
    "is_unknown": false,
    "confidence": 0.89,
    "confidence_band": "high",
    "severity": "moderate",
    "affected_plant_estimate": 0.21
  },
  "evidence": { "frames_analyzed": 16, "supporting_frames": 12, "leaf_regions_analyzed": 43 },
  "model_versions": { "detector": "yolo11-v3", "classifier": "effnet-v2", "aggregation": "bayes-v1" }
}
```
`404` if `status != ready`; body includes current `status` so the client can
keep polling.

### `GET /diagnosis/{video_diagnosis_id}`
Roles: uploader, agronomist, admin. Returns the farmer-facing report
(post-explanation-layer, PRD §30 shape): headline, confidence band,
severity, affected-plant estimate, "what we found," "what to do now."

## Feedback & verification

### `POST /diagnosis/{video_diagnosis_id}/feedback`
Roles: farmer (uploader). Body: `{ "correction_type": "disease_change"|"healthy_override"|"severity_change"|"other", "note": str|null }`
Response `201`: `{ "feedback_id": uuid }`. Always written with lower
`trust_weight` than an agronomist verification — never merged into
`verified_labels`.

### `POST /diagnosis/{video_diagnosis_id}/verify`
Roles: agronomist only. Body:
```json
{
  "disease_id": "uuid|null",
  "is_healthy_override": false,
  "severity_level": 2,
  "affected_plant_estimate_independent": 0.18,
  "is_blind_relabel": false
}
```
Response `201`: `{ "verified_label_id": uuid, "is_gold": false }`.
`affected_plant_estimate_independent` must be supplied independently by the
agronomist, not pre-filled from the AI's own estimate — see `[L8]`.

## Agronomist dashboard

### `GET /agronomist/queue`
Roles: agronomist, admin. Query params: `?limit=&cursor=`. Sorted by
lowest AI confidence first (that's where review time adds the most value).
`200`: paginated list of `{ video_diagnosis_id, disease, confidence,
severity, created_at }`.

### `GET /agronomist/cases/{video_diagnosis_id}`
Roles: agronomist, admin. Full case detail: video reference, all supporting
frame evidence, prior verifications if any (for consensus review), AI
diagnosis.

## B2B / enterprise

### `GET /b2b/dashboard`
Roles: enterprise, admin. Requires org context (derived from JWT `org_id`).
`200`: aggregate counts matching PRD §31 shape (`total_farms`, `healthy`,
`at_risk`, `disease_detected`, `top_diseases`, `high_risk_farms`).
*Backed by OLAP/read-replica once volume justifies it — Phase 9; OLTP
Postgres directly at pilot scale.*

### `GET /b2b/drilldown`
Roles: enterprise, admin. Query params: `?district=&fpo=&farm_id=&field_id=`.
Each level of the drill-down (`Disease → District → FPO → Farm → Field →
Video Evidence`, PRD §31) is a filter refinement on the same endpoint.
**Tenant isolation is enforced server-side** — an enterprise JWT can never
retrieve another tenant's rows regardless of query params (row-level
security, Phase 9 ticket `FR-P9-06`).

## Admin / model governance

### `GET /admin/model-versions`
Roles: admin. `200`: list of `model_versions` rows.

### `POST /admin/model-versions`
Roles: admin. Registers a newly trained model (called from the training
pipeline, not typically the UI). Body: `{ "model_name": str, "version_hash":
str, "training_dataset_version": str, "eval_metrics": object }`. Always
created with `deployment_status = "shadow"`.

### `PATCH /admin/model-versions/{id}/deployment-status`
Roles: admin. Body: `{ "deployment_status": "canary"|"production"|"retired",
"release_gate_record_id": uuid }`. **Rejects the transition to
`production` unless a passing release-gate record is referenced** — see
Testing & Eval Strategy doc §Release Gate. This is the enforcement point for
Architecture Reference §4 rule 12 ("no model auto-promotes").

### `GET /admin/golden-set`
Roles: admin. Lists `golden_set_items`, filterable by `subset` and
`set_version`.

### `POST /admin/golden-set/items`
Roles: admin. Body: `{ "video_id": uuid, "subset": "frozen_regression"|"refreshed", "set_version": str }`

## Errors

All error responses: `{ "error_code": str, "message": str, "request_id": str }`.
Standard codes: `401 unauthorized`, `403 forbidden` (RBAC or tenant-isolation
violation), `404 not_found`, `409 conflict` (e.g. re-verifying an
already-gold label outside the consensus flow), `422 validation_error`,
`503 upstream_unavailable` (GPU inference endpoint or LLM API down —
distinguished from a genuine `failed` video status).