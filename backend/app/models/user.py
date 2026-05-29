from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    reviewer = "reviewer"
    senior_reviewer = "senior_reviewer"
    administrator = "administrator"
    compliance_officer = "compliance_officer"
    operations = "operations"
    vendor_user = "vendor_user"


# In-memory user store (replace with DB in production)
USERS_DB: dict[str, dict] = {
    "admin@idp.local": {
        "user_id": "usr_001",
        "email": "admin@idp.local",
        "display_name": "Admin User",
        "role": UserRole.administrator,
        "hashed_password": "",  # set on startup
        "is_active": True,
    },
    "reviewer@idp.local": {
        "user_id": "usr_002",
        "email": "reviewer@idp.local",
        "display_name": "Reviewer User",
        "role": UserRole.reviewer,
        "hashed_password": "",
        "is_active": True,
    },
}


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserOut"


class UserOut(BaseModel):
    user_id: str
    email: str
    display_name: str
    role: UserRole
    is_active: bool


TokenResponse.model_rebuild()
