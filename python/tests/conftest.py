"""Shared pytest fixtures for elfa-mcp tests."""

import pytest
import os
import json
from unittest.mock import AsyncMock, patch, MagicMock

# Make sure we're using test environment
os.environ["ELFA_API_KEY"] = "test-api-key"


@pytest.fixture
def mock_api_response():
    """Create a mock API response with success."""
    def _create_response(data=None, success=True, metadata=None):
        response = {"success": success}
        if data is not None:
            response["data"] = data
        if metadata is not None:
            response["metadata"] = metadata
        return response
    return _create_response


@pytest.fixture
def mock_httpx_response():
    """Create a mock httpx response."""
    class MockResponse:
        def __init__(self, status_code=200, json_data=None):
            self.status_code = status_code
            self._json_data = json_data or {}

        def json(self):
            return self._json_data

        def raise_for_status(self):
            if self.status_code >= 400:
                from httpx import HTTPStatusError
                raise HTTPStatusError(
                    "Error", request=MagicMock(), response=self)

    return MockResponse


@pytest.fixture
def mock_api_client():
    """Create a mock Elfa API client."""
    with patch('elfa_mcp.api_client.ElfaClient') as mock_client_class:
        mock_instance = AsyncMock()
        mock_client_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def api_key_status_data():
    """Sample API key status data."""
    return {
        "remainingRequests": {
            "monthly": 9500,
            "daily": 950
        },
        "isExpired": False,
        "limits": {
            "monthly": 10000,
            "daily": 1000
        },
        "usage": {
            "monthly": 500,
            "daily": 50
        },
        "createdAt": "2023-01-01T00:00:00Z",
        "expiresAt": "2024-01-01T00:00:00Z",
        "monthlyRequestLimit": 10000,
        "dailyRequestLimit": 1000,
        "status": "active",
        "name": "Test API Key",
        "id": 12345
    }


@pytest.fixture
def mentions_data():
    """Sample mentions data."""
    return [
        {
            "id": "123456",
            "type": "tweet",
            "content": "This is a test tweet about #BTC",
            "originalUrl": "https://twitter.com/user/status/123456",
            "likeCount": 10,
            "replyCount": 5,
            "repostCount": 3,
            "viewCount": 1000,
            "mentionedAt": "2023-03-15T12:30:45Z",
            "account": {
                "id": 987654,
                "username": "testuser",
                "data": {
                    "name": "Test User",
                    "description": "This is a test account",
                    "profileImageUrl": "https://example.com/image.jpg",
                    "profileBannerUrl": "https://example.com/banner.jpg",
                    "userSince": "2020-01-01",
                    "location": "Test Location"
                },
                "isVerified": True
            }
        }
    ]


@pytest.fixture
def trending_tokens_data():
    """Sample trending tokens data."""
    return {
        "pageSize": 20,
        "page": 1,
        "total": 100,
        "data": [
            {
                "change_percent": 25.5,
                "previous_count": 100,
                "current_count": 125,
                "token": "BTC"
            },
            {
                "change_percent": -10.0,
                "previous_count": 50,
                "current_count": 45,
                "token": "ETH"
            }
        ]
    }


@pytest.fixture
def account_stats_data():
    """Sample account stats data."""
    return {
        "followerEngagementRatio": 2.5,
        "averageEngagement": 150,
        "smartFollowingCount": 75
    }
