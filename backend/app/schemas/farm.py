from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field as PydanticField

class CropOut(BaseModel):
    id: str
    name: str
    taxonomy_version: str

    model_config = ConfigDict(from_attributes=True)

class DiseaseOut(BaseModel):
    id: str
    crop_id: str
    name: str
    taxonomy_version: str

    model_config = ConfigDict(from_attributes=True)

class FarmCreate(BaseModel):
    name: str = PydanticField(min_length=1, max_length=255)
    state: str | None = None
    district: str | None = None

class FarmOut(BaseModel):
    id: str
    owner_user_id: str
    name: str
    state: str | None = None
    district: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FieldCreate(BaseModel):
    name: str = PydanticField(min_length=1, max_length=255)
    crop_id: str | None = None
    area_hectares: float | None = None

class FieldOut(BaseModel):
    id: str
    farm_id: str
    name: str
    crop_id: str | None = None
    area_hectares: float | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FieldHealthScoreOut(BaseModel):
    field_id: str
    fasal_health_score: int
    components: dict[str, float]
    zones: list[dict]
    latest_diagnosis_summary: dict | None = None
