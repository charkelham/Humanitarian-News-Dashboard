"""
Update broken RSS feed URLs for humanitarian news sources.
This script is idempotent and safe to run multiple times.
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import Source

# Mapping of source name -> correct RSS URL
UPDATED_URLS = {
    "ReliefWeb – Latest": "https://reliefweb.int/updates/rss.xml",
    "ReliefWeb – Disasters": "https://reliefweb.int/disasters/rss.xml",
    "UN OCHA": "https://www.unocha.org/rss.xml",
    "UNHCR": "https://www.unhcr.org/feeds/news",
    "WFP": "https://www.wfp.org/news/rss",
    "UNICEF": "https://www.unicef.org/feeds/press-releases.rss",
}


async def update_rss_sources():
    """Update RSS feed URLs for sources with broken/outdated URLs."""
    async with AsyncSessionLocal() as db:
        for source_name, new_url in UPDATED_URLS.items():
            query = select(Source).where(Source.name == source_name)
            result = await db.execute(query)
            source = result.scalar_one_or_none()

            if source is None:
                print(f"⚠️  Source not found: {source_name} (skipping)")
                continue

            if source.rss_url == new_url:
                print(f"✅ {source_name}: URL already up to date")
                continue

            old_url = source.rss_url
            source.rss_url = new_url
            print(f"🔄 {source_name}: {old_url} -> {new_url}")

        await db.commit()
        print("✅ RSS source URLs updated successfully")


if __name__ == "__main__":
    asyncio.run(update_rss_sources())
