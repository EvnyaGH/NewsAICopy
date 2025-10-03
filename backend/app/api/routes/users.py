from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserDTO

router = APIRouter()


@router.get("/me", response_model=UserDTO, summary="Get current user")
def read_users_me(
        current_user: User = Depends(get_current_user),
) -> UserDTO:
    user_dto = UserDTO.model_validate(current_user)
    return user_dto
