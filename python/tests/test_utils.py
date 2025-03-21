"""Tests for utility functions."""

import pytest
import time
from datetime import datetime, timezone
from elfa_mcp.utils import (
    format_date,
    format_engagement_stats,
    convert_timestamp_to_unix,
    validate_time_window
)


class TestFormatDate:
    def test_format_valid_date(self):
        """Test formatting a valid ISO date string."""
        date_str = "2023-01-15T12:30:45Z"
        formatted = format_date(date_str)
        assert "January 15, 2023" in formatted
        assert "12:30:45" in formatted

    def test_invalid_date_returns_original(self):
        """Test that invalid dates return the original string."""
        date_str = "not-a-date"
        assert format_date(date_str) == date_str


class TestFormatEngagementStats:
    def test_format_complete_metrics(self):
        """Test formatting with all metrics present."""
        metrics = {
            'like_count': 10,
            'reply_count': 5,
            'repost_count': 3,
            'quote_count': 2,
            'view_count': 1000
        }
        formatted = format_engagement_stats(metrics)
        assert "Likes: 10" in formatted
        assert "Replies: 5" in formatted
        assert "Reposts: 3" in formatted
        assert "Quotes: 2" in formatted
        assert "Views: 1000" in formatted

    def test_format_partial_metrics(self):
        """Test formatting with only some metrics present."""
        metrics = {
            'like_count': 10,
            'view_count': 1000
        }
        formatted = format_engagement_stats(metrics)
        assert "Likes: 10" in formatted
        assert "Views: 1000" in formatted
        assert "Replies" not in formatted

    def test_format_empty_metrics(self):
        """Test formatting with empty metrics."""
        metrics = {}
        formatted = format_engagement_stats(metrics)
        assert formatted == ""


class TestConvertTimestampToUnix:
    def test_convert_hours(self):
        """Test converting hours to Unix timestamp."""
        now = time.time()
        hours_ago = convert_timestamp_to_unix("24h")
        # Should be approximately 24 hours ago (with some tolerance for test execution time)
        assert abs((now - hours_ago) - 24*3600) < 5

    def test_convert_days(self):
        """Test converting days to Unix timestamp."""
        now = time.time()
        days_ago = convert_timestamp_to_unix("7d")
        # Should be approximately 7 days ago
        assert abs((now - days_ago) - 7*24*3600) < 5

    def test_convert_weeks(self):
        """Test converting weeks to Unix timestamp."""
        now = time.time()
        weeks_ago = convert_timestamp_to_unix("2w")
        # Should be approximately 2 weeks ago
        assert abs((now - weeks_ago) - 2*7*24*3600) < 5

    def test_convert_iso_date(self):
        """Test converting ISO date to Unix timestamp."""
        iso_date = "2023-01-01T00:00:00Z"
        expected_timestamp = int(
            datetime(2023, 1, 1, tzinfo=timezone.utc).timestamp())
        assert convert_timestamp_to_unix(iso_date) == expected_timestamp

    def test_invalid_format_raises_error(self):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError):
            convert_timestamp_to_unix("invalid")


class TestValidateTimeWindow:
    def test_valid_preset_time_windows(self):
        """Test validation of preset time windows."""
        presets = ["1h", "6h", "12h", "24h", "48h", "7d", "14d", "30d"]
        for preset in presets:
            assert validate_time_window(preset) == preset

    def test_valid_custom_time_windows(self):
        """Test validation of custom time windows."""
        custom = ["2h", "36h", "3d", "10d"]
        for window in custom:
            assert validate_time_window(window) == window

    def test_invalid_time_window_raises_error(self):
        """Test that invalid time windows raise ValueError."""
        invalid = ["h", "1m", "1y", "invalid", "-1h", "0d"]
        for window in invalid:
            with pytest.raises(ValueError):
                validate_time_window(window)
