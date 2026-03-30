"""
Topic tagging service for humanitarian news articles.
"""

import re
from typing import List, Tuple, Dict
from collections import Counter

from app.services.nlp.topic_data import TOPIC_KEYWORDS, get_all_topics


class TopicTagger:
    """
    Tags articles with humanitarian crisis topics using keyword matching.
    """
    
    def __init__(self, max_topics: int = 3):
        """
        Initialize topic tagger.
        
        Args:
            max_topics: Maximum number of topic tags to return
        """
        self.max_topics = max_topics
        self._build_keyword_index()
    
    def _build_keyword_index(self):
        """Build keyword indices for fast lookup."""
        self.positive_keywords: Dict[str, List[str]] = {}
        self.negative_keywords: Dict[str, List[str]] = {}
        
        for topic_id, (positive, negative) in TOPIC_KEYWORDS.items():
            self.positive_keywords[topic_id] = [kw.lower() for kw in positive]
            self.negative_keywords[topic_id] = [kw.lower() for kw in negative]
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words and multi-word phrases.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens (words and phrases)
        """
        if not text:
            return []
        
        # Lowercase
        text = text.lower()
        
        # Generate n-grams (1-5 words)
        tokens = []
        words = re.findall(r'\b\w+\b', text)
        
        # Add individual words
        tokens.extend(words)
        
        # Add bigrams
        for i in range(len(words) - 1):
            tokens.append(f"{words[i]} {words[i+1]}")
        
        # Add trigrams
        for i in range(len(words) - 2):
            tokens.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        # Add 4-grams
        for i in range(len(words) - 3):
            tokens.append(f"{words[i]} {words[i+1]} {words[i+2]} {words[i+3]}")
        
        # Add 5-grams
        for i in range(len(words) - 4):
            tokens.append(f"{words[i]} {words[i+1]} {words[i+2]} {words[i+3]} {words[i+4]}")
        
        return tokens
    
    def _score_topics(
        self,
        tokens: List[str],
        title_tokens: List[str],
    ) -> Counter:
        """
        Score topics based on keyword matches.
        
        Args:
            tokens: Tokens from full text
            title_tokens: Tokens from title
            
        Returns:
            Counter with topic scores
        """
        topic_scores = Counter()
        
        for topic_id in get_all_topics():
            positive_kws = self.positive_keywords[topic_id]
            negative_kws = self.negative_keywords[topic_id]
            
            # Score positive keywords
            for token in tokens:
                if token in positive_kws:
                    # Title matches get higher weight
                    weight = 3 if token in title_tokens else 1
                    
                    # Longer phrases get higher weight (more specific)
                    phrase_length = len(token.split())
                    weight *= phrase_length
                    
                    topic_scores[topic_id] += weight
            
            # Penalize negative keywords
            for token in tokens:
                if token in negative_kws:
                    # Subtract points for negative keywords
                    penalty = 2 if token in title_tokens else 1
                    topic_scores[topic_id] -= penalty
        
        return topic_scores
    
    def tag_article(
        self,
        title: str,
        content: str = None,
    ) -> List[str]:
        """
        Tag article with humanitarian crisis topics.
        
        Args:
            title: Article title
            content: Article content text (optional)
            
        Returns:
            List of topic IDs (max 3)
        """
        # Combine title and content
        full_text = title
        if content:
            full_text += " " + content
        
        if not full_text.strip():
            return []
        
        # Tokenize
        title_tokens = set(self._tokenize(title))
        full_tokens = self._tokenize(full_text)
        
        # Score topics
        topic_scores = self._score_topics(full_tokens, title_tokens)
        
        # Get top N topics with positive scores
        top_topics = [
            topic_id for topic_id, score in topic_scores.most_common(self.max_topics)
            if score > 0
        ]
        
        return top_topics
    
    def tag_text(self, text: str) -> List[str]:
        """
        Simple convenience method to tag text.
        
        Args:
            text: Text to tag
            
        Returns:
            List of topic IDs
        """
        return self.tag_article(text, None)
