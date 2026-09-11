import hashlib
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.deps import get_db, require_role
from app.core.audit import write_audit_log
from app.models.identity import User, UserRole
from app.models.contact import ContactInquiry

router = APIRouter(tags=['Contact'])


class InquiryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=3, max_length=320, pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    message: str = Field(min_length=10, max_length=5000)
    consent: Literal[True]

    @field_validator('name', 'email', 'message', mode='before')
    @classmethod
    def strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value


@router.post('/contact', status_code=201)
async def create_inquiry(payload: InquiryCreate, request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    peer = request.client.host if request.client else 'unknown'
    key = hashlib.sha256((settings.JWT_SECRET_KEY + ':' + peer).encode()).hexdigest()
    recent = (await db.execute(select(func.count(ContactInquiry.id)).where(ContactInquiry.request_key == key, ContactInquiry.created_at > datetime.now(timezone.utc) - timedelta(hours=1)))).scalar()
    if recent >= 10:
        raise HTTPException(status_code=429, detail='Too many messages. Please try again later.')
    inquiry = ContactInquiry(name=payload.name, email=payload.email, message=payload.message, request_key=key)
    db.add(inquiry); await db.commit(); await db.refresh(inquiry)
    return {'reference': inquiry.id, 'message': 'Your request is saved for the Rakshak team.'}


@router.get('/admin/inquiries')
async def list_inquiries(current_user: Annotated[User, Depends(require_role(UserRole.admin))], db: Annotated[AsyncSession, Depends(get_db)]):
    records = (await db.execute(select(ContactInquiry).order_by(ContactInquiry.created_at.desc()).limit(200))).scalars().all()
    return [{'id': item.id, 'name': item.name, 'email': item.email, 'message': item.message, 'status': item.status, 'created_at': item.created_at} for item in records]


@router.post('/admin/inquiries/{inquiry_id}/close')
async def close_inquiry(inquiry_id: str, current_user: Annotated[User, Depends(require_role(UserRole.admin))], db: Annotated[AsyncSession, Depends(get_db)]):
    inquiry = await db.get(ContactInquiry, inquiry_id)
    if not inquiry:
        raise HTTPException(status_code=404, detail='Request not found')
    inquiry.status = 'closed'
    await write_audit_log(db, actor_user_id=current_user.id, action='inquiry.closed', entity_type='inquiry', entity_id=inquiry.id)
    await db.commit()
    return {'status': 'closed'}
