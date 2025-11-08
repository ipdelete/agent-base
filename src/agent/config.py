"""Configuration management for Agent with multi-provider LLM support."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class AgentConfig:
    """Configuration for Agent.

    Supports four LLM providers:
    - openai: OpenAI API (gpt-5-mini, gpt-4o, etc.)
    - anthropic: Anthropic API (claude-sonnet-4-5, claude-opus-4, etc.)
    - azure: Azure OpenAI (gpt-5-codex, gpt-4o, etc.)
    - azure_ai_foundry: Azure AI Foundry with managed models
    """

    # LLM Provider (openai, anthropic, azure, or azure_ai_foundry)
    llm_provider: str

    # OpenAI (when llm_provider == "openai")
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"

    # Anthropic (when llm_provider == "anthropic")
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-5-20250929"

    # Azure OpenAI (when llm_provider == "azure")
    azure_openai_endpoint: str | None = None
    azure_openai_deployment: str | None = None
    azure_openai_api_version: str = "2024-08-01-preview"
    azure_openai_api_key: str | None = None
    # Uses AzureCliCredential for auth if API key not provided

    # Azure AI Foundry (when llm_provider == "azure_ai_foundry")
    azure_project_endpoint: str | None = None
    azure_model_deployment: str | None = None
    # Uses AzureCliCredential for auth, no API key needed

    # Agent-specific
    agent_data_dir: Path | None = None
    agent_session_dir: Path | None = None

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Load configuration from environment variables.

        Returns:
            AgentConfig instance with values from environment

        Example:
            >>> config = AgentConfig.from_env()
            >>> config.llm_provider
            'openai'
        """
        load_dotenv()

        llm_provider = os.getenv("LLM_PROVIDER", "openai")

        config = cls(
            llm_provider=llm_provider,
            # OpenAI
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
            # Anthropic
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929"),
            # Azure OpenAI
            azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_openai_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            azure_openai_api_version=os.getenv("AZURE_OPENAI_VERSION", "2024-08-01-preview"),
            azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            # Azure AI Foundry
            azure_project_endpoint=os.getenv("AZURE_PROJECT_ENDPOINT"),
            azure_model_deployment=os.getenv("AZURE_MODEL_DEPLOYMENT"),
        )

        # Set default paths
        home = Path.home()
        data_dir = os.getenv("AGENT_DATA_DIR", str(home / ".agent"))
        config.agent_data_dir = Path(data_dir).expanduser()
        config.agent_session_dir = config.agent_data_dir / "sessions"

        return config

    def validate(self) -> None:
        """Validate configuration based on selected provider.

        Raises:
            ValueError: If required configuration is missing for the selected provider

        Example:
            >>> config = AgentConfig(llm_provider="openai")
            >>> config.validate()  # Will raise ValueError if OPENAI_API_KEY missing
        """
        if self.llm_provider == "openai":
            if not self.openai_api_key:
                raise ValueError(
                    "OpenAI provider requires API key. Set OPENAI_API_KEY environment variable."
                )
        elif self.llm_provider == "anthropic":
            if not self.anthropic_api_key:
                raise ValueError(
                    "Anthropic provider requires API key. Set ANTHROPIC_API_KEY environment variable."
                )
        elif self.llm_provider == "azure":
            if not self.azure_openai_endpoint:
                raise ValueError(
                    "Azure OpenAI requires endpoint. Set AZURE_OPENAI_ENDPOINT environment variable."
                )
            if not self.azure_openai_deployment:
                raise ValueError(
                    "Azure OpenAI requires deployment name. Set AZURE_OPENAI_DEPLOYMENT_NAME environment variable."
                )
            # Note: Can use AzureCliCredential OR API key for auth
        elif self.llm_provider == "azure_ai_foundry":
            if not self.azure_project_endpoint:
                raise ValueError(
                    "Azure AI Foundry requires project endpoint. Set AZURE_PROJECT_ENDPOINT environment variable."
                )
            if not self.azure_model_deployment:
                raise ValueError(
                    "Azure AI Foundry requires model deployment name. Set AZURE_MODEL_DEPLOYMENT environment variable."
                )
            # Note: Uses AzureCliCredential for auth, user must be logged in via `az login`
        else:
            raise ValueError(
                f"Unknown LLM provider: {self.llm_provider}. "
                "Supported providers: openai, anthropic, azure, azure_ai_foundry"
            )

    def get_model_display_name(self) -> str:
        """Get display name for current model configuration.

        Returns:
            Human-readable model display name

        Example:
            >>> config = AgentConfig(llm_provider="openai", openai_model="gpt-4o")
            >>> config.get_model_display_name()
            'OpenAI/gpt-4o'
        """
        if self.llm_provider == "openai":
            return f"OpenAI/{self.openai_model}"
        elif self.llm_provider == "anthropic":
            return f"Anthropic/{self.anthropic_model}"
        elif self.llm_provider == "azure":
            return f"Azure OpenAI/{self.azure_openai_deployment}"
        elif self.llm_provider == "azure_ai_foundry":
            return f"Azure AI Foundry/{self.azure_model_deployment}"
        return "Unknown"
