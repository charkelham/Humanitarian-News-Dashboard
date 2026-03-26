"""
Tests for content extractor.
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app.services.ingest.content_extractor import ContentExtractor, ContentExtractionError


# Fixture helpers
def load_fixture(filename: str) -> str:
    """Load HTML fixture file."""
    fixture_path = Path(__file__).parent / "fixtures" / filename
    with open(fixture_path, 'r', encoding='utf-8') as f:
        return f.read()


@pytest.mark.asyncio
async def test_extract_content_simple_article():
    """Test content extraction from simple article."""
    html = load_fixture("sample_article.html")
    
    extractor = ContentExtractor()
    content = extractor.extract_content(html)
    
    assert content is not None
    assert "solar infrastructure" in content.lower()
    assert "renewable energy" in content.lower()
    assert "investment" in content.lower()
    # Footer should not be in content
    assert "copyright" not in content.lower()


@pytest.mark.asyncio
async def test_extract_content_complex_article():
    """Test content extraction from complex page with noise."""
    html = load_fixture("complex_article.html")
    
    extractor = ContentExtractor()
    content = extractor.extract_content(html)
    
    assert content is not None
    assert "wind energy" in content.lower()
    assert "offshore wind" in content.lower()
    # Ads and navigation should not be in content
    assert "advertisement" not in content.lower()
    assert "site header" not in content.lower()


@pytest.mark.asyncio
async def test_extract_content_short_article():
    """Test that very short content returns None."""
    html = load_fixture("short_article.html")
    
    extractor = ContentExtractor()
    content = extractor.extract_content(html)
    
    # Should return None because content is too short
    assert content is None


@pytest.mark.asyncio
async def test_extract_with_readability():
    """Test readability extraction."""
    html = load_fixture("sample_article.html")
    
    extractor = ContentExtractor()
    content = extractor.extract_with_readability(html)
    
    assert content is not None
    assert len(content) > 100
    assert "solar" in content.lower()


@pytest.mark.asyncio
async def test_extract_with_beautifulsoup():
    """Test BeautifulSoup fallback extraction."""
    html = load_fixture("sample_article.html")
    
    extractor = ContentExtractor()
    content = extractor.extract_with_beautifulsoup(html)
    
    assert content is not None
    assert len(content) > 100
    assert "solar" in content.lower()


@pytest.mark.asyncio
async def test_detect_language_english():
    """Test language detection for English text."""
    text = "This is a sample article about renewable energy and solar power in the United States."
    
    extractor = ContentExtractor()
    lang = extractor.detect_language(text)
    
    assert lang == "en"


@pytest.mark.asyncio
async def test_detect_language_short_text():
    """Test that very short text returns None."""
    text = "Too short"
    
    extractor = ContentExtractor()
    lang = extractor.detect_language(text)
    
    assert lang is None


@pytest.mark.asyncio
async def test_fetch_html_success():
    """Test successful HTML fetch."""
    extractor = ContentExtractor(timeout=10)
    
    mock_response = AsyncMock()
    mock_response.content = b"<html><body>Test content</body></html>"
    mock_response.status_code = 200
    mock_response.raise_for_status = AsyncMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        result = await extractor.fetch_html("https://example.com/article")
        
        assert result == "<html><body>Test content</body></html>"


@pytest.mark.asyncio
async def test_fetch_html_timeout():
    """Test HTML fetch with timeout."""
    import httpx
    
    extractor = ContentExtractor(timeout=5)
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.TimeoutException("Timeout")
        )
        
        with pytest.raises(ContentExtractionError, match="Timeout"):
            await extractor.fetch_html("https://example.com/article")


@pytest.mark.asyncio
async def test_fetch_html_http_error():
    """Test HTML fetch with HTTP error."""
    import httpx
    
    extractor = ContentExtractor(timeout=10)
    
    mock_response = AsyncMock()
    mock_response.status_code = 404
    mock_response.raise_for_status = AsyncMock(
        side_effect=httpx.HTTPStatusError("Not found", request=None, response=mock_response)
    )
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        
        with pytest.raises(ContentExtractionError, match="HTTP 404"):
            await extractor.fetch_html("https://example.com/article")


@pytest.mark.asyncio
async def test_extract_article_full_workflow():
    """Test full article extraction workflow."""
    html = load_fixture("sample_article.html")
    
    extractor = ContentExtractor()
    
    # Mock fetch_html
    extractor.fetch_html = AsyncMock(return_value=html)
    
    content, language = await extractor.extract_article("https://example.com/article")
    
    assert content is not None
    assert "solar" in content.lower()
    assert language == "en"


@pytest.mark.asyncio
async def test_extract_article_no_content():
    """Test extraction when no substantial content is found."""
    html = load_fixture("short_article.html")
    
    extractor = ContentExtractor()
    extractor.fetch_html = AsyncMock(return_value=html)
    
    content, language = await extractor.extract_article("https://example.com/article")
    
    assert content is None
    assert language is None


@pytest.mark.asyncio
async def test_polite_headers():
    """Test that polite HTTP headers are sent."""
    extractor = ContentExtractor(timeout=10, user_agent="TestBot/1.0")
    
    mock_response = AsyncMock()
    mock_response.content = b"<html>content</html>"
    mock_response.status_code = 200
    mock_response.raise_for_status = AsyncMock()
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        await extractor.fetch_html("https://example.com/article")
        
        # Check headers
        call_kwargs = mock_get.call_args.kwargs
        headers = call_kwargs.get('headers', {})
        
        assert headers.get('User-Agent') == "TestBot/1.0"
        assert 'Accept' in headers
        assert 'Accept-Language' in headers
        assert headers.get('Accept-Language') == "en-US,en;q=0.9"
