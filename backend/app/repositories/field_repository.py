from __future__ import annotations

from typing import Type

from fastapi import Depends
from sqlalchemy import text, nulls_last
from sqlalchemy.orm import Session

from app.api.deps.db import get_db
from app.models.field import Field

SQL_TREE_BY_NAME = text("""
SELECT jsonb_object_agg(top.name, top.children_json ORDER BY top.sort_order, top.name) AS fields
FROM (
  SELECT
    p.name,
    p.sort_order,
    COALESCE(
      (
        SELECT jsonb_agg(
                 jsonb_build_object(
                   'id', c.id,
                   'code', c.code,
                   'name', c.name,
                   'sort_order', c.sort_order
                 )
                 ORDER BY c.sort_order NULLS LAST, c.name
               )
        FROM fields c
        WHERE c.parent_id = p.id
      ),
      '[]'::jsonb
    ) AS children_json
  FROM fields p
  WHERE p.parent_id IS NULL
) AS top;
""")


class FieldRepository:
	"""Repository for `Field` model with simple, focused methods."""

	def __init__(self, db: Session) -> None:
		self.db = db

	def get_fields(self) -> list[Type[Field]]:
		# Ensure deterministic ordering: by sort_order (NULLS LAST), then by name
		return (
			self.db.query(Field)
			.where(Field.parent_id.is_(None))
			.order_by(nulls_last(Field.sort_order), Field.name)
			.all()
		)

	def get_sub_fields(self, parent_ids) -> list[Type[Field]]:
		# Ensure deterministic ordering within each parent: sort_order (NULLS LAST), then name
		return (
			self.db.query(Field)
			.where(Field.parent_id.in_(parent_ids))
			.order_by(nulls_last(Field.sort_order), Field.name)
			.all()
		)


def get_field_repository(db: Session = Depends(get_db)) -> FieldRepository:
	return FieldRepository(db)
