from typing import Annotated
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user, get_db
from app.core.security import create_access_token, create_refresh_token, decode_token, get_password_hash, verify_password
from app.models.identity import AccountStatus, User, UserRole
from datetime import datetime, timezone
from app.schemas.auth import TokenResponse, UserLogin, UserOut, UserRegister, UserUpdate
from app.core.audit import write_audit_log

router = APIRouter(prefix="/auth", tags=["Auth"])


class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=72)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: Annotated[AsyncSession, Depends(get_db)]):
    if not payload.email and not payload.phone:
        raise HTTPException(status_code=400, detail="Either email or phone is required")
    if not payload.consent_to_data_processing:
        raise HTTPException(status_code=400, detail="Consent to data processing is required")

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
        role=UserRole.farmer,
        display_name=payload.display_name,
        account_status=AccountStatus.active.value,
        consent_accepted_at=datetime.now(timezone.utc),
    )
    db.add(new_user)
    await db.flush()
    await write_audit_log(db, actor_user_id=new_user.id, action="user.registered", entity_type="user", entity_id=new_user.id, metadata={"role": new_user.role.value})
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
    if user.account_status != AccountStatus.active.value:
        detail = "This application is awaiting platform review" if user.account_status == AccountStatus.pending.value else "This account is not approved"
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    access_token = create_access_token(subject=user.id, role=user.role.value, org_id=user.org_id, token_version=user.token_version)
    refresh_token = create_refresh_token(subject=user.id, token_version=user.token_version)
    await write_audit_log(db, actor_user_id=user.id, action="user.logged_in", entity_type="user", entity_id=user.id)
    await db.commit()
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
        if not user or user.account_status != AccountStatus.active.value:
            raise HTTPException(status_code=401, detail="User not found")
        if data.get("version", 0) != user.token_version:
            raise HTTPException(status_code=401, detail="Session has been revoked")
        new_access_token = create_access_token(subject=user.id, role=user.role.value, org_id=user.org_id, token_version=user.token_version)
        return RefreshResponse(access_token=new_access_token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.get("/me", response_model=UserOut)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_me(payload: UserUpdate, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    if payload.training_consent is not None:
        current_user.training_consent = payload.training_consent
        await write_audit_log(db, actor_user_id=current_user.id, action="user.training_consent_changed", entity_type="user", entity_id=current_user.id, metadata={"accepted": payload.training_consent})
    if payload.display_name is not None:
        current_user.display_name = payload.display_name
    if payload.phone is not None and payload.phone != current_user.phone:
        existing = (await db.execute(select(User).where(User.phone == payload.phone, User.id != current_user.id))).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=409, detail="User with this phone already exists")
        current_user.phone = payload.phone
    await write_audit_log(db, actor_user_id=current_user.id, action="user.profile_updated", entity_type="user", entity_id=current_user.id)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.post('/logout-all')
async def logout_all(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    from sqlalchemy import update
    await db.execute(update(User).where(User.id == current_user.id).values(token_version=User.token_version + 1))
    await write_audit_log(db, actor_user_id=current_user.id, action='user.sessions_revoked', entity_type='user', entity_id=current_user.id)
    await db.commit()
    return {'message': 'All sessions have been signed out'}

@router.post('/password')
async def change_password(payload: PasswordChange, current_user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=403, detail='Current password is incorrect')
    if len(payload.new_password.encode('utf-8')) > 72:
        raise HTTPException(status_code=422, detail='Password must be at most 72 UTF-8 bytes')
    current_user.password_hash = get_password_hash(payload.new_password)
    current_user.token_version += 1
    await write_audit_log(db, actor_user_id=current_user.id, action='user.password_changed', entity_type='user', entity_id=current_user.id)
    await db.commit()
    return {'message': 'Password changed. Sign in again on each device.'}
