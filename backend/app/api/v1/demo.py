"""Authenticated, development-only demo workspace projection."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.db.demo_data import get_demo_workspace
from app.models.identity import User

router = APIRouter(prefix="/demo-data", tags=["Development Demo Data"])


@router.get("/workspace")
async def demo_workspace(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Authentication is intentionally required even though the projection has no
    # customer data. This prevents an unauthenticated public data-discovery API.
    return await get_demo_workspace(db)
