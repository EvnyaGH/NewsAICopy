"""
Paper Models
============

Database models for research papers and related entities in the Zara ETL system.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Index, UniqueConstraint, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Paper(Base):
    """
    Research paper model storing comprehensive paper information.
    
    This model stores all paper-related data including:
    - Bibliographic information (title, abstract, DOI, arXiv ID)
    - Content and processing data (extracted text, chunks)
    - Categorization through hierarchical fields
    - Processing status and timestamps
    
    Relationships:
    - authors: Many-to-many through PaperAuthor junction table
    - fields: Many-to-many through PaperField junction table  
    - primary_field: Many-to-one to top-level field
    - primary_subfield: Many-to-one to subfield
    - articles: One-to-many with Article model
    """
    
    __tablename__ = "papers"
    
    # Basic bibliographic information
    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Paper title"
    )
    
    abstract: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Paper abstract/summary"
    )
    
    # Identifiers
    doi: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Digital Object Identifier"
    )
    
    arxiv_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        unique=True,
        comment="arXiv identifier (e.g., 2301.12345v1)"
    )
    
    # Content processing
    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Generated summary of the paper"
    )
    
    keywords: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        nullable=True,
        comment="Keywords and subject terms"
    )
    
    # Field classification (new hierarchical system)
    primary_field_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("fields.id"),
        nullable=True,
        comment="Primary top-level field (e.g., physics, cs)"
    )
    
    primary_subfield_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("fields.id"),
        nullable=True,
        comment="Primary subfield (e.g., astro-ph, cs.AI)"
    )
    
    # URLs and external references
    pdf_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="URL to PDF file"
    )
    
    # Publication dates
    published_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date paper was published"
    )
    
    submitted_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date paper was submitted to arXiv"
    )
    
    updated_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date paper was last updated on arXiv"
    )
    
    # Processing status
    status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default="pending",
        comment="Processing status (pending, processing, completed, failed)"
    )
    
    # Extracted content
    extracted_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Full extracted text from PDF"
    )
    
    text_chunks: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Chunked text data for LLM processing"
    )
    
    # Processing metadata
    processing_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Metadata about processing (models used, costs, etc.)"
    )
    
    # Quality metrics
    quality_score: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        comment="Quality score for the paper (0.0-1.0)"
    )
    
    extraction_method: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Method used for text extraction"
    )
    
    # File information
    pdf_path: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="Local path to stored PDF file"
    )
    
    pdf_size: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="PDF file size in bytes"
    )
    
    page_count: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="Number of pages in PDF"
    )
    
    # Relationships
    
    # Field relationships (hierarchical taxonomy)
    primary_field = relationship(
        "Field",
        foreign_keys=[primary_field_id],
        back_populates="papers_primary_field"
    )
    
    primary_subfield = relationship(
        "Field", 
        foreign_keys=[primary_subfield_id],
        back_populates="papers_primary_subfield"
    )
    
    # Many-to-many relationships
    paper_authors = relationship(
        "PaperAuthor",
        back_populates="paper",
        cascade="all, delete-orphan",
        order_by="PaperAuthor.author_order"
    )
    
    paper_fields = relationship(
        "PaperField",
        back_populates="paper",
        cascade="all, delete-orphan"
    )
    
    # One-to-many relationships
    articles = relationship(
        "Article",
        back_populates="paper",
        cascade="all, delete-orphan"
    )
    
    # Indexes and constraints
    __table_args__ = (
        Index('ix_papers_title', 'title'),
        Index('ix_papers_arxiv_id', 'arxiv_id'),
        Index('ix_papers_doi', 'doi'),
        Index('ix_papers_status', 'status'),
        Index('ix_papers_published_date', 'published_date'),
        Index('ix_papers_submitted_date', 'submitted_date'),
        Index('ix_papers_primary_field_id', 'primary_field_id'),
        Index('ix_papers_primary_subfield_id', 'primary_subfield_id'),
        Index('ix_papers_quality_score', 'quality_score'),
        # Composite indexes for common queries
        Index('ix_papers_status_submitted', 'status', 'submitted_date'),
        Index('ix_papers_field_submitted', 'primary_field_id', 'submitted_date'),
    )
    
    # Properties for convenience
    
    @property
    def authors(self) -> List['AuthorProfile']:
        """Get ordered list of authors."""
        return [pa.author for pa in sorted(self.paper_authors, key=lambda x: x.author_order or 0)]
    
    @property
    def author_names(self) -> List[str]:
        """Get list of author names in order."""
        return [author.name for author in self.authors]
    
    @property
    def fields(self) -> List['Field']:
        """Get all associated fields."""
        return [pf.field for pf in self.paper_fields]
    
    @property
    def field_codes(self) -> List[str]:
        """Get list of field codes."""
        return [field.code for field in self.fields]
    
    @property
    def corresponding_authors(self) -> List['AuthorProfile']:
        """Get list of corresponding authors."""
        return [pa.author for pa in self.paper_authors if pa.corresponding]
    
    @property
    def word_count(self) -> Optional[int]:
        """Get approximate word count from extracted text."""
        if not self.extracted_text:
            return None
        return len(self.extracted_text.split())
    
    @property
    def is_processed(self) -> bool:
        """Check if paper has been fully processed."""
        return self.status == "completed"
    
    @property
    def has_articles(self) -> bool:
        """Check if paper has generated articles."""
        return len(self.articles) > 0
    
    # Utility methods
    
    def add_author(self, author: 'AuthorProfile', order: Optional[int] = None, 
                   corresponding: bool = False) -> 'PaperAuthor':
        """
        Add an author to this paper.
        
        Args:
            author: Author to add
            order: Order of author (defaults to next available)
            corresponding: Whether this is a corresponding author
            
        Returns:
            PaperAuthor: The created junction record
        """
        if order is None:
            # Get next available order
            existing_orders = [pa.author_order for pa in self.paper_authors if pa.author_order]
            order = max(existing_orders, default=0) + 1
        
        from . import PaperAuthor
        paper_author = PaperAuthor(
            paper=self,
            author=author,
            author_order=order,
            corresponding=corresponding
        )
        self.paper_authors.append(paper_author)
        return paper_author
    
    def add_field(self, field: 'Field') -> 'PaperField':
        """
        Add a field to this paper.
        
        Args:
            field: Field to add
            
        Returns:
            PaperField: The created junction record
        """
        from . import PaperField
        paper_field = PaperField(paper=self, field=field)
        self.paper_fields.append(paper_field)
        return paper_field
    
    def set_processing_metadata(self, key: str, value: Any) -> None:
        """
        Set a processing metadata value.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        if self.processing_metadata is None:
            self.processing_metadata = {}
        self.processing_metadata[key] = value
    
    def get_processing_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get a processing metadata value.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Any: Metadata value or default
        """
        if self.processing_metadata is None:
            return default
        return self.processing_metadata.get(key, default)
    
    def __repr__(self) -> str:
        """String representation of the paper."""
        return f"<Paper(arxiv_id='{self.arxiv_id}', title='{self.title[:50]}...')>"


class PaperAuthor(Base):
    """
    Junction table for Paper ↔ Author many-to-many relationship.
    
    This model stores the relationship between papers and authors,
    including author order and corresponding author status.
    """
    
    __tablename__ = "paper_authors"
    
    # Foreign keys
    paper_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("papers.id"),
        nullable=False,
        comment="Reference to paper"
    )
    
    author_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("author_profiles.id"),
        nullable=False,
        comment="Reference to author"
    )
    
    # Additional fields
    author_order: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Order of author in author list (1-based)"
    )
    
    corresponding: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        comment="Whether this author is a corresponding author"
    )
    
    # Relationships
    paper = relationship("Paper", back_populates="paper_authors")
    author = relationship("AuthorProfile", back_populates="paper_authors")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('paper_id', 'author_id', name='uq_paper_authors_paper_author'),
        UniqueConstraint('paper_id', 'author_order', name='uq_paper_authors_paper_order'),
        Index('ix_paper_authors_paper_id', 'paper_id'),
        Index('ix_paper_authors_author_id', 'author_id'),
        Index('ix_paper_authors_order', 'author_order'),
        Index('ix_paper_authors_corresponding', 'corresponding'),
    )
    
    def __repr__(self) -> str:
        """String representation of the paper-author relationship."""
        return f"<PaperAuthor(paper_id={self.paper_id}, author_id={self.author_id}, order={self.author_order})>"


class PaperField(Base):
    """
    Junction table for Paper ↔ Field many-to-many relationship.
    
    This model stores additional field associations for papers
    beyond the primary field and subfield.
    """
    
    __tablename__ = "paper_fields"
    
    # Foreign keys
    paper_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("papers.id"),
        nullable=False,
        comment="Reference to paper"
    )
    
    field_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("fields.id"),
        nullable=False,
        comment="Reference to field"
    )
    
    # Relationships
    paper = relationship("Paper", back_populates="paper_fields")
    field = relationship("Field", back_populates="paper_fields")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('paper_id', 'field_id', name='uq_paper_fields_paper_field'),
        Index('ix_paper_fields_paper_id', 'paper_id'),
        Index('ix_paper_fields_field_id', 'field_id'),
    )
    
    def __repr__(self) -> str:
        """String representation of the paper-field relationship."""
        return f"<PaperField(paper_id={self.paper_id}, field_id={self.field_id})>"
