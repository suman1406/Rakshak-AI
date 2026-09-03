# Rakshak AI web

Frontend-only MVP prototype for the Rakshak AI PRD. It includes the public marketing site, the agronomist review workspace, and the B2B organization analytics workspace. The farmer workflow remains in `frontend/mobile` as the primary farmer experience.

The current route-compatible React router is mounted by `app/[[...slug]]/page.tsx` while the screens are migrated to native Next.js routes. Workspace screens load their data through `src/services/liveWorkspaceApi.ts`, which maps FastAPI contracts into the display models. The client does not fall back to fixture data when the API is unavailable.

## Run locally

```bash
pnpm install
pnpm dev
```

Open `http://localhost:3000` and sign in with a real agronomist, enterprise, or admin account. Set `NEXT_PUBLIC_API_URL` before starting the web client.

## Build

```bash
pnpm build
```
