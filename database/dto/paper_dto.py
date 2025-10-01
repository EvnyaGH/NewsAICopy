"""
Paper Data Transfer Objects
===========================

Pydantic DTOs for Paper model and related entities.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, UUID
from pydantic import BaseModel, Field, ConfigDict, computed_field

from .author_dto import AuthorProfileDTO
from .field_dto import FieldDTO


class PaperBaseDTO(BaseModel):
    """Base DTO with common Paper fields."""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    title: str = Field(..., description="Paper title", max_length=1000)
    abstract: Optional[str] = Field(None, description="Paper abstract/summary")
    doi: Optional[str] = Field(None, description="Digital Object Identifier", max_length=255)
    arxiv_id: Optional[str] = Field(None, description="arXiv identifier", max_length=50)
    summary: Optional[str] = Field(None, description="Generated summary")
    keywords: Optional[List[str]] = Field(None, description="Keywords and subject terms")
    pdf_url: Optional[str] = Field(None, description="URL to PDF file", max_length=512)
    status: Optional[str] = Field("pending", description="Processing status", max_length=50)


class PaperCreateDTO(PaperBaseDTO):
    """DTO for creating a new Paper."""
    
    # Required fields for creation
    title: str = Field(..., description="Paper title", min_length=5, max_length=1000)
    
    # Optional creation fields
    published_date: Optional[datetime] = Field(None, description="Publication date")
    submitted_date: Optional[datetime] = Field(None, description="Submission date")
    updated_date: Optional[datetime] = Field(None, description="Last update date")
    
    # Field classification
    primary_field_code: Optional[str] = Field(None, description="Primary field code")
    primary_subfield_code: Optional[str] = Field(None, description="Primary subfield code")
    additional_field_codes: Optional[List[str]] = Field(None, description="Additional field codes")
    
    # Author information
    author_names: Optional[List[str]] = Field(None, description="Author names in order")
    corresponding_author_emails: Optional[List[str]] = Field(None, description="Corresponding author emails")
    
    # Content (usually added later during processing)
    extracted_text: Optional[str] = Field(None, description="Extracted text from PDF")
    pdf_path: Optional[str] = Field(None, description="Local path to PDF", max_length=512)
    pdf_size: Optional[int] = Field(None, description="PDF file size in bytes", ge=0)
    page_count: Optional[int] = Field(None, description="Number of PDF pages", ge=0)


class PaperUpdateDTO(BaseModel):
    """DTO for updating an existing Paper."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # All fields optional for updates
    title: Optional[str] = Field(None, description="Paper title", min_length=5, max_length=1000)
    abstract: Optional[str] = Field(None, description="Paper abstract")
    doi: Optional[str] = Field(None, description="DOI", max_length=255)
    arxiv_id: Optional[str] = Field(None, description="arXiv ID", max_length=50)
    summary: Optional[str] = Field(None, description="Generated summary")
    keywords: Optional[List[str]] = Field(None, description="Keywords")
    pdf_url: Optional[str] = Field(None, description="PDF URL", max_length=512)
    status: Optional[str] = Field(None, description="Processing status", max_length=50)
    
    # Dates
    published_date: Optional[datetime] = Field(None, description="Publication date")
    submitted_date: Optional[datetime] = Field(None, description="Submission date")
    updated_date: Optional[datetime] = Field(None, description="Last update date")
    
    # Processing fields
    extracted_text: Optional[str] = Field(None, description="Extracted text")
    text_chunks: Optional[Dict[str, Any]] = Field(None, description="Chunked text data")
    processing_metadata: Optional[Dict[str, Any]] = Field(None, description="Processing metadata")
    quality_score: Optional[float] = Field(None, description="Quality score", ge=0.0, le=1.0)
    extraction_method: Optional[str] = Field(None, description="Extraction method", max_length=50)
    
    # File information
    pdf_path: Optional[str] = Field(None, description="PDF path", max_length=512)
    pdf_size: Optional[int] = Field(None, description="PDF size", ge=0)
    page_count: Optional[int] = Field(None, description="Page count", ge=0)


class PaperDTO(PaperBaseDTO):
    """DTO for Paper model responses."""
    
    # Database fields
    id: UUID = Field(..., description="Paper ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Full paper information
    published_date: Optional[datetime] = Field(None, description="Publication date")
    submitted_date: Optional[datetime] = Field(None, description="Submission date")
    updated_date: Optional[datetime] = Field(None, description="Last update date")
    
    # Processing information
    extracted_text: Optional[str] = Field(None, description="Extracted text from PDF")
    text_chunks: Optional[Dict[str, Any]] = Field(None, description="Chunked text data")
    processing_metadata: Optional[Dict[str, Any]] = Field(None, description="Processing metadata")
    quality_score: Optional[float] = Field(None, description="Quality score (0.0-1.0)")
    extraction_method: Optional[str] = Field(None, description="Text extraction method")
    
    # File information
    pdf_path: Optional[str] = Field(None, description="Local PDF path")
    pdf_size: Optional[int] = Field(None, description="PDF file size in bytes")
    page_count: Optional[int] = Field(None, description="Number of pages")
    
    # Relationships (populated by mappers)
    authors: Optional[List[AuthorProfileDTO]] = Field(None, description="Paper authors")
    primary_field: Optional[FieldDTO] = Field(None, description="Primary field")
    primary_subfield: Optional[FieldDTO] = Field(None, description="Primary subfield")
    fields: Optional[List[FieldDTO]] = Field(None, description="All associated fields")
    
    # Computed fields
    @computed_field
    @property
    def word_count(self) -> Optional[int]:
        """Approximate word count from extracted text."""
        if not self.extracted_text:
            return None
        return len(self.extracted_text.split())
    
    @computed_field  
    @property
    def is_processed(self) -> bool:
        """Whether paper has been fully processed."""
        return self.status == "completed"
    
    @computed_field
    @property
    def author_count(self) -> int:
        """Number of authors."""
        return len(self.authors) if self.authors else 0
    
    @computed_field
    @property
    def field_count(self) -> int:
        """Number of associated fields."""
        return len(self.fields) if self.fields else 0
    
    @computed_field
    @property
    def has_pdf(self) -> bool:
        """Whether paper has an associated PDF."""
        return bool(self.pdf_url or self.pdf_path)


class PaperListDTO(BaseModel):
    """DTO for paginated paper list responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Database fields
    id: UUID = Field(..., description="Paper ID")
    title: str = Field(..., description="Paper title")
    arxiv_id: Optional[str] = Field(None, description="arXiv identifier")
    status: Optional[str] = Field(None, description="Processing status")
    quality_score: Optional[float] = Field(None, description="Quality score")
    
    # Dates
    published_date: Optional[datetime] = Field(None, description="Publication date")
    submitted_date: Optional[datetime] = Field(None, description="Submission date")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    # Summary information
    author_count: int = Field(0, description="Number of authors")
    field_count: int = Field(0, description="Number of fields")
    word_count: Optional[int] = Field(None, description="Word count")
    
    # Primary classification
    primary_field_name: Optional[str] = Field(None, description="Primary field name")
    primary_subfield_name: Optional[str] = Field(None, description="Primary subfield name")


class PaperSearchDTO(BaseModel):
    """DTO for paper search parameters."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Search terms
    query: Optional[str] = Field(None, description="Search query", max_length=255)
    arxiv_id: Optional[str] = Field(None, description="Specific arXiv ID", max_length=50)
    doi: Optional[str] = Field(None, description="Specific DOI", max_length=255)
    
    # Filters
    status: Optional[List[str]] = Field(None, description="Processing statuses to include")
    field_codes: Optional[List[str]] = Field(None, description="Field codes to include")
    author_names: Optional[List[str]] = Field(None, description="Author names to include")
    
    # Date ranges
    published_after: Optional[datetime] = Field(None, description="Published after date")
    published_before: Optional[datetime] = Field(None, description="Published before date")
    submitted_after: Optional[datetime] = Field(None, description="Submitted after date")
    submitted_before: Optional[datetime] = Field(None, description="Submitted before date")
    
    # Quality filters
    min_quality_score: Optional[float] = Field(None, description="Minimum quality score", ge=0.0, le=1.0)
    max_quality_score: Optional[float] = Field(None, description="Maximum quality score", ge=0.0, le=1.0)
    
    # Pagination
    page: int = Field(1, description="Page number", ge=1)
    size: int = Field(50, description="Page size", ge=1, le=100)
    
    # Sorting
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", description="Sort order (asc/desc)")


class PaperStatsDTO(BaseModel):
    """DTO for paper statistics."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Counts
    total_papers: int = Field(..., description="Total number of papers")
    processed_papers: int = Field(..., description="Number of processed papers")
    pending_papers: int = Field(..., description="Number of pending papers")
    failed_papers: int = Field(..., description="Number of failed papers")
    
    # Quality metrics
    average_quality_score: Optional[float] = Field(None, description="Average quality score")
    high_quality_papers: int = Field(0, description="Papers above quality threshold")
    
    # Content metrics
    total_word_count: Optional[int] = Field(None, description="Total word count across all papers")
    average_word_count: Optional[float] = Field(None, description="Average word count per paper")
    
    # Processing metrics
    processing_success_rate: float = Field(..., description="Processing success rate (0.0-1.0)")
    average_processing_time: Optional[float] = Field(None, description="Average processing time in seconds")
    
    # Field distribution
    top_fields: Optional[List[Dict[str, Any]]] = Field(None, description="Most common fields")
    
    # Recent activity
    papers_this_week: int = Field(0, description="Papers added this week")
    papers_this_month: int = Field(0, description="Papers added this month")
