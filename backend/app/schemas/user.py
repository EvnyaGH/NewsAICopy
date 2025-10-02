from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class RoleDTO(BaseModel):
    # Assuming your Role DB model has at least an 'id' and 'name'
    # Adjust these fields based on your actual Role DB model
    id: UUID
    name: str

    class Config:
        from_attributes = True


class UserDTO(BaseModel):
    id: UUID
    email: EmailStr
    display_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    profile_image_url: str | None = None
    roles: list = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    roles: list[RoleDTO] = Field(default_factory=list)  # Changed to list[RoleDTO]

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    email_verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True
