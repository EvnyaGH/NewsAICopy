from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.common import SuccessResponse

router = APIRouter()


class Health(BaseModel):
    status: str


@router.get(
    "/health",
    summary="Service health",
    description="Returns a simple status map to indicate the service is running.",
    response_model=SuccessResponse[Health],
)
def health() -> SuccessResponse[Health]:
    return SuccessResponse(code=200, data=Health(status="ok"))
