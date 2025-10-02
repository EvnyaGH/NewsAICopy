from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, UUID, Text, ARRAY, ForeignKey, Boolean, BigInteger, UniqueConstraint, Integer
from sqlalchemy.dialects.postgresql import JSONB, ENUM

from app.db.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime


class AuthorProfile(Base):
	__tablename__ = "author_profiles"

	id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
	name = Column(Text, nullable=False)
	affiliation = Column(Text)
	email = Column(Text)
	bio = Column(Text)
	orcid = Column(Text, unique=True)
	website = Column(Text)
	created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
	updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

	# Relationships
	papers = relationship("PaperAuthor", back_populates="author")


class PaperAuthor(Base):
    __tablename__ = "paper_authors"
    __table_args__ = (
        UniqueConstraint("paper_id", "author_id", name="uq_paper_author"),
        UniqueConstraint("paper_id", "author_order", name="uq_paper_author_order"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paper_id = Column(UUID(as_uuid=True), ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("author_profiles.id", ondelete="RESTRICT"), nullable=False)
    author_order = Column(Integer)
    corresponding = Column(Boolean, default=False, nullable=False)
    contribution = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    paper = relationship("Paper", back_populates="authors")
    author = relationship("AuthorProfile", back_populates="papers")