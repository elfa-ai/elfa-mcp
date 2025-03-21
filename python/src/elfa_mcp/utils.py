"""
Utility functions for the Elfa MCP server.
"""

import time
import datetime
from typing import Dict, Any


def format_date(date_string: str) -> str:
    """Format a date string for display.

    Args:
        date_string: ISO format date string

    Returns:
        A user-friendly formatted date string
    """
    try:
        dt = datetime.datetime.fromisoformat(
            date_string.replace('Z', '+00:00'))
        return dt.strftime("%B %d, %Y, %H:%M:%S UTC")
    except (ValueError, AttributeError):
        return date_string


def format_engagement_stats(metrics: Dict[str, Any]) -> str:
    """Format engagement statistics for display.

    Args:
        metrics: Dict containing engagement metrics

    Returns:
        Formatted string with engagement statistics
    """
    stats = []

    if 'like_count' in metrics:
        stats.append(f"Likes: {metrics['like_count']}")

    if 'reply_count' in metrics:
        stats.append(f"Replies: {metrics['reply_count']}")

    if 'repost_count' in metrics:
        stats.append(f"Reposts: {metrics['repost_count']}")

    if 'quote_count' in metrics:
        stats.append(f"Quotes: {metrics['quote_count']}")

    if 'view_count' in metrics:
        stats.append(f"Views: {metrics['view_count']}")

    return " | ".join(stats)


def convert_timestamp_to_unix(timestamp: str) -> int:
    """Convert a human-readable time description to a Unix timestamp.

    Args:
        timestamp: String like "24h", "7d", "30d" or ISO date

    Returns:
        Unix timestamp (seconds since epoch)
    """
    now = time.time()

    # Check if it's a relative time
    if timestamp.endswith('h'):
        hours = int(timestamp[:-1])
        return int(now - (hours * 3600))

    if timestamp.endswith('d'):
        days = int(timestamp[:-1])
        return int(now - (days * 86400))

    if timestamp.endswith('w'):
        weeks = int(timestamp[:-1])
        return int(now - (weeks * 7 * 86400))

    if timestamp.endswith('m'):
        months = int(timestamp[:-1])
        return int(now - (months * 30 * 86400))  # Approximation

    # Try to parse as ISO date
    try:
        dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return int(dt.timestamp())
    except (ValueError, AttributeError):
        raise ValueError(f"Cannot parse timestamp: {timestamp}")


def validate_time_window(time_window: str) -> str:
    """Validate the time window format.

    Args:
        time_window: String like "1h", "24h", "7d"

    Returns:
        The validated time window, or raises ValueError
    """
    valid_formats = ["1h", "6h", "12h", "24h", "48h", "7d", "14d", "30d"]
    if time_window not in valid_formats:
        if time_window.endswith('h') or time_window.endswith('d'):
            try:
                value = int(time_window[:-1])
                if value > 0:
                    return time_window
            except ValueError:
                pass
        raise ValueError(
            f"Invalid time window format: {time_window}. Expected formats: {', '.join(valid_formats)}")
    return time_window
