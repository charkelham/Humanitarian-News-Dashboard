"""
One-off script to re-run topic and country tagging on existing articles that
have content_text but are missing topic_tags.

The ingestion pipeline skips articles where content_text is already set, so
existing articles never get re-tagged when the tagger improves.  Run this
script once after deploying improved keywords to backfill all untagged articles.

Usage:
    cd backend
    python scripts/retag_articles.py

    # To retag ALL articles (including ones that already have tags), pass --all:
    python scripts/retag_articles.py --all
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from sqlalchemy.orm import joinedload

from app.db.session import AsyncSessionLocal
from app.db.models import Article, ArticleChunk, Source
from app.services.nlp.topic_tagger import TopicTagger
from app.services.nlp.country_tagger import CountryTagger

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BATCH_SIZE = 50


async def main() -> None:
    retag_all = "--all" in sys.argv

    topic_tagger = TopicTagger()
    country_tagger = CountryTagger()

    async with AsyncSessionLocal() as db:
        # Build query
        query = (
            select(Article)
            .join(Source, Article.source_id == Source.id)
            .options(joinedload(Article.source))
            .where(Article.content_text.isnot(None))
        )
        if not retag_all:
            query = query.where(
                (Article.topic_tags.is_(None)) | (Article.topic_tags == [])
            )

        result = await db.execute(query)
        articles = result.scalars().all()

    total = len(articles)
    logger.info(
        f"Found {total} article(s) to retag"
        + (" (--all mode: including already-tagged)" if retag_all else "")
    )

    if total == 0:
        logger.info("Nothing to do.")
        return

    updated = 0
    errors = 0

    for batch_start in range(0, total, BATCH_SIZE):
        batch = articles[batch_start : batch_start + BATCH_SIZE]

        batch_updated = 0
        async with AsyncSessionLocal() as db:
            for article in batch:
                try:
                    # Re-attach the article to this session
                    article_db = await db.get(Article, article.id)
                    if article_db is None:
                        continue

                    # Fetch the source name (needed for NESO special case)
                    source_result = await db.execute(
                        select(Source).where(Source.id == article_db.source_id)
                    )
                    source = source_result.scalar_one_or_none()
                    source_name = source.name if source else ""

                    title = article_db.title or ""
                    content = article_db.content_text or ""

                    # Country tagging — NESO is always GB
                    if source_name == "NESO":
                        new_country_codes = ["GB"]
                    else:
                        new_country_codes, _ = country_tagger.tag_article(
                            title=title,
                            content=content,
                        )

                    # Topic tagging
                    new_topic_tags = topic_tagger.tag_article(
                        title=title,
                        content=content,
                    )

                    article_db.country_codes = new_country_codes
                    article_db.topic_tags = new_topic_tags

                    # Update denormalized fields on all chunks for this article
                    chunks_result = await db.execute(
                        select(ArticleChunk).where(
                            ArticleChunk.article_id == article_db.id
                        )
                    )
                    chunks = chunks_result.scalars().all()
                    for chunk in chunks:
                        chunk.topic_tags = new_topic_tags
                        chunk.country_codes = new_country_codes

                    batch_updated += 1

                except Exception as exc:
                    logger.error(f"Error retagging article {article.id}: {exc}")
                    errors += 1
                    await db.rollback()
                    continue

            try:
                await db.commit()
                updated += batch_updated
            except Exception as exc:
                logger.error(f"Commit failed for batch starting at {batch_start}: {exc}")
                await db.rollback()
                errors += batch_updated
                continue

        # Log progress every BATCH_SIZE articles
        processed = min(batch_start + BATCH_SIZE, total)
        logger.info(f"Progress: {processed}/{total} processed ({updated} updated, {errors} errors)")

    logger.info(
        f"\nDone. Total: {total} | Updated: {updated} | Errors: {errors}"
    )


if __name__ == "__main__":
    asyncio.run(main())
