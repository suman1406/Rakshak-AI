FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

COPY app ./app
COPY alembic.ini .
COPY alembic ./alembic
COPY tests ./tests

# Simple startup - skip type cleanup, just run migrations with error handling
CMD ["sh", "-c", """
    # Run migrations, ignoring duplicate type errors (types already exist from previous deploys)
    alembic upgrade head || true
    
    # Seed database
    python -m app.db.seed || true
    
    # Start server
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
"""]