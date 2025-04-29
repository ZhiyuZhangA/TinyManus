from tools.base import BaseTool
from pydantic import PrivateAttr
from typing import Dict
import httpx

_GOOGLE_SEARCH_DESCRIPTION = (
    "Search Google using a query string and return relevant results. "
    "Use this tool when external knowledge is required."
)


class GoogleSearchTool(BaseTool):
    _api_key: str = PrivateAttr()
    _engine_id: str = PrivateAttr()

    name: str = "google_search"
    description: str = _GOOGLE_SEARCH_DESCRIPTION
    parameters: Dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to look up."
            },
            "num": {
                "type": "integer",
                "description": "The number of results to return from the search query."
            }
        },
        "required": ["query", "num"],
    }

    def set_api_key(self, search_api_key: str, engine_id: str):
        self._api_key = search_api_key
        self._engine_id = engine_id

    async def execute(self, query: str, num: int):
        base_urls = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self._api_key,
            'cx': self._engine_id,
            'q': query,
            'num': num
        }

        response = httpx.get(base_urls, params=params)
        response.raise_for_status()

        return response.json()

