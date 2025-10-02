from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel


T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    code: int
    data: T


class ErrorResponse(BaseModel):
    code: int
    title: str
    message: str


__all__ = ["SuccessResponse", "ErrorResponse"]
