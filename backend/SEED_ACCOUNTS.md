# Local seed accounts

# Local seed accounts

The backend container seeds these accounts automatically when it starts. They are for local testing only and must not be used in a production deployment.

The Docker image runs `python -m app.db.seed`. The canonical seeded accounts are below.

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@rakshak.demo` | `RakshakAdmin@123` |
| Organization | `workspace@rakshak.local` | `RakshakDemo@123` |
| Agronomist | `agronomist@rakshak.local` | `RakshakDemo@123` |
| Farmer | `farmer@rakshak.local` | `RakshakDemo@123` |

The role is stored in `users.role` and is authoritative. The web client supports admin, organization (enterprise), agronomist, and farmer workspace views. These credentials are development-only and must be rotated or removed before a real deployment.
