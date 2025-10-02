from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, UUID, Text, ARRAY, ForeignKey, Boolean, BigInteger, UniqueConstraint, Integer
from sqlalchemy.dialects.postgresql import JSONB, ENUM

from app.db.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime

# Enums
block_type_enum = ENUM(
	"title", "paragraph", "subheading", "quote", "image",
	name="block_type", create_type=False
)

class Article(Base):
	__tablename__ = "articles"

	id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
	paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
	title = Column(Text, nullable=False)
	slug = Column(Text, unique=True, nullable=False)
	status = Column(Text)
	featured_image_url = Column(Text)
	is_edited = Column(Boolean, default=False, nullable=False)
	view_count = Column(BigInteger, default=0, nullable=False)
	engagement_metrics = Column(JSONB)
	created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
	updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

	# Relationships
	paper = relationship("Paper", back_populates="articles")
	blocks = relationship("ArticleBlock", back_populates="article", cascade="all, delete-orphan")
	prompts = relationship("ArticlePrompt", back_populates="article", cascade="all, delete-orphan")


class ArticleBlock(Base):
	__tablename__ = "article_blocks"
	__table_args__ = (UniqueConstraint("article_id", "order_index", name="uq_article_block_order"),)

	id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
	article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
	block_type = Column(block_type_enum, nullable=False)
	content = Column(Text)
	order_index = Column(Integer, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
	updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

	# Relationships
	article = relationship("Article", back_populates="blocks")
