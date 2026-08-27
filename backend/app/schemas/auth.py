from pydantic import BaseModel, ConfigDict
from ..models.identity import UserRole

class UserRegister(BaseModel):
    email: str | None = None
    phone: str | None = None
    password: str
    role: UserRole = UserRole.farmer
    display_name: str | None = None

class UserLogin(BaseModel):
    email_or_phone: str
    password: str

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
