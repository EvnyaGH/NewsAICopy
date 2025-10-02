"""
Data Transfer Objects (DTOs)
============================

Pydantic models for API serialization and data validation in the Zara ETL system.

DTOs provide a clean interface between the database models and external APIs,
ensuring type safety and validation for all data transfers. Each DTO corresponds
to a database model but may include computed fields, nested relationships,
and API-specific formatting.

Structure:
- Base DTOs with common fields
- Request DTOs for API inputs (create/update operations)
- Response DTOs for API outputs (read operations)  
- Nested DTOs for complex relationships
"""

from .author_dto import AuthorProfileDTO, AuthorProfileCreateDTO, AuthorProfileUpdateDTO
from .article_dto import (
    ArticleDTO, ArticleCreateDTO, ArticleUpdateDTO,
    ArticleBlockDTO, ArticleBlockCreateDTO, ArticleBlockUpdateDTO
)
from .paper_dto import PaperDTO, PaperCreateDTO, PaperUpdateDTO
from .field_dto import FieldDTO, FieldCreateDTO, FieldUpdateDTO
from .prompt_dto import PromptDTO, PromptCreateDTO, PromptUpdateDTO

__all__ = [
    # Author DTOs
    "AuthorProfileDTO",
    "AuthorProfileCreateDTO", 
    "AuthorProfileUpdateDTO",
    
    # Article DTOs
    "ArticleDTO",
    "ArticleCreateDTO",
    "ArticleUpdateDTO",
    "ArticleBlockDTO",
    "ArticleBlockCreateDTO",
    "ArticleBlockUpdateDTO",
    
    # Paper DTOs
    "PaperDTO",
    "PaperCreateDTO",
    "PaperUpdateDTO",
    
    # Field DTOs
    "FieldDTO",
    "FieldCreateDTO",
    "FieldUpdateDTO",
    
    # Prompt DTOs
    "PromptDTO",
    "PromptCreateDTO",
    "PromptUpdateDTO",
]
