import uuid
from datetime import datetime

from sqlalchemy import Column, ForeignKey, UUID, UniqueConstraint, TIMESTAMP

from app.db.base import Base


class UserFieldInterest(Base):
	__tablename__ = "user_field_interests"

	id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
	user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
	field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
	created_at = Column(TIMESTAMP, nullable=False, default=datetime.now())

	__table_args__ = (
		UniqueConstraint("user_id", "field_id", name="uq_user_field_interest"),
	)
