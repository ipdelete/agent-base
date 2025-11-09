# Agent Template

Production-ready foundation for building AI agents with extensible tools. Built on Microsoft Agent Framework.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview

Build AI-powered conversational agents with custom tools. Clean architecture, multi-provider LLM support, and comprehensive testing built-in.

```bash
agent -p "say hello to Alice"
# ✓ Complete (2.0s) - msg:1 tool:1
# Hello, Alice! ◉‿◉

agent  # Interactive mode with auto-save sessions
```

**[📖 Full Usage Guide](USAGE.md)** | **[🚀 Quick Start](#quick-setup)**

## Features

### 🤖 Multi-Provider LLM Support
- **OpenAI**: Direct OpenAI API (gpt-5-mini, gpt-4o, etc.)
- **Anthropic**: Direct Anthropic API (claude-sonnet-4-5, claude-opus-4, etc.)
- **Azure OpenAI**: Azure-hosted OpenAI models (gpt-5-codex, gpt-4o, etc.) - fastest!
- **Azure AI Foundry**: Microsoft's managed AI platform with 1,800+ models

### 🎛️ Interactive Experience
- **Interactive mode**: Multi-turn conversations with auto-save sessions
- **Execution visualization**: Real-time display of thinking and tool calls
- **Conversation history**: Resume sessions with `--continue`
- **Keyboard shortcuts**: ESC to clear, shell commands with `!`
- **Context status bar**: Right-aligned path and branch display before each prompt

### ⌨️ Keyboard Shortcuts
- **Shell commands**: Execute system commands with `!` (e.g., `!ls`, `!git status`)
- **Quick clear**: Press `ESC` to clear the prompt
- **Mixed workflows**: Combine AI conversations with direct shell access
- **No context switching**: Stay in agent while checking system state

### 🏗️ Clean Architecture
- **Class-based toolsets** with dependency injection (no global state)
- **Event-driven design** for loose coupling
- **High test coverage** (85%+ maintained)
- **Extensible patterns** for adding custom tools

## Prerequisites

**Required:**
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- One of the supported LLM providers (OpenAI, Anthropic, Azure OpenAI, or Azure AI Foundry)

**Optional:**
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) - auth via `az login` for Azure providers

## Quick Setup

```bash
# Install from source
git clone https://github.com/danielscholl/agent-template.git
cd agent-template
uv sync

# Configure required credentials
cp .env.example .env
# Edit .env with your LLM provider credentials
```

**Authenticate with CLI tools** (if using Azure AI Foundry):
```bash
az login      # For Azure AI Foundry
```

**OR use API keys**:
```bash
# Edit .env file:
# LLM_PROVIDER=openai
# OPENAI_API_KEY=your-key
```

**Verify setup**:
```bash
uv run agent --check    # Check dependencies and configuration
uv run agent --config   # Show current configuration
```

## Usage

```bash
# Interactive chat mode
agent

# Single query
agent -p "say hello to Alice"

# Health check
agent --check

# Get help
agent --help
```

### Interactive Mode Features

In interactive mode, you can:

- **Ask questions**: Natural language interactions
- **Use tools**: Agent automatically selects and calls appropriate tools
- **Execute shell commands**: `!ls`, `!git status`, `!docker ps`
- **Clear prompt**: Press `ESC` to clear current input
- **Auto-saved sessions**: Exit and resume anytime with `agent --continue`
- **Switch sessions**: Use `/continue` to pick from saved sessions

**See [USAGE.md](USAGE.md) for comprehensive examples and patterns.**

## Configuration

Configure via `.env` file:

```bash
# Required
LLM_PROVIDER=openai                  # openai, anthropic, azure, azure_ai_foundry
OPENAI_API_KEY=sk-your-key

# Optional
AGENT_DATA_DIR=~/.agent              # Session storage
LOG_LEVEL=info                       # debug, info, warning, error
```

See [.env.example](.env.example) for all provider options (OpenAI, Anthropic, Azure OpenAI, Azure AI Foundry).

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code quality guidelines, and contribution workflow.

### Quick Development Setup

```bash
# Install development dependencies
uv sync --all-extras

# Run tests
uv run pytest --cov=src/agent --cov-fail-under=85

# Code quality checks
uv run black src/ tests/
uv run ruff check --fix src/ tests/
uv run mypy src/agent/
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code quality guidelines, and contribution workflow.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- CLI powered by [Rich](https://rich.readthedocs.io/) and [Typer](https://typer.tiangolo.com/)
- Testing with [pytest](https://pytest.org/)
