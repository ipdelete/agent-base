"""Configuration fixtures for testing."""

import pytest

from agent.config import AgentConfig


@pytest.fixture
def mock_openai_config():
    """Create mock OpenAI configuration."""
    return AgentConfig(
        llm_provider="openai",
        openai_api_key="test-key",
        openai_model="gpt-5-mini",
    )


@pytest.fixture
def mock_anthropic_config():
    """Create mock Anthropic configuration."""
    return AgentConfig(
        llm_provider="anthropic",
        anthropic_api_key="test-key",
        anthropic_model="claude-sonnet-4-5-20250929",
    )


@pytest.fixture
def mock_azure_foundry_config():
    """Create mock Azure AI Foundry configuration."""
    return AgentConfig(
        llm_provider="azure_ai_foundry",
        azure_project_endpoint="https://test-project.services.ai.azure.com/api/projects/test",
        azure_model_deployment="gpt-4o",
    )


@pytest.fixture
def mock_config(mock_openai_config):
    """Default mock configuration (OpenAI)."""
    return mock_openai_config
