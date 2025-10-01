"""
Field Data Transfer Objects
===========================

Pydantic DTOs for Field model (hierarchical taxonomy system).
"""

from datetime import datetime
from typing import Optional, List, UUID, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, computed_field


class FieldBaseDTO(BaseModel):
    """Base DTO with common Field fields."""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    code: str = Field(..., description="Field code (e.g., 'physics', 'cs.AI')", max_length=50)
    name: str = Field(..., description="Human-readable field name", max_length=255)
    sort_order: Optional[int] = Field(None, description="Sort order within parent")


class FieldCreateDTO(FieldBaseDTO):
    """DTO for creating a new Field."""
    
    # Required fields for creation
    code: str = Field(..., description="Field code", min_length=1, max_length=50)
    name: str = Field(..., description="Field name", min_length=1, max_length=255)
    
    # Optional creation fields
    parent_code: Optional[str] = Field(None, description="Parent field code for hierarchy")
    sort_order: Optional[int] = Field(0, description="Sort order")


class FieldUpdateDTO(BaseModel):
    """DTO for updating an existing Field."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # All fields optional for updates
    code: Optional[str] = Field(None, description="Field code", min_length=1, max_length=50)
    name: Optional[str] = Field(None, description="Field name", min_length=1, max_length=255)
    parent_code: Optional[str] = Field(None, description="Parent field code")
    sort_order: Optional[int] = Field(None, description="Sort order")


class FieldDTO(FieldBaseDTO):
    """DTO for Field model responses."""
    
    # Database fields
    id: UUID = Field(..., description="Field ID")
    parent_id: Optional[UUID] = Field(None, description="Parent field ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Relationships (populated by mappers)
    parent: Optional['FieldDTO'] = Field(None, description="Parent field")
    children: Optional[List['FieldDTO']] = Field(None, description="Child fields")
    
    # Computed fields
    @computed_field
    @property
    def full_path(self) -> str:
        """Full hierarchical path."""
        if hasattr(self, '_full_path'):
            return self._full_path
        # Computed by mapper or service
        return self.code
    
    @computed_field
    @property
    def is_top_level(self) -> bool:
        """Whether this is a top-level field."""
        return self.parent_id is None
    
    @computed_field
    @property
    def depth(self) -> int:
        """Depth level in hierarchy."""
        if hasattr(self, '_depth'):
            return self._depth
        return 0 if self.is_top_level else 1
    
    @computed_field
    @property
    def child_count(self) -> int:
        """Number of direct children."""
        return len(self.children) if self.children else 0
    
    @computed_field
    @property
    def paper_count(self) -> int:
        """Number of papers in this field (set by mapper)."""
        return getattr(self, '_paper_count', 0)


# Enable forward references
FieldDTO.model_rebuild()


class FieldTreeDTO(BaseModel):
    """DTO for hierarchical field tree representation."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Field information
    id: UUID = Field(..., description="Field ID")
    code: str = Field(..., description="Field code")
    name: str = Field(..., description="Field name")
    full_path: str = Field(..., description="Full hierarchical path")
    depth: int = Field(..., description="Depth in hierarchy")
    sort_order: Optional[int] = Field(None, description="Sort order")
    
    # Tree structure
    children: List['FieldTreeDTO'] = Field(default_factory=list, description="Child fields")
    
    # Statistics
    paper_count: int = Field(0, description="Papers in this field")
    descendant_paper_count: int = Field(0, description="Papers in this field and descendants")


FieldTreeDTO.model_rebuild()


class FieldListDTO(BaseModel):
    """DTO for flat field list responses."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Database fields
    id: UUID = Field(..., description="Field ID")
    code: str = Field(..., description="Field code")
    name: str = Field(..., description="Field name")
    full_path: str = Field(..., description="Full hierarchical path")
    depth: int = Field(..., description="Depth in hierarchy")
    is_top_level: bool = Field(..., description="Is top-level field")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    # Parent information
    parent_id: Optional[UUID] = Field(None, description="Parent field ID")
    parent_name: Optional[str] = Field(None, description="Parent field name")
    
    # Statistics
    paper_count: int = Field(0, description="Number of papers")
    child_count: int = Field(0, description="Number of child fields")


class FieldSearchDTO(BaseModel):
    """DTO for field search parameters."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Search terms
    query: Optional[str] = Field(None, description="Search query for code/name", max_length=255)
    code: Optional[str] = Field(None, description="Specific field code", max_length=50)
    name: Optional[str] = Field(None, description="Field name", max_length=255)
    
    # Hierarchy filters
    parent_code: Optional[str] = Field(None, description="Parent field code")
    top_level_only: Optional[bool] = Field(None, description="Only top-level fields")
    depth: Optional[int] = Field(None, description="Specific depth level", ge=0)
    max_depth: Optional[int] = Field(None, description="Maximum depth", ge=0)
    
    # Paper count filters
    min_papers: Optional[int] = Field(None, description="Minimum paper count", ge=0)
    max_papers: Optional[int] = Field(None, description="Maximum paper count", ge=0)
    has_papers: Optional[bool] = Field(None, description="Has associated papers")
    
    # Date filters
    created_after: Optional[datetime] = Field(None, description="Created after date")
    created_before: Optional[datetime] = Field(None, description="Created before date")
    
    # Pagination
    page: int = Field(1, description="Page number", ge=1)
    size: int = Field(50, description="Page size", ge=1, le=100)
    
    # Sorting
    sort_by: str = Field("sort_order", description="Sort field")
    sort_order: str = Field("asc", description="Sort order (asc/desc)")
    
    # Response format
    include_children: bool = Field(False, description="Include child fields")
    include_ancestors: bool = Field(False, description="Include ancestor fields")


class FieldStatsDTO(BaseModel):
    """DTO for field statistics."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Counts
    total_fields: int = Field(..., description="Total number of fields")
    top_level_fields: int = Field(..., description="Number of top-level fields")
    max_depth: int = Field(..., description="Maximum depth in hierarchy")
    
    # Paper distribution
    total_papers: int = Field(..., description="Total papers across all fields")
    fields_with_papers: int = Field(..., description="Fields with papers")
    average_papers_per_field: float = Field(..., description="Average papers per field")
    
    # Most popular fields
    top_fields_by_papers: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Most popular fields by paper count"
    )
    
    # Recent activity
    new_fields_this_week: int = Field(0, description="New fields this week")
    new_fields_this_month: int = Field(0, description="New fields this month")
    
    # Hierarchy metrics
    average_depth: float = Field(..., description="Average depth of all fields")
    average_children_per_parent: float = Field(..., description="Average children per parent field")


class FieldPaperCountDTO(BaseModel):
    """DTO for field paper count information."""
    
    model_config = ConfigDict(from_attributes=True)
    
    field_id: UUID = Field(..., description="Field ID")
    field_code: str = Field(..., description="Field code")
    field_name: str = Field(..., description="Field name")
    direct_papers: int = Field(..., description="Papers directly in this field")
    descendant_papers: int = Field(..., description="Papers in descendant fields")
    total_papers: int = Field(..., description="Total papers (direct + descendants)")


class BulkFieldOperationDTO(BaseModel):
    """DTO for bulk field operations."""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Operation type
    operation: str = Field(..., description="Operation type (create, update, delete, move)")
    
    # Field targets
    field_codes: List[str] = Field(..., description="Field codes to operate on")
    
    # Operation data
    data: Optional[Dict[str, Any]] = Field(None, description="Operation-specific data")
    
    # Options
    dry_run: bool = Field(False, description="Preview operation without executing")
    force: bool = Field(False, description="Force operation even with warnings")
