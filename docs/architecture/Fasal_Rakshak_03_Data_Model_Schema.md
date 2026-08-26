# Fasal Rakshak — Data Model / Schema (DDL-Ready)

This is the authoritative Postgres schema. It should be translated directly
into Alembic migrations (Phase 1 introduces the identity/farm/taxonomy
tables + the prediction-table skeletons with `*_model_version` columns;
later phases add columns/tables as noted inline). Do not hand-diverge from
this document without recording the deviation as an ADR
(`docs/adr/ADR-000N.md`).

## Conventions

- Primary keys: `UUID DEFAULT gen_random_uuid()` (requires the `pgcrypto`
  extension).
- Timestamps: `TIMESTAMPTZ`, always UTC.
- Every table that represents a prediction carries a non-nullable
  `*_model_version TEXT` column — see Architecture Reference §4 rule 4.
- Enums are Postgres `CREATE TYPE ... AS ENUM`, not free-text columns, so
  invalid states are rejected at the DB layer, not just the app layer.
- Taxonomy tables (`crops`, `diseases`) are versioned rows, not hardcoded
  enums — new disease classes are data, not a code deploy.

## Extensions

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

## Enums

```sql
CREATE TYPE user_role AS ENUM ('farmer','agronomist','admin','enterprise');
CREATE TYPE org_type AS ENUM ('fpo','insurer','input_company','bank','gov','research','other');
CREATE TYPE video_status AS ENUM (
    'uploaded','validating','processing','analyzing','aggregating',
    'ready','failed','insufficient_evidence'
);
CREATE TYPE detection_class AS ENUM ('plant','leaf','diseased_leaf','lesion','stem','pod');
CREATE TYPE confidence_band AS ENUM ('high','medium','low');
CREATE TYPE deployment_status AS ENUM ('shadow','canary','production','retired');
CREATE TYPE decision_authority_status AS ENUM ('advisory_only','human_confirmed');
CREATE TYPE source_channel AS ENUM ('neutral_agronomist','insurer','input_company','bank','other_commercial');
CREATE TYPE correction_type AS ENUM ('disease_change','healthy_override','severity_change','other');
CREATE TYPE golden_subset AS ENUM ('frozen_regression','refreshed');
CREATE TYPE dataset_split AS ENUM ('train','val','test');
```

## Identity & organizations

```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    org_type org_type NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE,
    phone TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    role user_role NOT NULL,
    org_id UUID REFERENCES organizations(id),
    display_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_users_org_id ON users(org_id);
```
*Phase 1. RBAC roles are the four from PRD §5/§32. Retrofitting roles later
is the single most annoying migration to defer — this is why it's Phase 1.*

## Taxonomy

```sql
CREATE TABLE crops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    taxonomy_version TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (name, taxonomy_version)
);

CREATE TABLE diseases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crop_id UUID NOT NULL REFERENCES crops(id),
    name TEXT NOT NULL,
    taxonomy_version TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (crop_id, name, taxonomy_version)
);
```
*Phase 1 (empty/stub), populated in Phase 3 once the launch taxonomy
(Rust, Bacterial Blight, Frogeye Leaf Spot, Septoria Brown Spot, Healthy,
Other/Unknown) is validated against an agronomist/ICAR reference.*

## Farms & fields

```sql
CREATE TABLE farms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_user_id UUID NOT NULL REFERENCES users(id),
    org_id UUID REFERENCES organizations(id),
    name TEXT NOT NULL,
    state TEXT,
    district TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_farms_owner ON farms(owner_user_id);
CREATE INDEX idx_farms_org ON farms(org_id);

CREATE TABLE fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farm_id UUID NOT NULL REFERENCES farms(id),
    name TEXT NOT NULL,
    crop_id UUID REFERENCES crops(id),
    area_hectares NUMERIC,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_fields_farm ON fields(farm_id);
```

## Video pipeline

```sql
CREATE TABLE videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    field_id UUID NOT NULL REFERENCES fields(id),
    uploaded_by UUID NOT NULL REFERENCES users(id),
    status video_status NOT NULL DEFAULT 'uploaded',
    quality_score NUMERIC,
    gps_geohash VARCHAR(12),            -- ~1km truncated, default-exposed
    raw_gps_encrypted BYTEA,            -- precise coords, encrypted at rest, restricted access (Arch §4 rule 11)
    storage_path TEXT NOT NULL,
    duration_seconds NUMERIC,
    device_metadata JSONB,              -- {"phone_model": "...", "os": "...", "app_version": "..."} — drift-monitoring slice
    total_frames_extracted INT,
    usable_frames_count INT,
    error_detail TEXT,                  -- populated when status = 'failed'
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_videos_field ON videos(field_id);
CREATE INDEX idx_videos_status ON videos(status);
CREATE INDEX idx_videos_uploaded_by ON videos(uploaded_by);

CREATE TABLE frames (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID NOT NULL REFERENCES videos(id),
    storage_path TEXT NOT NULL,
    blur_score NUMERIC,
    exposure_score NUMERIC,
    is_selected BOOLEAN NOT NULL DEFAULT false,
    sequence_index INT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_frames_video ON frames(video_id);
```

## Predictions

```sql
CREATE TABLE detections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    frame_id UUID NOT NULL REFERENCES frames(id),
    bbox JSONB NOT NULL,                 -- {"x":0.12,"y":0.34,"w":0.10,"h":0.08} normalized coords
    class detection_class NOT NULL,
    detector_confidence NUMERIC NOT NULL,
    detector_model_version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_detections_frame ON detections(frame_id);
CREATE INDEX idx_detections_model_version ON detections(detector_model_version);

CREATE TABLE frame_diagnoses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    detection_id UUID NOT NULL REFERENCES detections(id),
    probability_distribution JSONB NOT NULL,  -- {"rust":0.89,"bacterial_blight":0.05,"healthy":0.04,"other":0.02}
    classifier_model_version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_frame_diagnoses_detection ON frame_diagnoses(detection_id);

CREATE TABLE video_diagnoses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID NOT NULL REFERENCES videos(id),
    disease_id UUID REFERENCES diseases(id),     -- NULL when is_unknown = true
    is_unknown BOOLEAN NOT NULL DEFAULT false,   -- open-set routing (Arch §4 rule 13)
    confidence NUMERIC NOT NULL,                 -- post-calibration only (Arch §4 rule 9)
    confidence_band confidence_band NOT NULL,
    severity_level SMALLINT CHECK (severity_level BETWEEN 0 AND 3),
    affected_plant_estimate NUMERIC,
    supporting_frames INT,
    total_frames INT,
    aggregation_model_version TEXT NOT NULL,
    decision_authority decision_authority_status NOT NULL DEFAULT 'advisory_only',  -- [L13]
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_video_diagnoses_video ON video_diagnoses(video_id);
CREATE INDEX idx_video_diagnoses_disease ON video_diagnoses(disease_id);
```
*`decision_authority` and the `*_model_version` columns exist from the
Phase 1 migration even though only one model version exists at the time —
see Implementation Plan Phase 1.*

## Verification & feedback (structurally separate from predictions)

```sql
CREATE TABLE verified_labels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_diagnosis_id UUID NOT NULL REFERENCES video_diagnoses(id),
    agronomist_id UUID NOT NULL REFERENCES users(id),
    disease_id UUID REFERENCES diseases(id),
    is_healthy_override BOOLEAN NOT NULL DEFAULT false,
    severity_level SMALLINT CHECK (severity_level BETWEEN 0 AND 3),
    affected_plant_estimate_independent NUMERIC,   -- independently observed, NOT derived from the detector — [L8]
    source_channel source_channel NOT NULL DEFAULT 'neutral_agronomist',  -- [L4]
    consensus_group_id UUID,             -- groups 2+ reviews of the same video_diagnosis
    is_gold BOOLEAN NOT NULL DEFAULT false,  -- true only once consensus_group has 2+ agreeing reviews
    is_blind_relabel BOOLEAN NOT NULL DEFAULT false,   -- periodic anchoring-bias check — [L2]
    ai_suggestion_was_shown BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_verified_labels_video_diagnosis ON verified_labels(video_diagnosis_id);
CREATE INDEX idx_verified_labels_source_channel ON verified_labels(source_channel);
CREATE INDEX idx_verified_labels_consensus_group ON verified_labels(consensus_group_id);

CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_diagnosis_id UUID NOT NULL REFERENCES video_diagnoses(id),
    farmer_user_id UUID NOT NULL REFERENCES users(id),
    correction_type correction_type NOT NULL,
    note TEXT,
    trust_weight NUMERIC NOT NULL DEFAULT 0.2,   -- always lower than agronomist verification
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_feedback_video_diagnosis ON feedback(video_diagnosis_id);
```

## Governance & MLOps

```sql
CREATE TABLE model_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name TEXT NOT NULL,             -- e.g. 'disease_classifier_soybean'
    version_hash TEXT NOT NULL,
    training_dataset_version TEXT NOT NULL,
    eval_metrics JSONB,                   -- component + end-to-end metrics recorded at release time
    deployment_status deployment_status NOT NULL DEFAULT 'shadow',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (model_name, version_hash)
);
CREATE INDEX idx_model_versions_name_status ON model_versions(model_name, deployment_status);

CREATE TABLE golden_set_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID NOT NULL REFERENCES videos(id),
    subset golden_subset NOT NULL,
    set_version TEXT NOT NULL,            -- e.g. '2027-Q1'
    added_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_golden_set_items_subset_version ON golden_set_items(subset, set_version);

CREATE TABLE dataset_splits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID NOT NULL REFERENCES videos(id),
    split dataset_split NOT NULL,
    split_version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (video_id, split_version)      -- one assignment per video per split_version — enforces video-level splitting, [L7]
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id UUID,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
```

## Notes

- **`dataset_splits` is the enforcement mechanism for `[L7]`.** The
  stratified-split utility (`ml/data_pipeline/stratified_split.py`) writes
  to this table at the video level; any training script must join through
  `dataset_splits`, never re-derive a split from frame IDs directly. A CI
  check (see Testing & Eval Strategy doc) should assert no `frames` for a
  given `video_id` appear across two different `split` values within the
  same `split_version`.
- **Retention:** `videos.storage_path` objects are subject to an S3
  lifecycle policy (auto-archive/delete raw video after N days per the
  product's retention policy) — the DB row persists after the underlying
  object is archived/deleted; `storage_path` resolution should handle a
  "no longer available" case gracefully rather than erroring.
- **Multi-tenancy:** row-level security / tenant scoping (via `org_id` on
  `users`/`farms`) is introduced structurally now but only *enforced* at the
  Postgres RLS level in Phase 9, once B2B/FPO multi-tenancy is live — see
  backlog ticket `FR-P9-06`.
- **Why `is_gold` instead of just counting rows:** consensus is computed
  asynchronously (2+ agronomists may review at different times); `is_gold`
  is a materialized flag updated when the second agreeing review lands, so
  training-export queries don't need to re-aggregate consensus logic every
  run.