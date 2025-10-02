"""
Base Database Model
===================

Base SQLAlchemy model with common fields and configurations
for all models in the Zara ETL production system.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped, mapped_column


@as_declarative()
class Base:
    """
    Base class for all database models.
    
    Provides common fields that all entities should have:
    - id: Primary key UUID
    - created_at: Timestamp when record was created
    - updated_at: Timestamp when record was last updated
    
    Also provides common table naming convention.
    """
    
    # Common fields for all models
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Primary key UUID"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when record was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when record was last updated"
    )

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Automatically generate table name from class name.
        Converts CamelCase to snake_case.
        
        Examples:
        - AuthorProfile -> author_profiles
        - PaperField -> paper_fields
        - Article -> articles
        """
        # Convert CamelCase to snake_case
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        
        # Add 's' for plural if not already plural
        if not name.endswith('s'):
            name += 's'
            
        return name

    def to_dict(self) -> dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Returns:
            dict: Dictionary representation of the model
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                # Convert datetime to ISO format string
                result[column.name] = value.isoformat()
            elif isinstance(value, uuid.UUID):
                # Convert UUID to string
                result[column.name] = str(value)
            else:
                result[column.name] = value
        return result

    def update_from_dict(self, data: dict[str, Any]) -> None:
        """
        Update model instance from dictionary.
        
        Args:
            data: Dictionary with field names and values
        """
        for key, value in data.items():
            if hasattr(self, key) and key not in ('id', 'created_at'):
                setattr(self, key, value)
        
        # Always update the updated_at timestamp
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        """
        String representation of the model.
        
        Returns:
            str: String representation showing class name and ID
        """
        return f"<{self.__class__.__name__}(id={self.id})>"
