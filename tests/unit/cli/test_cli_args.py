"""Unit tests for CLI argument overrides."""

import os
from unittest.mock import patch

import pytest

from agent.config.schema import AgentSettings


@pytest.mark.unit
@pytest.mark.cli
class TestCLIArgumentOverrides:
    """Tests for --provider and --model CLI argument functionality."""

    def test_provider_cli_override_openai(self):
        """Test --provider openai overrides LLM_PROVIDER environment variable."""
        # Preserve HOME/USERPROFILE for Path.home()
        env_vars = {"LLM_PROVIDER": "openai"}
        if "HOME" in os.environ:
            env_vars["HOME"] = os.environ["HOME"]
        if "USERPROFILE" in os.environ:
            env_vars["USERPROFILE"] = os.environ["USERPROFILE"]

        with patch.dict(os.environ, env_vars, clear=True):
            config = AgentConfig.from_env()
            assert config.llm_provider == "openai"

    def test_provider_cli_override_local(self):
        """Test --provider local overrides LLM_PROVIDER environment variable."""
        # Preserve HOME/USERPROFILE for Path.home()
        env_vars = {"LLM_PROVIDER": "local"}
        if "HOME" in os.environ:
            env_vars["HOME"] = os.environ["HOME"]
        if "USERPROFILE" in os.environ:
            env_vars["USERPROFILE"] = os.environ["USERPROFILE"]

        with patch.dict(os.environ, env_vars, clear=True):
            config = AgentConfig.from_env()
            assert config.llm_provider == "local"

    def test_model_cli_override_for_openai(self):
        """Test --model overrides AGENT_MODEL for OpenAI provider."""
        # Preserve HOME/USERPROFILE for Path.home()
        env_vars = {"LLM_PROVIDER": "openai", "AGENT_MODEL": "gpt-5-mini"}
        if "HOME" in os.environ:
            env_vars["HOME"] = os.environ["HOME"]
        if "USERPROFILE" in os.environ:
            env_vars["USERPROFILE"] = os.environ["USERPROFILE"]

        with patch.dict(os.environ, env_vars, clear=True):
            config = AgentConfig.from_env()
            assert config.openai_model == "gpt-5-mini"

    def test_model_cli_override_for_local(self):
        """Test --model overrides AGENT_MODEL for local provider."""
        # Preserve HOME/USERPROFILE for Path.home()
        env_vars = {"LLM_PROVIDER": "local", "AGENT_MODEL": "ai/qwen3"}
        if "HOME" in os.environ:
            env_vars["HOME"] = os.environ["HOME"]
        if "USERPROFILE" in os.environ:
            env_vars["USERPROFILE"] = os.environ["USERPROFILE"]

        with patch.dict(os.environ, env_vars, clear=True):
            config = AgentConfig.from_env()
            assert config.local_model == "ai/qwen3"

    def test_model_cli_override_for_anthropic(self):
        """Test --model overrides AGENT_MODEL for Anthropic provider."""
        # Preserve HOME/USERPROFILE for Path.home()
        env_vars = {
            "LLM_PROVIDER": "anthropic",
            "AGENT_MODEL": "claude-opus-4-20250514",
        }
        if "HOME" in os.environ:
            env_vars["HOME"] = os.environ["HOME"]
        if "USERPROFILE" in os.environ:
            env_vars["USERPROFILE"] = os.environ["USERPROFILE"]

        with patch.dict(os.environ, env_vars, clear=True):
            config = AgentConfig.from_env()
            assert config.anthropic_model == "claude-opus-4-20250514"

    def test_model_cli_override_for_gemini(self):
        """Test --model overrides AGENT_MODEL for Gemini provider."""
        # Preserve HOME/USERPROFILE for Path.home()
        env_vars = {"LLM_PROVIDER": "gemini", "AGENT_MODEL": "gemini-2.5-pro"}
        if "HOME" in os.environ:
            env_vars["HOME"] = os.environ["HOME"]
        if "USERPROFILE" in os.environ:
            env_vars["USERPROFILE"] = os.environ["USERPROFILE"]

        with patch.dict(os.environ, env_vars, clear=True):
            config = AgentConfig.from_env()
            assert config.gemini_model == "gemini-2.5-pro"

    def test_provider_and_model_cli_override_together(self):
        """Test both --provider and --model can be used together."""
        # Preserve HOME/USERPROFILE for Path.home()
        env_vars = {"LLM_PROVIDER": "local", "AGENT_MODEL": "ai/phi4"}
        if "HOME" in os.environ:
            env_vars["HOME"] = os.environ["HOME"]
        if "USERPROFILE" in os.environ:
            env_vars["USERPROFILE"] = os.environ["USERPROFILE"]

        with patch.dict(os.environ, env_vars, clear=True):
            config = AgentConfig.from_env()
            assert config.llm_provider == "local"
            assert config.local_model == "ai/phi4"

    def test_cli_override_without_env_file(self):
        """Test CLI overrides work even without .env file."""
        # Preserve HOME/USERPROFILE for Path.home()
        env_vars = {"LLM_PROVIDER": "local"}
        if "HOME" in os.environ:
            env_vars["HOME"] = os.environ["HOME"]
        if "USERPROFILE" in os.environ:
            env_vars["USERPROFILE"] = os.environ["USERPROFILE"]

        with patch.dict(os.environ, env_vars, clear=True):
            config = AgentConfig.from_env()
            assert config.llm_provider == "local"
            # Should use default model
            assert config.local_model == "ai/phi4"

    def test_provider_override_with_multiple_switches(self):
        """Test switching between providers via environment variable override."""
        # First use local
        # Preserve HOME/USERPROFILE for Path.home()
        env_vars = {"LLM_PROVIDER": "local"}
        if "HOME" in os.environ:
            env_vars["HOME"] = os.environ["HOME"]
        if "USERPROFILE" in os.environ:
            env_vars["USERPROFILE"] = os.environ["USERPROFILE"]

        with patch.dict(os.environ, env_vars, clear=True):
            config1 = AgentConfig.from_env()
            assert config1.llm_provider == "local"

        # Then switch to openai
        env_vars = {"LLM_PROVIDER": "openai"}
        if "HOME" in os.environ:
            env_vars["HOME"] = os.environ["HOME"]
        if "USERPROFILE" in os.environ:
            env_vars["USERPROFILE"] = os.environ["USERPROFILE"]

        with patch.dict(os.environ, env_vars, clear=True):
            config2 = AgentConfig.from_env()
            assert config2.llm_provider == "openai"

        # And back to local with different model
        env_vars = {"LLM_PROVIDER": "local", "AGENT_MODEL": "ai/qwen3"}
        if "HOME" in os.environ:
            env_vars["HOME"] = os.environ["HOME"]
        if "USERPROFILE" in os.environ:
            env_vars["USERPROFILE"] = os.environ["USERPROFILE"]

        with patch.dict(os.environ, env_vars, clear=True):
            config3 = AgentConfig.from_env()
            assert config3.llm_provider == "local"
            assert config3.local_model == "ai/qwen3"
