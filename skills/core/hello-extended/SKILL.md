---
name: hello-extended
description: Extended hello skill demonstrating both Python toolsets and standalone scripts for greeting capabilities.
version: 1.0.0
author: agent-base
toolsets:
  - toolsets.hello:HelloExtended
scripts_ignore:
  - "*_test.py"
  - "_*.py"
---

# Hello Extended

Example skill demonstrating the hybrid approach: structured Python toolsets for
frequently-used operations AND standalone PEP 723 scripts for context-heavy operations.

## When to Use This Skill

Use when you need:
- Multi-language greeting generation (toolset)
- Time-aware personalized greetings (script)
- Advanced greeting formatting (script)

## Python Toolsets

### HelloExtended Toolset
Provides structured, testable greeting methods:
- `greet_in_language()` - Generate greetings in different languages
- `greet_multiple()` - Generate multiple greetings at once

Access these through normal tool calls (loaded into agent context).

## Standalone Scripts

### `scripts/advanced_greeting.py`
Context-heavy greeting script with complex formatting options.
Use `--help` to see all options, then `--json` for structured output.

**Progressive disclosure**: This script is NOT loaded until you execute it.

## Usage Pattern

1. For simple, frequent greetings → Use HelloExtended toolset methods
2. For complex, rare greetings → Use `script_help` then `script_run` on advanced_greeting.py

This hybrid approach balances developer experience (toolsets) with LLM efficiency (scripts).
