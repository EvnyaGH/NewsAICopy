from __future__ import annotations

from typing import List
from fastapi import Depends
from uuid import UUID

from app.exceptions.exceptions import UserDoesNotExist
from app.repositories.interest_repository import InterestRepository, get_interest_repository


class InterestService:
	def __init__(self, interest_repo: InterestRepository):
		self._interest_repo = interest_repo

	def get_interests(self, user_id: UUID) -> List[dict[str, List]] | None:
		if user_id is None:
			raise UserDoesNotExist("invalid user id")

		interests = self._interest_repo.get(user_id)

		return interests

	def create_interest(self, user_id: UUID, field_id: UUID) -> dict:
		interest = self._interest_repo.insert(user_id, field_id)

		return {"message": "Successfully added interest for field {} and user {} ".format(interest.field_id,
																						  interest.user_id)}

	def delete_interest(self, user_id: UUID, field_id: UUID) -> dict:
		self._interest_repo.remove(user_id, field_id)

		return {"message": "Successfully removed field {} from user's interest".format(field_id)}


def get_interest_service(
	interest_repo: InterestRepository = Depends(get_interest_repository),
) -> InterestService:
	return InterestService(interest_repo)
