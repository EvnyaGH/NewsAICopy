from __future__ import annotations

import uuid
from typing import Optional, List

from sqlalchemy import UUID, ForeignKey, text, UniqueConstraint, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base


class Field(Base):
	"""
	The field that the paper is published in, ie Physics, Computer Science, etc.
	A self-referential table that has a parent child relationship
	Computer Science (field/parent) -> Artificial Intelligence (subfield/child).
	"""
	__tablename__ = "fields"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		server_default=text("gen_random_uuid()"),
	)

	code: Mapped[str] = mapped_column(nullable=False)  # e.g. 'physics', 'astro-ph'
	name: Mapped[str] = mapped_column(nullable=False)  # display name
	sort_order: Mapped[Optional[int]] = mapped_column(default=None)

	parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
		UUID(as_uuid=True),
		ForeignKey("fields.id", ondelete="SET NULL"),
		nullable=True,
	)

	# Self-referential relationship
	parent: Mapped[Optional["Field"]] = relationship(
		back_populates="children",
		remote_side="Field.id",
		lazy="joined",
	)
	children: Mapped[List["Field"]] = relationship(
		back_populates="parent",
		cascade="all, delete-orphan",  # delete children if removed from parent.children collection
		passive_deletes=True,
		order_by="Field.sort_order.nulls_last(), Field.name",
	)

	__table_args__ = (
		UniqueConstraint("parent_id", "code", name="uq_fields_parent_code"),
		Index("ix_fields_parent_code", "parent_id", "code"),
		Index("ix_fields_parent_sort", "parent_id", "sort_order"),
	)

	def __repr__(self) -> str:
		return f"<Field id={self.id} code={self.code!r} name={self.name!r} parent_id={self.parent_id}>"
