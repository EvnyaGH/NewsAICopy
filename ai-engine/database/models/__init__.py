"""
Database Models Package
=======================

SQLAlchemy ORM models for the Zara ETL production system.

This package contains all database models implementing the full ER schema:
- Base: Common base class with UUID primary keys and timestamps
- Papers: Research paper storage with hierarchical field classification
- Articles: Generated article content with structured blocks
- Authors: Author profile management with ORCID integration
- Fields: Hierarchical taxonomy system for paper classification
- Prompts: AI prompt templates with versioning and performance tracking

All models follow consistent patterns:
- UUID primary keys
- created_at/updated_at timestamps  
- Proper foreign key relationships
- Performance indexes
- Type hints and documentation
"""

from .base import Base
from .authors import AuthorProfile
from .fields import Field
from .prompts import Prompt, PromptType
from .papers import Paper, PaperAuthor, PaperField
from .articles import Article, ArticleBlock, ArticlePrompt, BlockType

# Export all models
__all__ = [
    # Base model
    "Base",
    
    # Author models
    "AuthorProfile",
    
    # Field/taxonomy models
    "Field",
    
    # Prompt models  
    "Prompt",
    "PromptType",
    
    # Paper models
    "Paper",
    "PaperAuthor", 
    "PaperField",
    
    # Article models
    "Article",
    "ArticleBlock",
    "ArticlePrompt",
    "BlockType",
]

# Model registry for easy access
MODEL_REGISTRY = {
    "author_profiles": AuthorProfile,
    "fields": Field,
    "prompts": Prompt,
    "papers": Paper,
    "paper_authors": PaperAuthor,
    "paper_fields": PaperField,
    "articles": Article,
    "article_blocks": ArticleBlock,
    "article_prompts": ArticlePrompt,
}

def get_model_by_table_name(table_name: str):
    """
    Get model class by table name.
    
    Args:
        table_name: Name of the database table
        
    Returns:
        Model class or None if not found
    """
    return MODEL_REGISTRY.get(table_name)
