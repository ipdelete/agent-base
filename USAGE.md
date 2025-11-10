# Agent Template Usage Guide

Comprehensive guide for using Agent Template to build AI-powered conversational agents.

## Table of Contents

- [Getting Started](#getting-started)
- [Interactive Mode](#interactive-mode)
- [Single Prompt Mode](#single-prompt-mode)
- [Visualization Modes](#visualization-modes)
- [Session Management](#session-management)
- [Building Custom Tools](#building-custom-tools)
- [Examples](#examples)

## Getting Started

### Basic Commands

```bash
# Interactive chat mode
agent

# Single query execution
agent -p "say hello to Alice"

# Check system dependencies
agent --check

# Show configuration
agent --config

# Get help
agent --help
```

### Interactive Mode Commands

```
/clear               # Clear screen and reset conversation context
/continue            # Resume a previous session
/purge               # Delete all saved sessions
/help                # Show help message
!command             # Execute shell command (e.g., !ls, !git status)
exit                 # Exit agent
```

## Interactive Mode

Start an interactive conversation session:

```bash
agent
```

### Features

- **Multi-turn conversations**: Context maintained across messages
- **Auto-save**: Sessions automatically saved on exit
- **Command history**: Navigate previous inputs with ↑/↓ arrows
- **Shell integration**: Execute system commands with `!` prefix
- **Keyboard shortcuts**: ESC to clear prompt

### Example Session

```bash
$ agent

Agent - AI-powered conversational assistant
Version 0.1.0 • OpenAI/gpt-5-mini

 ~/project [⎇ main]                              OpenAI/gpt-5-mini · v0.1.0
────────────────────────────────────────────────────────────────────────

> Say hello to Alice
✓ Complete (2.0s) - msg:1 tool:1

Hello, Alice! ◉‿◉

────────────────────────────────────────────────────────────────────────

> What tools do you have?
✓ Complete (1.5s) - msg:2 tool:0

I have two greeting tools available:
1. hello_world - Say hello to someone
2. greet_user - Greet in different languages (English, Spanish, French)

────────────────────────────────────────────────────────────────────────

> exit

Session auto-saved as 'auto-2025-11-08-11-15-30'
Goodbye!
```

### Shell Commands

Execute system commands without leaving the agent:

```bash
> !ls -la
# Shows directory listing

> !git status
# Shows git status

> !docker ps
# Shows running containers

> Now analyze those containers
# Agent can reference previous shell output in conversation
```

### Keyboard Shortcuts

- **ESC** - Clear current prompt
- **Ctrl+D** - Exit interactive mode
- **Ctrl+C** - Interrupt current operation
- **↑/↓** - Navigate command history

## Single Prompt Mode

Execute a single query and exit:

```bash
agent -p "your prompt here"
```

### Basic Examples

```bash
# Simple greeting
agent -p "say hello"

# Use tool with parameter
agent -p "say hello to Bob"

# Multi-language greeting
agent -p "greet Alice in Spanish"
```

### Output Format

By default, shows completion summary with timing and tool usage:

```bash
$ agent -p "say hello to Alice"
✓ Complete (2.0s) - msg:1 tool:1

Hello, Alice! ◉‿◉

────────────────────────────────────────────────────────────────────────
```

Where:
- `✓ Complete` - Execution finished successfully
- `(2.0s)` - Total execution time
- `msg:1` - Number of LLM messages
- `tool:1` - Number of tool calls made

## Visualization Modes

Control execution visualization detail:

### Minimal Mode (Default)

Shows only completion summary:

```bash
agent -p "say hello"
# ✓ Complete (2.0s) - msg:1 tool:1
```

### Verbose Mode

Shows full execution tree with LLM thinking and tool calls:

```bash
agent -p "say hello to Alice" --verbose
```

Output:
```
• Phase 1: hello_world (6.1s)
├── • Thinking (1 messages) - Response received (6.2s)
└── • → hello_world (Alice) - Complete (0.0s)

Hello, Alice! ◉‿◉

────────────────────────────────────────────────────────────────────────
```

### Quiet Mode

Minimal output, response only:

```bash
agent -p "say hello" --quiet
# Hello, World! ◉‿◉
```

## Session Management

### Auto-Save

Sessions are automatically saved on exit:

```bash
$ agent
> say hello
> exit

Session auto-saved as 'auto-2025-11-08-11-15-30'
Goodbye!
```

### Resume Last Session

Resume the most recent session:

```bash
agent --continue
```

### Resume Specific Session

Pick from saved sessions:

```bash
$ agent
> /continue

Available Sessions:
  1. auto-2025-11-08-11-15-30 (5m ago) "say hello"
  2. auto-2025-11-08-10-30-45 (1h ago) "greet Alice"

Select session [1-2]: 1
✓ Loaded 'auto-2025-11-08-11-15-30' (2 messages)

> continue the conversation...
```

### Clear Session

Start fresh conversation in current session:

```bash
> /clear
# Screen cleared, context reset
```

### Delete All Sessions

Remove all saved sessions:

```bash
> /purge
⚠ This will delete ALL 5 saved sessions.
Continue? (y/n): y
✓ Deleted 5 sessions
```

**Note:** The agent automatically maintains conversation context, so when you resume a session it will remember information from earlier in the conversation.

## Building Custom Tools

Agent Template uses a class-based toolset architecture for building custom tools.

### Create a New Toolset

```python
from agent.tools.toolset import AgentToolset
from agent.config import AgentConfig
from typing import Annotated
from pydantic import Field

class MyTools(AgentToolset):
    """My custom tools."""

    def get_tools(self):
        """Return list of tool functions."""
        return [self.my_tool]

    async def my_tool(
        self,
        arg: Annotated[str, Field(description="Argument description")]
    ) -> dict:
        """Tool description for LLM.

        Args:
            arg: Argument description

        Returns:
            Structured response with success field
        """
        try:
            result = self._do_work(arg)
            return self._create_success_response(
                result=result,
                message="Operation completed"
            )
        except Exception as e:
            return self._create_error_response(
                error="execution_failed",
                message=str(e)
            )
```

### Register Toolset

```python
from agent import Agent, AgentConfig
from mytools import MyTools

config = AgentConfig.from_env()
agent = Agent(
    config=config,
    toolsets=[HelloTools(config), MyTools(config)]
)
```

See [docs/design/architecture.md](docs/design/architecture.md) for detailed tool development patterns.

## Examples

### Example 1: Basic Usage

```bash
agent -p "say hello"
# ✓ Complete (1.5s) - msg:1 tool:1
# Hello, World! ◉‿◉
```

### Example 2: Custom Name

```bash
agent -p "say hello to Bob"
# ✓ Complete (2.0s) - msg:1 tool:1
# Hello, Bob! ◉‿◉
```

### Example 3: Multi-Language Greeting

```bash
agent -p "greet Alice in Spanish"
# ✓ Complete (2.1s) - msg:1 tool:1
# ¡Hola, Alice!

agent -p "greet Pierre in French"
# ✓ Complete (1.9s) - msg:1 tool:1
# Bonjour, Pierre!
```

### Example 4: Interactive Conversation

```bash
$ agent

> what tools do you have?
✓ Complete (1.5s) - msg:1 tool:0

I have two greeting tools...

> say hello to everyone
✓ Complete (2.0s) - msg:2 tool:1

Hello, everyone! ◉‿◉

> exit
```

### Example 5: Verbose Execution

```bash
agent -p "say hello to Alice" --verbose

• Phase 1: hello_world (6.1s)
├── • Thinking (1 messages) - Response received (6.2s)
└── • → hello_world (Alice) - Complete (0.0s)

Hello, Alice! ◉‿◉
```

### Example 6: Shell Integration

```bash
$ agent

> !ls -la
# Directory listing shown...

> !git status
# Git status shown...

> what files did I just list?
# Agent can reference the shell output
```

### Example 7: Session Resume

```bash
# Day 1
$ agent
> say hello to Alice
> exit
Session auto-saved as 'auto-2025-11-08-14-30-00'

# Day 2
$ agent --continue
✓ Loaded 'auto-2025-11-08-14-30-00' (3 messages)

> continue our conversation
# Context restored, conversation continues...
```

## Troubleshooting

### Configuration Issues

**Issue: "Configuration validation failed"**

```bash
# Check configuration
agent --check

# Common fixes:
# 1. Verify .env file exists
# 2. Check LLM_PROVIDER is set correctly
# 3. Verify API keys are set
```

**Issue: "Unknown LLM provider"**

Valid providers:
- `openai` - Direct OpenAI API
- `anthropic` - Direct Anthropic API
- `azure` - Azure OpenAI (fastest, supports gpt-5-codex)
- `azure_ai_foundry` - Azure AI Foundry platform

### Azure Authentication

**Issue: "Azure authentication failed"**

```bash
# Login with Azure CLI
az login

# Verify endpoint and deployment name in .env
AZURE_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-id
AZURE_MODEL_DEPLOYMENT=gpt-4o
```

### Debug Mode

Enable verbose logging:

```bash
LOG_LEVEL=debug agent -p "your prompt"
```

## Tips and Tricks

1. **Fast queries**: Use `-p` for quick one-off questions
2. **Save context**: Use interactive mode for multi-turn conversations
3. **Shell integration**: Use `!` prefix for quick system checks
4. **Session management**: Sessions auto-save on exit; resume with `agent --continue`
5. **Verbose debugging**: Use `--verbose` to see tool execution flow
6. **Multiple providers**: Test with different LLM providers for comparison

## Environment Variables

Key configuration options:

```bash
# LLM Provider Selection
LLM_PROVIDER=openai                  # openai, anthropic, azure, azure_ai_foundry

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5-mini              # Default

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929  # Default

# Azure OpenAI (fastest option!)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5-codex
AZURE_OPENAI_API_KEY=your-key        # Optional if using az login

# Azure AI Foundry
AZURE_PROJECT_ENDPOINT=https://...
AZURE_MODEL_DEPLOYMENT=gpt-4o

# Agent Settings
AGENT_DATA_DIR=~/.agent              # Session storage
LOG_LEVEL=info                       # debug, info, warning, error
```

See [.env.example](.env.example) for complete configuration options.
