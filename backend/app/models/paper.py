from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, UUID, Text, ARRAY
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime


class Paper(Base):
	__tablename__ = "papers"

	id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
	title = Column(Text, nullable=False)
	abstract = Column(Text)
	doi = Column(Text)
	arxiv_id = Column(Text)
	primary_subject = Column(Text)
	primary_category = Column(Text)
	subjects = Column(ARRAY(Text))
	categories = Column(ARRAY(Text))
	pdf_url = Column(Text)
	published_date = Column(DateTime)
	submitted_date = Column(DateTime)
	updated_date = Column(DateTime)
	status = Column(Text)
	extracted_text = Column(Text)
	text_chunks = Column(JSONB)
	created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
	updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

	# Relationships
	articles = relationship("Article", back_populates="paper", cascade="all, delete-orphan")
	authors = relationship("PaperAuthor", back_populates="paper")
