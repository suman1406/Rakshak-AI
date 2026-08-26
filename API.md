# Rakshak AI API contract

The Next.js web client and Flutter mobile client use the same FastAPI base URL. Responses are JSON and all protected requests will carry a bearer token once persistent auth is wired to the deployment.

## Core flow

1. `POST /api/v1/auth/login`
2. `POST /api/v1/fields`
3. `POST /api/v1/videos`
4. Poll `GET /api/v1/videos/{video_id}/status`
5. Read `GET /api/v1/videos/{video_id}/analysis`
6. Submit `POST /api/v1/diagnosis/{analysis_id}/feedback`
7. Agronomists submit `POST /api/v1/diagnosis/{analysis_id}/verify`

The analysis response contains crop, disease, confidence, confidence band, severity, affected-plant estimate, evidence counts, evidence-frame references, recommendation, and a guarded explanation. `high` means at least 90%, `medium` means 70 to 89%, and `low` means below 70%.

## Safety

The report must use “possible” or “consistent with” language. A low-confidence result is an inability to confidently classify the condition and must not be presented as a diagnosis.

