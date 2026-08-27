from fastapi import APIRouter
from .auth import router as auth_router
from .farms import router as farms_router
from .fields import router as fields_router
from .videos import router as videos_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(farms_router)
api_router.include_router(fields_router)
api_router.include_router(videos_router)
