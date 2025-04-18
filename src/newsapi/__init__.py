import os
from dotenv import load_dotenv

load_dotenv()

KEYS = {
    "NEWSAPI_KEY": ("NewsAPI key is required. Set `NEWSAPI_KEY` environment variable."),
    "NEWSAPI_URL": ("NewsAPI URL is required. Set `NEWSAPI_URL` environment variable."),
}

for key, msg in KEYS.items():
    try:
        _ = os.environ[key]
    except KeyError:
        raise ValueError(msg)
