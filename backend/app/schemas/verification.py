from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field as PydanticField
from ..models.verification import SourceChannel

class VerifyCreate(BaseModel):
    disease_id: str | None = None
    is_healthy_override: bool = False
    severity_level: int = PydanticField(ge=0, le=3, default=1)
    affected_plant_estimate_independent: float = PydanticField(ge=0.0, le=1.0)
    source_channel: SourceChannel = SourceChannel.neutral_agronomist
    is_blind_relabel: bool = False

class VerifiedLabelOut(BaseModel):
    id: str
    video_diagnosis_id: str
    agronomist_id: str
    disease_id: str | None = None
    is_healthy_override: bool
    severity_level: int | None = None
    affected_plant_estimate_independent: float | None = None
    source_channel: SourceChannel
    is_gold: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AgronomistQueueItem(BaseModel):
    video_diagnosis_id: str
    video_id: str
    field_id: str
    crop: str
    disease_name: str
    confidence: float
    confidence_band: str
    severity: str
    created_at: datetime
