"""Unit tests for agent.observability module.

Note: The main observability setup is handled by agent_framework.observability.
This module only tests our custom helper functions for span context management.
"""

import pytest

from agent.observability import get_current_agent_span, set_current_agent_span


@pytest.mark.unit
class TestSpanContextHelpers:
    """Tests for span context management helpers."""

    def test_set_and_get_current_agent_span(self):
        """Test setting and getting the current agent span."""
        mock_span = "test_span"

        set_current_agent_span(mock_span)
        result = get_current_agent_span()

        assert result == mock_span

    def test_get_current_agent_span_returns_none_when_not_set(self):
        """Test get_current_agent_span returns None when no span is set."""
        # Reset by setting None
        set_current_agent_span(None)

        result = get_current_agent_span()
        assert result is None

    def test_set_current_agent_span_handles_none(self):
        """Test set_current_agent_span handles None gracefully."""
        # Should not raise
        set_current_agent_span(None)

        result = get_current_agent_span()
        assert result is None
