# Rakshak AI

Fasal Rakshak is a video intelligence pilot for soybean crop health. The repository contains a Next.js web surface, a Flutter mobile farmer app, and a FastAPI/Python processing backend.

## Repository

- `frontend/web`: public landing page and role dashboards.
- `frontend/mobile`: Flutter farmer mobile app.
- `backend`: FastAPI API, background worker, and model pipeline adapters.

## Local run

1. Copy `.env.example` to `.env` and provide storage/model credentials.
2. Start infrastructure with `docker compose up --build`.
3. Run the web app with `cd frontend/web; pnpm install; pnpm dev`.
4. Run the mobile app with `cd frontend/mobile; flutter pub get; flutter run`.
5. Run backend tests with `cd backend; python -m pytest`.

The baseline pipeline is intentionally conservative: it reports visual indications, never confirmed diagnoses, and uses a model adapter so validated weights can be added later.

