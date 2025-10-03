from app.models.article import Article
from app.repositories.article_repository import ArticleRepository


class ArticleService:
	def __init__(self, article_repo: ArticleRepository):
		self._article_repo = article_repo

	def fetch_article(self, article_id: str, slug: str) -> Article | None:
		if article_id:
			self._article_repo.get_article_by_id(article_id)

		if slug:
			pass

		return None


def get_article_service(article_repo: ArticleRepository) -> ArticleService:
	return ArticleService(article_repo)
