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

# Create startup script that uses Python to drop types
RUN echo '#!/usr/bin/env python3' > /app/start.py && \
    echo 'import os' >> /app/start.py && \
    echo 'import psycopg' >> /app/start.py && \
    echo 'from psycopg import sql' >> /app/start.py && \
    echo '' >> /app/start.py && \
    echo 'ENUM_TYPES = ["reviewstatus", "videostatus", "confidenceband", "decisionauthoritystatus", "userrole"]' >> /app/start.py && \
    echo '' >> /app/start.py && \
    echo 'def drop_types():' >> /app/start.py && \
    echo '    try:' >> /app/start.py && \
    echo '        conn = psycopg.connect(os.environ.get("DATABASE_URL"))' >> /app/start.py && \
    echo '        cur = conn.cursor()' >> /app/start.py && \
    echo '        for t in ENUM_TYPES:' >> /app/start.py && \
    echo '            try:' >> /app/start.py && \
    echo '                cur.execute(sql.SQL("DROP TYPE IF EXISTS {} CASCADE").format(sql.Identifier(t)))' >> /app/start.py && \
    echo '                print(f"Dropped type: {t}")' >> /app/start.py && \
    echo '            except Exception as e:' >> /app/start.py && \
    echo '                print(f"Could not drop {t}: {e}")' >> /app/start.py && \
    echo '        conn.commit()' >> /app/start.py && \
    echo '        cur.close()' >> /app/start.py && \
    echo '        conn.close()' >> /app/start.py && \
    echo '    except Exception as e:' >> /app/start.py && \
    echo '        print(f"Database connection failed: {e}")' >> /app/start.py && \
    echo '' >> /app/start.py && \
    echo 'if __name__ == "__main__":' >> /app/start.py && \
    echo '    drop_types()' >> /app/start.py

# Create the full startup script
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'python /app/start.py' >> /app/start.sh && \
    echo 'alembic upgrade head' >> /app/start.sh && \
    echo 'python -m app.db.seed' >> /app/start.sh && \
    echo 'python -m uvicorn app.main:app --host 0.0.0.0 --port 8000' >> /app/start.sh && \
    chmod +x /app/start.sh

CMD ["/app/start.sh"]