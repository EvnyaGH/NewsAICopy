import logging

from fastapi import Depends
from app.exceptions.exceptions import DuplicateInterestError, APIError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased

from app.api.deps import get_db
from app.models import interest
from app.models.field import Field
from app.models.interest import UserFieldInterest


class InterestRepository:
	def __init__(self, db: Session):
		self._db = db

	def get(self, user_id):
		"""Return all fields/subfields a user is interested in, nested by parent."""

		Parent = aliased(Field)

		# join interests → fields → parent
		rows = (
			self._db.query(
				Field.id.label("field_id"),
				Field.code.label("field_code"),
				Field.name.label("field_name"),
				Field.parent_id,
				Parent.id.label("parent_id"),
				Parent.code.label("parent_code"),
				Parent.name.label("parent_name"),
			)
			.join(UserFieldInterest, UserFieldInterest.field_id == Field.id)
			.outerjoin(Parent, Field.parent_id == Parent.id)
			.filter(UserFieldInterest.user_id == user_id)
			.all()
		)

		# nest into { parent: {id, code, name, subfields: [...] } }
		nested = {}
		for row in rows:
			if row.parent_id:  # subfield
				if row.parent_id not in nested:
					nested[row.parent_id] = {
						"id": row.parent_id,
						"code": row.parent_code,
						"name": row.parent_name,
						"subfields": [],
					}
				nested[row.parent_id]["subfields"].append(
					{
						"id": row.field_id,
						"code": row.field_code,
						"name": row.field_name,
					}
				)
			else:  # top-level field
				if row.field_id not in nested:
					nested[row.field_id] = {
						"id": row.field_id,
						"code": row.field_code,
						"name": row.field_name,
						"subfields": [],
					}

		return list(nested.values())

	def insert(self, user_id, field_id):
		interest = UserFieldInterest(field_id=field_id, user_id=user_id)
		try:
			self._db.add(interest)
			self._db.commit()
			self._db.refresh(interest)
			return interest
		except IntegrityError as e:
			self._db.rollback()
			msg = str(getattr(e, "orig", e))
			if "user_field_interests_user_id_field_id_key" in msg:
				raise DuplicateInterestError("Interest already added")
			# Fall back to a generic error to avoid leaking DB details
			raise APIError("Invalid user_id or field_id")

	def remove(self, user_id, field_id):
		deleted = self._db.query(UserFieldInterest).filter_by(field_id=field_id, user_id=user_id).delete()
		if not deleted:
			raise APIError("Interest not found")


def get_interest_repository(db: Session = Depends(get_db)) -> InterestRepository:
	return InterestRepository(db)
