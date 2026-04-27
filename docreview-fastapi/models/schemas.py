# models/schemas.py  –  Pydantic request & response schemas
# from __future__ import annotations
from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from pydantic import BaseModel

# class AppointmentVerifyRequest(BaseModel):
#     doctor_id: str
#     appointment_date: str

# ── Shared base ───────────────────────────────────────────────
class UserBase(BaseModel):
    name:  str   = Field(..., min_length=2, max_length=80,  examples=["Rohit Bisht"])
    email: EmailStr = Field(...,                             examples=["rohit@example.com"])


# ── Register request ─────────────────────────────────────────
class RegisterRequest(UserBase):
    password: str = Field(..., min_length=6, max_length=72, examples=["mypassword123"])

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @field_validator("name")
    @classmethod
    def name_no_numbers(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^[\w\s.\-']+$", v):
            raise ValueError("Name contains invalid characters")
        return v


# ── Login request ─────────────────────────────────────────────
class LoginRequest(BaseModel):
    email:    EmailStr = Field(..., examples=["rohit@example.com"])
    password: str      = Field(..., examples=["mypassword123"])


# ── Public user profile (returned in responses) ───────────────
class UserPublic(UserBase):
    id:          str
    role:        str
    created_at:  datetime
    last_login:  Optional[datetime] = None
    login_count: int = 0

    model_config = {"from_attributes": True}


# ── Auth response (login / register) ─────────────────────────
class AuthResponse(BaseModel):
    success: bool  = True
    message: str
    token:   str
    user:    UserPublic


# ── Generic success / error responses ────────────────────────
class SuccessResponse(BaseModel):
    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    success: bool  = False
    message: str
    field:   Optional[str] = None


# ── Me response ───────────────────────────────────────────────
class MeResponse(BaseModel):
    success: bool = True
    user:    UserPublic
RegisterRequest.model_rebuild()
LoginRequest.model_rebuild()
UserPublic.model_rebuild()
AuthResponse.model_rebuild()