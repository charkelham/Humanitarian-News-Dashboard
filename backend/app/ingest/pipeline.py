"""
Full ingestion pipeline: RSS fetch -> extraction -> tagging -> chunking -> embeddings.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.db.models import Source, Article, ArticleChunk
from app.services.ingest.ingestion_service import IngestionService
from app.services.ingest.fetcher import RSSFetcher
from app.services.ingest.rss_parser import RSSParser
from app.services.ingest.content_extractor import ContentExtractor
from app.services.ingest.web_scraper import get_scraper
from app.services.nlp.country_tagger import CountryTagger
from app.services.nlp.topic_tagger import TopicTagger
from app.services.rag.chunking_service import ChunkingService
from app.services.rag.embedding_provider import OpenAIEmbeddingProvider
from app.settings import Settings

logger = logging.getLogger(__name__)


class IngestionMetrics:
    """Structured metrics for ingestion run."""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.sources_processed = 0
        self.articles_fetched = 0
        self.articles_new = 0
        self.articles_updated = 0
        self.articles_extracted = 0
        self.articles_tagged = 0
        self.chunks_created = 0
        self.chunks_embedded = 0
        self.errors = []
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        return {
            "start_time": self.start_time.isoformat(),
            "duration_seconds": round(duration, 2),
            "sources_processed": self.sources_processed,
            "articles_fetched": self.articles_fetched,
            "articles_new": self.articles_new,
            "articles_updated": self.articles_updated,
            "articles_extracted": self.articles_extracted,
            "articles_tagged": self.articles_tagged,
            "chunks_created": self.chunks_created,
            "chunks_embedded": self.chunks_embedded,
            "errors": len(self.errors),
            "error_details": self.errors[:10],  # First 10 errors
        }
    
    def log_summary(self):
        """Log metrics summary."""
        metrics = self.to_dict()
        logger.info(
            f"Ingestion completed in {metrics['duration_seconds']}s: "
            f"{metrics['sources_processed']} sources, "
            f"{metrics['articles_new']} new articles, "
            f"{metrics['chunks_created']} chunks, "
            f"{metrics['chunks_embedded']} embeddings, "
            f"{metrics['errors']} errors"
        )
        if self.errors:
            logger.warning(f"Errors encountered: {self.errors[:5]}")


async def run_full_ingestion_pipeline() -> Dict[str, Any]:
    """
    Run complete ingestion pipeline for all enabled sources.
    
    Steps:
    1. Fetch RSS feeds
    2. Parse articles
    3. Extract content (readability)
    4. Tag countries and topics
    5. Chunk articles
    6. Generate embeddings
    
    Returns:
        Dictionary with ingestion metrics
    """
    metrics = IngestionMetrics()
    logger.info("=" * 80)
    logger.info("Starting full ingestion pipeline")
    logger.info("=" * 80)
    
    # Initialize services
    settings = Settings()
    fetcher = RSSFetcher()
    parser = RSSParser()
    extractor = ContentExtractor()
    country_tagger = CountryTagger()
    topic_tagger = TopicTagger()
    chunking_service = ChunkingService()
    embedding_provider = OpenAIEmbeddingProvider(api_key=settings.OPENAI_API_KEY)
    
    async with AsyncSessionLocal() as db:
        # Get enabled sources
        query = select(Source).where(Source.enabled == True)
        result = await db.execute(query)
        sources = result.scalars().all()
        
        if not sources:
            logger.warning("No enabled sources found")
            return metrics.to_dict()
        
        logger.info(f"Found {len(sources)} enabled sources")
        
        # Process each source
        for source in sources:
            try:
                logger.info(f"Processing source: {source.name} (type: {source.type})")
                metrics.sources_processed += 1
                
                # Cache source fields to avoid lazy load failures after any DB rollback
                source_name = source.name
                source_type = source.type
                source_id_val = source.id
                
                # Fetch articles based on source type
                parsed_articles = []
                
                if source_type == "web_scraper":
                    # Step 1: Scrape website
                    try:
                        scraper = get_scraper(source.rss_url)  # rss_url field stores scraper name
                        if not scraper:
                            error_msg = f"Unknown scraper: {source.rss_url}"
                            logger.error(error_msg)
                            metrics.errors.append(error_msg)
                            continue
                        
                        raw_articles = await scraper.scrape_articles(max_pages=3)
                        logger.info(f"  Scraped {len(raw_articles)} articles")
                        
                        # Convert to parsed article format
                        for raw_article in raw_articles:
                            # Compute hash from URL
                            import hashlib
                            url_hash = hashlib.sha256(raw_article.url.encode('utf-8')).hexdigest()
                            
                            parsed_articles.append({
                                "title": raw_article.title,
                                "url": raw_article.url,
                                "published_at": raw_article.published_at,
                                "summary": raw_article.summary,
                                "hash": url_hash,
                                "image_url": raw_article.image_url,
                            })
                        
                        metrics.articles_fetched += len(parsed_articles)
                    except Exception as e:
                        error_msg = f"Failed to scrape {source.name}: {str(e)}"
                        logger.error(error_msg)
                        metrics.errors.append(error_msg)
                        continue
                
                else:
                    # Step 1: Fetch RSS feed (default behavior)
                    try:
                        xml_content = await fetcher.fetch_feed(source.rss_url)
                    except Exception as e:
                        error_msg = f"Failed to fetch {source.name}: {str(e)}"
                        logger.error(error_msg)
                        metrics.errors.append(error_msg)
                        continue
                    
                    # Step 2: Parse articles
                    try:
                        entries = parser.parse_feed(xml_content)
                        # Convert RSSEntry objects to dicts
                        parsed_articles = []
                        for entry in entries:
                            parsed_articles.append({
                                "title": entry.title,
                                "url": entry.url,
                                "published_at": entry.published_at,
                                "summary": entry.summary,
                                "hash": parser.compute_content_hash(entry.title, entry.url, entry.summary),
                            })
                        metrics.articles_fetched += len(parsed_articles)
                        logger.info(f"  Fetched {len(parsed_articles)} articles")
                    except Exception as e:
                        error_msg = f"Failed to parse {source.name}: {str(e)}"
                        logger.error(error_msg)
                        metrics.errors.append(error_msg)
                        continue
                
                # Step 3-6: Process each article
                for parsed_article in parsed_articles:
                    try:
                        # Upsert article
                        existing_query = select(Article).where(
                            Article.url == parsed_article["url"]
                        )
                        existing_result = await db.execute(existing_query)
                        existing_article = existing_result.scalar_one_or_none()
                        
                        if existing_article:
                            # Skip if already has content
                            if existing_article.content_text:
                                continue
                            article = existing_article
                            metrics.articles_updated += 1
                        else:
                            # Create new article
                            article = Article(
                                source_id=source_id_val,
                                title=parsed_article["title"],
                                url=parsed_article["url"],
                                hash=parsed_article.get("hash"),
                                published_at=parsed_article.get("published_at"),
                                raw_summary=parsed_article.get("summary"),
                            )
                            db.add(article)
                            metrics.articles_new += 1
                        
                        await db.flush()
                        
                        # Query article fields to avoid greenlet errors
                        article_url = article.url
                        article_id = article.id
                        
                        # Step 3: Extract content
                        try:
                            content, language, extracted_image_url = await extractor.extract_article(article_url)
                            article.content_text = content
                            article.language = language
                            
                            # Use scraper-provided image URL if available, otherwise use extracted one
                            final_image_url = parsed_article.get("image_url") or extracted_image_url
                            
                            # Fallback to source logo if still missing for specific sources
                            if not final_image_url:
                                if source_name == "NESO":
                                    final_image_url = "/source-logos/neso.png"
                                    logger.info(f"  🖼️  Using NESO logo as fallback")
                                elif 'eia.gov' in article_url.lower():
                                    final_image_url = "/source-logos/eia.jpg"
                                    logger.info(f"  🖼️  Using EIA logo as fallback")
                            
                            if final_image_url:
                                if not article.article_metadata:
                                    article.article_metadata = {}
                                article.article_metadata["image_url"] = final_image_url
                            
                            metrics.articles_extracted += 1
                        except Exception as e:
                            logger.warning(f"  Extraction failed for {article_url}: {e}")
                            continue
                        
                        # Step 4: Tag countries and topics
                        # Query fields explicitly to avoid greenlet errors in async context
                        article_title = article.title
                        article_content_text = article.content_text
                        
                        try:
                            # Country tagging - NESO is always UK
                            if source_name == "NESO":
                                article.country_codes = ["GB"]
                            else:
                                country_results, country_metadata = country_tagger.tag_article(
                                    title=article_title,
                                    content=article_content_text
                                )
                                article.country_codes = country_results
                            
                            # Topic tagging
                            topic_results = topic_tagger.tag_article(
                                title=article_title,
                                content=article_content_text
                            )
                            article.topic_tags = topic_results
                            
                            metrics.articles_tagged += 1
                        except Exception as e:
                            logger.warning(f"  Tagging failed for {article.url}: {e}")
                        
                        await db.flush()
                        
                        # Step 5: Chunk article
                        if article.content_text:
                            try:
                                # Delete existing chunks
                                existing_chunks_query = select(ArticleChunk).where(
                                    ArticleChunk.article_id == article.id
                                )
                                existing_chunks_result = await db.execute(existing_chunks_query)
                                existing_chunks = existing_chunks_result.scalars().all()
                                for chunk in existing_chunks:
                                    await db.delete(chunk)
                                
                                # Create new chunks
                                chunks = chunking_service.chunk_article(
                                    content_text=article.content_text,
                                )
                                
                                chunk_texts = []
                                chunk_objects = []
                                
                                for chunk_data in chunks:
                                    chunk = ArticleChunk(
                                        article_id=article.id,
                                        chunk_index=chunk_data["chunk_index"],
                                        text=chunk_data["text"],
                                        # Denormalize for faster filtering
                                        country_codes=article.country_codes,
                                        topic_tags=article.topic_tags,
                                        published_at=article.published_at,
                                    )
                                    chunk_objects.append(chunk)
                                    chunk_texts.append(chunk_data["text"])
                                
                                metrics.chunks_created += len(chunk_objects)
                                
                                # Step 6: Generate embeddings in batch
                                if chunk_texts:
                                    try:
                                        logger.info(f"  Generating embeddings for {len(chunk_texts)} chunks...")
                                        embeddings = await embedding_provider.embed(chunk_texts)
                                        logger.info(f"  ✅ Generated {len(embeddings)} embeddings")
                                        
                                        for chunk_obj, embedding in zip(chunk_objects, embeddings):
                                            chunk_obj.embedding = embedding
                                        
                                        metrics.chunks_embedded += len(embeddings)
                                    except Exception as e:
                                        logger.error(f"  ❌ Embedding failed for {article.url}: {e}")
                                        import traceback
                                        logger.error(traceback.format_exc())
                                        # Still save chunks without embeddings
                                
                                # Save chunks
                                for chunk_obj in chunk_objects:
                                    db.add(chunk_obj)
                                
                            except Exception as e:
                                logger.warning(f"  Chunking failed for {article.url}: {e}")
                                import traceback
                                logger.error(traceback.format_exc())
                        
                        await db.commit()
                        
                    except Exception as e:
                        error_msg = f"Failed to process article {parsed_article.get('url')}: {str(e)}"
                        logger.error(error_msg)
                        metrics.errors.append(error_msg)
                        await db.rollback()
                        continue
                
            except Exception as e:
                error_msg = f"Failed to process source {source.name}: {str(e)}"
                logger.error(error_msg)
                metrics.errors.append(error_msg)
                continue
    
    # Log summary
    logger.info("=" * 80)
    metrics.log_summary()
    logger.info("=" * 80)
    
    return metrics.to_dict()


if __name__ == "__main__":
    # Allow running as script for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(run_full_ingestion_pipeline())
