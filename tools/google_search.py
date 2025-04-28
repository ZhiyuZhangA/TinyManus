from serpapi import GoogleSearch
from tools.base_tool import BaseTool
from pydantic import PrivateAttr
import json
from typing import Optional, Dict

_GOOGLE_SEARCH_DESCRIPTION = (
    "Search Google using a query string and return relevant results. "
    "Use this tool when external knowledge is required."
)


class GoogleSearchTool(BaseTool):
    _api_key: str = PrivateAttr()

    name: str = "google_search"
    description: str = _GOOGLE_SEARCH_DESCRIPTION
    parameters: Dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to look up."
            }
        },
        "required": ["query"],
    }

    def set_api_key(self, api_key: str):
        self._api_key = api_key

    def executes(self, query: str):
        params = {
            "engine": "google",
            "q": query,
            "api_key": self._api_key,
            "num": 10
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        if "error" in results:
            return {"error": results["error"]}

        top_results = []
        for result in results.get("organic_results", [])[:10]:
            top_results.append({
                "title": result.get("title"),
                "link": result.get("link"),
                "snippet": result.get("snippet")
            })

        return top_results

