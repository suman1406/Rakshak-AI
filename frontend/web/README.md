# Rakshak AI web

Frontend-only MVP prototype for the Rakshak AI PRD. It includes the public marketing site, the agronomist review workspace, and the B2B organization analytics workspace. The farmer workflow remains in `frontend/mobile` as the primary farmer experience.

The current route-compatible React router is mounted by `app/[[...slug]]/page.tsx` while the screens are migrated to native Next.js routes. Mock data is intentionally isolated in `src/data` and `src/services/mockApi.ts` so it can later be replaced by the FastAPI contracts.

## Run locally

```bash
pnpm install
pnpm dev
```

Open `http://localhost:3000`. Choose either the Agronomist review workspace or Organization analytics workspace from the login screen. This is simulated workspace access, not real authentication: the selected role is fixed for the session and there is no role-switch dropdown inside the app shell.

## Build

```bash
pnpm build
```
