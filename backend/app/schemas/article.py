from pydantic import BaseModel


class ArticleDTO(BaseModel):
	class Config:
		from_attributes = True
