"""
RAG chat service for answering questions using retrieved context.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, any_

from app.db.models import Article
from app.services.rag.vector_search import VectorSearchService, SearchFilters, SearchResult
from app.services.rag.chat_provider import ChatProvider
from app.services.rag.embedding_provider import EmbeddingProvider
from app.services.nlp.topic_data import TOPIC_KEYWORDS
from app.services.nlp.country_data import detect_countries_in_text


@dataclass
class Citation:
    """Citation for a source article."""
    id: int
    title: str
    url: str
    published_at: Optional[datetime]
    source: str
    chunk_id: int
    similarity: float


@dataclass
class ChatResponse:
    """Response from chat service."""
    answer: str
    citations: List[Citation]
    confidence: str  # high, medium, low
    filters_applied: Dict[str, Any]


class ChatService:
    """
    Service for RAG-based question answering.
    """
    
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        chat_provider: ChatProvider,
        min_similarity_threshold: float = 0.5,
        low_confidence_threshold: float = 0.65,
    ):
        """
        Initialize chat service.
        
        Args:
            embedding_provider: Provider for query embeddings
            chat_provider: Provider for chat completions
            min_similarity_threshold: Minimum similarity to consider a chunk relevant
            low_confidence_threshold: Threshold for low confidence warning
        """
        self.embedding_provider = embedding_provider
        self.chat_provider = chat_provider
        self.vector_search = VectorSearchService(embedding_provider)
        self.min_similarity_threshold = min_similarity_threshold
        self.low_confidence_threshold = low_confidence_threshold
    
    def _build_system_prompt(self, chunks: List[SearchResult]) -> str:
        """
        Build system prompt with context and instructions.
        
        Args:
            chunks: Retrieved chunks
            
        Returns:
            System prompt text
        """
        # Build context from chunks
        context_parts = []
        for i, chunk in enumerate(chunks, start=1):
            context_parts.append(
                f"[{i}] {chunk.chunk_text}\n"
                f"(Source: {chunk.article_title}, Published: {chunk.published_at.strftime('%Y-%m-%d') if chunk.published_at else 'Unknown'})"
            )
        
        context = "\n\n".join(context_parts)
        
        # Build system prompt
        system_prompt = f"""You are an AI assistant specialized in humanitarian crises, displacement, and early warning analysis.

Your task is to answer questions using the context provided below. Follow these rules:

1. **Prioritize the provided context**: Your primary goal is to surface information from the news articles provided.
2. **Synthesize with general knowledge**: You can use your general knowledge to provide background, context, or explanations that make the answer more complete and easier to understand.
3. **Cite sources**: Always cite the source articles using bracketed numbers like [1], [2], etc. when you use information from them.
4. **Be transparent**: If the context doesn't contain enough information to answer a specific part of the question, you can say so, but provide a helpful answer based on what IS there and your general understanding.
5. **Concise and Professional**: Be concise but comprehensive.

Context:
{context}

Now answer the user's question by combining the latest news from the context above with your general expertise in humanitarian affairs."""
        
        return system_prompt
    
    def _extract_citations(
        self,
        chunks: List[SearchResult],
    ) -> List[Citation]:
        """
        Extract unique article citations from chunks.
        
        Args:
            chunks: Retrieved chunks
            
        Returns:
            List of unique citations
        """
        # Track unique articles (deduplicate by article_id)
        seen_articles = set()
        citations = []
        
        for chunk in chunks:
            if chunk.article_id not in seen_articles:
                citations.append(Citation(
                    id=chunk.article_id,
                    title=chunk.article_title,
                    url=chunk.article_url,
                    published_at=chunk.published_at,
                    source=chunk.article_url.split('/')[2] if '://' in chunk.article_url else 'Unknown',  # Extract domain
                    chunk_id=chunk.chunk_id,
                    similarity=chunk.similarity,
                ))
                seen_articles.add(chunk.article_id)
        
        return citations
    
    def _assess_confidence(self, chunks: List[SearchResult]) -> str:
        """
        Assess confidence level based on retrieval quality.
        
        Args:
            chunks: Retrieved chunks
            
        Returns:
            Confidence level: 'high', 'medium', or 'low'
        """
        if not chunks:
            return "low"
        
        max_similarity = max(c.similarity for c in chunks)
        avg_similarity = sum(c.similarity for c in chunks) / len(chunks)
        
        if max_similarity >= 0.8 and avg_similarity >= 0.7:
            return "high"
        elif max_similarity >= self.low_confidence_threshold:
            return "medium"
        else:
            return "low"
    
    def _extract_country_from_question(self, question: str) -> Optional[str]:
        """
        Extract country name from question and convert to ISO code.
        """
        detected = detect_countries_in_text(question)
        return detected[0] if detected else None

    def _extract_topics_from_question(self, question: str) -> List[str]:
        """
        Extract topics from question based on keyword mapping.
        
        Args:
            question: User question
            
        Returns:
            List of topic IDs
        """
        question_lower = question.lower()
        extracted_topics = []
        
        for topic_id, (pos_keywords, _) in TOPIC_KEYWORDS.items():
            if any(keyword in question_lower for keyword in pos_keywords):
                extracted_topics.append(topic_id)
        
        return extracted_topics
    
    async def _search_articles_by_country(
        self,
        db: AsyncSession,
        country_code: str,
        filters: Optional[SearchFilters] = None,
        limit: int = 10,
    ) -> List[Article]:
        """
        Search for articles tagged with a specific country and optional topics.
        """
        query = select(Article).where(
            country_code == any_(Article.country_codes)
        )
        
        # Add topic filters if present
        if filters and filters.topics:
            from sqlalchemy.dialects.postgresql import array
            query = query.where(Article.topic_tags.op("&&")(filters.topics))
            
        query = query.order_by(Article.published_at.desc()).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def _keyword_search_articles(
        self,
        db: AsyncSession,
        question: str,
        filters: Optional[SearchFilters] = None,
        limit: int = 5,
    ) -> List[Article]:
        """
        Search for articles by keyword in title or content, respecting filters.
        """
        # Clean up question and extract meaningful words
        question_lower = question.lower()
        stopwords = {
            'do', 'we', 'have', 'any', 'articles', 'article', 'on', 'about', 
            'the', 'a', 'an', 'is', 'are', 'tell', 'me', 'what', 'who', 
            'when', 'where', 'why', 'how', 'can', 'you', 'show', 'find'
        }
        
        words = [w.strip('.,!?') for w in question_lower.split()]
        keywords = [w for w in words if w not in stopwords and len(w) > 3]
        
        if not keywords:
            return []
        
        phrases = []
        if len(keywords) >= 2:
            phrases.append(' '.join(keywords))
            for i in range(len(keywords) - 1):
                phrases.append(f"{keywords[i]} {keywords[i+1]}")
        
        conditions = []
        for phrase in phrases:
            conditions.append(Article.title.ilike(f'%{phrase}%'))
        
        for keyword in keywords:
            if len(keyword) > 5:
                conditions.append(Article.title.ilike(f'%{keyword}%'))
        
        if not conditions:
            return []
        
        query = select(Article).where(or_(*conditions))
        
        # Apply strict country/topic filters to keyword search
        if filters:
            if filters.countries:
                query = query.where(Article.country_codes.op("&&")(filters.countries))
            if filters.topics:
                query = query.where(Article.topic_tags.op("&&")(filters.topics))
        
        from sqlalchemy import case
        order_cases = []
        for i, phrase in enumerate(phrases):
            order_cases.append((Article.title.ilike(f'%{phrase}%'), i))
        
        if order_cases:
            query = query.order_by(
                case(*order_cases, else_=999)
            )
        
        query = query.limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def chat(
        self,
        db: AsyncSession,
        question: str,
        filters: Optional[SearchFilters] = None,
        k: int = 8,
    ) -> ChatResponse:
        """
        Answer a question using RAG with proactive filtering.
        """
        # 1. Eagerly extract filters from question
        extracted_country = self._extract_country_from_question(question)
        extracted_topics = self._extract_topics_from_question(question)
        
        # 2. Merge with provided filters
        if not filters:
            filters = SearchFilters()
            
        if extracted_country:
            # If the question mentions a country, STRICTLY use that country filter
            # even if the dashboard context said something else.
            filters.countries = [extracted_country]
            
        if extracted_topics:
            if not filters.topics:
                filters.topics = extracted_topics
            else:
                # Merge if existing, prioritizing question-extracted topics
                filters.topics = list(set(filters.topics + extracted_topics))

        # 3. Retrieve relevant chunks with STRICT filters first
        chunks = await self.vector_search.search_with_threshold(
            db=db,
            query=question,
            filters=filters,
            k=k,
            min_similarity=self.min_similarity_threshold,
        )
        
        # 4. Assess confidence
        confidence = self._assess_confidence(chunks)
        
        # 5. Handle low confidence / no results - try fallback
        if not chunks or confidence == "low":
            # If we had country filters, try broader article-level search as first fallback
            if filters.countries:
                for country_code in filters.countries:
                    country_articles = await self._search_articles_by_country(
                        db, country_code, filters=filters, limit=10
                    )
                    if country_articles:
                        return await self._generate_response_from_articles(
                            question, country_articles, "country", filters
                        )
            
            # Try keyword search as second fallback (STRICTLY within filters)
            keyword_articles = await self._keyword_search_articles(db, question, filters=filters)
            if keyword_articles:
                return await self._generate_response_from_articles(
                    question, keyword_articles, "keyword", filters
                )
            
            # Final fallback: General knowledge
            return await self._generate_general_knowledge_response(question, filters)
        
        # 6. Build prompt and generate answer (Normal path)
        system_prompt = self._build_system_prompt(chunks)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ]
        
        answer = await self.chat_provider.generate(
            messages=messages,
            temperature=0.1,
            max_tokens=1000,
        )
        
        return ChatResponse(
            answer=answer,
            citations=self._extract_citations(chunks),
            confidence=confidence,
            filters_applied=self._serialize_filters(filters),
        )

    async def _generate_response_from_articles(
        self, 
        question: str, 
        articles: List[Article], 
        source_type: str,
        filters: SearchFilters
    ) -> ChatResponse:
        """Helper to generate response from a list of articles (fallback)."""
        context_parts = []
        for i, article in enumerate(articles[:5], start=1):
            content_snippet = article.content_text[:400] if article.content_text else article.raw_summary or "No content available"
            context_parts.append(
                f"[{i}] {article.title}\n"
                f"Published: {article.published_at.strftime('%Y-%m-%d') if article.published_at else 'Unknown'}\n"
                f"Content: {content_snippet}..."
            )
        
        context = "\n\n".join(context_parts)
        
        system_prompt = f"""You are an AI assistant specializing in humanitarian crises, displacement, conflict, and early warning.
        
Below are relevant articles from our database that {'match your requested location' if source_type == 'country' else 'contain keywords from your question'}:

{context}

Answer the user's question based on these articles and your general knowledge. Summarize key trends or developments.
Cite sources by referencing the article numbers [1], [2], etc."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ]
        
        answer = await self.chat_provider.generate(
            messages=messages,
            temperature=0.2,
            max_tokens=1000,
        )
        
        citations = [
            Citation(
                id=article.id,
                title=article.title,
                url=article.url,
                published_at=article.published_at,
                source=article.url.split('/')[2] if '://' in article.url else 'Unknown',
                chunk_id=0,
                similarity=0.0,
            )
            for article in articles[:5]
        ]
        
        return ChatResponse(
            answer=answer,
            citations=citations,
            confidence="medium",
            filters_applied=self._serialize_filters(filters),
        )

    async def _generate_general_knowledge_response(self, question: str, filters: SearchFilters) -> ChatResponse:
        """Final fallback using general knowledge."""
        general_prompt = """You are an AI assistant specializing in humanitarian crises, displacement, conflict, and early warning.
            
The user has asked a question, but we don't have relevant articles in our database to answer it directly.
However, you can use your general knowledge to provide a helpful answer.

IMPORTANT: At the end of your response, add a note that this answer is based on general knowledge 
since we don't have specific articles on this topic in our database.

Be helpful, accurate, and concise."""
        
        messages = [
            {"role": "system", "content": general_prompt},
            {"role": "user", "content": question},
        ]
        
        answer = await self.chat_provider.generate(
            messages=messages,
            temperature=0.3,
            max_tokens=1000,
        )
        
        return ChatResponse(
            answer=answer,
            citations=[],
            confidence="low",
            filters_applied=self._serialize_filters(filters),
        )

    def _serialize_filters(self, filters: Optional[SearchFilters]) -> Dict[str, Any]:
        """Serialize filters for response."""
        if not filters:
            return {}
        
        result = {}
        if filters.countries:
            result["countries"] = filters.countries
        if filters.topics:
            result["topics"] = filters.topics
        if filters.date_from:
            result["date_from"] = filters.date_from.isoformat()
        if filters.date_to:
            result["date_to"] = filters.date_to.isoformat()
        
        return result
