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

# Create startup script
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'psql "$DATABASE_URL" -c "DROP TYPE IF EXISTS reviewstatus CASCADE;" || true' >> /app/start.sh && \
    echo 'psql "$DATABASE_URL" -c "DROP TYPE IF EXISTS videostatus CASCADE;" || true' >> /app/start.sh && \
    echo 'psql "$DATABASE_URL" -c "DROP TYPE IF EXISTS confidenceband CASCADE;" || true' >> /app/start.sh && \
    echo 'psql "$DATABASE_URL" -c "DROP TYPE IF EXISTS decisionauthoritystatus CASCADE;" || true' >> /app/start.sh && \
    echo 'psql "$DATABASE_URL" -c "DROP TYPE IF EXISTS userrole CASCADE;" || true' >> /app/start.sh && \
    echo 'alembic upgrade head' >> /app/start.sh && \
    echo 'python -m app.db.seed' >> /app/start.sh && \
    echo 'python -m uvicorn app.main:app --host 0.0.0.0 --port 8000' >> /app/start.sh && \
    chmod +x /app/start.sh

CMD ["/app/start.sh"]