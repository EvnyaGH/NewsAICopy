"""
Article Models
==============

Database models for generated articles and related entities in the Zara ETL system.
"""

import enum
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import String, Text, Boolean, BigInteger, Integer, ForeignKey, Index, UniqueConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class BlockType(enum.Enum):
    """
    Enumeration of different article block types.
    
    Values:
    - title: Article title/headline
    - paragraph: Regular paragraph content
    - subheading: Section subheading
    - quote: Pull quote or blockquote
    - image: Image with caption
    """
    TITLE = "title"
    PARAGRAPH = "paragraph"
    SUBHEADING = "subheading"
    QUOTE = "quote"
    IMAGE = "image"


class Article(Base):
    """
    Generated article model storing article metadata and relationships.
    
    This model stores article-level information including:
    - Basic article metadata (title, slug, status)
    - Visual elements (featured image)
    - Editorial information (edited status)
    - Performance metrics (views, engagement)
    - Relationship to source paper
    - Relationship to article blocks (content structure)
    
    Relationships:
    - paper: Many-to-one with Paper model (source paper)
    - blocks: One-to-many with ArticleBlock model (content structure)
    - prompts: Many-to-many through ArticlePrompt junction table
    """
    
    __tablename__ = "articles"
    
    # Foreign key to source paper
    paper_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("papers.id"),
        nullable=False,
        comment="Reference to source paper"
    )
    
    # Basic article information
    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Article title/headline"
    )
    
    slug: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="URL-friendly slug for the article"
    )
    
    # Publishing status
    status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default="draft",
        comment="Publication status (draft, review, published, archived)"
    )
    
    # Visual elements
    featured_image_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="URL to featured image"
    )
    
    # Editorial information
    is_edited: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether article has been manually edited"
    )
    
    # Performance metrics
    view_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
        comment="Number of page views"
    )
    
    engagement_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Engagement metrics (time on page, shares, etc.)"
    )
    
    # SEO and metadata
    meta_title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="SEO meta title"
    )
    
    meta_description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="SEO meta description"
    )
    
    meta_keywords: Mapped[Optional[List[str]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="SEO keywords as JSON array"
    )
    
    # Quality metrics
    quality_score: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        comment="Quality score for the article (0.0-1.0)"
    )
    
    readability_score: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        comment="Readability score (e.g., Flesch Reading Ease)"
    )
    
    # Generation metadata
    generation_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Metadata about article generation (model, prompts, costs, etc.)"
    )
    
    # Publishing information
    published_at: Mapped[Optional[Any]] = mapped_column(
        nullable=True,
        comment="Timestamp when article was published"
    )
    
    # Relationships
    paper = relationship("Paper", back_populates="articles")
    
    blocks = relationship(
        "ArticleBlock",
        back_populates="article",
        cascade="all, delete-orphan",
        order_by="ArticleBlock.order_index"
    )
    
    article_prompts = relationship(
        "ArticlePrompt",
        back_populates="article",
        cascade="all, delete-orphan"
    )
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_articles_paper_id', 'paper_id'),
        Index('ix_articles_slug', 'slug'),
        Index('ix_articles_status', 'status'),
        Index('ix_articles_title', 'title'),
        Index('ix_articles_view_count', 'view_count'),
        Index('ix_articles_quality_score', 'quality_score'),
        Index('ix_articles_published_at', 'published_at'),
        Index('ix_articles_is_edited', 'is_edited'),
        # Composite indexes for common queries
        Index('ix_articles_status_published', 'status', 'published_at'),
        Index('ix_articles_paper_status', 'paper_id', 'status'),
    )
    
    # Properties for convenience
    
    @property
    def prompts(self) -> List['Prompt']:
        """Get all prompts used for this article."""
        return [ap.prompt for ap in self.article_prompts]
    
    @property
    def word_count(self) -> int:
        """Calculate approximate word count from all text blocks."""
        word_count = 0
        for block in self.blocks:
            if block.content and block.block_type in [BlockType.PARAGRAPH, BlockType.QUOTE]:
                word_count += len(block.content.split())
        return word_count
    
    @property
    def is_published(self) -> bool:
        """Check if article is published."""
        return self.status == "published"
    
    @property
    def reading_time_minutes(self) -> int:
        """Estimate reading time in minutes (assuming 200 words per minute)."""
        return max(1, self.word_count // 200)
    
    # Utility methods
    
    def add_block(self, block_type: BlockType, content: str, order_index: Optional[int] = None) -> 'ArticleBlock':
        """
        Add a content block to this article.
        
        Args:
            block_type: Type of block to add
            content: Block content
            order_index: Position in article (defaults to end)
            
        Returns:
            ArticleBlock: The created block
        """
        if order_index is None:
            # Get next available order
            existing_orders = [block.order_index for block in self.blocks]
            order_index = max(existing_orders, default=0) + 1
        
        block = ArticleBlock(
            article=self,
            block_type=block_type,
            content=content,
            order_index=order_index
        )
        self.blocks.append(block)
        return block
    
    def add_prompt(self, prompt: 'Prompt') -> 'ArticlePrompt':
        """
        Associate a prompt with this article.
        
        Args:
            prompt: Prompt to associate
            
        Returns:
            ArticlePrompt: The created association
        """
        article_prompt = ArticlePrompt(article=self, prompt=prompt)
        self.article_prompts.append(article_prompt)
        return article_prompt
    
    def increment_views(self, count: int = 1) -> None:
        """
        Increment the view count.
        
        Args:
            count: Number of views to add (default 1)
        """
        self.view_count += count
    
    def set_engagement_metric(self, key: str, value: Any) -> None:
        """
        Set an engagement metric value.
        
        Args:
            key: Metric key
            value: Metric value
        """
        if self.engagement_metrics is None:
            self.engagement_metrics = {}
        self.engagement_metrics[key] = value
    
    def get_engagement_metric(self, key: str, default: Any = None) -> Any:
        """
        Get an engagement metric value.
        
        Args:
            key: Metric key
            default: Default value if key not found
            
        Returns:
            Any: Metric value or default
        """
        if self.engagement_metrics is None:
            return default
        return self.engagement_metrics.get(key, default)
    
    def set_generation_metadata(self, key: str, value: Any) -> None:
        """
        Set generation metadata.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        if self.generation_metadata is None:
            self.generation_metadata = {}
        self.generation_metadata[key] = value
    
    def get_generation_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get generation metadata.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Any: Metadata value or default
        """
        if self.generation_metadata is None:
            return default
        return self.generation_metadata.get(key, default)
    
    def get_content_by_type(self, block_type: BlockType) -> List[str]:
        """
        Get all content blocks of a specific type.
        
        Args:
            block_type: Type of blocks to retrieve
            
        Returns:
            List[str]: List of content strings
        """
        return [
            block.content for block in self.blocks 
            if block.block_type == block_type and block.content
        ]
    
    def get_full_content(self) -> str:
        """
        Get full article content as concatenated string.
        
        Returns:
            str: Full article content
        """
        content_parts = []
        for block in sorted(self.blocks, key=lambda x: x.order_index):
            if block.content:
                content_parts.append(block.content)
        return "\n\n".join(content_parts)
    
    def __repr__(self) -> str:
        """String representation of the article."""
        return f"<Article(slug='{self.slug}', title='{self.title[:50]}...')>"


class ArticleBlock(Base):
    """
    Individual content block within an article.
    
    Articles are composed of multiple blocks (paragraphs, headings, quotes, etc.)
    in a specific order. This allows for flexible article structure and rendering.
    """
    
    __tablename__ = "article_blocks"
    
    # Foreign key to parent article
    article_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("articles.id"),
        nullable=False,
        comment="Reference to parent article"
    )
    
    # Block information
    block_type: Mapped[BlockType] = mapped_column(
        Enum(BlockType),
        nullable=False,
        comment="Type of content block"
    )
    
    content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Block content"
    )
    
    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Order position within article"
    )
    
    # Additional block metadata
    block_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Additional block-specific metadata"
    )
    
    # Relationships
    article = relationship("Article", back_populates="blocks")
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('article_id', 'order_index', name='uq_article_blocks_article_order'),
        Index('ix_article_blocks_article_id', 'article_id'),
        Index('ix_article_blocks_type', 'block_type'),
        Index('ix_article_blocks_order', 'order_index'),
        Index('ix_article_blocks_article_order', 'article_id', 'order_index'),
    )
    
    # Utility methods
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set block metadata.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        if self.block_metadata is None:
            self.block_metadata = {}
        self.block_metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get block metadata.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Any: Metadata value or default
        """
        if self.block_metadata is None:
            return default
        return self.block_metadata.get(key, default)
    
    @property
    def word_count(self) -> int:
        """Get word count for this block."""
        if not self.content:
            return 0
        return len(self.content.split())
    
    def __repr__(self) -> str:
        """String representation of the article block."""
        content_preview = (self.content[:50] + "...") if self.content else "None"
        return f"<ArticleBlock(type={self.block_type.value}, order={self.order_index}, content='{content_preview}')>"


class ArticlePrompt(Base):
    """
    Junction table for Article ↔ Prompt many-to-many relationship.
    
    This model tracks which prompts were used to generate which articles,
    supporting prompt versioning and A/B testing.
    """
    
    __tablename__ = "article_prompts"
    
    # Foreign keys
    article_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("articles.id"),
        nullable=False,
        comment="Reference to article"
    )
    
    prompt_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("prompts.id"),
        nullable=False,
        comment="Reference to prompt"
    )
    
    # Relationships
    article = relationship("Article", back_populates="article_prompts")
    prompt = relationship("Prompt", back_populates="article_prompts")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('article_id', 'prompt_id', name='uq_article_prompts_article_prompt'),
        Index('ix_article_prompts_article_id', 'article_id'),
        Index('ix_article_prompts_prompt_id', 'prompt_id'),
    )
    
    def __repr__(self) -> str:
        """String representation of the article-prompt relationship."""
        return f"<ArticlePrompt(article_id={self.article_id}, prompt_id={self.prompt_id})>"
