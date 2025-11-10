# Testing Guide

Test organization and workflows for agent-base.

## Test Types

| Type | Purpose | Speed |
|------|---------|-------|
| **Unit** | Isolated component testing | Fast |
| **Integration** | Component interaction (mocked LLM) | Fast |
| **Validation** | CLI subprocess tests | Moderate |
| **LLM** | Real AI behavior (requires API key) | Slow |

Only LLM tests make API calls. All others are free to run.

## Quick Start

```bash
# Run all tests (excludes LLM)
uv run pytest -m "not llm" -n auto
# ~220 tests in 4 seconds

# Run ALL tests including LLM (requires API key)
uv run pytest -n auto
# ~242 tests in 30 seconds
```

**Note:** Use `uv run pytest` (not `pytest`) to ensure correct environment. Use `-n auto` for parallel execution.

### Common Workflows

```bash
# Fast feedback during development
uv run pytest -m unit -n auto

# Before committing (CI equivalent)
uv run pytest -m "not llm" -n auto --cov=src/agent --cov-fail-under=85

# Specific feature area
uv run pytest -m tools
uv run pytest -m middleware

# Real LLM tests (requires OPENAI_API_KEY)
uv run pytest -m llm
```

## Test Organization

```
tests/
├── unit/                      # Fast, isolated tests
│   ├── core/                  # Agent, config, events
│   ├── tools/                 # Tool implementations
│   ├── cli/                   # CLI interface
│   ├── middleware/            # Middleware
│   ├── display/               # Display system
│   ├── persistence/           # Session management
│   └── memory/                # Memory components
├── integration/               # Component interaction (mocked LLM)
│   └── llm/                   # Real LLM tests (requires API key)
├── validation/                # CLI subprocess tests
├── fixtures/                  # Shared test fixtures
├── helpers/                   # Test utilities
├── templates/                 # Templates for new tests
└── mocks/                     # Mock implementations
```

## Writing Tests

Use templates from `tests/templates/`:

```bash
# New tool
cp tests/templates/test_tool_template.py tests/unit/tools/test_my_tool.py

# Integration test
cp tests/templates/test_integration_template.py tests/integration/test_my_feature.py

# LLM test
cp tests/templates/test_llm_template.py tests/integration/llm/test_my_llm.py
```

Add appropriate markers:

```python
import pytest
from tests.helpers import assert_success_response

@pytest.mark.unit          # or integration, validation, llm
@pytest.mark.tools         # feature area
async def test_my_function(tool_config):
    tool = MyTool(tool_config)
    result = await tool.my_function("input")
    assert_success_response(result)
```

## Markers

Run specific test categories:

```bash
# By test type
uv run pytest -m unit
uv run pytest -m integration

# By feature area
uv run pytest -m tools
uv run pytest -m middleware

# Combine with AND
uv run pytest -m "unit and tools"

# Exclude with NOT
uv run pytest -m "not llm"
```

Available markers:
- **Type:** `unit`, `integration`, `validation`, `llm`
- **Area:** `tools`, `middleware`, `display`, `cli`, `agent`, `config`, `events`, `persistence`, `memory`
- **Provider:** `requires_openai`, `requires_anthropic`, `requires_azure`

## Test Utilities

**Fixtures** (`tests/fixtures/`):
- `mock_config` - Test configuration
- `mock_chat_client` - Mocked LLM client
- `agent_instance` - Pre-configured agent

**Helpers** (`tests/helpers/`):
- `assert_success_response(result)` - Validate success format
- `assert_error_response(result, "code")` - Validate error format
- `build_test_config(provider)` - Create test configs

See `tests/fixtures/` and `tests/helpers/` for details.

## Coverage

Minimum 85% coverage required (CI enforced).

```bash
uv run pytest --cov=src/agent --cov-report=html
open htmlcov/index.html
```

**Excluded from coverage:** CLI orchestration, display rendering, error definitions

## CI Pipeline

CI runs free tests only:

```bash
pytest -m "not llm" --cov=src/agent --cov-fail-under=85
```

Quality gates: Black, Ruff, MyPy, PyTest (85% coverage)

## See Also

- `tests/integration/llm/README.md` - LLM testing guide
- `tests/templates/` - Test templates
- `CONTRIBUTING.md` - Development guidelines
