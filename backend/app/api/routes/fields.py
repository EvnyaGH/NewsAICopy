from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.schemas.common import SuccessResponse
from app.schemas.field import FieldDTO
from app.services.field_service import FieldService, get_field_service

router = APIRouter()


@router.get(
	"/",
	status_code=status.HTTP_200_OK,
	summary="Retrieve all fields with sub-fields.",
	response_model=SuccessResponse[list[FieldDTO]],
)
def get_fields(field_service: FieldService = Depends(get_field_service)) -> SuccessResponse[list[FieldDTO]]:
	data = field_service.get()
	return SuccessResponse(code=200, data=data)
