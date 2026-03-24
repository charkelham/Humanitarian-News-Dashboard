"""Test keyword search."""
import asyncio
from sqlalchemy import select, or_
from app.db.session import AsyncSessionLocal
from app.db.models import Article


async def test_keyword_search():
    question = "tell me about hecate energy"
    
    # Replicate the logic from chat_service
    question_lower = question.lower()
    stopwords = {
        'do', 'we', 'have', 'any', 'articles', 'article', 'on', 'about', 
        'the', 'a', 'an', 'is', 'are', 'tell', 'me', 'what', 'who', 
        'when', 'where', 'why', 'how', 'can', 'you','situation', 'latest', 'recent', 'current', 'update', 'updates',
        'happening', 'going', 'news', 'focus', 'should', 'worst',
        'crisis', 'crises', 'report', 'reports', 'right', 'now',
        'fcdo', 'heros', 'please', 'give', 'need', 'information' 'show', 'find'
    }
    
    words = [w.strip('.,!?') for w in question_lower.split()]
    keywords = [w for w in words if w not in stopwords and len(w) > 3]
    
    print(f"Question: {question}")
    print(f"Keywords: {keywords}")
    
    # Build phrases
    phrases = []
    if len(keywords) >= 2:
        phrases.append(' '.join(keywords))
        for i in range(len(keywords) - 1):
            phrases.append(f"{keywords[i]} {keywords[i+1]}")
    
    print(f"Phrases: {phrases}")
    
    async with AsyncSessionLocal() as db:
        conditions = []
        for phrase in phrases:
            conditions.append(Article.title.ilike(f'%{phrase}%'))
            print(f"  Searching for: '%{phrase}%'")
        
        for keyword in keywords:
            if len(keyword) > 5:
                conditions.append(Article.title.ilike(f'%{keyword}%'))
                print(f"  Searching for: '%{keyword}%' (long keyword)")
        
        if conditions:
            query = select(Article).where(or_(*conditions)).limit(5)
            result = await db.execute(query)
            articles = result.scalars().all()
            
            print(f"\nFound {len(articles)} articles:")
            for article in articles:
                print(f"  - {article.title}")
        else:
            print("\nNo search conditions!")


if __name__ == "__main__":
    asyncio.run(test_keyword_search())
