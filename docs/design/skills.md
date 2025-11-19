## Skill Development Guide

This guide explains how to create custom skills for agent-base.

## Table of Contents

- [Overview](#overview)
- [Skill Structure](#skill-structure)
- [SKILL.md Manifest](#skillmd-manifest)
- [Toolsets vs Scripts](#toolsets-vs-scripts)
- [Creating a Python Toolset](#creating-a-python-toolset)
- [Creating a PEP 723 Script](#creating-a-pep-723-script)
- [Testing Your Skill](#testing-your-skill)
- [Best Practices](#best-practices)

## Overview

Skills extend agent-base with domain-specific capabilities while maintaining minimal context overhead through **progressive disclosure**.

**Key Principle**: Don't load code into context unless it's actually being used.

## Skill Structure

Minimal skill structure:

```
my-skill/
├── SKILL.md              # Required: Manifest with YAML front matter
├── toolsets/             # Optional: Python toolset classes
│   ├── __init__.py
│   └── mytools.py
└── scripts/              # Optional: PEP 723 standalone scripts
    ├── status.py
    └── process.py
```

You can have:
- **Toolsets only** (like a traditional Python package)
- **Scripts only** (like kalshi-markets: 10 scripts, no toolsets)
- **Hybrid** (like hello-extended: both patterns)

## SKILL.md Manifest

Every skill must have a `SKILL.md` file with YAML front matter:

```yaml
---
name: my-skill
description: Brief description of what this skill does (max 500 chars)
version: 1.0.0
author: Your Name
repository: https://github.com/yourusername/my-skill
toolsets:
  - toolsets.mytools:MyToolset
scripts_ignore:
  - "*_test.py"
  - "_*.py"
---

# My Skill

Usage instructions in markdown format...

## When to Use

- Use case 1
- Use case 2

## Available Tools

### Toolset Methods
- `my_tool()` - Does something useful

### Scripts
- `scripts/status.py` - Check status
```

### Required Fields

- **name**: Alphanumeric + hyphens/underscores, 1-64 chars
- **description**: What the skill does (1-500 chars)

### Optional Fields

- **version**: Semantic version (e.g., "1.0.0")
- **author**: Author name
- **repository**: Git repository URL
- **license**: License identifier (e.g., "MIT")
- **toolsets**: List of Python classes in "module:Class" format
- **scripts**: Explicit script list (auto-discovered if omitted)
- **scripts_ignore**: Glob patterns to exclude (e.g., "*_test.py")

### Name Normalization

Skill names are **case-insensitive** with **hyphen/underscore equivalence**:

- `Kalshi-Markets` == `kalshi-markets` == `kalshi_markets`
- All normalize to canonical form: `kalshi-markets` (lowercase, hyphens)

## Toolsets vs Scripts

### Use Python Toolsets When:

- ✅ Frequently used operations
- ✅ Need testing and type safety
- ✅ Tools share state or configuration
- ✅ IDE autocomplete is valuable
- ✅ Context overhead is acceptable (<1K tokens)

Example: hello-extended toolset with `greet_in_language()`

### Use Standalone Scripts When:

- ✅ Infrequent or context-heavy operations
- ✅ Complex logic that would bloat context
- ✅ Self-contained operations (no shared state)
- ✅ Progressive disclosure is critical
- ✅ Want zero context until execution

Example: kalshi-markets scripts (10 scripts, <500 token overhead)

### Hybrid Approach (Best of Both Worlds)

Combine both patterns in one skill:
- Toolsets for common operations → Fast, type-safe
- Scripts for rare operations → Zero context overhead

Example: hello-extended skill

## Creating a Python Toolset

1. **Create toolset file**: `toolsets/mytools.py`

```python
from typing import Annotated
from pydantic import Field
from agent.tools.toolset import AgentToolset

class MyToolset(AgentToolset):
    """My custom toolset."""

    def get_tools(self) -> list:
        """Return list of tool functions."""
        return [self.my_tool]

    async def my_tool(
        self,
        input: Annotated[str, Field(description="Input parameter")],
    ) -> dict:
        """Tool description for the LLM.

        Args:
            input: Parameter description

        Returns:
            Structured response dict
        """
        # Implementation
        result = f"Processed: {input}"

        return self._create_success_response(
            result=result,
            message="Tool executed successfully"
        )
```

2. **Register in SKILL.md**:

```yaml
---
name: my-skill
description: My custom skill
toolsets:
  - toolsets.mytools:MyToolset
---
```

3. **Test it**:

```bash
export AGENT_SKILLS="my-skill"
agent -p "Use my_tool to process 'hello'"
```

## Creating a PEP 723 Script

1. **Create script file**: `scripts/status.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx>=0.27.0",
#     "click>=8.1.0",
# ]
# ///
"""Status check script.

This script is self-contained with embedded dependencies (PEP 723).
Not loaded into context - executed only when needed.
"""

import json
import click
import httpx


@click.command()
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
def main(json_output: bool):
    """Check system status.

    Examples:
        $ status.py
        $ status.py --json
    """
    status = check_status()

    if json_output:
        # CRITICAL: When --json is set, emit ONLY valid JSON to stdout
        # No print statements, no banners, no extra text
        click.echo(json.dumps(status, indent=2))
    else:
        # Human-readable format
        click.echo(f"Status: {status['status']}")
        click.echo(f"Timestamp: {status['timestamp']}")


def check_status() -> dict:
    """Check status and return data."""
    return {
        "status": "operational",
        "timestamp": "2025-01-01T00:00:00Z"
    }


if __name__ == "__main__":
    main()
```

2. **Key Script Conventions**:

- ✅ Must support `--help` flag
- ✅ Should support `--json` flag for structured output
- ✅ When `--json`: Emit ONLY valid JSON to stdout (no banners)
- ✅ Use stderr for logs/warnings
- ✅ Exit code 0 for success, non-zero for errors
- ✅ UTF-8 encoding for stdout/stderr
- ✅ PEP 723 for dependencies

3. **Test it**:

```bash
# Direct execution
uv run skills/core/my-skill/scripts/status.py --help
uv run skills/core/my-skill/scripts/status.py --json

# Via agent
export AGENT_SKILLS="my-skill"
agent -p "Use script_help to learn about my-skill status script"
agent -p "Use script_run to check status"
```

## Testing Your Skill

### Manual Installation (Phase 1)

```bash
# Copy to bundled skills directory
cp -r my-skill/ skills/core/

# Enable and test
export AGENT_SKILLS="my-skill"
agent --check  # Verify skill loads

# Test toolset
agent -p "Use my_tool with input 'test'"

# Test script
agent -p "Use script_list to see my-skill scripts"
agent -p "Use script_help for my-skill status script"
agent -p "Use script_run to execute status"
```

### Unit Testing

Create tests for your toolsets:

```python
# tests/unit/skills/test_my_skill.py
import pytest
from my_skill.toolsets.mytools import MyToolset
from unittest.mock import Mock

@pytest.mark.asyncio
async def test_my_tool():
    config = Mock()
    toolset = MyToolset(config)
    result = await toolset.my_tool("test input")

    assert result["success"] is True
    assert "test input" in result["result"]
```

## Best Practices

### Naming

- **Skill names**: `my-skill-name` (lowercase, hyphens)
- **Script names**: `status.py` (lowercase, .py extension)
- **Tool names**: Prefix with context to avoid collisions (e.g., `kalshi_search` not `search`)

### Progressive Disclosure

Follow the kalshi-markets pattern:
1. Don't read scripts unless absolutely needed
2. Use `script_help` first to understand options
3. Then execute with `script_run`
4. Keep SKILL.md instructions concise

### Context Efficiency

Target <5K tokens overhead for the entire skill system:
- Keep SKILL.md concise (<500 lines)
- Use scripts for complex operations
- Only use toolsets for frequent, simple operations

### Security

- ✅ No path traversal in skill names
- ✅ No symbolic links in scripts/ directory
- ✅ Validate all user inputs in tools
- ✅ Use subprocess safely (shell=False)

### Error Handling

Always return structured responses:

```python
# Success
return self._create_success_response(
    result=data,
    message="Operation completed"
)

# Error
return self._create_error_response(
    error="not_found",
    message="Resource not found"
)
```

## Publishing Your Skill

Phase 2 will support git-based installation:

```bash
# Install from git
agent skill add https://github.com/yourusername/my-skill

# Update
agent skill update my-skill

# Remove
agent skill remove my-skill
```

For now, share as git repository and users can manually copy to `skills/core/`.

## Examples

Study the bundled skills:

1. **kalshi-markets** - Pure script-based skill
   - 10 standalone scripts
   - Zero toolsets
   - Perfect progressive disclosure

2. **hello-extended** - Hybrid skill
   - Python toolset for common operations
   - Script for complex operations
   - Shows both patterns

## Troubleshooting

### Skill not loading

```bash
# Check AGENT_SKILLS is set
echo $AGENT_SKILLS

# Verify SKILL.md has valid YAML
cat skills/core/my-skill/SKILL.md

# Check agent logs
agent --check
```

### Script execution fails

```bash
# Test script directly
uv run skills/core/my-skill/scripts/status.py --help

# Check script has PEP 723 dependencies block
head -10 skills/core/my-skill/scripts/status.py
```

### Toolset import fails

```bash
# Verify module:Class format in SKILL.md
# Ensure file path matches: toolsets.hello → toolsets/hello.py
# Check class inherits from AgentToolset
```

## Next Steps

1. Create your skill following this guide
2. Test manually in `skills/core/`
3. Share on GitHub
4. (Phase 2) Enable git installation
