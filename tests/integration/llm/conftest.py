"""Fixtures for real LLM integration tests.

⚠️ These fixtures create agents with REAL LLM clients that make API calls!

Fixtures automatically skip if API keys are not set.
"""

import os

import pytest

from agent.agent import Agent
from agent.config import AgentConfig


# Cost tracking (simple implementation)
_test_costs = {}


@pytest.fixture
def openai_agent():
    """Create agent with real OpenAI client.

    Automatically skips if OPENAI_API_KEY is not set.

    Example:
        @pytest.mark.llm
        @pytest.mark.requires_openai
        async def test_something(openai_agent):
            response = await openai_agent.run("test")
    """
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set - skipping real LLM test")

    config = AgentConfig(
        llm_provider="openai",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model="gpt-4o-mini",  # Cheaper model for testing
    )

    return Agent(config=config)


@pytest.fixture
def anthropic_agent():
    """Create agent with real Anthropic client.

    Automatically skips if ANTHROPIC_API_KEY is not set.

    Example:
        @pytest.mark.llm
        @pytest.mark.requires_anthropic
        async def test_something(anthropic_agent):
            response = await anthropic_agent.run("test")
    """
    if not os.getenv("ANTHROPIC_API_KEY"):
        pytest.skip("ANTHROPIC_API_KEY not set - skipping real LLM test")

    config = AgentConfig(
        llm_provider="anthropic",
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        anthropic_model="claude-sonnet-4-5-20250929",  # Latest Sonnet model
    )

    return Agent(config=config)


@pytest.fixture
def azure_openai_agent():
    """Create agent with real Azure OpenAI client.

    Automatically skips if Azure credentials are not set.

    Example:
        @pytest.mark.llm
        @pytest.mark.requires_azure
        async def test_something(azure_openai_agent):
            response = await azure_openai_agent.run("test")
    """
    if not os.getenv("AZURE_OPENAI_ENDPOINT"):
        pytest.skip("Azure OpenAI credentials not set - skipping real LLM test")

    config = AgentConfig(
        llm_provider="azure",
        azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_openai_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
        azure_openai_api_version=os.getenv(
            "AZURE_OPENAI_API_VERSION", "2024-10-01-preview"
        ),
    )

    return Agent(config=config)


@pytest.fixture
def azure_ai_foundry_agent():
    """Create agent with real Azure AI Foundry client.

    Automatically skips if Azure AI Foundry credentials are not set.

    Example:
        @pytest.mark.llm
        @pytest.mark.requires_azure
        async def test_something(azure_ai_foundry_agent):
            response = await azure_ai_foundry_agent.run("test")
    """
    if not os.getenv("AZURE_PROJECT_ENDPOINT"):
        pytest.skip("Azure AI Foundry credentials not set - skipping real LLM test")

    config = AgentConfig(
        llm_provider="azure_ai_foundry",
        azure_project_endpoint=os.getenv("AZURE_PROJECT_ENDPOINT"),
        azure_model_deployment=os.getenv("AZURE_MODEL_DEPLOYMENT", "gpt-4o"),
    )

    return Agent(config=config)


@pytest.fixture(autouse=True)
def track_llm_test_cost(request):
    """Track estimated cost of LLM tests (autouse for all tests in this directory).

    This is a simple implementation - actual costs depend on prompt/response length.
    """
    test_name = request.node.name

    # Cost tracking happens here
    yield

    # After test completes, could log cost
    # For now, just a placeholder for future cost tracking implementation


def pytest_configure(config):
    """Print cost warning when LLM tests are about to run."""
    if config.option.markexpr and "llm" in config.option.markexpr:
        print("\n" + "=" * 70)
        print("⚠️  RUNNING REAL LLM TESTS - THESE MAKE API CALLS AND COST MONEY")
        print("=" * 70)
        print(f"\n💰 Estimated cost: ~$0.005 per test run")
        print(f"📊 Target: < $0.01 total for all LLM tests\n")


def pytest_collection_modifyitems(config, items):
    """Mark all tests in this directory with @pytest.mark.llm."""
    llm_path_marker = "integration/llm"

    for item in items:
        if llm_path_marker in str(item.fspath):
            item.add_marker(pytest.mark.llm)
            item.add_marker(pytest.mark.slow)
