from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from mcp.server.fastmcp import FastMCP, Context
from dotenv import load_dotenv

from newsapi.connector import NewsAPIConnector
from newsapi.models import ArticleResponse

load_dotenv()

mcp = FastMCP("News Server", dependencies=["httpx", "python-dotenv"])
news_api_connector = NewsAPIConnector()


@mcp.tool()
async def fetch_news(
    query: str,
    from_date: str | None,
    to_date: str | None,
    language: str = "en",
    sort_by: str = "publishedAt",
    page_size: int = 10,
    page: int = 1,
    ctx: Context = None,
) -> ArticleResponse:
    """
    Retrieves news articles.

    Args:
        query: Keywords or phrases to search for
        from_date: Optional start date (YYYY-MM-DD)
        to_date: Optional end date (YYYY-MM-DD)
        language: Language code (default: en)
        sort_by: Sort order (default: publishedAt, popularity, relevancy)
        page_size: Number of results per page (default: 10, max: 100)
        page: Page number for pagination (default: 1)
        ctx: MCP Context

    Returns:
        News Articles
    """
    if not is_valid_date(from_date):
        return error_response("Error: Invalid 'from_date' format. Use YYYY-MM-DD.")
    if not is_valid_date(to_date):
        return error_response("Error: Invalid 'to_date' format. Use YYYY-MM-DD.")
    if not is_valid_sort_by(sort_by):
        return error_response(
            "Error: invalid 'sort_by' value. Use 'relevancy', 'popularity', or 'publishedAt'."
        )

    if ctx:
        ctx.info(f"Searching news for: {query}")

    params = {
        k: v
        for k, v in {
            "q": query,
            "from": from_date,
            "to": to_date,
            "language": language,
            "sortBy": sort_by,
            "pageSize": min(page_size, 100),
            "page": page,
        }.items()
        if v is not None
    }

    success, result = await news_api_connector.search_everything(**params)
    return result


@mcp.tool()
async def fetch_top_headlines(
    category: str,
    query: str,
    country: str = "us",
    page_size: int = 10,
    page: int = 1,
    ctx: Context = None,
) -> ArticleResponse:
    """
    Retrieves top headlines.

    Args:
        category: Optional category (e.g., business, entertainment, health, science, sports, technology)
        query: Optional keywords or phrases to search for
        country: Country code (default: us)
        page_size: Number of results per page (default: 10, max: 100)
        page: Page number for pagination (default: 1)
        ctx: MCP Context

    Returns:
        Top Headlines
    """
    if category and not is_valid_category(category):
        return error_response(
            "Invalid 'category' value. Use 'business', 'entertainment', 'health', 'science', 'sports', or 'technology'."
        )

    params = {
        k: v
        for k, v in {
            "q": query,
            "country": country,
            "category": category,
            "pageSize": min(page_size, 100),
            "page": page,
        }.items()
        if v is not None
    }

    success, result = await news_api_connector.get_top_headlines(**params)
    return result


def is_valid_date(date_str: Optional[str]) -> bool:
    """
    Validate that a string is in YYYY-MM-DD format.
    """
    if date_str is None:
        return True

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_sort_by(sort_by: str) -> bool:
    """
    Validate that sort_by is one of the allowed values.
    """
    return sort_by in ["relevancy", "popularity", "publishedAt"]


def is_valid_category(category: str) -> bool:
    """
    Validate that category is one of the allowed values.
    """
    return category in [
        "business",
        "entertainment",
        "general",
        "health",
        "science",
        "sports",
        "technology",
    ]


def error_response(message: str) -> ArticleResponse:
    """
    Create an error response.
    """
    return ArticleResponse(status="error", message=message, articles=[], totalResults=0)


if __name__ == "__main__":
    mcp.run(transport="stdio")
