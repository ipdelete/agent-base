# Skills Development Guide

Complete guide for creating, optimizing, and using skills in agent-base.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Skill Structure](#skill-structure)
- [SKILL.md Manifest](#skillmd-manifest)
- [Self-Contained Skills](#self-contained-skills)
- [Creating Scripts](#creating-scripts)
- [Optimization for Speed](#optimization-for-speed)
- [Testing](#testing)
- [Best Practices](#best-practices)
- [Examples](#examples)

---

## Overview

Skills extend agent-base with domain-specific capabilities while maintaining minimal context overhead through **progressive disclosure**.

### Key Principle
**Don't load code into context unless it's actually being used.**

Skills are self-contained, git-based packages that:
- Load on-demand via `AGENT_SKILLS` environment variable
- Use PEP 723 for dependency management (no core project bloat)
- Support natural language invocation
- Maintain <5K token overhead per skill

---

## Quick Start

### Create a New Skill

```bash
# 1. Create directory structure
mkdir -p skills/core/my-skill/scripts

# 2. Create SKILL.md manifest
cat > skills/core/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: Brief description with trigger keywords
---

# my-skill

## 🎯 Triggers
**When user wants to:**
- Do thing 1
- Do thing 2

## Scripts

### my-script
**What:** Does something useful
**Pattern:** User wants X → `script_run my-skill my-script --arg "VALUE" --json`
**Example:** "Do X" → `script_run my-skill my-script --arg "X" --json`
EOF

# 3. Create PEP 723 script
cat > skills/core/my-skill/scripts/my-script.py << 'EOF'
#!/usr/bin/env python3
# /// script
# dependencies = [
#     "click",
# ]
# ///

import click
import json

@click.command()
@click.option("--arg", required=True)
@click.option("--json", "output_json", is_flag=True)
def main(arg: str, output_json: bool):
    result = {"success": True, "result": f"Processed: {arg}"}

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"Result: {result['result']}")

if __name__ == "__main__":
    main()
EOF

chmod +x skills/core/my-skill/scripts/my-script.py

# 4. Test it
export AGENT_SKILLS="my-skill"
agent -p "Do something with test"
```

---

## Skill Structure

### Recommended: Script-Only (Self-Contained)

```
my-skill/
├── SKILL.md              # Required: Manifest
└── scripts/              # Required: PEP 723 scripts
    ├── main.py          # Each manages own dependencies
    └── helper.py
```

**Benefits:**
- ✅ No core project dependencies
- ✅ Fully portable
- ✅ Easy to extract to separate repo
- ✅ Zero context until execution

### Legacy: Hybrid (Being Deprecated)

```
my-skill/
├── SKILL.md
├── toolsets/            # ⚠️ Requires core dependencies
│   └── tools.py
└── scripts/
    └── advanced.py
```

**Use toolsets only if:**
- Extremely frequent operations (>10x per session)
- Shared state absolutely required
- Willing to add dependencies to core project

**Recommendation:** Use scripts for everything. They're fast enough with `uv run`.

---

## SKILL.md Manifest

### Optimized Template

```markdown
---
name: skill-name
description: One-line description with ALL trigger keywords users might say
---

# skill-name

## 🎯 Triggers
**When user wants to:**
- Natural language intent 1
- Natural language intent 2
- Natural language intent 3

**Skip when:**
- Built-in capability exists
- Out of scope scenario

## Scripts

### script-name
**What:** Brief one-line description
**Pattern:** User phrase → `script_run skill-name script-name --arg "USER_VALUE" --json`
**Example:** "Real user request" → `script_run skill-name script-name --arg "value" --json`

### another-script
**What:** Another capability
**Pattern:** User phrase → `script_run skill-name another-script --flag --json`
**Example:** "Different request" → `script_run skill-name another-script --flag --json`

## Quick Reference
```
User: "Pattern 1"  → script_run skill-name script1 --arg "X" --json
User: "Pattern 2"  → script_run skill-name script2 --json
```

## Requires
- Environment variables (if any)
- External services (if any)
```

### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Lowercase with hyphens, 1-64 chars | `web-access` |
| `description` | One-line with trigger keywords | `Search web and fetch pages` |

### Optional Fields

| Field | Description |
|-------|-------------|
| `version` | Semantic version | `1.0.0` |
| `author` | Creator name | `Your Name` |
| `repository` | Git URL | `https://github.com/user/skill` |
| `toolsets` | ⚠️ Deprecated - use scripts | `toolsets.module:Class` |

### Name Normalization

Skill names are case-insensitive with hyphen/underscore equivalence:
- `My-Skill` == `my-skill` == `my_skill`
- All normalize to: `my-skill` (lowercase, hyphens)

---

## Self-Contained Skills

### PEP 723 Dependencies

Each script manages its own dependencies:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "httpx>=0.27.0",
#     "beautifulsoup4>=4.12.0",
#     "click>=8.1.0",
# ]
# ///
```

**Benefits:**
- ✅ No pyproject.toml changes
- ✅ `uv run` installs automatically
- ✅ Skill is truly portable
- ✅ Dependencies documented in script

**Example: web-access skill**
```
web-access/
├── SKILL.md
└── scripts/
    ├── fetch.py   # deps: httpx, beautifulsoup4, markdownify, click
    └── search.py  # deps: httpx, click, pandas
```

No core project dependencies required!

---

## Creating Scripts

### Script Template

```python
#!/usr/bin/env python3
# /// script
# dependencies = [
#     "click>=8.1.0",
#     "httpx>=0.27.0",  # add what you need
# ]
# ///

"""
Script Description

Brief explanation of what this script does.

Usage:
    uv run script.py --arg "value"
    uv run script.py --arg "value" --json
"""

import json
import click


@click.command()
@click.option("--arg", required=True, help="Argument description")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def main(arg: str, output_json: bool):
    """
    Script functionality description.

    Examples:
        uv run script.py --arg "test"
        uv run script.py --arg "test" --json
    """
    try:
        # Your logic here
        result = process(arg)

        if output_json:
            # CRITICAL: Only JSON output, no other text
            click.echo(json.dumps({
                "success": True,
                "result": result,
                "message": "Processed successfully"
            }, indent=2))
        else:
            # Human-readable output
            click.echo(f"Result: {result}")

    except Exception as e:
        if output_json:
            click.echo(json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2))
        else:
            click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


def process(arg: str) -> str:
    """Business logic."""
    return f"Processed: {arg}"


if __name__ == "__main__":
    main()
```

### Script Conventions

Must have:
- ✅ `--help` flag (click provides automatically)
- ✅ `--json` flag for structured output
- ✅ Valid JSON only when `--json` is set
- ✅ Exit code 0 for success, non-zero for errors
- ✅ PEP 723 dependency block

Should have:
- ✅ Docstring with usage examples
- ✅ Error handling with structured responses
- ✅ Human-readable output when not `--json`

---

## Optimization for Speed

### The Pattern

**System Prompt** teaches HOW skills work (general framework)
**SKILL.md** teaches WHAT this skill does (specific patterns)
**Result:** Agent maps natural language → invocation in one step

### What/Pattern/Example Format

For each script, provide:

```markdown
### script-name
**What:** One-line description
**Pattern:** Natural language → exact command with USER_PLACEHOLDER
**Example:** "Real user phrase" → `script_run skill script --arg "value" --json`
```

**Why this works:**
- Agent sees user intent → matches pattern → substitutes value
- No mental translation needed
- Copy-paste ready with placeholders

### Quick Reference Section

Add common patterns for instant lookup:

```markdown
## Quick Reference
```
User: "Search for X"     → script_run web-access search --query "X" --json
User: "Fetch URL"        → script_run web-access fetch --url "URL" --json
User: "Get status"       → script_run my-skill status --json
```
```

### Natural Language Triggers

Use how users actually talk:

✅ **Good:**
```markdown
**When user wants to:**
- Search the internet
- Get current information
- Fetch a web page
```

❌ **Bad:**
```markdown
**When user wants to:**
- Execute HTTP GET requests
- Perform RESTful API calls
- Initiate web retrieval operations
```

### Token Budget

Target: **<250 tokens per skill**

Distribution:
- YAML description: 50 tokens (pack with keywords)
- Triggers: 40 tokens (natural language)
- Scripts: 120 tokens (What/Pattern/Example)
- Quick Reference: 40 tokens

---

## Testing

### Manual Testing

```bash
# 1. Enable skill
export AGENT_SKILLS="my-skill"

# 2. Verify loading
agent --check

# 3. Test script discovery
agent -p "Use script_list to see my-skill scripts"

# 4. Test script help
agent -p "Use script_help for my-skill my-script"

# 5. Test natural language
agent -p "Do something with test data"  # Should auto-invoke

# 6. Test direct execution
uv run skills/core/my-skill/scripts/my-script.py --help
uv run skills/core/my-skill/scripts/my-script.py --arg "test" --json
```

### Validation Checklist

- [ ] Script has PEP 723 dependencies block
- [ ] Script supports `--help` and `--json`
- [ ] `--json` output is valid JSON (no extra text)
- [ ] SKILL.md has What/Pattern/Example for each script
- [ ] Natural language invocation works without "use script_run"
- [ ] Total SKILL.md is <250 tokens
- [ ] All environment variables documented
- [ ] Script returns exit code 0 on success

---

## Best Practices

### Naming

| Type | Convention | Example |
|------|-----------|---------|
| Skill name | lowercase-with-hyphens | `web-access` |
| Script name | lowercase.py | `search.py` |
| Flags | lowercase-with-hyphens | `--query`, `--count` |

### Security

- ✅ Validate all user inputs
- ✅ No path traversal in names
- ✅ No symbolic links
- ✅ Use subprocess safely (shell=False)
- ✅ Sanitize URLs and file paths

### Error Handling

Always return structured responses:

```json
{
  "success": true,
  "result": "data here",
  "message": "Optional message"
}
```

```json
{
  "success": false,
  "error": "error_code",
  "message": "Human-readable error"
}
```

### Progressive Disclosure

- SKILL.md: Discovery layer (triggers, patterns)
- `script_help`: Detailed options
- `script_run`: Execution

Don't document every parameter in SKILL.md - use `script_help` for details.

### Context Efficiency

- Keep SKILL.md concise (<250 tokens)
- Use scripts for all complex logic
- Always use `--json` for structured output
- Front-load trigger keywords in description

---

## Examples

### Example 1: web-access (Script-Only)

**Structure:**
```
web-access/
├── SKILL.md
└── scripts/
    ├── fetch.py   # PEP 723: httpx, beautifulsoup4, markdownify, click
    └── search.py  # PEP 723: httpx, click, pandas
```

**SKILL.md:**
```markdown
---
name: web-access
description: Search the web and fetch page content
---

# web-access

## 🎯 Triggers
**When user wants to:**
- Search the internet
- Get current/recent information
- Fetch content from a URL

## Scripts

### search
**What:** Search web via Brave API (cached 6hrs)
**Pattern:** User wants to search → `script_run web-access search --query "USER_QUERY" --json`
**Example:** "Search for python" → `script_run web-access search --query "python" --json`

### fetch
**What:** Fetch and convert web page to markdown
**Pattern:** User provides URL → `script_run web-access fetch --url "USER_URL" --json`
**Example:** "Get https://example.com" → `script_run web-access fetch --url "https://example.com" --json`

## Quick Reference
```
User: "Search for X"      → script_run web-access search --query "X" --json
User: "Fetch https://..." → script_run web-access fetch --url "https://..." --json
```

## Requires
- `BRAVE_API_KEY` for search
```

**Why it works:**
- ✅ No core dependencies (100% PEP 723)
- ✅ Natural language works: "Search for X"
- ✅ Clear patterns with examples
- ✅ Self-contained and portable

### Example 2: kalshi-markets (10 Scripts)

**Structure:**
```
kalshi-markets/
├── SKILL.md
└── scripts/
    ├── status.py
    ├── markets.py
    ├── search.py
    ├── get.py
    ├── events.py
    ├── series.py
    ├── orderbook.py
    ├── trades.py
    ├── portfolio.py
    └── history.py
```

**Categorized listing in SKILL.md:**
```markdown
## Scripts

**Status & Discovery:**
- `status.py` - Is Kalshi operational?
- `markets.py` - Browse all markets
- `search.py --query "term"` - Find markets

**Details:**
- `get.py --ticker XXX` - Market details
- `events.py` - List events
- `series.py` - List series

**Trading:**
- `orderbook.py --ticker XXX` - Order book
- `trades.py --ticker XXX` - Trade history
```

**Why it works:**
- ✅ Categorization aids selection
- ✅ Inline argument patterns
- ✅ Progressive disclosure (10 scripts, <300 tokens)

---

## Anti-Patterns

### ❌ Don't: Add Dependencies to Core

```toml
# pyproject.toml
dependencies = [
    "beautifulsoup4",  # ❌ Only needed by one skill!
]
```

Use PEP 723 instead!

### ❌ Don't: Verbose SKILL.md

```markdown
# ❌ BAD (too verbose)
This skill provides comprehensive web access capabilities utilizing
the Brave Search API with built-in caching mechanisms that persist
for 6 hours to optimize performance and reduce API calls...
```

```markdown
# ✅ GOOD (concise)
## 🎯 Triggers
**When user wants to:** search internet, fetch pages, get current info
```

### ❌ Don't: Missing Patterns

```markdown
# ❌ BAD (no pattern)
### search
Searches the web. Flags: --query, --count, --json
```

```markdown
# ✅ GOOD (with pattern)
### search
**Pattern:** User wants to search → `script_run web-access search --query "USER_QUERY" --json`
**Example:** "Search for python" → `script_run web-access search --query "python" --json`
```

### ❌ Don't: Technical Triggers

```markdown
# ❌ BAD
**When user wants to:**
- Execute HTTP GET requests
- Perform RESTful API operations
```

```markdown
# ✅ GOOD
**When user wants to:**
- Fetch a web page
- Search the internet
```

---

## Publishing Skills

### Current: Manual Installation

```bash
# Share as git repository
git clone https://github.com/user/my-skill
cp -r my-skill/ agent-base/skills/core/
```

### Future: Git-Based Installation

```bash
# Phase 2 feature (coming soon)
agent skill add https://github.com/user/my-skill
agent skill update my-skill
agent skill remove my-skill
```

---

## Troubleshooting

### Skill not loading

```bash
# Check environment
echo $AGENT_SKILLS

# Verify YAML is valid
head -10 skills/core/my-skill/SKILL.md

# Check logs
agent --check
```

### Script fails to execute

```bash
# Test directly
uv run skills/core/my-skill/scripts/my-script.py --help

# Check PEP 723 block
head -10 skills/core/my-skill/scripts/my-script.py

# Verify dependencies
uv run skills/core/my-skill/scripts/my-script.py  # uv installs deps
```

### Natural language doesn't work

- Check SKILL.md has Pattern/Example for each script
- Verify triggers match how users actually talk
- Add Quick Reference section for common cases
- Test with exact phrases from examples

---

## Summary

**Best Practices:**
1. ✅ Use PEP 723 scripts (no core dependencies)
2. ✅ Provide What/Pattern/Example for each script
3. ✅ Include Quick Reference for common cases
4. ✅ Use natural language triggers
5. ✅ Keep SKILL.md <250 tokens
6. ✅ Always support `--json` flag
7. ✅ Test with natural language

**Result:** Skills that are fast, portable, and work naturally with user language!
