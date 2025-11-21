"""Integration tests for agent with HelloTools."""

import pytest

from agent.agent import Agent
from agent.config.schema import AgentSettings
from agent.tools.hello import HelloTools
from tests.mocks.mock_client import MockChatClient

# Module-level marker for all tests in this file
pytestmark = [pytest.mark.integration, pytest.mark.tools]


@pytest.mark.asyncio
async def test_agent_with_hello_tools():
    """Test full agent integration with HelloTools."""
    config = AgentSettings()
    config.providers.enabled = ["openai"]
    config.providers.openai.api_key = "test-key"
    config.providers.openai.model = "gpt-5-mini"

    # Use mock client to avoid real LLM calls
    mock_client = MockChatClient(response="Hello from integration test!")

    # Create agent with HelloTools
    toolsets = [HelloTools(config)]
    agent = Agent(settings=config, chat_client=mock_client, toolsets=toolsets)

    # Verify tools registered
    assert len(agent.tools) == 2
    assert agent.tools[0].__name__ == "hello_world"
    assert agent.tools[1].__name__ == "greet_user"

    # Run agent
    response = await agent.run("Say hello")
    assert response == "Hello from integration test!"


@pytest.mark.asyncio
async def test_agent_run_stream_integration():
    """Test agent streaming with HelloTools."""
    config = AgentSettings()
    config.providers.enabled = ["openai"]
    config.providers.openai.api_key = "test-key"

    mock_client = MockChatClient(response="Hello World")
    agent = Agent(settings=config, chat_client=mock_client)

    # Collect streamed chunks
    chunks = []
    async for chunk in agent.run_stream("Test"):
        chunks.append(chunk)

    # Should get "Hello" and "World" as separate chunks
    assert len(chunks) == 2
    assert "Hello" in "".join(chunks)
    assert "World" in "".join(chunks)


@pytest.mark.asyncio
async def test_hello_tools_directly():
    """Test HelloTools can be instantiated and called directly."""
    config = AgentSettings()
    config.providers.enabled = ["openai"]
    config.providers.openai.api_key = "test-key"

    tools = HelloTools(config)

    # Test hello_world
    result = await tools.hello_world("Integration Test")
    assert result["success"] is True
    assert "Integration Test" in result["result"]

    # Test greet_user
    result = await tools.greet_user("Integration", "es")
    assert result["success"] is True
    assert "¡Hola" in result["result"]


@pytest.mark.asyncio
async def test_agent_with_multiple_provider_configs():
    """Test agent can be created with different provider configs."""
    mock_client = MockChatClient(response="Test")

    # OpenAI config
    openai_config = AgentSettings()
    openai_config.providers.enabled = ["openai"]
    openai_config.providers.openai.api_key = "test-key"
    agent_openai = Agent(settings=openai_config, chat_client=mock_client)
    assert agent_openai.config.llm_provider == "openai"

    # Anthropic config
    anthropic_config = AgentSettings()
    anthropic_config.providers.enabled = ["anthropic"]
    anthropic_config.providers.anthropic.api_key = "test-key"
    agent_anthropic = Agent(settings=anthropic_config, chat_client=mock_client)
    assert agent_anthropic.config.llm_provider == "anthropic"

    # Azure OpenAI config
    azure_openai_config = AgentSettings()
    azure_openai_config.providers.enabled = ["azure"]
    azure_openai_config.providers.azure.endpoint = "https://test.openai.azure.com"
    azure_openai_config.providers.azure.deployment = "gpt-5-codex"
    agent_azure_openai = Agent(settings=azure_openai_config, chat_client=mock_client)
    assert agent_azure_openai.config.llm_provider == "azure"

    # Azure AI Foundry config
    azure_config = AgentSettings()
    azure_config.providers.enabled = ["foundry"]
    azure_config.providers.foundry.project_endpoint = "https://test.ai.azure.com"
    azure_config.providers.foundry.model_deployment = "gpt-4o"
    agent_azure = Agent(settings=azure_config, chat_client=mock_client)
    assert agent_azure.config.llm_provider == "foundry"


@pytest.mark.asyncio
async def test_full_stack_config_to_agent_to_tools():
    """Test complete flow from config loading to agent execution."""
    # 1. Load config
    config = AgentSettings()
    config.providers.enabled = ["openai"]
    config.providers.openai.api_key = "test-key"

    # 2. Create toolsets
    hello_tools = HelloTools(config)
    assert len(hello_tools.get_tools()) == 2

    # 3. Create agent with tools
    mock_client = MockChatClient(response="Complete!")
    agent = Agent(settings=config, chat_client=mock_client, toolsets=[hello_tools])

    # 4. Verify full integration
    assert agent.config == config
    assert len(agent.toolsets) == 1
    assert len(agent.tools) == 2
    assert agent.agent is not None

    # 5. Execute
    response = await agent.run("Test")
    assert response == "Complete!"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tool_error_handling_integration():
    """Test tool error handling through full stack."""
    config = AgentSettings()
    config.providers.enabled = ["openai"]
    config.providers.openai.api_key = "test-key"
    tools = HelloTools(config)

    # Test error case
    result = await tools.greet_user("Test", "invalid_lang")

    assert result["success"] is False
    assert result["error"] == "unsupported_language"
    assert "invalid_lang" in result["message"]


@pytest.mark.asyncio
async def test_provider_switching_with_mock():
    """Test switching between providers with mocked client."""
    mock_client = MockChatClient(response="Provider test response")

    # OpenAI config
    openai_config = AgentSettings()
    openai_config.providers.enabled = ["openai"]
    openai_config.providers.openai.api_key = "test"

    # Anthropic config
    anthropic_config = AgentSettings()
    anthropic_config.providers.enabled = ["anthropic"]
    anthropic_config.providers.anthropic.api_key = "test"

    # Azure config
    azure_config = AgentSettings()
    azure_config.providers.enabled = ["azure"]
    azure_config.providers.azure.endpoint = "https://test.openai.azure.com"
    azure_config.providers.azure.deployment = "gpt-5-codex"

    # Foundry config
    foundry_config = AgentSettings()
    foundry_config.providers.enabled = ["foundry"]
    foundry_config.providers.foundry.project_endpoint = "https://test.ai.azure.com"
    foundry_config.providers.foundry.model_deployment = "gpt-4o"

    # Test all 4 providers with same mock client
    providers = [
        ("openai", openai_config),
        ("anthropic", anthropic_config),
        ("azure", azure_config),
        ("foundry", foundry_config),
    ]

    for provider_name, config in providers:
        # Create agent with mocked client
        agent = Agent(settings=config, chat_client=mock_client)

        # Execute
        response = await agent.run("test")

        # Verify
        assert response == "Provider test response"
        assert agent.config.llm_provider == provider_name
