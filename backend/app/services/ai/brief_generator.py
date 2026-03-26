"""
AI Brief Generation Service

Generates country-specific humanitarian situation briefs from ingested articles.
"""

import re
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Article
from app.services.rag.chat_provider import ChatProvider


def _strip_html(text: str) -> str:
    """Remove HTML tags and decode common HTML entities."""
    if not text:
        return text
    text = re.sub(r'<[^>]+>', ' ', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>') \
               .replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


@dataclass
class BriefRequest:
    """Request for generating a brief."""
    country_code: Optional[str] = None
    topic: Optional[str] = None
    days: int = 7
    max_articles: int = 15


@dataclass
class BriefResponse:
    """Generated brief response."""
    brief: str
    article_count: int
    country_code: Optional[str]
    topic: Optional[str]
    date_range: dict
    articles: Optional[List[dict]] = None


class BriefGenerator:
    """
    Service for generating AI briefs from articles.
    """
    
    def __init__(self, chat_provider: ChatProvider):
        """
        Initialize brief generator.
        
        Args:
            chat_provider: Provider for chat completions
        """
        self.chat_provider = chat_provider
    
    async def generate_brief(
        self,
        db: AsyncSession,
        request: BriefRequest,
    ) -> BriefResponse:
        """
        Generate a brief based on recent articles.
        
        Args:
            db: Database session
            request: Brief generation request
            
        Returns:
            Generated brief with metadata
        """
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=request.days)
        
        # Fetch relevant articles
        articles = await self._fetch_articles(
            db=db,
            country_code=request.country_code,
            topic=request.topic,
            start_date=start_date,
            end_date=end_date,
            limit=request.max_articles,
        )
        
        if not articles:
            return BriefResponse(
                brief="No articles found matching the specified criteria.",
                article_count=0,
                country_code=request.country_code,
                topic=request.topic,
                date_range={
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            )
        
        # Generate brief using AI
        brief = await self._generate_brief_text(
            articles=articles,
            country_code=request.country_code,
            topic=request.topic,
        )
        
        # Prepare article metadata for frontend
        article_metadata = [
            {
                "id": article.id,
                "title": article.title,
                "url": article.url,
                "image_url": article.article_metadata.get('image_url') if article.article_metadata else None,
                "source_name": article.source.name if article.source else None,
            }
            for article in articles[:5]  # First 5 articles for images
        ]
        
        return BriefResponse(
            brief=brief,
            article_count=len(articles),
            articles=article_metadata,
            country_code=request.country_code,
            topic=request.topic,
            date_range={
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
        )
    
    async def _fetch_articles(
        self,
        db: AsyncSession,
        country_code: Optional[str],
        topic: Optional[str],
        start_date: datetime,
        end_date: datetime,
        limit: int,
    ) -> List[Article]:
        """
        Fetch articles matching criteria.
        
        Args:
            db: Database session
            country_code: Country code filter (e.g., 'US', 'UK')
            topic: Topic filter
            start_date: Start date for articles
            end_date: End date for articles
            limit: Maximum number of articles
            
        Returns:
            List of matching articles
        """
        from sqlalchemy.orm import selectinload
        
        # Build query with eager loading of source relationship
        query = select(Article).options(selectinload(Article.source)).where(
            and_(
                Article.published_at >= start_date,
                Article.published_at <= end_date,
            )
        )
        
        # Apply country filter if specified
        if country_code:
            # Use PostgreSQL ANY operator for array matching
            query = query.where(
                Article.country_codes.any(country_code)
            )
        
        # Apply topic filter if specified
        if topic:
            # Use PostgreSQL ANY operator for array matching
            query = query.where(
                Article.topic_tags.any(topic)
            )
        
        # Order by date (newest first) and limit
        query = query.order_by(Article.published_at.desc()).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def _generate_brief_text(
        self,
        articles: List[Article],
        country_code: Optional[str],
        topic: Optional[str],
    ) -> str:
        """
        Generate brief text using AI.
        
        Args:
            articles: List of articles to summarize
            country_code: Country code for context
            topic: Topic for context
            
        Returns:
            Generated brief text
        """
        # Build context from articles
        article_summaries = []
        for i, article in enumerate(articles, start=1):
            # Use country_codes and topic_tags arrays directly
            countries = article.country_codes or []
            topics = article.topic_tags or []
            
            # Use content_text instead of content
            raw_preview = (article.content_text[:500] if article.content_text else article.raw_summary) if (article.content_text or article.raw_summary) else None
            content_preview = _strip_html(raw_preview)[:500] if raw_preview else "No content available"
            
            # Build article summary
            summary = f"""
[{i}] {article.title}
Published: {article.published_at.strftime('%Y-%m-%d') if article.published_at else 'Unknown'}
Countries: {', '.join(countries) if countries else 'None'}
Topics: {', '.join(topics) if topics else 'None'}
URL: {article.url}

{content_preview}...
            """.strip()
            article_summaries.append(summary)
        
        context = "\n\n".join(article_summaries)
        
        # Build prompt
        filter_desc = []
        if country_code:
            filter_desc.append(f"country: {country_code}")
        if topic:
            filter_desc.append(f"topic: {topic}")
        
        filters_text = f" ({', '.join(filter_desc)})" if filter_desc else ""
        
        system_prompt = f"""You are a humanitarian analyst producing situation briefs for FCDO / HEROS early warning, synthesizing recent developments from news articles{filters_text}.

Writing Principles:
- Maintain a neutral, analytical tone throughout
- Focus on crisis developments, displacement figures, access constraints, funding gaps, and protection concerns
- Explain outcomes through conflict dynamics, climate factors, and humanitarian system capacity
- Avoid advocacy or speculative language
- Make uncertainty explicit when discussing projections or unverified reports

Opening Requirement:
Begin with the most significant development or emerging trend from the articles (e.g., escalation in violence, new displacement wave, famine declaration, disease outbreak, or funding shortfall).

Structure:
1. Lead with the key development or pattern
2. Explain the underlying drivers and context
3. Discuss implications for affected populations and humanitarian response
4. Identify what comes next and the key indicators to monitor

Style Constraints:
- Short to medium-length sentences
- Minimal adjectives and adverbs
- No rhetorical questions
- No generic conclusions or calls to action
- Write 300-500 words total

Source Handling:
- Synthesize the provided articles into original analysis
- Do not quote sources directly
- Reference articles using [1], [2] format when citing specific facts
- Do not mention "the articles" or "according to sources" - write as direct analysis

Output:
- Write for humanitarian professionals and policy makers
- Assume familiarity with humanitarian coordination systems (clusters, HRPs, HNOs), IPC phases, and protection frameworks
- Focus on what the news means for affected populations and response actors

Here are the articles to analyze:

{context}

Write the brief now:"""
        
        # Generate response using chat provider
        response = await self.chat_provider.generate(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Please generate the brief based on the articles provided."},
            ],
            temperature=0.3,
            max_tokens=2000,
        )
        
        return response
