from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from pydantic.alias_generators import to_camel


class ArticleSource(BaseModel):
    """Represents a news source in the NewsAPI."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str | None
    name: str | None


class Article(BaseModel):
    """Represents a news article from the NewsAPI."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    source: ArticleSource
    author: str | None
    title: str | None
    description: str | None
    url: HttpUrl | None
    urlToImage: HttpUrl | None
    publishedAt: datetime | None
    content: str | None


class NewsResponse(BaseModel):
    """Represents a response from the NewsAPI containing articles."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    status: str
    totalResults: int
    articles: list[Article]
