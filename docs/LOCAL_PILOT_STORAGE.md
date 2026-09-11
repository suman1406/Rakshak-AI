# Private evidence storage and legacy migration

Docker Compose now stores uploaded videos and extracted frames in private MinIO objects. The named `rakshak-minio` volume preserves these objects across container replacement. API and worker use the same bucket, credentials and database. They do not depend on shared local filesystem paths.

S3-compatible production storage uses `STORAGE_BACKEND=s3`, a private bucket, region, endpoint and appropriate credentials or a supported AWS credential chain. `s3://bucket/key` references are persisted; no public object URLs are returned. The API authorizes the user before retrieving media and sends `Cache-Control: private, no-store`. Local object caches are expendable and pruned on API hosts hourly (objects older than 24 hours) and during worker retention maintenance.

## Existing local records

A previous checkout stored evidence under `/app/storage` or a shared local volume. Preserve that volume and database backup before replacing it. Run the migration on a host that can still read those files, with `LOCAL_STORAGE_DIR` pointing to their containing root and S3 configured:

```sh
python -m app.migrate_media
python -m app.migrate_media --apply
```

The default is a dry run. Apply copies available local video/frame files, updates database references, and retains original files for backup review. Already migrated S3 references are skipped. Missing or outside-root files are counted as unavailable. The tool cannot recover evidence already lost from an ephemeral deployment.

## Retention and training

`EVIDENCE_RETENTION_DAYS` defaults to 180. One Celery beat scheduler runs daily evidence expiry; only terminal old scans are eligible. Media expires while assessment and audit records remain. Retained local API cache copies are pruned independently and are no longer accessible through the expired-media API.

```sh
python -m app.retention
python -m app.retention --apply
python -m app.dataset_export --help
```

Retention is a dry run without `--apply`. Training exports require explicit uploader opt-in, available unexpired media and an expert label. Revoking consent excludes future exports; it cannot remove records already copied into an external training environment. The manifest contains private object references and stable field-based data splits; it excludes names, contacts and free-text notes.

Back up PostgreSQL and the evidence bucket together. Cloud lifecycle rules must be coordinated with application retention. Keep buckets private and run a restore exercise before relying on production backups.
