from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.deps import get_current_user, get_db
from ...core.security import create_access_token, create_refresh_token, get_password_hash, verify_password
from ...models.identity import User, UserRole
from ...schemas.auth import TokenResponse, UserLogin, UserOut, UserRegister

router = APIRouter(prefix="/auth", tags=["Auth"])

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
        role=payload.role,
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
        # Demo fallback for frictionless local testing
        if payload.email_or_phone.startswith("demo-") or payload.email_or_phone == "demo@rakshak.ai":
            user = User(
                id="demo-user",
                email="demo@rakshak.ai",
                password_hash="demo",
                role=UserRole.farmer,
                display_name="Demo Farmer",
            )
        else:
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

@router.get("/me", response_model=UserOut)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
