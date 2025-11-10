# Agent Base

Production-ready conversational AI agent with extensible architecture.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview

A complete conversational agent built on Microsoft Agent Framework with multi-provider LLM support, conversation memory, and session management. Designed for extension through custom toolsets.

```bash
agent -p "say hello to Alice"
# Complete (2.0s)
# Hello, Alice!

agent  # Interactive mode with auto-save sessions
```

## Features

**Multi-Provider LLM Support**
- OpenAI (gpt-5-mini, gpt-4o)
- Anthropic (claude-sonnet-4-5, claude-opus-4)
- Azure OpenAI (gpt-5-codex, gpt-4o)
- Azure AI Foundry

**Conversation Features**
- Conversation memory with context persistence
- Automatic session saving and resume
- Multi-turn context awareness
- Session switching and management

**Extensible Architecture**
- Class-based toolset system for custom tools
- Event-driven design for loose coupling
- Dependency injection for testing
- Test coverage above 85%

## Quick Start

**Prerequisites**
- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- API credentials for at least one LLM provider
- (Optional) [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) for Azure providers

**Installation**

```bash
git clone https://github.com/danielscholl/agent-base.git
cd agent-base
uv sync
```

**Configuration**

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

For OpenAI:
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
```

For Azure providers, authenticate via Azure CLI:
```bash
az login
```

**Verification**

```bash
uv run agent --check    # Validate configuration
uv run agent --config   # Display current settings
```

## Usage

Basic commands:

```bash
agent                          # Start interactive mode
agent -p "your question"       # Single query
agent --continue               # Resume last session
agent --help                   # Show all options
```

Interactive mode supports:
- Natural language queries with automatic tool selection
- Shell command execution via `!` prefix (e.g., `!git status`, `!ls`)
- Session persistence (automatically saved on exit)
- ESC to clear the current prompt
- `/continue` to switch between saved sessions

See [USAGE.md](USAGE.md) for detailed examples and usage patterns.

## Configuration

Environment variables are loaded from `.env`:

```bash
# Provider selection (openai, anthropic, azure, azure_ai_foundry)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key

# Optional settings
AGENT_DATA_DIR=~/.agent              # Session storage location
LOG_LEVEL=info                       # Logging verbosity
```

See [.env.example](.env.example) for all available configuration options, including custom system prompt support via `AGENT_SYSTEM_PROMPT`.

## Extending Agent Base

Add custom tools by creating toolsets:

```python
from agent.tools.toolset import AgentToolset

class MyTools(AgentToolset):
    def get_tools(self):
        return [self.my_tool]

    async def my_tool(self, arg: str) -> dict:
        """Your custom tool."""
        return self._create_success_response(result="...")
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guide.

## Development

```bash
uv sync --all-extras              # Install dev dependencies
uv run pytest --cov=src/agent     # Run tests with coverage
uv run black src/ tests/          # Format code
uv run ruff check --fix src/      # Lint code
uv run mypy src/agent/            # Type check
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- CLI powered by [Rich](https://rich.readthedocs.io/) and [Typer](https://typer.tiangolo.com/)
- Testing with [pytest](https://pytest.org/)
