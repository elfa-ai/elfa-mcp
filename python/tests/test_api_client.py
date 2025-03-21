"""Tests for the Elfa API client."""

import os
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

import httpx
from elfa_mcp.api_client import ElfaClient, get_client

class TestElfaClient:
    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        client = ElfaClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.headers["x-elfa-api-key"] == "test-key"

    def test_init_with_environment_var(self):
        """Test initialization using environment variable."""
        with patch.dict(os.environ, {"ELFA_API_KEY": "env-key"}):
            client = ElfaClient()
            assert client.api_key == "env-key"
            assert client.headers["x-elfa-api-key"] == "env-key"

    def test_init_without_api_key_raises_error(self):
        """Test that initialization without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                ElfaClient()

    @pytest.mark.asyncio
    async def test_make_request_successful(self, mock_httpx_response):
        """Test successful API request."""
        mock_response = mock_httpx_response(
            status_code=200,
            json_data={"success": True, "data": {"key": "value"}}
        )
        
        with patch("httpx.AsyncClient.get", AsyncMock(return_value=mock_response)):
            client = ElfaClient(api_key="test-key")
            result = await client._make_request("/test-endpoint")
            
            assert result == {"success": True, "data": {"key": "value"}}

    @pytest.mark.asyncio
    async def test_make_request_unauthorized(self, mock_httpx_response):
        """Test unauthorized API request."""
        mock_response = mock_httpx_response(status_code=401)
        
        with patch("httpx.AsyncClient.get", AsyncMock(return_value=mock_response)):
            client = ElfaClient(api_key="test-key")
            
            with pytest.raises(Exception) as exc_info:
                await client._make_request("/test-endpoint")
            
            assert "API key is invalid or expired" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_make_request_server_error(self, mock_httpx_response):
        """Test API request with server error."""
        mock_response = mock_httpx_response(status_code=500)
        
        with patch("httpx.AsyncClient.get", AsyncMock(return_value=mock_response)):
            client = ElfaClient(api_key="test-key")
            
            with pytest.raises(Exception) as exc_info:
                await client._make_request("/test-endpoint")
            
            assert "API request failed with status code 500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_make_request_network_error(self):
        """Test API request with network error."""
        with patch("httpx.AsyncClient.get", AsyncMock(side_effect=httpx.RequestError("Network error", request=MagicMock()))):
            client = ElfaClient(api_key="test-key")
            
            with pytest.raises(Exception) as exc_info:
                await client._make_request("/test-endpoint")
            
            assert "Request error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_api_key_status(self, mock_api_response):
        """Test get_api_key_status method."""
        client = ElfaClient(api_key="test-key")
        client._make_request = AsyncMock(return_value=mock_api_response({"key": "value"}))
        
        result = await client.get_api_key_status()
        
        client._make_request.assert_called_once_with("/v1/key-status")
        assert result == mock_api_response({"key": "value"})

    @pytest.mark.asyncio
    async def test_get_mentions(self, mock_api_response):
        """Test get_mentions method."""
        client = ElfaClient(api_key="test-key")
        client._make_request = AsyncMock(return_value=mock_api_response([{"id": "123"}]))
        
        result = await client.get_mentions(limit=50, offset=10)
        
        client._make_request.assert_called_once_with("/v1/mentions", {"limit": 50, "offset": 10})
        assert result == mock_api_response([{"id": "123"}])

    # Add similar tests for other API methods...

class TestGetClient:
    def test_get_client_creates_singleton(self):
        """Test that get_client creates a singleton instance."""
        with patch("elfa_mcp.api_client.ElfaClient") as mock_client_class:
            mock_client_class.return_value = "test-client-instance"
            
            # First call should create a new instance
            client1 = get_client()
            assert client1 == "test-client-instance"
            mock_client_class.assert_called_once()
            
            # Second call should reuse the existing instance
            mock_client_class.reset_mock()
            client2 = get_client()
            assert client2 == "test-client-instance"
            mock_client_class.assert_not_called()