"""
Field Models
============

Database models for hierarchical field/taxonomy system in the Zara ETL system.
Supports the arXiv subject classification hierarchy.
"""

from typing import Optional, List
from uuid import UUID

from sqlalchemy import String, Integer, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Field(Base):
    """
    Hierarchical field/taxonomy model for categorizing papers.
    
    This model implements a tree structure for arXiv subject classifications:
    - Top level: physics, cs, math, etc.
    - Sub level: astro-ph, cond-mat, cs.AI, cs.CL, etc.
    
    Examples:
    - physics (parent=NULL)
      ├─ astro-ph
      ├─ cond-mat
      └─ physics.gen-ph
    - cs (parent=NULL)
      ├─ cs.AI
      ├─ cs.CL
      └─ cs.LG
    
    Relationships:
    - papers: Papers with this as primary field/subfield
    - parent: Parent field (for hierarchy)
    - children: Child fields under this field
    """
    
    __tablename__ = "fields"
    
    # Core identification
    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Field code (e.g., 'physics', 'astro-ph', 'cs.AI')"
    )
    
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Human-readable field name"
    )
    
    # Hierarchy support
    parent_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("fields.id"),
        nullable=True,
        comment="Parent field ID for hierarchy"
    )
    
    # Ordering and organization
    sort_order: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=0,
        comment="Sort order within parent"
    )
    
    # Self-referential relationship for hierarchy
    parent = relationship(
        "Field",
        remote_side="Field.id",
        back_populates="children"
    )
    
    children = relationship(
        "Field",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    
    # Relationships with papers
    papers_primary_field = relationship(
        "Paper",
        foreign_keys="Paper.primary_field_id",
        back_populates="primary_field"
    )
    
    papers_primary_subfield = relationship(
        "Paper", 
        foreign_keys="Paper.primary_subfield_id",
        back_populates="primary_subfield"
    )
    
    paper_fields = relationship(
        "PaperField",
        back_populates="field",
        cascade="all, delete-orphan"
    )
    
    # Constraints and indexes
    __table_args__ = (
        # Unique constraint: code must be unique within parent scope
        UniqueConstraint(
            'parent_id', 'code',
            name='uq_fields_parent_code'
        ),
        
        # Performance indexes
        Index('ix_fields_code', 'code'),
        Index('ix_fields_parent_id', 'parent_id'),
        Index('ix_fields_sort_order', 'sort_order'),
        Index('ix_fields_parent_sort', 'parent_id', 'sort_order'),
    )
    
    @property
    def full_path(self) -> str:
        """
        Get the full hierarchical path of this field.
        
        Returns:
            str: Full path like 'physics.astro-ph' or 'cs.AI'
        """
        if self.parent:
            return f"{self.parent.full_path}.{self.code}"
        return self.code
    
    @property
    def is_top_level(self) -> bool:
        """Check if this is a top-level field (no parent)."""
        return self.parent_id is None
    
    @property
    def depth(self) -> int:
        """Get the depth level of this field in the hierarchy."""
        if self.parent_id is None:
            return 0
        return self.parent.depth + 1
    
    @property
    def descendant_count(self) -> int:
        """Get total count of all descendants."""
        count = len(self.children)
        for child in self.children:
            count += child.descendant_count
        return count
    
    def get_ancestors(self) -> List['Field']:
        """
        Get all ancestor fields from root to parent.
        
        Returns:
            List[Field]: List of ancestor fields, root first
        """
        if not self.parent:
            return []
        ancestors = self.parent.get_ancestors()
        ancestors.append(self.parent)
        return ancestors
    
    def get_descendants(self) -> List['Field']:
        """
        Get all descendant fields recursively.
        
        Returns:
            List[Field]: List of all descendant fields
        """
        descendants = list(self.children)
        for child in self.children:
            descendants.extend(child.get_descendants())
        return descendants
    
    def get_siblings(self) -> List['Field']:
        """
        Get sibling fields (same parent).
        
        Returns:
            List[Field]: List of sibling fields
        """
        if not self.parent:
            # Top-level fields - get other top-level fields
            return [f for f in Field.query.filter_by(parent_id=None).all() 
                   if f.id != self.id]
        
        return [f for f in self.parent.children if f.id != self.id]
    
    @classmethod
    def get_top_level_fields(cls) -> List['Field']:
        """
        Get all top-level fields (no parent).
        
        Returns:
            List[Field]: List of top-level fields
        """
        from sqlalchemy.orm import sessionmaker
        # This would need to be called with a session
        # Return empty list for now - implement in service layer
        return []
    
    @classmethod
    def find_by_code(cls, code: str) -> Optional['Field']:
        """
        Find field by code.
        
        Args:
            code: Field code to search for
            
        Returns:
            Optional[Field]: Field if found, None otherwise
        """
        # This would need to be called with a session
        # Return None for now - implement in service layer
        return None
    
    def __repr__(self) -> str:
        """String representation of the field."""
        return f"<Field(code='{self.code}', name='{self.name}', parent_id={self.parent_id})>"
