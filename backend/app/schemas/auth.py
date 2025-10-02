from __future__ import annotations

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    display_name: str
    roles: list[str]


class VerifyEmailRequest(BaseModel):
    token: str


class ResendEmailVerificationRequest(BaseModel):
    email: EmailStr
    password: str
