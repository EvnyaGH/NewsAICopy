from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, UUID, Text, ARRAY, ForeignKey, Boolean, BigInteger, UniqueConstraint, Integer
from sqlalchemy.dialects.postgresql import JSONB, ENUM

from app.db.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime

prompt_type_enum = ENUM(
	"article", "image", "video", "text-to-speech",
	name="prompt_type", create_type=False
)


class Prompt(Base):
	__tablename__ = "prompts"

	id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
	name = Column(Text, nullable=False)
	type = Column(prompt_type_enum, nullable=False)
	image_generation_prompt = Column(Text)
	description = Column(Text)
	created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
	updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

	# Relationships
	articles = relationship("ArticlePrompt", back_populates="prompt")


class ArticlePrompt(Base):
	__tablename__ = "article_prompts"
	__table_args__ = (UniqueConstraint("article_id", "prompt_id", name="uq_article_prompt"),)

	id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
	article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
	prompt_id = Column(UUID(as_uuid=True), ForeignKey("prompts.id", ondelete="RESTRICT"), nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

	# Relationships
	article = relationship("Article", back_populates="prompts")
	prompt = relationship("Prompt", back_populates="articles")
