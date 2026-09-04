from contextlib import asynccontextmanager
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
from app.db.session import async_session_factory, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Fasal Rakshak API...")
    # Initialize DB tables
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
    logger.info("Database schema initialized successfully.")
    yield
    logger.info("Shutting down Fasal Rakshak API...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
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

# API v1 Routers
app.include_router(api_router, prefix=settings.API_V1_STR)
