FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY requirements-storage.txt .
RUN pip install --no-cache-dir -r requirements-storage.txt && apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/app

COPY app ./app
COPY alembic.ini .
COPY alembic ./alembic
COPY tests ./tests
COPY pytest.ini .
COPY scripts ./scripts

RUN groupadd --gid 10001 rakshak && useradd --uid 10001 --gid 10001 --create-home rakshak && mkdir -p /app/storage && chown -R 10001:10001 /app/storage
USER 10001:10001

CMD ["sh", "-c", "alembic upgrade head && exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]
