import os
import httpx
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple, cast
from .models import ArticleResponse, Article, ArticleSource


class NewsAPIConnector:
    """
    Handles a connection with the NewsAPI and retrieves news articles.
    """

    def __init__(self):
        self.api_key = os.getenv("NEWSAPI_KEY")
        self.base_url = os.getenv("NEWSAPI_URL")

    async def get_client(self) -> httpx.AsyncClient:
        """
        Creates and returns an httpx client configured for NewsAPI.

        Returns:
            An httpx.AsyncClient with proper headers and timeouts.
        """
        return httpx.AsyncClient(timeout=30.0, headers={"X-Api-Key": self.api_key})

    async def search_everything(
        self,
        query: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        language: str = "en",
        sort_by: str = "publishedAt",
        page_size: int = 10,
        page: int = 1,
    ) -> Tuple[bool, Union[str, ArticleResponse]]:
        """
        Retrieves News Articles from the NewsAPI "/everything" endpoint.

        Args:
            query: Keywords or phrases to search for
            from_date: Optional start date (YYYY-MM-DD)
            to_date: Optional end date (YYYY-MM-DD)
            language: Language code (default: en)
            sort_by: Sort order (relevancy, popularity, publishedAt)
            page_size: Number of results per page (default: 10, max: 100)
            page: Page number for pagination

        Returns:
            A tuple containing (success, result) where:
            - success: A boolean indicating if the request was successful
            - result: Either an error message (string) or the validated ArticleResponse model
        """
        if not self._is_valid_date(from_date):
            return False, "Invalid from_date format. Use YYYY-MM-DD."
        if not self._is_valid_date(to_date):
            return False, "Invalid to_date format. Use YYYY-MM-DD."

        valid_sort_options = ["relevancy", "popularity", "publishedAt"]
        if sort_by not in valid_sort_options:
            return False, f"sort_by must be one of {valid_sort_options}"

        params = {
            "q": query,
            "language": language,
            "sortBy": sort_by,
            "pageSize": min(page_size, 100),  # Ensure we do not exceed API limit
            "page": page,
        }

        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        async with await self.get_client() as client:
            try:
                response = await client.get(f"{self.base_url}everything", params=params)
                response.raise_for_status()
                data = response.json()
                article_response = ArticleResponse.model_validate(data)

                return True, article_response

            except httpx.RequestError as e:
                return False, f"Request error: {str(e)}"

            except Exception as e:
                return False, f"Unexpected error: {str(e)}"

    async def get_top_headlines(
        self,
        country: str = "us",
        category: Optional[str] = None,
        query: Optional[str] = None,
        page_size: int = 10,
        page: int = 1,
    ) -> Tuple[bool, Union[str, ArticleResponse]]:
        """
        Retrieves Top-Headlines Articles from the NewsAPI "/top-headlines" endpoint.

        Args:
            country: Country code (default: us)
            category: Optional category (business, entertainment, general, health, science, sports, technology)
            query: Optional search term
            page_size: Number of results per page (default: 10, max: 100)
            page: Page number for pagination

        Returns:
            A tuple containing (success, result) where:
            - success: A boolean indicating if the request was successful
            - result: Either an error message (string) or the validated ArticleResponse model
        """
        valid_categories = [
            "business",
            "entertainment",
            "general",
            "health",
            "science",
            "sports",
            "technology",
        ]
        if category and category not in valid_categories:
            return False, f"category must be one of {valid_categories}"

        params = {
            "country": country,
            "pageSize": min(page_size, 100),  # Ensure we do not exceed API limit
            "page": page,
        }

        if category:
            params["category"] = category
        if query:
            params["q"] = query

        async with await self.get_client() as client:
            try:
                response = await client.get(
                    f"{self.base_url}top-headlines", params=params
                )
                response.raise_for_status()
                data = response.json()
                article_response = ArticleResponse.model_validate(data)
                return True, article_response

            except httpx.RequestError as e:
                return False, f"Request error: {str(e)}"

            except Exception as e:
                return False, f"Unexpected error: {str(e)}"

    @staticmethod
    def _is_valid_date(date_str: Optional[str]) -> bool:
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
