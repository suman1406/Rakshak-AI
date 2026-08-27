from fastapi import APIRouter
from .admin import router as admin_router
from .agronomist import router as agronomist_router
from .auth import router as auth_router
from .b2b import router as b2b_router
from .diagnosis import router as diagnosis_router
from .farms import router as farms_router
from .fields import router as fields_router
from .videos import router as videos_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(farms_router)
api_router.include_router(fields_router)
api_router.include_router(videos_router)
api_router.include_router(diagnosis_router)
api_router.include_router(agronomist_router)
api_router.include_router(b2b_router)
api_router.include_router(admin_router)
