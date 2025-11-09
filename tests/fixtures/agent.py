"""Agent and client fixtures for testing."""

import pytest

from agent.agent import Agent
from tests.mocks.mock_client import MockChatClient


@pytest.fixture
def mock_chat_client():
    """Create mock chat client."""
    return MockChatClient(response="Hello from mock!")


@pytest.fixture
def agent_instance(mock_config, mock_chat_client):
    """Create agent with mocks.

    Args:
        mock_config: Configuration fixture (from config.py)
        mock_chat_client: Mock client fixture

    Returns:
        Agent instance configured for testing
    """
    return Agent(
        config=mock_config,
        chat_client=mock_chat_client,
    )
