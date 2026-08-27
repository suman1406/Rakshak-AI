# Local seed accounts

The backend container seeds these accounts automatically when it starts. They are for local testing only and must not be used in a production deployment.

All accounts use the password `Rakshak@2026`.

| Role | Email |
| --- | --- |
| Agronomist | `agronomist.one@rakshak.ai` |
| Agronomist | `agronomist.two@rakshak.ai` |
| Organization admin | `admin.one@rakshak.ai` |
| Organization admin | `admin.two@rakshak.ai` |
| Farmer mobile app | `farmer.one@rakshak.ai` |
| Farmer mobile app | `farmer.two@rakshak.ai` |

The role is stored in the `users.role` column and is never selected by the login client. The web client accepts only `agronomist` and `org_admin`; farmer accounts are intended for the Flutter app.
