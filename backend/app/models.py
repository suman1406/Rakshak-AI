from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field as PydanticField

class Role(str, Enum):
    farmer = "farmer"
    agronomist = "agronomist"
    admin = "admin"

class User(BaseModel):
    id: str
    email: str
    role: Role
    organization_id: str | None = None

class FieldCreate(BaseModel):
    name: str = PydanticField(min_length=1, max_length=120)
    crop: str = "soybean"

class Field(FieldCreate):
    id: str
    owner_id: str

class VideoCreate(BaseModel):
    field_id: str
    filename: str
    consent: bool

class Video(BaseModel):
    id: str
    field_id: str
    status: str
    filename: str
    created_at: datetime

class Diagnosis(BaseModel):
    crop: str = "soybean"
    disease: str = "soybean_rust"
    confidence: float
    confidence_band: str
    severity: str
    affected_plant_estimate: float
    evidence: dict[str, Any]
    recommendation: dict[str, Any]
    explanation: str

class Feedback(BaseModel):
    label: str = PydanticField(pattern="^(confirm|change|healthy|uncertain)$")
    note: str = ""
