from pydantic import BaseModel, Field
from enum import Enum


class UserRole(str, Enum):
    reviewer = "reviewer"
    senior_reviewer = "senior_reviewer"
    administrator = "administrator"
    compliance_officer = "compliance_officer"
    operations = "operations"
    vendor_user = "vendor_user"


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str = Field(max_length=254)
    display_name: str = Field(min_length=2, max_length=80, strip_whitespace=True)
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    user_id: str
    email: str
    display_name: str
    role: UserRole
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut
