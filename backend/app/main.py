from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import farm, identity, video, prediction, verification, governance  # Register models with Base.metadata
from .api.v1.router import api_router
from .core.config import settings
from .core.logging import RequestLoggingMiddleware, logger
from .db.base import Base
from .db.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Fasal Rakshak API...")
    # Initialize DB tables for local/dev/prod SQLite execution
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
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

# Middlewares
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
