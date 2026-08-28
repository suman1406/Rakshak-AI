import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base import Base

class VideoStatus(str, enum.Enum):
    uploaded = "uploaded"
    validating = "validating"
    processing = "processing"
    analyzing = "analyzing"
    aggregating = "aggregating"
    ready = "ready"
    failed = "failed"
    insufficient_evidence = "insufficient_evidence"

class Video(Base):
    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    field_id: Mapped[str] = mapped_column(String(36), ForeignKey("fields.id"), nullable=False, index=True)
    uploaded_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    status: Mapped[VideoStatus] = mapped_column(Enum(VideoStatus), nullable=False, default=VideoStatus.uploaded, index=True)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    gps_geohash: Mapped[str | None] = mapped_column(String(12), nullable=True)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    device_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    total_frames_extracted: Mapped[int | None] = mapped_column(Integer, nullable=True)
    usable_frames_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    job_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    job_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_failure_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    field: Mapped["Field"] = relationship("Field", back_populates="videos")
    frames: Mapped[list["Frame"]] = relationship("Frame", back_populates="video", cascade="all, delete-orphan")
    diagnoses: Mapped[list["VideoDiagnosis"]] = relationship("VideoDiagnosis", back_populates="video", cascade="all, delete-orphan")

class Frame(Base):
    __tablename__ = "frames"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id: Mapped[str] = mapped_column(String(36), ForeignKey("videos.id"), nullable=False, index=True)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    blur_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    exposure_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_selected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sequence_index: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    video: Mapped[Video] = relationship("Video", back_populates="frames")
    detections: Mapped[list["Detection"]] = relationship("Detection", back_populates="frame", cascade="all, delete-orphan")
