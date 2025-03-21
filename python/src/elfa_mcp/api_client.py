"""
Client library for interacting with the Elfa API.
"""

import os
import httpx
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

# Constants
BASE_URL = "https://api.elfa.ai"
DEFAULT_TIMEOUT = 30.0  # seconds


class ElfaClient:
    """Client for interacting with the Elfa API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Elfa API client.

        Args:
            api_key: Elfa API key. If not provided, will look for ELFA_API_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get("ELFA_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key must be provided either directly or via ELFA_API_KEY environment variable")

        self.headers = {
            "x-elfa-api-key": self.api_key,
            "Accept": "application/json"
        }

    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the Elfa API.

        Args:
            endpoint: API endpoint to call (without base URL)
            params: Query parameters to include

        Returns:
            API response as a dictionary
        """
        url = urljoin(BASE_URL, endpoint)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=DEFAULT_TIMEOUT
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise Exception("API key is invalid or expired") from e
                else:
                    raise Exception(
                        f"API request failed with status code {e.response.status_code}") from e
            except httpx.RequestError as e:
                raise Exception(f"Request error: {str(e)}") from e

    async def get_api_key_status(self) -> Dict[str, Any]:
        """Get the current status of the API key."""
        return await self._make_request("/v1/key-status")

    async def get_mentions(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get mentions with smart engagement."""
        params = {
            "limit": limit,
            "offset": offset
        }
        return await self._make_request("/v1/mentions", params)

    async def get_top_mentions(self,
                               ticker: str,
                               time_window: str = "1h",
                               page: int = 1,
                               page_size: int = 10,
                               include_account_details: bool = False) -> Dict[str, Any]:
        """Get top mentions for a specific ticker."""
        params = {
            "ticker": ticker,
            "timeWindow": time_window,
            "page": page,
            "pageSize": page_size,
            "includeAccountDetails": include_account_details
        }
        return await self._make_request("/v1/top-mentions", params)

    async def search_mentions(self,
                              keywords: str,
                              from_time: int,
                              to_time: int,
                              limit: int = 20,
                              search_type: Optional[str] = None,
                              cursor: Optional[str] = None) -> Dict[str, Any]:
        """Search mentions by keywords."""
        params = {
            "keywords": keywords,
            "from": from_time,
            "to": to_time,
            "limit": limit
        }

        if search_type:
            params["searchType"] = search_type

        if cursor:
            params["cursor"] = cursor

        return await self._make_request("/v1/mentions/search", params)

    async def get_trending_tokens(self,
                                  time_window: str = "24h",
                                  page: int = 1,
                                  page_size: int = 50,
                                  min_mentions: int = 5) -> Dict[str, Any]:
        """Get trending tokens."""
        params = {
            "timeWindow": time_window,
            "page": page,
            "pageSize": page_size,
            "minMentions": min_mentions
        }
        return await self._make_request("/v1/trending-tokens", params)

    async def get_account_smart_stats(self, username: str) -> Dict[str, Any]:
        """Get smart stats for an account."""
        params = {
            "username": username
        }
        return await self._make_request("/v1/account/smart-stats", params)


# Singleton instance for the client
_client_instance = None


def get_client() -> ElfaClient:
    """Get or create the Elfa API client singleton instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = ElfaClient()
    return _client_instance
