# Test Infrastructure Guide

Quick guide to testing in agent-template.

## Testing Strategy

We use **4 test types** organized for clarity and efficiency:

| Type | Purpose | Speed | Costs $ |
|------|---------|-------|---------|
| **Unit** | Test code logic in isolation | Fast | No |
| **Integration** | Test components together (mocked LLM) | Fast | No |
| **Validation** | Test CLI commands via subprocess | Moderate | No |
| **LLM** | Test real AI behavior | Slow | Yes |

**Clear separation**: Only LLM integration tests make real API calls. All other tests are free.

## Recommended Commands

⚠️ **Always use `uv run pytest`

```bash
# Fast development workflow (recommended)
uv run pytest -m unit -n auto              # Fast, free

# Before commit (recommended)
uv run pytest -m "not llm" -n auto         # All free tests

# With coverage
uv run pytest --cov=src/agent --cov-fail-under=85

# Real LLM tests (opt-in, costs money)
export OPENAI_API_KEY=sk-...
uv run pytest -m llm
```

## Test Organization

```
tests/
├── unit/                      # Fast, isolated tests
│   ├── core/                  # Agent, config, events
│   ├── tools/                 # Tool implementations
│   ├── display/               # Display system
│   ├── cli/                   # CLI interface
│   ├── middleware/            # Middleware
│   └── persistence/           # Session management
│
├── integration/               # Components working together (mocked LLM)
│   └── llm/                   # Real LLM tests (⚠️ costs money)
│
├── validation/                # CLI subprocess tests
├── fixtures/                  # Shared fixtures
├── helpers/                   # Test utilities
├── templates/                 # Templates for new tests
└── mocks/                     # MockChatClient
```

## Writing New Tests

### Pattern: Use Templates

1. **Adding a new tool?**
   ```bash
   cp tests/templates/test_tool_template.py tests/unit/tools/test_my_tool.py
   # Customize for your tool
   ```

2. **Adding integration tests?**
   ```bash
   cp tests/templates/test_integration_template.py tests/integration/test_my_feature.py
   # Customize for your feature
   ```

3. **Testing with real LLMs?**
   ```bash
   cp tests/templates/test_llm_template.py tests/integration/llm/test_my_llm.py
   # Add @pytest.mark.llm and provider markers
   ```

### Where to Put Tests

| What You're Testing | Where It Goes |
|---------------------|---------------|
| New tool function | `tests/unit/tools/test_<tool>.py` |
| Tool + Agent integration | `tests/integration/test_<feature>.py` |
| CLI command | `tests/validation/agent_validation.yaml` |
| Real LLM behavior | `tests/integration/llm/test_<feature>.py` |
| Middleware | `tests/unit/middleware/test_<feature>.py` |
| Display logic | `tests/unit/display/test_<feature>.py` |

### Test Pattern Example

```python
# tests/unit/tools/test_my_tool.py
import pytest
from agent.tools.my_tool import MyTool
from tests.helpers import assert_success_response

@pytest.mark.unit
@pytest.mark.tools
class TestMyTool:
    @pytest.mark.asyncio
    async def test_my_function(self, tool_config):
        tool = MyTool(tool_config)
        result = await tool.my_function("input")
        assert_success_response(result)
```

## CI/CD

**Default CI runs**:
```bash
pytest -m "not llm" --cov=src/agent --cov-fail-under=85
```

**What this does**:
- Runs unit, integration, and validation tests
- Skips LLM tests (too expensive for every commit)
- Validation prompt tests skip if LLM not configured
- Enforces 85% coverage minimum

**Quality checks** (all must pass):
- Black formatting
- Ruff linting
- MyPy type checking
- PyTest with 85% coverage

## Understanding Markers

**Markers** are pytest labels that let you select which tests to run. Instead of running the entire test suite, you can run just the ones you need.

**Discover available markers**:
```bash
uv run pytest --markers | grep ":" | head -20
```

### Available Markers

| Category | Marker | Use When |
|----------|--------|----------|
| **Test Type** | `unit` | Fast feedback during development |
| | `integration` | Testing components together |
| | `validation` | Testing CLI commands |
| | `llm` | Testing real AI (⚠️ costs $) |
| **Feature Area** | `tools` | Working on tools |
| | `middleware` | Working on middleware |
| | `display` | Working on display |
| | `cli` | Working on CLI |
| | `agent` | Working on core agent |
| | `config` | Working on configuration |
| | `events` | Working on event bus |
| | `persistence` | Working on sessions |
| **Speed** | `fast` | Quick smoke tests |
| | `slow` | Exclude long-running tests |
| **LLM Provider** | `requires_openai` | OpenAI integration tests |
| | `requires_anthropic` | Anthropic integration tests |
| | `requires_azure` | Azure integration tests |

### Common Marker Patterns

```bash
# Run by test type
uv run pytest -m unit                    # All unit tests
uv run pytest -m integration             # All integration tests

# Run by feature area (focus on what you're changing)
uv run pytest -m tools                   # All tool tests
uv run pytest -m middleware              # All middleware tests
uv run pytest -m display                 # All display tests

# Combine markers with AND
uv run pytest -m "unit and tools"        # Unit tests for tools only
uv run pytest -m "integration and tools" # Integration tests for tools

# Exclude markers with NOT
uv run pytest -m "not llm"               # Everything except LLM (CI default)
uv run pytest -m "not llm and not slow"  # Exclude expensive/slow tests
```

## Test Utilities

**Fixtures** (in `tests/fixtures/`):
- `mock_config` - Default test configuration
- `mock_chat_client` - MockChatClient for LLM mocking
- `agent_instance` - Pre-configured agent with mocks

**Helpers** (in `tests/helpers/`):
- `assert_success_response(result)` - Validate success format
- `assert_error_response(result, "error_code")` - Validate error format
- `build_test_config(provider="openai")` - Create test configs

**Example**:
```python
from tests.helpers import assert_success_response

async def test_my_tool(toolset):
    result = await toolset.my_function()
    assert_success_response(result)  # Checks format automatically
```

## Coverage

**Target**: 85% overall (enforced by CI)

**Check coverage**:
```bash
uv run pytest --cov=src/agent --cov-report=term-missing --cov-report=html
open htmlcov/index.html
```

**Excluded from coverage**: CLI orchestration, display rendering, error definitions

## Related Documentation

- **LLM Tests**: See `tests/integration/llm/README.md` for real LLM testing guide
- **Templates**: Check `tests/templates/` for full examples
- **Contributing**: See `CONTRIBUTING.md` for development guidelines
- **ADR-0008**: Testing strategy decisions in `docs/decisions/`
