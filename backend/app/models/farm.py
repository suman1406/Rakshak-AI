import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base import Base

class Crop(Base):
    __tablename__ = "crops"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    taxonomy_version: Mapped[str] = mapped_column(String(50), nullable=False, default="v1.0")
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (UniqueConstraint("name", "taxonomy_version", name="uq_crops_name_version"),)
    diseases: Mapped[list["Disease"]] = relationship("Disease", back_populates="crop")
    fields: Mapped[list["Field"]] = relationship("Field", back_populates="crop")

class Disease(Base):
    __tablename__ = "diseases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    crop_id: Mapped[str] = mapped_column(String(36), ForeignKey("crops.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    taxonomy_version: Mapped[str] = mapped_column(String(50), nullable=False, default="v1.0")
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (UniqueConstraint("crop_id", "name", "taxonomy_version", name="uq_diseases_crop_name_version"),)
    crop: Mapped[Crop] = relationship("Crop", back_populates="diseases")
    diagnoses: Mapped[list["VideoDiagnosis"]] = relationship("VideoDiagnosis", back_populates="disease")

class Farm(Base):
    __tablename__ = "farms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    org_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="farms")
    fields: Mapped[list["Field"]] = relationship("Field", back_populates="farm")

class Field(Base):
    __tablename__ = "fields"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_id: Mapped[str] = mapped_column(String(36), ForeignKey("farms.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    crop_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("crops.id"), nullable=True)
    area_hectares: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    farm: Mapped[Farm] = relationship("Farm", back_populates="fields")
    crop: Mapped[Crop | None] = relationship("Crop", back_populates="fields")
    videos: Mapped[list["Video"]] = relationship("Video", back_populates="field")
