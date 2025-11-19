# Feature: Web Access Skill

## Feature Description

Create a new skill for agent-base that enables web access capabilities through two primary functions:
1. **Web Search** - Search the internet using the Brave Search API
2. **Web Fetch** - Retrieve and parse web page content from URLs

The skill will use a hybrid architecture combining Python toolsets for simple fetch operations with PEP 723 scripts for complex search operations with caching. This follows the progressive disclosure pattern to maintain minimal context overhead (<5K tokens).

## User Story

**As a** conversational AI agent user
**I want to** search the internet and retrieve web content
**So that** I can access real-time information, current events, and online resources beyond the agent's knowledge cutoff

## Problem Statement

The agent-base currently lacks internet access capabilities, limiting its usefulness for:
- Finding current information about recent events
- Accessing documentation from URLs
- Searching for specific online resources
- Gathering data from web sources
- Verifying facts with current information

Users need a reliable, efficient way to extend the agent with web access without bloating the core codebase or context window.

## Solution Statement

Implement a `web-access` skill using the established skills architecture with:

**Script-based architecture** (fully self-contained):
- PEP 723 standalone scripts - no core project dependencies
- Progressive disclosure pattern - not loaded until executed
- Each script manages its own dependencies via PEP 723

**For Web Fetch**:
- `fetch.py` script using `httpx` for HTTP requests
- Supports HTML-to-markdown conversion using `beautifulsoup4` and `markdownify`
- Configurable timeout and size limits

**For Web Search**:
- `search.py` script using Brave Search API
- Direct API calls (no caching to avoid disk writes)
- Supports multiple result formats via `--json` flag

## Related Documentation

### Requirements
- [docs/design/skills.md](../design/skills.md) - Complete skill development guide

### Architecture Decisions
- [ADR-0006: Class-Based Toolset Architecture](../decisions/0006-class-based-toolset-architecture.md) - Toolset design patterns
- [ADR-0007: Tool Response Format](../decisions/0007-tool-response-format.md) - Standard response structure
- [ADR-0008: Testing Strategy](../decisions/0008-testing-strategy-and-coverage-targets.md) - Testing requirements

## Codebase Analysis Findings

Based on comprehensive analysis of the agent-base codebase:

### Architecture Patterns
- **Skill Structure**: `skills/core/{skill-name}/` with SKILL.md manifest
- **Toolset Pattern**: Inherit from `AgentToolset`, implement `get_tools()`, use Pydantic Field annotations
- **Script Pattern**: PEP 723 self-contained scripts in `scripts/` directory
- **Loading**: Dynamic import via `src/agent/skills/loader.py` using importlib

### Naming Conventions
- Skill names: lowercase with hyphens (`web-access`)
- Tool functions: prefixed with context (`web_search`, `web_fetch`)
- Script files: lowercase with `.py` extension (`search.py`, `fetch.py`)
- Class names: PascalCase (`WebAccessToolset`)

### Similar Implementations
**kalshi-markets skill** (scripts/search.py:61-197):
- Implements caching with TTL (6 hours)
- Uses pandas DataFrame for fast searches
- HTTP client with httpx
- Supports `--json` flag for structured output

**hello-extended skill** (toolsets/hello.py):
- Demonstrates toolset pattern with Pydantic annotations
- Standard response format using `_create_success_response()` and `_create_error_response()`
- Async method signatures with type hints

### Integration Patterns
- Toolsets expose methods via `get_tools()` list
- Scripts accessed via wrapper tools: `script_list`, `script_help`, `script_run`
- SKILL.md instructions injected into system prompt
- Environment variables for configuration (e.g., `BRAVE_API_KEY`)

## Archon Project

**Project ID**: `72923090-8d99-49ee-b482-ad5fb168f92b`

## Relevant Files

### Existing Files (Reference)
- `skills/core/kalshi-markets/scripts/search.py` - Caching pattern reference
- `skills/core/kalshi-markets/scripts/status.py` - HTTP client pattern
- `skills/core/hello-extended/toolsets/hello.py` - Toolset pattern reference
- `skills/core/hello-extended/SKILL.md` - Hybrid skill manifest example
- `src/agent/skills/loader.py` - Skill loading mechanism
- `src/agent/tools/toolset.py` - Base AgentToolset class

### New Files
- `skills/core/web-access/SKILL.md` - Skill manifest and instructions
- `skills/core/web-access/scripts/fetch.py` - Web fetch script (HTML → markdown)
- `skills/core/web-access/scripts/search.py` - Brave Search script (stateless)
- `.env.example` - Add BRAVE_API_KEY documentation

## Implementation Status

✅ **Completed** - All phases implemented as script-based skill

### Phase 1: Foundation ✅
1. ✅ Created skill directory structure
2. ✅ Added environment variable configuration
3. ✅ Set up error handling patterns
4. ✅ Created SKILL.md manifest

### Phase 2: Web Fetch Script ✅
1. ✅ Implemented fetch.py as PEP 723 script
2. ✅ Added HTML parsing and markdown conversion
3. ✅ Implemented response formatting
4. ✅ Added URL validation and error handling

### Phase 3: Web Search Script ✅
1. ✅ Created PEP 723 search.py script
2. ✅ Implemented Brave Search API integration
3. ✅ Direct API calls (no disk caching)
4. ✅ Support for `--json` flag

### Phase 4: Testing & Documentation ✅
1. ✅ Integration testing validated (no unit tests - skills are portable)
2. ✅ Script execution tested successfully
3. ✅ Integration testing with agent confirmed
4. ✅ Documentation updated

## Step by Step Tasks

### Task 1: Create Skill Directory Structure
- Description: Set up the web-access skill directory with required files
- Files to create:
  - `skills/core/web-access/`
  - `skills/core/web-access/toolsets/__init__.py`
  - `skills/core/web-access/scripts/`
- Archon task: Will be created during implementation

### Task 2: Create SKILL.md Manifest
- Description: Write the skill manifest with YAML front matter and usage instructions
- Files to create:
  - `skills/core/web-access/SKILL.md`
- Requirements:
  - Define name, description, version
  - Register WebAccessToolset
  - Provide clear usage instructions
  - Include triggers and quick guide
- Archon task: Will be created during implementation

### Task 3: Implement WebAccessToolset Class
- Description: Create Python toolset for web_fetch functionality
- Files to create:
  - `skills/core/web-access/toolsets/web.py`
- Implementation details:
  - Inherit from AgentToolset
  - Implement `get_tools()` method
  - Add async `web_fetch(url: str)` method
  - Use httpx for HTTP requests
  - Support timeout configuration
  - Implement HTML to markdown conversion
  - Add comprehensive error handling
- Archon task: Will be created during implementation

### Task 4: Implement Brave Search Script
- Description: Create standalone PEP 723 script for web search with caching
- Files to create:
  - `skills/core/web-access/scripts/search.py`
- Implementation details:
  - PEP 723 dependency block (httpx, click, pandas)
  - Brave Search API integration
  - Local caching mechanism (6 hour TTL)
  - Support for --query, --count, --json flags
  - Environment variable for BRAVE_API_KEY
  - Error handling for API failures
  - Progressive disclosure pattern
- Reference: `skills/core/kalshi-markets/scripts/search.py` for caching pattern
- Archon task: Will be created during implementation

### Task 5: Add Environment Configuration
- Description: Document required environment variables
- Files to modify:
  - `.env.example`
- Add variables:
  ```bash
  # Brave Search API (required for web-access skill)
  BRAVE_API_KEY=your-brave-api-key-here

  # Web Fetch Configuration (optional)
  WEB_FETCH_TIMEOUT=30  # seconds
  WEB_FETCH_MAX_SIZE=1048576  # 1MB
  ```
- Archon task: Will be created during implementation

### Task 6: Write Unit Tests
- Description: Create comprehensive unit tests for WebAccessToolset
- Files to create:
  - `tests/unit/skills/test_web_access.py`
- Test coverage:
  - Test successful web_fetch
  - Test timeout handling
  - Test invalid URL handling
  - Test HTTP error handling
  - Test HTML parsing
  - Mock httpx responses
- Archon task: Will be created during implementation

### Task 7: Update pyproject.toml Dependencies
- Description: Add required dependencies for web access functionality
- Files to modify:
  - `pyproject.toml`
- Dependencies to add:
  ```toml
  "httpx>=0.27.0",           # HTTP client
  "beautifulsoup4>=4.12.0",  # HTML parsing
  "markdownify>=0.11.0",     # HTML to Markdown conversion
  ```
- Archon task: Will be created during implementation

### Task 8: Integration Testing
- Description: Test skill loading and execution with agent
- Test scenarios:
  - Verify skill loads with `agent --check`
  - Test web_fetch with sample URL
  - Test script_help for search script
  - Test script_run for web search
  - Verify caching mechanism
  - Test error scenarios (invalid URL, API key missing, timeout)
- Commands to run:
  ```bash
  export AGENT_SKILLS="web-access"
  export BRAVE_API_KEY="test-key"
  agent --check
  agent -p "Use web_fetch to get https://example.com"
  agent -p "Use script_help for web-access search"
  agent -p "Use script_run to search for 'anthropic'"
  ```
- Archon task: Will be created during implementation

### Task 9: Documentation Updates
- Description: Update project documentation to include web-access skill
- Files to modify:
  - `README.md` - Add to bundled skills list
  - `docs/SKILLS.md` - Add as example skill
- Documentation should include:
  - Skill description and capabilities
  - Environment variable requirements
  - Usage examples
  - Brave API key setup instructions
- Archon task: Will be created during implementation

## Testing Strategy

### Unit Tests

**Toolset Tests** (`tests/unit/skills/test_web_access.py`):
```python
@pytest.mark.asyncio
async def test_web_fetch_success(mock_config):
    """Should fetch and parse content successfully."""

@pytest.mark.asyncio
async def test_web_fetch_timeout(mock_config):
    """Should handle timeout gracefully."""

@pytest.mark.asyncio
async def test_web_fetch_invalid_url(mock_config):
    """Should reject invalid URLs."""

@pytest.mark.asyncio
async def test_web_fetch_http_error(mock_config):
    """Should handle HTTP errors."""
```

**Script Tests** (Direct execution):
```bash
# Test help output
uv run skills/core/web-access/scripts/search.py --help

# Test search without API key (should error)
uv run skills/core/web-access/scripts/search.py --query "test" --json

# Test search with API key
export BRAVE_API_KEY="test-key"
uv run skills/core/web-access/scripts/search.py --query "anthropic" --json
```

### Integration Tests

**Via Agent**:
```bash
export AGENT_SKILLS="web-access"
export BRAVE_API_KEY="your-key"

# Test skill loading
agent --check

# Test web_fetch
agent -p "Fetch the content from https://www.anthropic.com"

# Test search discovery
agent -p "Use script_list to see web-access scripts"

# Test search help
agent -p "Use script_help for web-access search"

# Test search execution
agent -p "Search the web for information about Claude Code"
```

### Edge Cases

1. **Missing API Key**
   - Search script should fail gracefully with clear error message
   - Web fetch should work independently (no API key needed)

2. **Invalid URLs**
   - Non-HTTP/HTTPS URLs should be rejected
   - Malformed URLs should return error response

3. **Timeout Scenarios**
   - Slow servers should timeout after configured duration
   - Timeout should return structured error response

4. **Large Responses**
   - HTML content exceeding max size should be truncated
   - Clear warning in response message

5. **Caching Behavior**
   - First search builds cache (2-5 minutes)
   - Subsequent searches are instant
   - Cache expires after 6 hours
   - Force rebuild with --rebuild-cache flag

6. **API Rate Limits**
   - Brave API errors should be caught and reported
   - Caching reduces API calls to once per 6 hours

## Acceptance Criteria

- [x] Skill directory structure created with all required files
- [x] SKILL.md manifest is valid and complete
- [x] fetch.py validates URLs and handles errors gracefully
- [x] fetch.py supports timeout configuration via environment variable
- [x] HTML content is converted to clean markdown
- [x] Search script uses Brave Search API successfully
- [x] Search script is stateless (no disk caching)
- [x] Search script supports --query, --count, and --json flags
- [x] Search script validates BRAVE_API_KEY environment variable
- [x] Scripts are self-contained with PEP 723 dependencies (no core bloat)
- [x] All existing tests pass (865/871 - only LLM integration failures)
- [x] Scripts execute directly via `uv run`
- [x] Skill loads successfully with `AGENT_SKILLS="web-access"`
- [x] Agent can discover and execute scripts via script_run
- [x] Agent can use natural language ("Search for X", "Fetch URL")
- [x] README.md updated with web-access skill information
- [x] .env.example documents required environment variables
- [x] Error messages are clear and actionable
- [x] Response format follows ADR-0007 standard
- [x] Documentation consolidated to docs/design/skills.md

## Validation Commands

```bash
# Install dependencies
cd /Users/danielscholl/source/github/danielscholl/agent-base
uv sync

# Run unit tests
uv run pytest tests/unit/skills/test_web_access.py -v

# Run all tests to ensure no regressions
uv run pytest

# Test script directly
export BRAVE_API_KEY="your-key-here"
uv run skills/core/web-access/scripts/search.py --help
uv run skills/core/web-access/scripts/search.py --query "anthropic" --count 5 --json

# Test with agent
export AGENT_SKILLS="web-access"
export BRAVE_API_KEY="your-key-here"
agent --check
agent -p "Fetch https://www.anthropic.com and summarize the content"
agent -p "Search the web for information about Claude AI and show top 5 results"

# Verify caching behavior
agent -p "Search for 'python' (should build cache on first run)"
agent -p "Search for 'javascript' (should use cache, instant results)"

# Test error handling
unset BRAVE_API_KEY
agent -p "Search for 'test' (should fail with clear error about missing API key)"

# Code quality checks
uv run ruff check skills/core/web-access/
uv run mypy skills/core/web-access/toolsets/
```

## Notes

### Dependencies
**Toolset** (added to pyproject.toml):
- httpx >= 0.27.0 - Modern async HTTP client
- beautifulsoup4 >= 4.12.0 - HTML parsing
- markdownify >= 0.11.0 - HTML to Markdown conversion

**Scripts** (PEP 723 inline):
- httpx - HTTP client for API calls
- click - CLI interface
- pandas - DataFrame for caching and fast search

### Configuration
The skill requires minimal configuration:
- `BRAVE_API_KEY` - Required for web search functionality
- `WEB_FETCH_TIMEOUT` - Optional (default: 30 seconds)
- `WEB_FETCH_MAX_SIZE` - Optional (default: 1MB)

### Security Considerations
- URL validation prevents SSRF attacks
- Timeout prevents hanging on slow servers
- Size limits prevent memory exhaustion
- API key stored in environment (not code)
- No execution of downloaded content
- HTML sanitization via beautifulsoup4

### Performance Optimization
- **Caching**: Search results cached locally for 6 hours
- **Progressive Disclosure**: Search script not loaded until executed
- **Context Efficiency**: Total skill overhead <2K tokens
- **Async Operations**: web_fetch uses async httpx for better performance

### Brave API Details
Based on Brave Search API documentation:
- **Endpoint**: `https://api.search.brave.com/res/v1/web/search`
- **Authentication**: `X-Subscription-Token` header
- **Free Tier**: Available with registration (no charge)
- **Rate Limits**: Varies by subscription level
- **Response Format**: JSON with web results, descriptions, metadata

### Future Enhancements (Post-Implementation)
1. Add image search support
2. Implement result filtering (by date, domain, etc.)
3. Support for custom search parameters (country, safesearch)
4. PDF content extraction for web_fetch
5. Automatic retry with exponential backoff
6. Cache statistics and management commands
7. Support for proxy configuration
8. Browser automation for JavaScript-heavy sites (playwright/selenium)

## Execution

This spec can be implemented using: `/sdlc:implement docs/specs/web-access-skill.md`

---

**Specification Version**: 1.0
**Created**: 2025-11-19
**Archon Project**: 72923090-8d99-49ee-b482-ad5fb168f92b
**Status**: Ready for Implementation
