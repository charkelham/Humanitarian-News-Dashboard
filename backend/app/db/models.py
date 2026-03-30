"""
SQLAlchemy models for Humanitarian News Dashboard.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey,
    Index, JSON, text, ARRAY
)
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.db.session import Base


class Source(Base):
    """RSS feed sources for news ingestion."""
    
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    type = Column(String(50), nullable=False, default="rss")  # rss, api, etc.
    rss_url = Column(Text, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    articles = relationship("Article", back_populates="source")
    
    def __repr__(self):
        return f"<Source(id={self.id}, name='{self.name}', enabled={self.enabled})>"


class Article(Base):
    """News articles with content and enrichment metadata."""
    
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    title = Column(Text, nullable=False)
    url = Column(Text, nullable=False, unique=True)
    published_at = Column(DateTime, nullable=True, index=True)
    fetched_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Content
    raw_summary = Column(Text, nullable=True)
    content_text = Column(Text, nullable=True)
    
    # Enrichment fields
    language = Column(String(10), nullable=True)  # ISO 639-1 code
    hash = Column(String(64), nullable=True, index=True)  # Content hash for deduplication
    country_codes = Column(ARRAY(String), nullable=True)  # ISO 3166-1 alpha-2 codes
    topic_tags = Column(ARRAY(String), nullable=True)  # Humanitarian crisis topics
    
    # Vector embedding for RAG
    embedding = Column(Vector(1536), nullable=True)  # OpenAI text-embedding-3-small dimension
    
    # Additional metadata (flexible JSON field)
    article_metadata = Column(JSON, nullable=True)
    
    # Relationships
    source = relationship("Source", back_populates="articles")
    chunks = relationship("ArticleChunk", back_populates="article", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:50]}...', source_id={self.source_id})>"


class ArticleChunk(Base):
    """Text chunks from articles with embeddings for RAG."""
    
    __tablename__ = "article_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=True)
    
    # Denormalized fields for filtering without joins
    country_codes = Column(ARRAY(String), nullable=True)
    topic_tags = Column(ARRAY(String), nullable=True)
    published_at = Column(DateTime, nullable=True, index=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship
    article = relationship("Article", back_populates="chunks")
    
    def __repr__(self):
        return f"<ArticleChunk(id={self.id}, article_id={self.article_id}, chunk_index={self.chunk_index})>"


class IngestionRun(Base):
    """Tracking metadata for each ingestion job run."""
    
    __tablename__ = "ingestion_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False)  # running, completed, failed
    
    # Statistics (new articles, updated, failed, etc.)
    stats = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<IngestionRun(id={self.id}, status='{self.status}', started_at={self.started_at})>"

class Brief(Base):
    """Cached AI-generated briefs for countries."""
    
    __tablename__ = "briefs"
    
    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String(2), nullable=False, index=True)
    content = Column(Text, nullable=False)
    article_count = Column(Integer, nullable=False, default=0)
    generated_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    days_range = Column(Integer, nullable=False, default=7)
    
    def __repr__(self):
        return f"<Brief(id={self.id}, country='{self.country_code}', generated_at={self.generated_at})>"

# Create indexes
Index("idx_articles_published_at", Article.published_at)
Index("idx_articles_source_id", Article.source_id)
Index("idx_articles_country_codes_gin", Article.country_codes, postgresql_using="gin")
Index("idx_articles_topic_tags_gin", Article.topic_tags, postgresql_using="gin")
Index("idx_articles_embedding_ivfflat", Article.embedding, postgresql_using="ivfflat")

Index("idx_article_chunks_article_id_index", ArticleChunk.article_id, ArticleChunk.chunk_index)
Index("idx_article_chunks_country_codes_gin", ArticleChunk.country_codes, postgresql_using="gin")
Index("idx_article_chunks_topic_tags_gin", ArticleChunk.topic_tags, postgresql_using="gin")
