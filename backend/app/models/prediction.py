import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, JSON, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base import Base

class DetectionClass(str, enum.Enum):
    plant = "plant"
    leaf = "leaf"
    diseased_leaf = "diseased_leaf"
    lesion = "lesion"
    stem = "stem"
    pod = "pod"

class ConfidenceBand(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"

class DecisionAuthorityStatus(str, enum.Enum):
    advisory_only = "advisory_only"
    human_confirmed = "human_confirmed"

class Detection(Base):
    __tablename__ = "detections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    frame_id: Mapped[str] = mapped_column(String(36), ForeignKey("frames.id"), nullable=False, index=True)
    bbox: Mapped[dict] = mapped_column(JSON, nullable=False)  # {"x": 0.12, "y": 0.34, "w": 0.10, "h": 0.08}
    detection_class: Mapped[DetectionClass] = mapped_column(Enum(DetectionClass), nullable=False)
    detector_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    detector_model_version: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    frame: Mapped["Frame"] = relationship("Frame", back_populates="detections")
    diagnoses: Mapped[list["FrameDiagnosis"]] = relationship("FrameDiagnosis", back_populates="detection", cascade="all, delete-orphan")

class FrameDiagnosis(Base):
    __tablename__ = "frame_diagnoses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    detection_id: Mapped[str] = mapped_column(String(36), ForeignKey("detections.id"), nullable=False, index=True)
    probability_distribution: Mapped[dict] = mapped_column(JSON, nullable=False)
    classifier_model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    detection: Mapped[Detection] = relationship("Detection", back_populates="diagnoses")

class VideoDiagnosis(Base):
    __tablename__ = "video_diagnoses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id: Mapped[str] = mapped_column(String(36), ForeignKey("videos.id"), nullable=False, index=True)
    disease_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("diseases.id"), nullable=True, index=True)
    is_unknown: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_band: Mapped[ConfidenceBand] = mapped_column(Enum(ConfidenceBand), nullable=False)
    severity_level: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)  # 0 to 3
    affected_plant_estimate: Mapped[float | None] = mapped_column(Float, nullable=True)
    supporting_frames: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_frames: Mapped[int | None] = mapped_column(Integer, nullable=True)
    aggregation_model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    decision_authority: Mapped[DecisionAuthorityStatus] = mapped_column(
        Enum(DecisionAuthorityStatus),
        nullable=False,
        default=DecisionAuthorityStatus.advisory_only
    )
    explanation: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    video: Mapped["Video"] = relationship("Video", back_populates="diagnoses")
    disease: Mapped["Disease | None"] = relationship("Disease", back_populates="diagnoses")
    verified_labels: Mapped[list["VerifiedLabel"]] = relationship("VerifiedLabel", back_populates="video_diagnosis")
    feedback: Mapped[list["Feedback"]] = relationship("Feedback", back_populates="video_diagnosis")
