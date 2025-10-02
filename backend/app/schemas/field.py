from __future__ import annotations

from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class SubFieldDTO(BaseModel):
    id: UUID
    code: str
    name: str
    sort_order: Optional[int] = None


class FieldDTO(BaseModel):
    id: UUID
    code: str
    name: str
    sort_order: Optional[int] = None
    subfields: List[SubFieldDTO] = Field(default_factory=list)


__all__ = ["FieldDTO", "SubFieldDTO"]

