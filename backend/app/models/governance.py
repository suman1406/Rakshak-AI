import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Enum, ForeignKey, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base import Base

class DeploymentStatus(str, enum.Enum):
    shadow = "shadow"
    canary = "canary"
    production = "production"
    retired = "retired"

class GoldenSubset(str, enum.Enum):
    frozen_regression = "frozen_regression"
    refreshed = "refreshed"

class DatasetSplit(str, enum.Enum):
    train = "train"
    val = "val"
    test = "test"

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    version_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    training_dataset_version: Mapped[str] = mapped_column(String(100), nullable=False)
    eval_metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    deployment_status: Mapped[DeploymentStatus] = mapped_column(
        Enum(DeploymentStatus),
        default=DeploymentStatus.shadow,
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (UniqueConstraint("model_name", "version_hash", name="uq_model_versions_name_hash"),)

class GoldenSetItem(Base):
    __tablename__ = "golden_set_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id: Mapped[str] = mapped_column(String(36), ForeignKey("videos.id"), nullable=False, index=True)
    subset: Mapped[GoldenSubset] = mapped_column(Enum(GoldenSubset), nullable=False, index=True)
    set_version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    video: Mapped["Video"] = relationship("Video")

class DatasetSplitItem(Base):
    __tablename__ = "dataset_splits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id: Mapped[str] = mapped_column(String(36), ForeignKey("videos.id"), nullable=False, index=True)
    split: Mapped[DatasetSplit] = mapped_column(Enum(DatasetSplit), nullable=False)
    split_version: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (UniqueConstraint("video_id", "split_version", name="uq_dataset_splits_video_version"),)
    video: Mapped["Video"] = relationship("Video")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
