from __future__ import annotations

from fastapi import Depends

from app.repositories.field_repository import FieldRepository, get_field_repository

class FieldService:
	def __init__(self, repo):
		self._repo = repo

	def get(self):
		"""Return all main fields embedded with their sub-fields."""
		# 1. Fetch top-level fields (parent_id IS NULL)
		fields = self._repo.get_fields()
		if not fields:
			return []

		# 2. Fetch all subfields in one query
		field_ids = [f.id for f in fields]
		sub_fields = self._repo.get_sub_fields(field_ids)

		# 3. Build parent list and index for fast lookups
		field_list = []
		parent_bucket = {}
		for f in fields:
			item = {
				"id": str(f.id),
				"code": f.code,
				"name": f.name,
				"sort_order": f.sort_order,
				"subfields": []
			}
			field_list.append(item)
			parent_bucket[f.id] = item

		# 4. Attach subfields to their parent
		for sf in sub_fields:
			parent = parent_bucket.get(sf.parent_id)
			if parent:  # ignore if parent isn’t in our top-level list
				parent["subfields"].append({
					"id": str(sf.id),
					"code": sf.code,
					"name": sf.name,
					"sort_order": sf.sort_order,
				})

		# 5. Sort subfields deterministically by sort_order (NULLS LAST), then name
		for parent in field_list:
			parent["subfields"].sort(
				key=lambda x: (
					x.get("sort_order") is None,
					x.get("sort_order") if x.get("sort_order") is not None else 0,
					x.get("name"),
				)
			)

		# Also ensure top-level fields are in the same deterministic order
		field_list.sort(
			key=lambda x: (
				x.get("sort_order") is None,
				x.get("sort_order") if x.get("sort_order") is not None else 0,
				x.get("name"),
			)
		)

		return field_list


def get_field_service(repo: FieldRepository = Depends(get_field_repository)) -> FieldService:
	return FieldService(repo)
