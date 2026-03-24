"""
Seed script: replace energy transition RSS sources with humanitarian feeds.

Run this once after deploying to clear out energy sources and add
the humanitarian feeds needed for SENTINEL.

Usage:
    cd backend
    python scripts/seed_humanitarian_sources.py

Or with Poetry:
    poetry run python scripts/seed_humanitarian_sources.py
"""

import asyncio
import logging
from sqlalchemy import delete, select
from app.db.session import AsyncSessionLocal
from app.db.models import Source

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Humanitarian RSS feeds
# Each dict maps to fields on the Source model.
# 'type' is left as "rss" (default pipeline behaviour).
# ---------------------------------------------------------------------------

HUMANITARIAN_SOURCES = [
    # ── OCHA / ReliefWeb ───────────────────────────────────────────────
    {
        "name": "ReliefWeb – Latest",
        "rss_url": "https://reliefweb.int/rss.xml/world/latest",
        "type": "rss",
        "tier": 1,       # tier 1 = most authoritative
        "enabled": True,
    },
    {
        "name": "ReliefWeb – Disasters",
        "rss_url": "https://reliefweb.int/rss.xml/disasters",
        "type": "rss",
        "tier": 1,
        "enabled": True,
    },
    {
        "name": "UN OCHA",
        "rss_url": "https://www.unocha.org/feeds/rss",
        "type": "rss",
        "tier": 1,
        "enabled": True,
    },

    # ── UN Agencies ────────────────────────────────────────────────────
    {
        "name": "UNHCR",
        "rss_url": "https://www.unhcr.org/rss/news.rss",
        "type": "rss",
        "tier": 1,
        "enabled": True,
    },
    {
        "name": "WFP",
        "rss_url": "https://www.wfp.org/rss.xml",
        "type": "rss",
        "tier": 1,
        "enabled": True,
    },
    {
        "name": "UNICEF",
        "rss_url": "https://www.unicef.org/press-releases/rss.xml",
        "type": "rss",
        "tier": 1,
        "enabled": True,
    },

    # ── ICRC ───────────────────────────────────────────────────────────
    {
        "name": "ICRC",
        "rss_url": "https://www.icrc.org/en/rss/news",
        "type": "rss",
        "tier": 1,
        "enabled": True,
    },

    # ── NGOs ───────────────────────────────────────────────────────────
    {
        "name": "MSF",
        "rss_url": "https://www.msf.org/rss/news",
        "type": "rss",
        "tier": 2,
        "enabled": True,
    },
    {
        "name": "IRC",
        "rss_url": "https://www.rescue.org/rss.xml",
        "type": "rss",
        "tier": 2,
        "enabled": True,
    },
    {
        "name": "Oxfam",
        "rss_url": "https://www.oxfam.org/en/rss.xml",
        "type": "rss",
        "tier": 2,
        "enabled": True,
    },

    # ── Specialist media ───────────────────────────────────────────────
    {
        "name": "The New Humanitarian",
        "rss_url": "https://www.thenewhumanitarian.org/rss.xml",
        "type": "rss",
        "tier": 2,
        "enabled": True,
    },
    {
        "name": "Devex – Humanitarian",
        "rss_url": "https://www.devex.com/rss/news",
        "type": "rss",
        "tier": 2,
        "enabled": True,
    },

    # ── Analysis / research ────────────────────────────────────────────
    {
        "name": "ACAPS",
        "rss_url": "https://www.acaps.org/feed",
        "type": "rss",
        "tier": 1,
        "enabled": True,
    },
    {
        "name": "Crisis Group",
        "rss_url": "https://www.crisisgroup.org/rss.xml",
        "type": "rss",
        "tier": 2,
        "enabled": True,
    },
]


async def seed():
    """Remove all existing sources and insert humanitarian feeds."""
    async with AsyncSessionLocal() as db:

        # Show what's currently in the DB
        existing = await db.execute(select(Source))
        current = existing.scalars().all()
        logger.info(f"Found {len(current)} existing sources:")
        for s in current:
            logger.info(f"  [{s.id}] {s.name} — {s.rss_url}")

        # Confirm before deleting
        if current:
            confirm = input(
                f"\nThis will DELETE all {len(current)} existing sources "
                f"and replace them with {len(HUMANITARIAN_SOURCES)} humanitarian feeds.\n"
                f"Type 'yes' to continue: "
            ).strip().lower()

            if confirm != "yes":
                logger.info("Aborted.")
                return

            # Delete all existing sources
            await db.execute(delete(Source))
            await db.commit()
            logger.info("Deleted all existing sources.")

        # Insert humanitarian sources
        for feed in HUMANITARIAN_SOURCES:
            # Check Source model fields — add only fields that exist
            source = Source(
                name=feed["name"],
                rss_url=feed["rss_url"],
                type=feed.get("type", "rss"),
                enabled=feed.get("enabled", True),
            )
            # Add tier to metadata if the Source model supports it
            # (safe to remove if your Source model has no 'tier' field)
            if hasattr(source, "tier"):
                source.tier = feed.get("tier", 2)

            db.add(source)

        await db.commit()
        logger.info(f"Inserted {len(HUMANITARIAN_SOURCES)} humanitarian sources.")

        # Confirm
        result = await db.execute(select(Source))
        new_sources = result.scalars().all()
        logger.info("\nSources now in database:")
        for s in new_sources:
            logger.info(f"  [{s.id}] {s.name}")

    logger.info("\nDone. Run the ingestion pipeline to start fetching articles:")
    logger.info("  docker compose exec backend python -m app.ingest.run_once")


if __name__ == "__main__":
    asyncio.run(seed())