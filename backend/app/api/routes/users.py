from fastapi import APIRouter, Depends

from app.api.deps.auth import get_current_user
from app.models.user import User
from app.schemas import SuccessResponse
from app.schemas.user import UserDTO

router = APIRouter()


@router.get("/me", response_model=SuccessResponse[UserDTO], summary="Get current user")
def read_users_me(
		current_user: User = Depends(get_current_user),
	) -> SuccessResponse[UserDTO]:
	user_dto = UserDTO.model_validate(current_user)
	return SuccessResponse(code=200, data=user_dto)
