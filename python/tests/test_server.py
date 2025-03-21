"""Tests for the MCP server functions."""

import pytest
from unittest.mock import patch, AsyncMock

from elfa_mcp.server import (
    get_api_key_info,
    get_smart_engagement_mentions,
    get_top_ticker_mentions,
    search_keyword_mentions,
    get_trending_tokens,
    get_account_stats
)


class TestMcpTools:
    @pytest.mark.asyncio
    async def test_get_api_key_info_success(self, mock_api_client, api_key_status_data, mock_api_response):
        """Test successful API key info retrieval."""
        mock_api_client.get_api_key_status.return_value = mock_api_response(
            api_key_status_data)

        with patch('elfa_mcp.server.get_client', return_value=mock_api_client):
            result = await get_api_key_info()

            mock_api_client.get_api_key_status.assert_called_once()
            assert "API Key Information" in result
            assert "Test API Key" in result
            assert "active" in result

    @pytest.mark.asyncio
    async def test_get_api_key_info_failure(self, mock_api_client, mock_api_response):
        """Test API key info retrieval failure."""
        mock_api_client.get_api_key_status.return_value = mock_api_response(
            success=False)

        with patch('elfa_mcp.server.get_client', return_value=mock_api_client):
            result = await get_api_key_info()

            mock_api_client.get_api_key_status.assert_called_once()
            assert "Failed to retrieve API key information" in result

    @pytest.mark.asyncio
    async def test_get_api_key_info_error(self, mock_api_client):
        """Test API key info retrieval error."""
        mock_api_client.get_api_key_status.side_effect = Exception(
            "Test error")

        with patch('elfa_mcp.server.get_client', return_value=mock_api_client):
            result = await get_api_key_info()

            mock_api_client.get_api_key_status.assert_called_once()
            assert "Error retrieving API key information" in result
            assert "Test error" in result

    @pytest.mark.asyncio
    async def test_get_smart_engagement_mentions_success(self, mock_api_client, mentions_data, mock_api_response):
        """Test successful mentions retrieval."""
        mock_api_client.get_mentions.return_value = mock_api_response(
            mentions_data,
            metadata={"total": 100, "limit": 10, "offset": 0}
        )

        with patch('elfa_mcp.server.get_client', return_value=mock_api_client):
            result = await get_smart_engagement_mentions(limit=10, offset=0)

            mock_api_client.get_mentions.assert_called_once_with(
                limit=10, offset=0)
            assert "Found 100 mentions" in result
            assert "testuser" in result
            assert "This is a test tweet about #BTC" in result

    @pytest.mark.asyncio
    async def test_get_top_ticker_mentions_success(self, mock_api_client, mock_api_response):
        """Test successful top ticker mentions retrieval."""
        mock_data = {
            "pageSize": 10,
            "page": 1,
            "total": 50,
            "data": [
                {
                    "content": "BTC is looking bullish!",
                    "mentioned_at": "2023-03-15T12:30:45Z",
                    "metrics": {
                        "like_count": 100,
                        "reply_count": 20,
                        "repost_count": 30,
                        "view_count": 5000
                    }
                }
            ]
        }

        mock_api_client.get_top_mentions.return_value = mock_api_response(
            mock_data)

        with patch('elfa_mcp.server.get_client', return_value=mock_api_client):
            result = await get_top_ticker_mentions(
                ticker="BTC",
                time_window="24h",
                page=1,
                page_size=10
            )

            mock_api_client.get_top_mentions.assert_called_once_with(
                ticker="BTC",
                time_window="24h",
                page=1,
                page_size=10,
                include_account_details=False
            )

            assert "Top mentions for BTC" in result
            assert "BTC is looking bullish!" in result
            assert "Likes: 100" in result

    # Add similar tests for other MCP tools...

    @pytest.mark.asyncio
    async def test_invalid_time_window_handled(self, mock_api_client):
        """Test that invalid time window is handled properly."""
        with patch('elfa_mcp.server.get_client', return_value=mock_api_client):
            result = await get_top_ticker_mentions(
                ticker="BTC",
                time_window="invalid"
            )

            assert "Error retrieving top mentions" in result
            assert "Invalid time window format" in result
