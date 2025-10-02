from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db


class ArticleRepository:
	def __init__(self, db: Session):
		self._db = db

	def get_article_by_id(self, article_id):
		pass


def get_article_repository(db: Session = Depends(get_db)) -> ArticleRepository:
	return ArticleRepository(db)
