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

### Observability & Monitoring
- **OpenTelemetry Integration**: Built-in telemetry with Azure Application Insights and Aspire Dashboard support
- **Local Development**: `/telemetry start` command for instant local observability (no Azure required!)
- **Session Tracking**: Correlate telemetry with log files via `session.id`
- **Token Metrics**: Track token usage and costs by model
- **Tool Tracing**: See full execution hierarchy including tool calls
- **Cross-Platform**: Works on Windows, Mac, and Linux

### Core Capabilities

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
uv run agent --check    # Validate configuration (includes Docker check)
uv run agent --config   # Display current settings
```

**Optional: Enable Local Observability**

```bash
# Start telemetry dashboard
export ENABLE_OTEL=true
uv run agent --telemetry start
```



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




## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- CLI powered by [Rich](https://rich.readthedocs.io/) and [Typer](https://typer.tiangolo.com/)
- Testing with [pytest](https://pytest.org/)
