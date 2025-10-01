"""
Prompt Models
=============

Database models for AI prompt templates and versioning in the Zara ETL system.
"""

import enum
from typing import Optional

from sqlalchemy import String, Text, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class PromptType(enum.Enum):
    """
    Enumeration of different prompt types used in the system.
    
    Values:
    - article: Prompts for generating article content
    - image: Prompts for generating image descriptions/requests
    - video: Prompts for generating video scripts/descriptions
    - text_to_speech: Prompts for text-to-speech generation
    """
    ARTICLE = "article"
    IMAGE = "image"
    VIDEO = "video"
    TEXT_TO_SPEECH = "text-to-speech"


class Prompt(Base):
    """
    AI prompt template model for storing and versioning prompts.
    
    This model stores different types of AI prompts used throughout
    the content generation pipeline:
    - Article generation prompts
    - Image generation prompts  
    - Video script prompts
    - Text-to-speech prompts
    
    Each prompt can have multiple versions and be associated with
    multiple articles through the ArticlePrompt junction table.
    
    Relationships:
    - articles: Many-to-many through ArticlePrompt junction table
    """
    
    __tablename__ = "prompts"
    
    # Basic Information
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Human-readable name for the prompt"
    )
    
    type: Mapped[PromptType] = mapped_column(
        Enum(PromptType),
        nullable=False,
        comment="Type of prompt (article, image, video, text-to-speech)"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Description of what this prompt does"
    )
    
    # Prompt Content
    image_generation_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="The actual prompt template text for image generation"
    )
    
    # Note: The original schema only shows image_generation_prompt,
    # but we should add other prompt content fields for different types
    article_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="The actual prompt template text for article generation"
    )
    
    video_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="The actual prompt template text for video generation"
    )
    
    tts_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="The actual prompt template text for text-to-speech"
    )
    
    # Versioning and metadata
    version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="1.0.0",
        comment="Version number of this prompt"
    )
    
    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
        comment="Whether this prompt version is currently active"
    )
    
    # Model configuration
    model_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Preferred AI model for this prompt"
    )
    
    temperature: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        default=0.1,
        comment="Temperature setting for AI model"
    )
    
    max_tokens: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        comment="Maximum tokens for AI model response"
    )
    
    # Performance tracking
    success_rate: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        comment="Success rate of this prompt (0.0-1.0)"
    )
    
    average_quality_score: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        comment="Average quality score achieved with this prompt"
    )
    
    usage_count: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
        comment="Number of times this prompt has been used"
    )
    
    # Relationships
    article_prompts = relationship(
        "ArticlePrompt",
        back_populates="prompt",
        cascade="all, delete-orphan"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_prompts_name', 'name'),
        Index('ix_prompts_type', 'type'),
        Index('ix_prompts_version', 'version'),
        Index('ix_prompts_active', 'is_active'),
        Index('ix_prompts_type_active', 'type', 'is_active'),
        Index('ix_prompts_name_version', 'name', 'version'),
    )
    
    @property
    def articles(self):
        """Get all articles that used this prompt."""
        return [ap.article for ap in self.article_prompts]
    
    @property
    def article_count(self) -> int:
        """Get count of articles that used this prompt."""
        return len(self.article_prompts)
    
    def get_prompt_content(self) -> Optional[str]:
        """
        Get the appropriate prompt content based on type.
        
        Returns:
            Optional[str]: The prompt content for this type
        """
        content_mapping = {
            PromptType.ARTICLE: self.article_prompt,
            PromptType.IMAGE: self.image_generation_prompt,
            PromptType.VIDEO: self.video_prompt,
            PromptType.TEXT_TO_SPEECH: self.tts_prompt,
        }
        return content_mapping.get(self.type)
    
    def set_prompt_content(self, content: str) -> None:
        """
        Set the prompt content based on type.
        
        Args:
            content: The prompt content to set
        """
        if self.type == PromptType.ARTICLE:
            self.article_prompt = content
        elif self.type == PromptType.IMAGE:
            self.image_generation_prompt = content
        elif self.type == PromptType.VIDEO:
            self.video_prompt = content
        elif self.type == PromptType.TEXT_TO_SPEECH:
            self.tts_prompt = content
    
    def increment_usage(self) -> None:
        """Increment the usage count for this prompt."""
        self.usage_count += 1
    
    def update_performance_metrics(self, quality_score: float, success: bool) -> None:
        """
        Update performance metrics for this prompt.
        
        Args:
            quality_score: Quality score for the generation (0.0-1.0)
            success: Whether the generation was successful
        """
        # Update success rate
        if self.success_rate is None:
            self.success_rate = 1.0 if success else 0.0
        else:
            # Running average
            total_attempts = self.usage_count
            successful_attempts = int(self.success_rate * total_attempts)
            if success:
                successful_attempts += 1
            self.success_rate = successful_attempts / (total_attempts + 1)
        
        # Update average quality score
        if self.average_quality_score is None:
            self.average_quality_score = quality_score
        else:
            # Running average
            total_score = self.average_quality_score * self.usage_count
            self.average_quality_score = (total_score + quality_score) / (self.usage_count + 1)
        
        # Increment usage
        self.increment_usage()
    
    @classmethod
    def get_active_by_type(cls, prompt_type: PromptType):
        """
        Get active prompts by type.
        
        Args:
            prompt_type: The type of prompt to retrieve
            
        Returns:
            Query for active prompts of the specified type
        """
        # This would need to be called with a session
        # Return None for now - implement in service layer
        return None
    
    def __repr__(self) -> str:
        """String representation of the prompt."""
        return f"<Prompt(name='{self.name}', type='{self.type.value}', version='{self.version}')>"
