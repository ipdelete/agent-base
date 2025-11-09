"""Core Agent class with multi-provider LLM support."""

import logging
from collections.abc import AsyncIterator
from typing import Any, cast

from agent.config import AgentConfig
from agent.tools.hello import HelloTools
from agent.tools.toolset import AgentToolset

logger = logging.getLogger(__name__)


class Agent:
    """Agent with multi-provider LLM support and extensible tools.

    Supports three LLM providers through Microsoft Agent Framework:
    - OpenAI: Direct OpenAI API
    - Anthropic: Direct Anthropic API
    - Azure AI Foundry: Microsoft's managed AI platform

    Example:
        >>> config = AgentConfig.from_env()
        >>> agent = Agent(config)
        >>> response = await agent.run("Say hello")
        >>> print(response)
        Hello! How can I help you today?
    """

    def __init__(
        self,
        config: AgentConfig | None = None,
        chat_client: Any | None = None,
        toolsets: list[AgentToolset] | None = None,
        middleware: list | None = None,
    ):
        """Initialize Agent.

        Args:
            config: Agent configuration (required if chat_client not provided)
            chat_client: Chat client for testing (optional, for dependency injection)
            toolsets: List of toolsets (default: HelloTools)
            middleware: List of middleware (framework auto-categorizes by type)

        Example:
            # Production use
            >>> config = AgentConfig.from_env()
            >>> agent = Agent(config)

            # Testing with mocks
            >>> from tests.mocks import MockChatClient
            >>> mock_client = MockChatClient(response="Test response")
            >>> agent = Agent(config=config, chat_client=mock_client)

            # With custom middleware
            >>> from agent.middleware import create_middleware
            >>> mw = create_middleware()
            >>> agent = Agent(config=config, middleware=mw)
        """
        self.config = config or AgentConfig.from_env()

        # Dependency injection for testing
        if chat_client is not None:
            self.chat_client = chat_client
        else:
            self.chat_client = self._create_chat_client()

        # Initialize toolsets (avoid global state)
        if toolsets is None:
            toolsets = [HelloTools(self.config)]
        self.toolsets = toolsets

        # Collect all tools from toolsets
        self.tools = []
        for toolset in self.toolsets:
            self.tools.extend(toolset.get_tools())

        # Initialize middleware (create default if not provided)
        if middleware is None:
            from agent.middleware import create_middleware

            middleware = create_middleware()
        self.middleware = middleware

        # Create agent
        self.agent = self._create_agent()

    def _create_chat_client(self) -> Any:
        """Create chat client based on configuration.

        Supports:
        - openai: OpenAI API (gpt-5-mini, gpt-4o, etc.)
        - anthropic: Anthropic API (claude-sonnet-4-5, claude-opus-4, etc.)
        - azure: Azure OpenAI (gpt-5-codex, gpt-4o, etc.)
        - azure_ai_foundry: Azure AI Foundry with managed models

        Returns:
            Configured chat client for the selected provider

        Raises:
            ValueError: If provider is unknown or not supported
        """
        if self.config.llm_provider == "openai":
            from agent_framework.openai import OpenAIChatClient

            return OpenAIChatClient(
                model_id=self.config.openai_model,
                api_key=self.config.openai_api_key,
            )
        elif self.config.llm_provider == "anthropic":
            from agent_framework.anthropic import AnthropicClient

            return AnthropicClient(
                model_id=self.config.anthropic_model,
                api_key=self.config.anthropic_api_key,
            )
        elif self.config.llm_provider == "azure":
            from agent_framework.azure import AzureOpenAIChatClient, AzureOpenAIResponsesClient
            from azure.identity import AzureCliCredential, DefaultAzureCredential

            # gpt-5-codex requires the responses endpoint, use AzureOpenAIResponsesClient
            # gpt-5-mini and others use chat completions endpoint, use AzureOpenAIChatClient
            deployment_name = self.config.azure_openai_deployment or ""
            use_responses_client = "codex" in deployment_name.lower()
            client_class = (
                AzureOpenAIResponsesClient if use_responses_client else AzureOpenAIChatClient
            )

            # Use API key if provided, otherwise use Azure CLI credential
            if self.config.azure_openai_api_key:
                return client_class(
                    endpoint=self.config.azure_openai_endpoint,
                    deployment_name=self.config.azure_openai_deployment,
                    api_version=self.config.azure_openai_api_version,
                    api_key=self.config.azure_openai_api_key,
                )
            else:
                # Try AzureCliCredential first, fall back to DefaultAzureCredential
                credential: AzureCliCredential | DefaultAzureCredential
                try:
                    credential = AzureCliCredential()
                    return client_class(
                        endpoint=self.config.azure_openai_endpoint,
                        deployment_name=self.config.azure_openai_deployment,
                        api_version=self.config.azure_openai_api_version,
                        credential=credential,
                    )
                except Exception:
                    credential = DefaultAzureCredential()
                    return client_class(
                        endpoint=self.config.azure_openai_endpoint,
                        deployment_name=self.config.azure_openai_deployment,
                        api_version=self.config.azure_openai_api_version,
                        credential=credential,
                    )
        elif self.config.llm_provider == "azure_ai_foundry":
            from agent_framework.azure import AzureAIAgentClient
            from azure.identity.aio import AzureCliCredential as AsyncAzureCliCredential

            return AzureAIAgentClient(
                project_endpoint=self.config.azure_project_endpoint,
                model_deployment_name=self.config.azure_model_deployment,
                async_credential=AsyncAzureCliCredential(),
            )
        else:
            raise ValueError(
                f"Unknown provider: {self.config.llm_provider}. "
                f"Supported: openai, anthropic, azure, azure_ai_foundry"
            )

    def _create_agent(self) -> Any:
        """Create agent with tools, instructions, and middleware.

        Returns:
            Configured agent instance ready to handle requests
        """
        instructions = """You are a helpful AI assistant that can use tools to assist with various tasks.

You help users with:
- Natural language interactions
- Information synthesis and summarization
- Tool-based task execution
- Context-aware conversations

Be helpful, concise, and clear in your responses."""

        return self.chat_client.create_agent(
            name="Agent",
            instructions=instructions,
            tools=self.tools,
            middleware=self.middleware,
        )

    def get_new_thread(self) -> Any:
        """Create a new conversation thread.

        Returns:
            New thread instance for maintaining conversation context

        Example:
            >>> agent = Agent(config)
            >>> thread = agent.get_new_thread()
            >>> response = await agent.run("Hello", thread=thread)
        """
        if hasattr(self.chat_client, "create_thread"):
            return self.chat_client.create_thread()
        # Fallback: some providers may not support explicit threads (e.g., OpenAI)
        # They manage conversation context automatically through message history
        return None

    async def run(self, prompt: str, thread: Any | None = None) -> str:
        """Run agent with prompt.

        Args:
            prompt: User prompt
            thread: Optional thread for conversation context

        Returns:
            Agent response as a string

        Example:
            >>> agent = Agent(config)
            >>> response = await agent.run("Say hello to Alice")
            >>> print(response)
            Hello, Alice!

            >>> # With thread for context
            >>> thread = agent.get_new_thread()
            >>> response = await agent.run("Hello", thread=thread)
        """
        if thread:
            result = await self.agent.run(prompt, thread=thread)
        else:
            result = await self.agent.run(prompt)

        # Handle different provider return types
        # OpenAI returns str, Anthropic returns AgentRunResponse with .text
        if isinstance(result, str):
            return result
        elif hasattr(result, "text"):
            return result.text
        else:
            return cast(str, result)

    async def run_stream(self, prompt: str, thread: Any | None = None) -> AsyncIterator[str]:
        """Run agent with streaming response.

        Args:
            prompt: User prompt
            thread: Optional thread for conversation context

        Yields:
            Response chunks as they become available

        Example:
            >>> agent = Agent(config)
            >>> async for chunk in agent.run_stream("Say hello"):
            ...     print(chunk, end="")
            Hello! How can I help you?

            >>> # With thread for context
            >>> thread = agent.get_new_thread()
            >>> async for chunk in agent.run_stream("Hello", thread=thread):
            ...     print(chunk, end="")
        """
        if thread:
            stream = self.agent.run_stream(prompt, thread=thread)
        else:
            stream = self.agent.run_stream(prompt)

        async for chunk in stream:
            # Handle different provider chunk types
            # OpenAI returns str, Anthropic returns AgentRunResponseUpdate with .text
            if isinstance(chunk, str):
                yield chunk
            elif hasattr(chunk, "text"):
                yield chunk.text
            else:
                yield str(chunk)
