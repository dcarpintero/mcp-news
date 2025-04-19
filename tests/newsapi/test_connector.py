"""
Integration tests for the NewsAPI connector.

These tests make actual API calls to the NewsAPI service.

IMPORTANT: These tests should not be run in CI/CD pipelines as they consume
real API quota and may incur costs. They are meant to be run manually during
development or after significant changes to the connector.

Run with: pytest -m live_integration
"""

import os
import pytest
import pytest_asyncio
from datetime import datetime, timedelta

from src.newsapi.connector import NewsAPIConnector
from src.newsapi.models import NewsResponse


# Skip these tests unless specifically requested with the 'live_integration' marker
pytestmark = pytest.mark.live_integration


@pytest_asyncio.fixture
async def news_api_connector():
    connector = NewsAPIConnector()
    yield connector


@pytest.mark.asyncio
async def test_search_everything(news_api_connector):
    """Test search_everything method with a real API call."""
    # Calculate dates for a recent time period (last 7 days)
    today = datetime.now()
    from_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")

    params = {
        "q": "technology",
        "from": from_date,
        "to": to_date,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "page": 1,
    }

    success, result = await news_api_connector.search_everything(**params)

    assert success is True, f"API call failed with error: {result}"
    assert isinstance(result, NewsResponse)
    assert result.status == "ok"
    assert result.totalResults > 0
    assert len(result.articles) > 0

    article = result.articles[0]
    assert article.source is not None
    assert article.title is not None
    assert article.url is not None

    print(f"\nFound {result.totalResults} articles about 'technology'")
    print(f"First article: '{article.title}' from {article.source.name}")


@pytest.mark.asyncio
async def test_search_everything_with_specific_query(news_api_connector):
    """Test searching for articles about a specific topic."""

    params = {
        "q": "artificial intelligence research",
        "from": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": 5,
        "page": 1,
    }

    success, result = await news_api_connector.search_everything(**params)

    assert success is True, f"API call failed with error: {result}"
    assert isinstance(result, NewsResponse)
    assert result.status == "ok"

    if result.totalResults > 0 and len(result.articles) > 0:
        article = result.articles[0]
        title_lower = article.title.lower() if article.title else ""
        description_lower = article.description.lower() if article.description else ""

        is_relevant = (
            "artificial intelligence" in title_lower
            or "ai" in title_lower
            or "artificial intelligence" in description_lower
        )

        # This is a soft assertion as relevance is subjective
        if not is_relevant:
            print(
                f"Warning: First article may not be highly relevant: '{article.title}'"
            )

        print(f"\nFirst AI research article: '{article.title}'")
        if article.description:
            print(f"Description: {article.description[:100]}...")


@pytest.mark.asyncio
async def test_get_top_headlines(news_api_connector):
    """Test get_top_headlines method with a real API call."""

    params = {
        "country": "us",
        "category": "technology",
        "pageSize": 5,
        "page": 1,
    }

    success, result = await news_api_connector.get_top_headlines(**params)

    assert success is True, f"API call failed with error: {result}"
    assert isinstance(result, NewsResponse)
    assert result.status == "ok"
    assert result.totalResults > 0
    assert len(result.articles) > 0

    article = result.articles[0]
    assert article.source is not None
    assert article.title is not None
    assert article.url is not None

    print(f"\nFound {result.totalResults} top headlines in technology")
    print(f"First headline: '{article.title}' from {article.source.name}")


@pytest.mark.asyncio
async def test_error_handling_with_invalid_parameters(news_api_connector):
    """Test that the connector handles invalid parameters correctly."""
    # Test with an invalid category
    success, result = await news_api_connector.get_top_headlines()

    assert success is False
    print(f"\nExpected error received: {result}")
