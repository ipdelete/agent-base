# Usage Guide

Complete reference for Agent Base features and workflows.

## Command Reference

### CLI Commands

```bash
agent                    # Interactive mode
agent -p "prompt"        # Single query
agent --continue         # Resume last session
agent --verbose          # Show execution details
agent --quiet            # Minimal output
agent --check            # Verify configuration
agent --config           # Show settings
agent --help             # Display help
```

### Interactive Commands

```
/clear                   # Clear conversation context
/continue                # Select previous session
/purge                   # Delete all sessions
/help                    # Show help
!command                 # Execute shell command
exit                     # Quit
```

### Keyboard Shortcuts

```
ESC                      # Clear prompt
Ctrl+D                   # Exit
Ctrl+C                   # Interrupt
↑/↓                      # Command history
```

## Getting Started

### First Run

Start an interactive session:

```bash
$ agent

Agent - AI-powered conversational assistant
Version 0.1.0 • OpenAI/gpt-5-mini

 ~/project [⎇ main]                              OpenAI/gpt-5-mini · v0.1.0
────────────────────────────────────────────────────────────────────────

> Say hello to Alice
✓ Complete (2.0s) - msg:1 tool:1

Hello, Alice!

────────────────────────────────────────────────────────────────────────

> exit

Session auto-saved as 'auto-2025-11-08-11-15-30'
Goodbye!
```

### Single Query Mode

Execute one prompt and exit:

```bash
$ agent -p "say hello to Alice"
✓ Complete (2.0s) - msg:1 tool:1

Hello, Alice!
```

## Interactive Mode

Features:
- Multi-turn conversations with persistent context
- Automatic session saving on exit
- Command history navigation (↑/↓)
- Shell command execution via `!` prefix
- ESC to clear current prompt

### Shell Integration

Execute system commands without leaving the agent:

```bash
> !ls -la
total 48
drwxr-xr-x  12 user  staff   384 Nov  8 11:15 .
drwxr-xr-x   5 user  staff   160 Nov  8 10:30 ..

> !git status
On branch main
Your branch is up to date with 'origin/main'.

> Analyze those git changes
The repository is clean with no pending changes...
```

### Multi-Turn Conversations

Context is maintained across messages:

```bash
> My name is Alice
Nice to meet you, Alice!

> What's my name?
Your name is Alice.
```

## Session Management

Sessions save automatically when you exit:

```bash
$ agent
> say hello
> exit
Session auto-saved as 'auto-2025-11-08-11-15-30'
```

Resume the most recent session:

```bash
$ agent --continue
✓ Loaded 'auto-2025-11-08-11-15-30' (2 messages)
```

Select from saved sessions:

```bash
$ agent
> /continue

Available Sessions:
  1. auto-2025-11-08-11-15-30 (5m ago) "say hello"
  2. auto-2025-11-08-10-30-45 (1h ago) "greet Alice"

Select session [1-2]: 1
✓ Loaded 'auto-2025-11-08-11-15-30' (2 messages)
```

Clear context without exiting:

```bash
> /clear
```

Delete all sessions:

```bash
> /purge
⚠ This will delete ALL 5 saved sessions.
Continue? (y/n): y
✓ Deleted 5 sessions
```

## Execution Modes

### Default Mode

Shows completion summary with timing:

```bash
$ agent -p "say hello"
✓ Complete (2.0s) - msg:1 tool:1

Hello, World!
```

### Verbose Mode

Shows full execution tree:

```bash
$ agent -p "say hello to Alice" --verbose

• Phase 1: hello_world (6.1s)
├── • Thinking (1 messages) - Response received (6.2s)
└── • → hello_world (Alice) - Complete (0.0s)

Hello, Alice!
```

### Quiet Mode

Response only, no metadata:

```bash
$ agent -p "say hello" --quiet
Hello, World!
```

## Building Custom Tools

Agent Template uses class-based toolsets for extensibility.

### Create a Toolset

```python
from agent.tools.toolset import AgentToolset
from typing import Annotated
from pydantic import Field

class MyTools(AgentToolset):
    """Custom tool implementation."""

    def get_tools(self):
        return [self.my_tool]

    async def my_tool(
        self,
        arg: Annotated[str, Field(description="Input parameter")]
    ) -> dict:
        """Tool description for LLM."""
        try:
            result = self._do_work(arg)
            return self._create_success_response(
                result=result,
                message="Success"
            )
        except Exception as e:
            return self._create_error_response(
                error="execution_failed",
                message=str(e)
            )
```

### Register Custom Tools

```python
from agent import Agent, AgentConfig
from mytools import MyTools

config = AgentConfig.from_env()
agent = Agent(
    config=config,
    toolsets=[HelloTools(config), MyTools(config)]
)
```

See [docs/design/architecture.md](docs/design/architecture.md) for detailed patterns.

## Configuration

Environment variables are loaded from `.env`:

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_PROVIDER` | Provider selection | `openai`, `anthropic`, `azure`, `azure_ai_foundry` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `OPENAI_MODEL` | Model name | `gpt-5-mini` |
| `ANTHROPIC_API_KEY` | Anthropic API key | `sk-ant-...` |
| `ANTHROPIC_MODEL` | Model name | `claude-sonnet-4-5-20250929` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | `https://...openai.azure.com/` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Deployment name | `gpt-5-codex` |
| `AZURE_OPENAI_API_KEY` | Azure API key (optional with `az login`) | `your-key` |
| `AZURE_PROJECT_ENDPOINT` | Azure AI Foundry endpoint | `https://...services.ai.azure.com/...` |
| `AZURE_MODEL_DEPLOYMENT` | Foundry deployment | `gpt-4o` |
| `AGENT_DATA_DIR` | Session storage location | `~/.agent` |
| `LOG_LEVEL` | Logging verbosity | `info`, `debug`, `warning`, `error` |

See [.env.example](.env.example) for complete options.

## Examples

### Basic Greetings

```bash
# Default greeting
$ agent -p "say hello"
Hello, World!

# With custom name
$ agent -p "say hello to Bob"
Hello, Bob!

# Multi-language
$ agent -p "greet Alice in Spanish"
¡Hola, Alice!

$ agent -p "greet Pierre in French"
Bonjour, Pierre!
```

### Verbose Execution

```bash
$ agent -p "say hello to Alice" --verbose

• Phase 1: hello_world (6.1s)
├── • Thinking (1 messages) - Response received (6.2s)
└── • → hello_world (Alice) - Complete (0.0s)

Hello, Alice!
```

### Session Resume

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
```

## Troubleshooting

### Configuration Validation

Check configuration and dependencies:

```bash
$ agent --check
✓ Python version: 3.12.0
✓ LLM Provider: openai
✓ API Key: Set
✓ All dependencies installed
```

Common issues:

1. **"Configuration validation failed"**
   - Verify `.env` file exists
   - Check `LLM_PROVIDER` value
   - Confirm API keys are set

2. **"Unknown LLM provider"**
   - Valid providers: `openai`, `anthropic`, `azure`, `azure_ai_foundry`

### Azure Authentication

For Azure providers, authenticate via CLI:

```bash
az login
```

Verify endpoint configuration in `.env`:

```bash
AZURE_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-id
AZURE_MODEL_DEPLOYMENT=gpt-4o
```

### Debug Mode

Enable verbose logging:

```bash
LOG_LEVEL=debug agent -p "your prompt"
```
