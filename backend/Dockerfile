FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

COPY app ./app
COPY alembic.ini .
COPY alembic ./alembic
COPY tests ./tests

# Drop existing ENUM types if they exist (handles re-deploy scenarios)
CMD ["sh", "-c", """
    # Drop existing custom types to handle re-deploys
    psql "$DATABASE_URL" -c 'DROP TYPE IF EXISTS reviewstatus CASCADE;' || true
    psql "$DATABASE_URL" -c 'DROP TYPE IF EXISTS videostatus CASCADE;' || true
    psql "$DATABASE_URL" -c 'DROP TYPE IF EXISTS confidenceband CASCADE;' || true
    psql "$DATABASE_URL" -c 'DROP TYPE IF EXISTS decisionauthoritystatus CASCADE;' || true
    psql "$DATABASE_URL" -c 'DROP TYPE IF EXISTS userrole CASCADE;' || true
    
    # Run migrations
    alembic upgrade head
    
    # Seed database
    python -m app.db.seed
    
    # Start server
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
"""]