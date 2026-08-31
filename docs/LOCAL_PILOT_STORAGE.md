# Local pilot evidence storage

The Docker Compose pilot uses the named `rakshak-evidence-local` volume mounted at `/app/storage` in both the API and worker containers. Uploaded videos and extracted frames therefore remain accessible to both processes and survive replacement of either container.

This is a deliberately single-host pilot constraint. The volume is not cross-host object storage, does not provide geographic replication, and must be backed up together with the PostgreSQL volume. Production deployment must replace this with private object storage and lifecycle/retention controls; the declared MinIO service is not yet part of the application evidence path.
