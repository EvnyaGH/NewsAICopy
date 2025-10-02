"""
Author Data Transfer Objects
============================

Pydantic DTOs for AuthorProfile model.
"""

from datetime import datetime
from typing import Optional, List, UUID
from pydantic import BaseModel, Field, ConfigDict, EmailStr, HttpUrl, computed_field


class AuthorProfileBaseDTO(BaseModel):
    """Base DTO with common AuthorProfile fields."""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    name: str = Field(..., description="Full name of the author", max_length=255)
    email: Optional[EmailStr] = Field(None, description="Author's email address")
    affiliation: Optional[str] = Field(None, description="Institutional affiliation")
    orcid: Optional[str] = Field(None, description="ORCID identifier", pattern=r"^\d{4}-\d{4}-\d{4}-\d{4}$")
    bio: Optional[str] = Field(None, description="Author biography")
    website: Optional[HttpUrl] = Field(None, description="Personal or professional website")


class AuthorProfileCreateDTO(AuthorProfileBaseDTO):
    """DTO for creating a new AuthorProfile."""
    
    # Required fields for creation
    name: str = Field(..., description="Full name", min_length=2, max_length=255)
    
    # Optional creation fields
    email: Optional[EmailStr] = Field(None, description="Email address")
    affiliation: Optional[str] = Field(None, description="Affiliation", max_length=500)
    orcid: Optional[str] = Field(
        None, 
        description="ORCID ID in format 0000-0000-0000-0000",
        pattern=r"^\d{4}-\d{4}-\d{4}-\d{4}$"
    )
    bio: Optional[str] = Field(None, description="Biography", max_length=2000)
    website: Optional[HttpUrl] = Field(None, description="Website URL")


class AuthorProfileUpdateDTO(BaseModel):
    """DTO for updating an existing AuthorProfile."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # All fields optional for updates
    name: Optional[str] = Field(None, description="Full name", min_length=2, max_length=255)
    email: Optional[EmailStr] = Field(None, description="Email address")
    affiliation: Optional[str] = Field(None, description="Affiliation", max_length=500)
    orcid: Optional[str] = Field(
        None, 
        description="ORCID ID", 
        pattern=r"^\d{4}-\d{4}-\d{4}-\d{4}$"
    )
    bio: Optional[str] = Field(None, description="Biography", max_length=2000)
    website: Optional[HttpUrl] = Field(None, description="Website URL")


class AuthorProfileDTO(AuthorProfileBaseDTO):
    """DTO for AuthorProfile model responses."""
    
    # Database fields
    id: UUID = Field(..., description="Author ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Computed fields
    @computed_field
    @property
    def paper_count(self) -> int:
        """Number of papers by this author (set by mapper)."""
        return getattr(self, '_paper_count', 0)
    
    @computed_field
    @property
    def has_orcid(self) -> bool:
        """Whether author has ORCID ID."""
        return bool(self.orcid)
    
    @computed_field
    @property
    def has_contact_info(self) -> bool:
        """Whether author has email or website."""
        return bool(self.email or self.website)
    
    @computed_field
    @property
    def display_name(self) -> str:
        """Display name with affiliation if available."""
        if self.affiliation:
            return f"{self.name} ({self.affiliation})"
        return self.name


class AuthorProfileListDTO(BaseModel):
    """DTO for paginated author list responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Database fields
    id: UUID = Field(..., description="Author ID")
    name: str = Field(..., description="Author name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    affiliation: Optional[str] = Field(None, description="Affiliation")
    orcid: Optional[str] = Field(None, description="ORCID ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    # Summary information
    paper_count: int = Field(0, description="Number of papers")
    has_contact_info: bool = Field(False, description="Has email or website")


class AuthorProfileSearchDTO(BaseModel):
    """DTO for author search parameters."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Search terms
    query: Optional[str] = Field(None, description="Search query for name/affiliation", max_length=255)
    name: Optional[str] = Field(None, description="Author name", max_length=255)
    email: Optional[EmailStr] = Field(None, description="Email address")
    orcid: Optional[str] = Field(None, description="ORCID ID", pattern=r"^\d{4}-\d{4}-\d{4}-\d{4}$")
    affiliation: Optional[str] = Field(None, description="Affiliation", max_length=255)
    
    # Filters
    has_orcid: Optional[bool] = Field(None, description="Filter by ORCID presence")
    has_email: Optional[bool] = Field(None, description="Filter by email presence")
    has_website: Optional[bool] = Field(None, description="Filter by website presence")
    
    # Paper count filters
    min_papers: Optional[int] = Field(None, description="Minimum paper count", ge=0)
    max_papers: Optional[int] = Field(None, description="Maximum paper count", ge=0)
    
    # Date filters
    created_after: Optional[datetime] = Field(None, description="Created after date")
    created_before: Optional[datetime] = Field(None, description="Created before date")
    
    # Pagination
    page: int = Field(1, description="Page number", ge=1)
    size: int = Field(50, description="Page size", ge=1, le=100)
    
    # Sorting
    sort_by: str = Field("name", description="Sort field (name, created_at, paper_count)")
    sort_order: str = Field("asc", description="Sort order (asc/desc)")


class AuthorProfileStatsDTO(BaseModel):
    """DTO for author statistics."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Counts
    total_authors: int = Field(..., description="Total number of authors")
    authors_with_orcid: int = Field(..., description="Authors with ORCID IDs")
    authors_with_email: int = Field(..., description="Authors with email addresses")
    authors_with_website: int = Field(..., description="Authors with websites")
    
    # Paper metrics
    total_papers: int = Field(..., description="Total papers across all authors")
    average_papers_per_author: float = Field(..., description="Average papers per author")
    max_papers_per_author: int = Field(..., description="Most papers by single author")
    
    # Activity metrics
    new_authors_this_week: int = Field(0, description="New authors this week")
    new_authors_this_month: int = Field(0, description="New authors this month")
    
    # Top institutions
    top_affiliations: Optional[List[dict]] = Field(None, description="Most common affiliations")
    
    # ORCID adoption rate
    orcid_adoption_rate: float = Field(..., description="Percentage with ORCID (0.0-1.0)")


class PaperAuthorDTO(BaseModel):
    """DTO for Paper-Author relationship."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Relationship fields
    author_id: UUID = Field(..., description="Author ID")
    paper_id: UUID = Field(..., description="Paper ID")
    author_order: Optional[int] = Field(None, description="Order in author list")
    corresponding: bool = Field(False, description="Is corresponding author")
    
    # Nested author information
    author: Optional[AuthorProfileDTO] = Field(None, description="Author details")
    
    # Timestamps
    created_at: datetime = Field(..., description="Relationship created timestamp")
