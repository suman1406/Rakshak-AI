# Rakshak AI web

Next.js App Router shell around the imported Rakshak AI frontend. The imported product views live under `src/screens`; the route-compatible legacy router is mounted by `app/[[...slug]]/page.tsx` so the existing demo flows continue to work while the UI is migrated to native Next.js routes.

## Run locally

```bash
pnpm install
pnpm dev
```

Open `http://localhost:3000`. Demo authentication is local-only and accepts the role-based demo accounts in the login screen. The Next.js conversion is frontend-only; future FastAPI calls should replace `src/services/mockApi.ts` behind the existing types.

## Build

```bash
pnpm build
```

