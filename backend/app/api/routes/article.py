from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.services.article_service import ArticleService, get_article_service
from app.services.session_service import get_session_service, SessionService

router = APIRouter()


@router.get(
	"/article/{slug}",
	status_code=status.HTTP_200_OK,
	summary="Retrieve an article by slug.",
)
def get_article(slug: str, article_service: ArticleService = Depends(get_article_service)):
	data = article_service.fetch_article("", slug)
	return data
