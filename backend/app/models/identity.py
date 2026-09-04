import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base import Base

class UserRole(str, enum.Enum):
    farmer = "farmer"
    agronomist = "agronomist"
    admin = "admin"
    enterprise = "enterprise"


class AccountStatus(str, enum.Enum):
    active = "active"
    pending = "pending"
    rejected = "rejected"

class OrgType(str, enum.Enum):
    fpo = "fpo"
    insurer = "insurer"
    input_company = "input_company"
    bank = "bank"
    gov = "gov"
    research = "research"
    other = "other"

class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    org_type: Mapped[OrgType] = mapped_column(Enum(OrgType), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    users: Mapped[list["User"]] = relationship("User", back_populates="organization")

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), unique=True, index=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.farmer)
    org_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Stored as text rather than a database enum so account decisions can be
    # migrated safely across the existing PostgreSQL deployments.
    account_status: Mapped[str] = mapped_column(String(16), nullable=False, default=AccountStatus.active.value, index=True)
    consent_accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    organization: Mapped[Organization | None] = relationship("Organization", back_populates="users")
    farms: Mapped[list["Farm"]] = relationship("Farm", back_populates="owner")
    onboarding_application: Mapped["OnboardingApplication | None"] = relationship(
        "OnboardingApplication", back_populates="applicant", foreign_keys="OnboardingApplication.applicant_user_id", uselist=False
    )


class OnboardingApplication(Base):
    __tablename__ = "onboarding_applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    applicant_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    application_type: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default=AccountStatus.pending.value, index=True)
    organization_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    requested_org_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    requested_plan_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reviewer_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    applicant: Mapped[User] = relationship("User", back_populates="onboarding_application", foreign_keys=[applicant_user_id])
    reviewer: Mapped[User | None] = relationship("User", foreign_keys=[reviewer_user_id])
