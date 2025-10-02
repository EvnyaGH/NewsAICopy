from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.deps.auth import get_current_user
from app.exceptions.exceptions import UserDoesNotExist
from app.models import User
from app.schemas.common import SuccessResponse
from app.schemas.interest import (
    AddInterestRequest,
    RemoveInterestRequest,
    MessageDTO,
    InterestFieldDTO,
)
from app.services.interest_service import InterestService, get_interest_service

router = APIRouter()


@router.get(
	"/",
	status_code=status.HTTP_200_OK,
	summary="Retrieve a user's interests.",
	response_model=SuccessResponse[list[InterestFieldDTO]],
)
def get_interests(
		current_user: User = Depends(get_current_user),
		interest_service: InterestService = Depends(get_interest_service)
) -> SuccessResponse[list[InterestFieldDTO]]:
	if current_user is None:
		raise UserDoesNotExist("Invalid session")

	if current_user.id is None:
		raise UserDoesNotExist("user_id does not exist")

	data = interest_service.get_interests(current_user.id)
	return SuccessResponse(code=200, data=data or [])


@router.post(
	"/",
	status_code=status.HTTP_200_OK,
	summary="Add a field to a user's interests.",
	response_model=SuccessResponse[MessageDTO],
)
def add_interests(
		request: AddInterestRequest,
		current_user: User = Depends(get_current_user),
		interest_service: InterestService = Depends(get_interest_service)
) -> SuccessResponse[MessageDTO]:
	if current_user is None:
		raise UserDoesNotExist("Invalid session")

	if current_user.id is None:
		raise UserDoesNotExist("user_id does not exist")

	data = interest_service.create_interest(current_user.id, request.field_id)
	return SuccessResponse(code=200, data=data)


@router.delete(
	"/",
	status_code=status.HTTP_200_OK,
	summary="Delete a field from a user's interests.",
	response_model=SuccessResponse[MessageDTO],
)
def remove_interests(
		request: RemoveInterestRequest,
		current_user: User = Depends(get_current_user),
		interest_service: InterestService = Depends(get_interest_service)
) -> SuccessResponse[MessageDTO]:
	if current_user is None:
		raise UserDoesNotExist("Invalid session")

	if current_user.id is None:
		raise UserDoesNotExist("user_id does not exist")

	data = interest_service.delete_interest(current_user.id, request.field_id)
	return SuccessResponse(code=200, data=data)
