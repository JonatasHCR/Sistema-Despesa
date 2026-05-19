FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /backend

# asyncpg é puro Python — não precisamos de gcc/libpq.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app
COPY main.py ./

# Usuário não-root
RUN groupadd --system app && useradd --system --gid app --home /backend app \
    && chown -R app:app /backend
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl --fail --silent http://localhost:8000/documentation > /dev/null || exit 1

# Migrations + uvicorn juntos. Em dev (override.yml) o reload é controlado por UVICORN_RELOAD.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn main:app --host 0.0.0.0 --port 8000 ${UVICORN_RELOAD:+--reload}"]
