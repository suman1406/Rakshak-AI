# Local seed accounts

The backend container seeds these accounts automatically when it starts. They are for local testing only and must not be used in a production deployment.

The Docker image runs `python -m app.db.seed`. The canonical seeded accounts are below.

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@rakshak.ai` | `Admin@1234` |
| Farmer | `rajan.patil@example.com` | `Farmer@1234` |
| Farmer | `sunita.devi@example.com` | `Farmer@1234` |
| Agronomist | `dr.mehta@rakshak.ai` | `Agro@1234` |
| Enterprise | `analyst@agroshield.com` | `Enterprise@1234` |

The role is stored in `users.role` and is authoritative. The web client is for agronomist/admin/enterprise workspaces; farmer accounts are intended for the Flutter app. These credentials are development-only and must be rotated or removed before a real deployment.
