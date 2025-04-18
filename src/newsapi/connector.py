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
        self, **kwargs
    ) -> Tuple[bool, Union[str, ArticleResponse]]:
        """
        Retrieves News Articles from the NewsAPI "/everything" endpoint.

        Args:
            **kwargs: Requests parameters as defined in https://newsapi.org/docs/endpoints/everything

        Returns:
            A tuple containing (success, result) where:
            - success: A boolean indicating if the request was successful
            - result: Either an error message (string) or the validated ArticleResponse model
        """
        async with await self.get_client() as client:
            params = kwargs
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
        self, **kwargs
    ) -> Tuple[bool, Union[str, ArticleResponse]]:
        """
        Retrieves Top-Headlines Articles from the NewsAPI "/top-headlines" endpoint.

        Args:
            **kwargs: Requests parameters as defined in https://newsapi.org/docs/endpoints/top-headlines

        Returns:
            A tuple containing (success, result) where:
            - success: A boolean indicating if the request was successful
            - result: Either an error message (string) or the validated ArticleResponse model
        """
        async with await self.get_client() as client:
            params = kwargs
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
