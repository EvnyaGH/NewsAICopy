"""
Author Models
=============

Database models for author-related entities in the Zara ETL system.
"""

from typing import Optional, List

from sqlalchemy import String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AuthorProfile(Base):
    """
    Author profile model storing information about research paper authors.
    
    This model stores comprehensive author information including:
    - Basic identification (name, email)
    - Professional details (affiliation, ORCID)
    - Additional metadata (bio, website)
    
    Relationships:
    - papers: Many-to-many through PaperAuthor junction table
    """
    
    __tablename__ = "author_profiles"
    
    # Basic Information
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Full name of the author"
    )
    
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Author's email address"
    )
    
    # Professional Information
    affiliation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Author's institutional affiliation"
    )
    
    orcid: Mapped[Optional[str]] = mapped_column(
        String(19),  # ORCID format: 0000-0000-0000-0000
        nullable=True,
        unique=True,
        comment="ORCID identifier"
    )
    
    # Additional Information
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Author biography or description"
    )
    
    website: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="Author's personal or professional website"
    )
    
    # Relationships
    # papers: Relationship defined in PaperAuthor junction table
    paper_authors = relationship(
        "PaperAuthor",
        back_populates="author",
        cascade="all, delete-orphan"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_author_profiles_name', 'name'),
        Index('ix_author_profiles_email', 'email'),
        Index('ix_author_profiles_orcid', 'orcid'),
        Index('ix_author_profiles_affiliation', 'affiliation'),
    )
    
    @property
    def papers(self) -> List['Paper']:
        """Get all papers by this author."""
        return [pa.paper for pa in self.paper_authors]
    
    @property
    def paper_count(self) -> int:
        """Get count of papers by this author."""
        return len(self.paper_authors)
    
    def __repr__(self) -> str:
        """String representation of the author."""
        return f"<AuthorProfile(name='{self.name}', orcid='{self.orcid}')>"
