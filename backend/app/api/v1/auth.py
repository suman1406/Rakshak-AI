from typing import Annotated
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user, get_db
from app.core.security import create_access_token, create_refresh_token, decode_token, get_password_hash, verify_password
from app.models.identity import User, UserRole
from app.schemas.auth import TokenResponse, UserLogin, UserOut, UserRegister

router = APIRouter(prefix="/auth", tags=["Auth"])


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: Annotated[AsyncSession, Depends(get_db)]):
    if not payload.email and not payload.phone:
        raise HTTPException(status_code=400, detail="Either email or phone is required")

    conditions = []
    if payload.email:
        conditions.append(User.email == payload.email)
    if payload.phone:
        conditions.append(User.phone == payload.phone)

    stmt = select(User).where(or_(*conditions))
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=409, detail="User with this email or phone already exists")

    new_user = User(
        email=payload.email,
        phone=payload.phone,
        password_hash=get_password_hash(payload.password),
        role=payload.role or UserRole.farmer,
        display_name=payload.display_name,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: Annotated[AsyncSession, Depends(get_db)]):
    stmt = select(User).where(
        or_(User.email == payload.email_or_phone, User.phone == payload.email_or_phone)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.id, role=user.role.value, org_id=user.org_id)
    refresh_token = create_refresh_token(subject=user.id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role,
        user_id=user.id,
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(payload: RefreshRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        data = decode_token(payload.refresh_token)
        if data.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = data.get("sub")
        stmt = select(User).where(User.id == user_id)
        user = (await db.execute(stmt)).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        new_access_token = create_access_token(subject=user.id, role=user.role.value, org_id=user.org_id)
        return RefreshResponse(access_token=new_access_token)
    except (jwt.PyJWTError, Exception):
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.get("/me", response_model=UserOut)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
