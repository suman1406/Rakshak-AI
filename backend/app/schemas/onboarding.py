from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.identity import OrgType


class ApplicationCreate(BaseModel):
    """A public application for a role that must be reviewed by a platform admin."""

    model_config = ConfigDict(extra="forbid")

    application_type: Literal["agronomist", "organization"]
    email: str | None = None
    phone: str | None = None
    access_phrase: str = Field(min_length=8, max_length=72)
    display_name: str = Field(min_length=2, max_length=255)
    consent_to_data_processing: bool
    organization_name: str | None = Field(default=None, min_length=2, max_length=255)
    organization_type: OrgType | None = None
    requested_plan_code: str | None = Field(default=None, max_length=50, pattern=r"^[a-z0-9_-]+$")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip().lower()
        if not value or "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("A valid email address is required")
        return value

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value or len(value) > 50:
            raise ValueError("A valid phone number is required")
        return value

    @model_validator(mode="after")
    def validate_application(self):
        if not self.email and not self.phone:
            raise ValueError("Either email or phone is required")
        if not self.consent_to_data_processing:
            raise ValueError("Consent to data processing is required")
        if self.application_type == "organization" and (not self.organization_name or not self.organization_type):
            raise ValueError("Organization name and type are required")
        if self.application_type == "agronomist" and any((self.organization_name, self.organization_type, self.requested_plan_code)):
            raise ValueError("Organization details are only accepted for organization applications")
        return self


class ApplicationDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: Literal["approved", "rejected"]
    review_note: str | None = Field(default=None, max_length=1000)


class PublicPlanOut(BaseModel):
    code: str
    name: str
    monthly_price_paise: int | None
    annual_price_paise: int | None
    farm_limit: int | None
    scan_limit: int | None


class ApplicationReceipt(BaseModel):
    reference: str
    status: Literal["pending"]
    message: str
