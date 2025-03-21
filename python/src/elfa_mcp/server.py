"""
MCP server implementation for Elfa API.
"""

import os
import time
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from elfa_mcp.api_client import get_client
from elfa_mcp.utils import (
    format_date,
    format_engagement_stats,
    convert_timestamp_to_unix,
    validate_time_window
)

# Initialize FastMCP server
mcp = FastMCP("elfa-api")


def main():
    """Run the MCP server."""
    # Initialize and run the server
    mcp.run(transport='stdio')


@mcp.tool()
async def get_api_key_info() -> str:
    """Get information about your Elfa API key, including usage limits and remaining requests."""
    try:
        client = get_client()
        response = await client.get_api_key_status()

        if response["success"]:
            data = response["data"]

            return f"""
API Key Information:
-------------------
Name: {data.get('name', 'N/A')}
Status: {data.get('status', 'N/A')}
Created: {format_date(data.get('createdAt', 'N/A'))}
Expires: {format_date(data.get('expiresAt', 'N/A'))}

Usage:
- Monthly: {data.get('usage', {}).get('monthly', 0)} / {data.get('monthlyRequestLimit', 'Unlimited')}
- Daily: {data.get('usage', {}).get('daily', 0)} / {data.get('dailyRequestLimit', 'Unlimited')}

Remaining Requests:
- Monthly: {data.get('remainingRequests', {}).get('monthly', 'N/A')}
- Daily: {data.get('remainingRequests', {}).get('daily', 'N/A')}
"""
        else:
            return "Failed to retrieve API key information."

    except Exception as e:
        return f"Error retrieving API key information: {str(e)}"


@mcp.tool()
async def get_smart_engagement_mentions(limit: int = 100, offset: int = 0) -> str:
    """
    Get tweets by smart accounts with significant engagement.

    Args:
        limit: Number of results to return (max 100)
        offset: Pagination offset
    """
    try:
        client = get_client()
        response = await client.get_mentions(limit=limit, offset=offset)

        if not response["success"]:
            return "Failed to retrieve mentions."

        mentions = response["data"]
        metadata = response["metadata"]

        result = f"Found {metadata['total']} mentions (showing {limit} from offset {offset}):\n\n"

        for idx, mention in enumerate(mentions, 1):
            account = mention.get("account", {})
            username = account.get("username", "Unknown")

            result += f"{idx}. @{username}: {mention.get('content', 'No content')}\n"
            result += f"   Type: {mention.get('type', 'N/A')} | "
            result += f"Posted: {format_date(mention.get('mentionedAt', 'N/A'))}\n"

            metrics = {
                'like_count': mention.get('likeCount', 0),
                'reply_count': mention.get('replyCount', 0),
                'repost_count': mention.get('repostCount', 0),
                'view_count': mention.get('viewCount', 0)
            }

            result += f"   {format_engagement_stats(metrics)}\n"
            result += f"   URL: {mention.get('originalUrl', 'N/A')}\n\n"

        return result

    except Exception as e:
        return f"Error retrieving mentions: {str(e)}"


@mcp.tool()
async def get_top_ticker_mentions(
    ticker: str,
    time_window: str = "1h",
    page: int = 1,
    page_size: int = 10,
    include_account_details: bool = False
) -> str:
    """
    Get the most significant mentions for a ticker symbol, ranked by relevance.

    Args:
        ticker: The ticker symbol to search for (e.g., "BTC" or "$BTC")
        time_window: Time window for mentions (e.g., "1h", "24h", "7d")
        page: Page number for pagination
        page_size: Number of items per page (max 50)
        include_account_details: Whether to include account details
    """
    try:
        # Validate time window
        validated_time_window = validate_time_window(time_window)

        client = get_client()
        response = await client.get_top_mentions(
            ticker=ticker,
            time_window=validated_time_window,
            page=page,
            page_size=page_size,
            include_account_details=include_account_details
        )

        if not response["success"]:
            return f"Failed to retrieve top mentions for {ticker}."

        data = response["data"]
        mentions = data.get("data", [])

        total_pages = (data['total'] // data['pageSize']) + 1
        result = f"Top mentions for {ticker} (time window: {validated_time_window}, page {page}/{total_pages}):\n\n"

        for idx, mention in enumerate(mentions, 1):
            metrics = mention.get("metrics", {})

            result += f"{idx}. {mention.get('content', 'No content')}\n"
            result += f"   Posted: {format_date(mention.get('mentioned_at', 'N/A'))}\n"
            result += f"   {format_engagement_stats(metrics)}\n\n"

        if not mentions:
            result += f"No mentions found for {ticker} in the {validated_time_window} time window."

        return result

    except Exception as e:
        return f"Error retrieving top mentions: {str(e)}"


@mcp.tool()
async def search_keyword_mentions(
    keywords: str,
    from_time: str,
    to_time: str,
    limit: int = 20,
    search_type: str = "and",
    cursor: str = None
) -> str:
    """
    Search for mentions containing specific keywords within a time range.

    Args:
        keywords: Up to 5 keywords to search for, separated by commas
        from_time: Start date (timestamp or relative time like "7d")
        to_time: End date (timestamp or relative time like "now")
        limit: Number of results to return (max 30)
        search_type: Type of search ("and" or "or")
        cursor: Cursor for pagination (optional)
    """
    try:
        # Convert time strings to unix timestamps
        from_timestamp = convert_timestamp_to_unix(
            from_time) if from_time != "now" else int(time.time())
        to_timestamp = convert_timestamp_to_unix(
            to_time) if to_time != "now" else int(time.time())

        client = get_client()
        response = await client.search_mentions(
            keywords=keywords,
            from_time=from_timestamp,
            to_time=to_timestamp,
            limit=limit,
            search_type=search_type,
            cursor=cursor
        )

        if not response["success"]:
            return f"Failed to search mentions for keywords: {keywords}."

        mentions = response["data"]
        metadata = response["metadata"]
        total = metadata.get("total", 0)
        next_cursor = metadata.get("cursor", "")

        result = f"Found {total} mentions for keywords: {keywords}\n"
        result += f"Search period: {from_time} to {to_time}\n"

        if next_cursor:
            result += f"Next cursor for pagination: {next_cursor}\n"

        result += "\n"

        for idx, mention in enumerate(mentions, 1):
            metrics = mention.get("metrics", {})
            account_info = mention.get("twitter_account_info", {})
            username = account_info.get("username", "Unknown")

            result += f"{idx}. @{username}: {mention.get('content', 'No content')}\n"
            result += f"   Type: {mention.get('type', 'N/A')} | "
            result += f"Posted: {format_date(mention.get('mentioned_at', 'N/A'))}\n"
            result += f"   {format_engagement_stats(metrics)}\n\n"

        if not mentions:
            result += "No mentions found matching your search criteria."

        return result

    except Exception as e:
        return f"Error searching mentions: {str(e)}"


@mcp.tool()
async def get_trending_tokens(
    time_window: str = "24h",
    page: int = 1,
    page_size: int = 20,
    min_mentions: int = 5
) -> str:
    """
    Get trending tokens based on mention count over a specified time period.

    Args:
        time_window: Time window for trending analysis (e.g., "24h", "7d")
        page: Page number for pagination
        page_size: Number of items per page (max 50)
        min_mentions: Minimum number of mentions required
    """
    try:
        # Validate time window
        validated_time_window = validate_time_window(time_window)

        client = get_client()
        response = await client.get_trending_tokens(
            time_window=validated_time_window,
            page=page,
            page_size=page_size,
            min_mentions=min_mentions
        )

        if not response["success"]:
            return "Failed to retrieve trending tokens."

        data = response["data"]
        tokens = data.get("data", [])

        total_pages = (data['total'] // data['pageSize']) + 1
        result = f"Trending tokens (time window: {validated_time_window}, page {page}/{total_pages}):\n\n"

        for idx, token in enumerate(tokens, 1):
            result += f"{idx}. {token.get('token', 'Unknown')}\n"
            result += f"   Current mentions: {token.get('current_count', 0)}\n"
            result += f"   Previous mentions: {token.get('previous_count', 0)}\n"
            result += f"   Change: {token.get('change_percent', 0):.2f}%\n\n"

        if not tokens:
            result += f"No trending tokens found in the {validated_time_window} time window with at least {min_mentions} mentions."

        return result

    except Exception as e:
        return f"Error retrieving trending tokens: {str(e)}"


@mcp.tool()
async def get_account_stats(username: str) -> str:
    """
    Get smart stats and social metrics for a Twitter account.

    Args:
        username: Twitter username (without @)
    """
    try:
        # Remove @ if present
        username = username.lstrip('@')

        client = get_client()
        response = await client.get_account_smart_stats(username=username)

        if not response["success"]:
            return f"Failed to retrieve account stats for @{username}."

        data = response["data"]

        result = f"Smart stats for @{username}:\n\n"
        result += f"Smart Following Count: {data.get('smartFollowingCount', 'N/A')}\n"
        result += f"Average Engagement: {data.get('averageEngagement', 'N/A')}\n"
        result += f"Follower Engagement Ratio: {data.get('followerEngagementRatio', 'N/A')}\n"

        return result

    except Exception as e:
        if "404" in str(e):
            return f"Account @{username} not found."
        return f"Error retrieving account stats: {str(e)}"

if __name__ == "__main__":
    main()
