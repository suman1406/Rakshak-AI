from contextlib import asynccontextmanager
import asyncio
from contextlib import suppress
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Explicit absolute imports for robust container execution
from app.models import billing, farm, identity, video, prediction, verification, governance  # Register all models with Base.metadata
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import RequestLoggingMiddleware, logger
from app.db.base import Base
from app.db.bootstrap_accounts import ensure_bootstrap_access_accounts, ensure_initial_admin_account
from app.db.catalog import ensure_disease_catalog
from app.db.plans import ensure_launch_plans
from app.db.session import async_session_factory, engine
from app.media_storage import media_storage


async def maintain_evidence_cache():
    # Every API host owns its cache; a worker's retention job cannot clean it.
    while True:
        try:
            await asyncio.to_thread(media_storage.prune_cache)
        except Exception:
            logger.exception('Could not prune local evidence cache')
        await asyncio.sleep(3600)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Fasal Rakshak API...")
    # Deployed environments are migrated by the entrypoint before serving traffic.
    if settings.ENVIRONMENT in ('local', 'development', 'test'):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    if settings.INITIAL_ADMIN_EMAIL or settings.INITIAL_ADMIN_PASSPHRASE:
        if not settings.INITIAL_ADMIN_EMAIL or not settings.INITIAL_ADMIN_PASSPHRASE:
            logger.error("Initial admin configuration is incomplete; no admin account was created.")
        else:
            async with async_session_factory() as session:
                created = await ensure_initial_admin_account(session, settings.INITIAL_ADMIN_EMAIL, settings.INITIAL_ADMIN_PASSPHRASE)
            logger.info("Initial platform-admin account %s.", "created" if created else "already exists")
    if settings.BOOTSTRAP_DEMO_ACCOUNTS:
        if not settings.DEMO_GATE_PASSWORD or settings.DEMO_GATE_PASSWORD == "change-this-demo-password":
            logger.error("Bootstrap accounts were requested but DEMO_GATE_PASSWORD is not configured; no accounts were created.")
        else:
            async with async_session_factory() as session:
                created_accounts = await ensure_bootstrap_access_accounts(session, settings.DEMO_GATE_PASSWORD)
            if created_accounts:
                logger.info("Created bootstrap access accounts: %s", ", ".join(created_accounts))
            else:
                logger.info("Bootstrap access accounts already exist.")
    # Seed disease taxonomy catalog (idempotent — safe on every restart)
    async with async_session_factory() as session:
        await ensure_disease_catalog(session)
        await ensure_launch_plans(session)
    logger.info("Database schema initialized successfully.")
    cache_maintenance = asyncio.create_task(maintain_evidence_cache())
    try:
        yield
    finally:
        cache_maintenance.cancel()
        with suppress(asyncio.CancelledError):
            await cache_maintenance
        await engine.dispose()
    logger.info("Shutting down Fasal Rakshak API...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.2.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


def _error_response(request: Request, status_code: int, message: str, error_code: str, headers: dict[str, str] | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error_code": error_code, "message": message, "request_id": getattr(request.state, "request_id", None)},
        headers=headers,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code = {401: "AUTHENTICATION_REQUIRED", 403: "FORBIDDEN", 404: "NOT_FOUND", 409: "CONFLICT"}.get(exc.status_code, "REQUEST_FAILED")
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return _error_response(request, exc.status_code, message, code, exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return _error_response(request, 422, "Request validation failed", "VALIDATION_ERROR")


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and return proper error with CORS headers."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error_code": "INTERNAL_ERROR", "message": "An internal error occurred"},
    )


# CORS must be the outermost middleware so error responses from logging or a
# route still include the browser's required access-control headers. FastAPI
# wraps middleware in reverse registration order, so it is added last.
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Health Checks (Arch Ref / Backlog FR-P1-05)
@app.get("/healthz", tags=["Health"])
@app.get("/health", tags=["Health"])
async def healthz():
    return {
        "status": "ok",
        "service": "rakshak-api",
        "environment": settings.ENVIRONMENT,
    }

@app.get('/readyz', tags=['Health'])
async def readiness():
    from sqlalchemy import text
    from redis.asyncio import Redis
    database_ready = queue_ready = storage_ready = False
    try:
        async with async_session_factory() as db:
            await db.execute(text('SELECT 1'))
        database_ready = True
    except Exception:
        pass
    redis = Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2, socket_timeout=2)
    try:
        queue_ready = bool(await redis.ping())
    except Exception:
        pass
    finally:
        await redis.aclose()
    try:
        if settings.STORAGE_BACKEND == 's3':
            await asyncio.to_thread(media_storage._client().head_bucket, Bucket=settings.S3_BUCKET_NAME)
        storage_ready = True
    except Exception:
        pass
    return JSONResponse(status_code=200 if database_ready and queue_ready and storage_ready else 503, content={'database': database_ready, 'queue': queue_ready, 'storage': storage_ready})

# API v1 Routers
app.include_router(api_router, prefix=settings.API_V1_STR)
