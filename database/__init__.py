"""
Zara ETL Production Database Package
=====================================

Database models, DTOs, and mappers for the Zara ETL production system.
This package contains all database-related functionality including:

- SQLAlchemy models for all entities
- Pydantic DTOs for API serialization
- Mapper classes for model ↔ DTO conversion
- Database connection and session management
- Alembic migrations

Structure:
- models/: SQLAlchemy ORM models
- dto/: Pydantic data transfer objects
- mappers/: Model ↔ DTO conversion logic
- migrations/: Alembic database migrations
"""

from .models.base import Base
from .models.papers import Paper, PaperAuthor, PaperField
from .models.articles import Article, ArticleBlock, ArticlePrompt
from .models.authors import AuthorProfile
from .models.fields import Field
from .models.prompts import Prompt

__version__ = "1.0.0"

__all__ = [
    # Base
    "Base",
    
    # Paper models
    "Paper",
    "PaperAuthor", 
    "PaperField",
    
    # Article models
    "Article",
    "ArticleBlock",
    "ArticlePrompt",
    
    # Author models
    "AuthorProfile",
    
    # Field/taxonomy models
    "Field",
    
    # Prompt models
    "Prompt",
]
