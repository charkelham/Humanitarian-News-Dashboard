"""
Seed script: populate the database with humanitarian RSS sources.

Safe to re-run at any time — by default it performs an upsert by name, so
sources that already exist in the DB are skipped.  Only new sources (those
whose name does not yet exist) are inserted.

To add new sources in the future, simply append them to HUMANITARIAN_SOURCES
and re-run this script; it will skip any source whose name already exists in
the DB and only insert the new ones.

Usage:
    cd backend
    python scripts/seed_humanitarian_sources.py

    # To wipe all existing sources and re-seed from scratch:
    python scripts/seed_humanitarian_sources.py --reset

Or with Poetry:
    poetry run python scripts/seed_humanitarian_sources.py
"""

import asyncio
import logging
import sys
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

    # ── More UN / intergovernmental ──────────────────────────────────────
    {
        "name": "IOM",
        "rss_url": "https://www.iom.int/rss/news.xml",
        "type": "rss",
        "tier": 1,
        "enabled": True,
    },
    {
        "name": "FAO",
        "rss_url": "https://www.fao.org/news/rss-feed/en/",
        "type": "rss",
        "tier": 1,
        "enabled": True,
    },
    {
        "name": "WHO – Emergencies",
        "rss_url": "https://www.who.int/rss-feeds/news-english.xml",
        "type": "rss",
        "tier": 1,
        "enabled": True,
    },

    # ── More NGOs ─────────────────────────────────────────────────────────
    {
        "name": "Save the Children",
        "rss_url": "https://www.savethechildren.net/rss.xml",
        "type": "rss",
        "tier": 2,
        "enabled": True,
    },
    {
        "name": "NRC (Norwegian Refugee Council)",
        "rss_url": "https://www.nrc.no/rss/",
        "type": "rss",
        "tier": 2,
        "enabled": True,
    },
    {
        "name": "Human Rights Watch",
        "rss_url": "https://www.hrw.org/rss/news.xml",
        "type": "rss",
        "tier": 2,
        "enabled": True,
    },
    {
        "name": "Amnesty International",
        "rss_url": "https://www.amnesty.org/en/feed/",
        "type": "rss",
        "tier": 2,
        "enabled": True,
    },
    {
        "name": "Care International",
        "rss_url": "https://www.care-international.org/rss.xml",
        "type": "rss",
        "tier": 2,
        "enabled": True,
    },
    {
        "name": "World Vision",
        "rss_url": "https://www.wvi.org/rss.xml",
        "type": "rss",
        "tier": 2,
        "enabled": True,
    },

    # ── Analysis / early warning ──────────────────────────────────────────
    {
        "name": "ReliefWeb – Analysis",
        "rss_url": "https://reliefweb.int/rss.xml/resources/assessment",
        "type": "rss",
        "tier": 1,
        "enabled": True,
    },
    {
        "name": "IFRC",
        "rss_url": "https://www.ifrc.org/rss/news.xml",
        "type": "rss",
        "tier": 1,
        "enabled": True,
    },
    {
        "name": "UN News – Humanitarian",
        "rss_url": "https://news.un.org/feed/subscribe/en/news/topic/humanitarian-aid/feed/rss.xml",
        "type": "rss",
        "tier": 1,
        "enabled": True,
    },
    {
        "name": "Al Jazeera – Middle East",
        "rss_url": "https://www.aljazeera.com/xml/rss/all.xml",
        "type": "rss",
        "tier": 2,
        "enabled": True,
    },
    {
        "name": "Voice of America – Africa",
        "rss_url": "https://www.voanews.com/api/epiqq-voa/_ygdqdrzt",
        "type": "rss",
        "tier": 2,
        "enabled": True,
    },
]


async def seed():
    """Upsert humanitarian sources by name (insert new, skip existing).

    Pass --reset on the command line to wipe all existing sources first and
    re-seed from scratch.
    """
    reset_mode = "--reset" in sys.argv

    async with AsyncSessionLocal() as db:

        # Show what's currently in the DB
        existing = await db.execute(select(Source))
        current = existing.scalars().all()
        logger.info(f"Found {len(current)} existing sources in DB.")

        if reset_mode:
            logger.info("--reset flag detected: deleting all existing sources.")
            await db.execute(delete(Source))
            await db.commit()
            logger.info("Deleted all existing sources.")
            existing_names: set[str] = set()
        else:
            existing_names = {s.name for s in current}

        # Upsert: insert only sources that don't exist yet
        inserted = 0
        skipped = 0
        for feed in HUMANITARIAN_SOURCES:
            if feed["name"] in existing_names:
                logger.info(f"  '{feed['name']}' already exists, skipping.")
                skipped += 1
                continue

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
            inserted += 1

        await db.commit()
        logger.info(f"Inserted {inserted} new source(s), skipped {skipped} existing.")

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