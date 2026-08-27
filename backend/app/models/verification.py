import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base import Base

class SourceChannel(str, enum.Enum):
    neutral_agronomist = "neutral_agronomist"
    insurer = "insurer"
    input_company = "input_company"
    bank = "bank"
    other_commercial = "other_commercial"

class CorrectionType(str, enum.Enum):
    disease_change = "disease_change"
    healthy_override = "healthy_override"
    severity_change = "severity_change"
    other = "other"

class VerifiedLabel(Base):
    __tablename__ = "verified_labels"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_diagnosis_id: Mapped[str] = mapped_column(String(36), ForeignKey("video_diagnoses.id"), nullable=False, index=True)
    agronomist_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    disease_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("diseases.id"), nullable=True)
    is_healthy_override: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    severity_level: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    affected_plant_estimate_independent: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_channel: Mapped[SourceChannel] = mapped_column(Enum(SourceChannel), default=SourceChannel.neutral_agronomist, nullable=False, index=True)
    consensus_group_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    is_gold: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_blind_relabel: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_suggestion_was_shown: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    video_diagnosis: Mapped["VideoDiagnosis"] = relationship("VideoDiagnosis", back_populates="verified_labels")
    agronomist: Mapped["User"] = relationship("User")
    disease: Mapped["Disease | None"] = relationship("Disease")

class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_diagnosis_id: Mapped[str] = mapped_column(String(36), ForeignKey("video_diagnoses.id"), nullable=False, index=True)
    farmer_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    correction_type: Mapped[CorrectionType] = mapped_column(Enum(CorrectionType), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    trust_weight: Mapped[float] = mapped_column(Float, default=0.2, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    video_diagnosis: Mapped["VideoDiagnosis"] = relationship("VideoDiagnosis", back_populates="feedback")
    farmer: Mapped["User"] = relationship("User")
