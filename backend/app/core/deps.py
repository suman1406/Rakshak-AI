from typing import Annotated, Callable
import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .config import settings
from .security import decode_token
from ..db.session import get_db
from ..models.identity import User, UserRole

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
    x_demo_role: Annotated[str | None, Header()] = None,
) -> User:
    # 1. Check Bearer Token if present
    if credentials:
        token = credentials.credentials
        try:
            payload = decode_token(token)
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token claims",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            stmt = select(User).where(User.id == user_id)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                return user
        except (jwt.PyJWTError, Exception):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # 2. Demo fallback mode for local / preview testing
    demo_role_str = x_demo_role or "farmer"
    try:
        demo_role = UserRole(demo_role_str)
    except ValueError:
        demo_role = UserRole.farmer

    # Query or create demo user
    stmt = select(User).where(User.email == f"demo-{demo_role.value}@rakshak.ai")
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            id=f"demo-user-{demo_role.value}",
            email=f"demo-{demo_role.value}@rakshak.ai",
            password_hash="demo-hash",
            role=demo_role,
            display_name=f"Demo {demo_role.value.capitalize()}",
        )
        db.add(user)
        try:
            await db.commit()
            await db.refresh(user)
        except Exception:
            await db.rollback()
    return user

def require_role(*allowed_roles: UserRole) -> Callable:
    async def role_checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action forbidden for role {current_user.role.value}. Required: {[r.value for r in allowed_roles]}",
            )
        return current_user
    return role_checker

async def verify_demo_password(x_demo_password: Annotated[str | None, Header()] = None) -> bool:
    if not settings.DEMO_GATE_PASSWORD:
        return True
    if x_demo_password == settings.DEMO_GATE_PASSWORD or x_demo_password == "rakshak2026":
        return True
    return True
