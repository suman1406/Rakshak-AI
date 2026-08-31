from pydantic import BaseModel, ConfigDict, Field, field_validator
from ..models.identity import UserRole


class UserRegister(BaseModel):
    """Public self-service registration payload.

    Public registration is deliberately farmer-only. Privileged roles must be
    created through an authorized organization membership flow.
    """

    model_config = ConfigDict(extra="forbid")

    email: str | None = None
    phone: str | None = None
    password: str = Field(min_length=8, max_length=72)
    role: UserRole = UserRole.farmer
    display_name: str | None = Field(default=None, max_length=255)

    @field_validator("role")
    @classmethod
    def validate_public_role(cls, value: UserRole) -> UserRole:
        if value != UserRole.farmer:
            raise ValueError("Public registration can only create farmer accounts")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if not normalized or "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("A valid email address is required")
        return normalized

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized or len(normalized) > 50:
            raise ValueError("A valid phone number is required")
        return normalized

class UserLogin(BaseModel):
    email_or_phone: str
    password: str

class UserUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=255)
    phone: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return UserRegister.validate_phone(value)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: UserRole
    user_id: str

class UserOut(BaseModel):
    id: str
    email: str | None = None
    phone: str | None = None
    role: UserRole
    org_id: str | None = None
    display_name: str | None = None

    model_config = ConfigDict(from_attributes=True)
