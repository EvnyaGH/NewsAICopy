from __future__ import annotations

from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AddInterestRequest(BaseModel):
	field_id: UUID

	class Config:
		from_attributes = True


class RemoveInterestRequest(BaseModel):
    field_id: UUID

    class Config:
        from_attributes = True


class MessageDTO(BaseModel):
    message: str


class InterestSubFieldDTO(BaseModel):
    id: UUID
    code: str
    name: str
    sort_order: Optional[int] = None


class InterestFieldDTO(BaseModel):
    id: UUID
    code: str
    name: str
    sort_order: Optional[int] = None
    subfields: List[InterestSubFieldDTO] = Field(default_factory=list)


__all__ = [
    "AddInterestRequest",
    "RemoveInterestRequest",
    "MessageDTO",
    "InterestFieldDTO",
    "InterestSubFieldDTO",
]
