# Test Infrastructure Guide

Comprehensive guide to testing in agent-template.

## ⚠️ Important: Always Use `uv run`

**All pytest commands must be prefixed with `uv run`** to use the project's virtual environment:

```bash
✅ CORRECT:   uv run pytest -m unit
❌ INCORRECT: pytest -m unit  # Will fail with "ModuleNotFoundError: No module named 'agent'"
```

This ensures pytest uses the correct Python environment with the `agent` package installed.

**💡 Tip: Use `-n auto` for parallel execution** (much faster):
```bash
uv run pytest -m unit -n auto  # Uses all CPU cores, ~3-5x faster
```

## Quick Reference

```bash
# Run all tests (excludes LLM by default)
uv run pytest

# Run by test type
uv run pytest -m unit              # Unit tests (fast, isolated) - 199 tests
uv run pytest -m integration       # Integration tests (mocked LLM) - 25 tests
uv run pytest -m validation        # CLI validation (subprocess) - 11 tests
uv run pytest -m llm              # Real LLM tests (⚠️ costs money) - 22 tests

# Run tests for specific feature area
uv run pytest -m tools            # Tool tests
uv run pytest -m display          # Display tests
uv run pytest -m middleware       # Middleware tests
uv run pytest -m cli              # CLI tests

# Run validation tests via subprocess
uv run pytest -m validation       # Via pytest
uv run python tests/validation/run_validation.py  # Standalone runner with YAML

# Run LLM tests (requires API keys, costs ~$0.005)
export OPENAI_API_KEY=your-key
uv run pytest -m llm

# Speed-based selection
uv run pytest -m fast             # Fast tests only
uv run pytest -m "not slow"       # Exclude slow tests

# Combined markers
uv run pytest -m "unit and tools"          # Unit tests for tools only
uv run pytest -m "integration and not llm" # Integration without real LLM

# Run tests in parallel (faster)
uv run pytest -n auto

# Run with coverage
uv run pytest --cov=src/agent --cov-report=term-missing
```

## Test Type Summary

| Type | Count | Speed | API Calls | Purpose |
|------|-------|-------|-----------|---------|
| **Unit** | 199 | Fast (~5s) | No | Test code logic in isolation |
| **Integration** | 25 | Moderate (~10s) | No (mocked) | Test components together |
| **Validation** | 11 | Moderate (~5s) | **Some** (⚠️ 7/11 cost $) | Test CLI via subprocess |
| **LLM Integration** | 22 | Slow (~30s) | Yes (⚠️ costs $) | Test with real LLMs |
| **Total** | 246 | ~50s (no LLM) | Varies | Complete coverage |

**Note on Validation Tests**: 4 tests are free (--help, --version, --check, --config), but 7 tests execute prompts via subprocess and will make real LLM API calls if `LLM_PROVIDER` is configured. They automatically skip if no LLM is configured.

## Test Organization

### Directory Structure

```
tests/
├── conftest.py                     # Main fixture file (imports from fixtures/)
├── fixtures/                       # Organized fixtures by component
│   ├── __init__.py
│   ├── agent.py                    # Agent fixtures (mock_chat_client, agent_instance)
│   └── config.py                   # Config fixtures (mock_config, mock_openai_config, etc.)
│
├── helpers/                        # Test utilities
│   ├── __init__.py
│   ├── assertions.py               # Custom assertions (assert_success_response, etc.)
│   └── builders.py                 # Test data builders (build_test_config, etc.)
│
├── templates/                      # Templates for new tests (not collected by pytest)
│   ├── test_tool_template.py       # Template for tool tests
│   ├── test_integration_template.py # Template for integration tests
│   └── test_llm_template.py        # Template for real LLM tests
│
├── mocks/                          # Test mocks
│   └── mock_client.py              # MockChatClient for LLM mocking
│
├── unit/                           # Fast, isolated unit tests
│   ├── core/                       # Core agent functionality
│   │   ├── test_agent.py
│   │   ├── test_config.py
│   │   └── test_events.py
│   ├── cli/                        # CLI tests
│   │   ├── test_cli.py
│   │   └── test_cli_toolbar.py
│   ├── display/                    # Display rendering tests
│   │   ├── test_display_context.py
│   │   ├── test_display_events.py
│   │   └── test_display_tree.py
│   ├── tools/                      # Tool tests
│   │   └── test_hello_tools.py
│   ├── middleware/                 # Middleware tests
│   │   └── test_middleware.py
│   └── persistence/                # Session persistence tests
│       └── test_persistence.py
│
├── integration/                    # Component integration tests (mocked LLM)
│   ├── test_hello_integration.py   # Tool integration
│   ├── test_middleware_integration.py  # Middleware integration
│   ├── test_session_persistence.py # Session persistence
│   └── llm/                        # ⚠️ Real LLM tests (costs money!)
│       ├── conftest.py             # Real agent fixtures
│       ├── test_openai_integration.py
│       ├── test_anthropic_integration.py
│       ├── test_tool_invocation.py
│       └── README.md               # LLM test documentation
│
└── validation/                     # CLI validation via subprocess
    ├── test_agent_validation.py
    ├── run_validation.py
    ├── agent_validation.yaml
    └── agent_validation_advanced.yaml
```

## Test Types

### Unit Tests (`tests/unit/`)

**Purpose**: Test components in isolation with mocked dependencies

**Characteristics**:
- Fast (< 100ms per test)
- No I/O operations
- All dependencies mocked
- Target: 100% coverage for business logic

**When to use**:
- Testing tool logic
- Testing configuration handling
- Testing event bus
- Testing data transformations

**Example**:
```python
@pytest.mark.unit
@pytest.mark.tools
class TestHelloTools:
    @pytest.mark.asyncio
    async def test_hello_world(self, hello_tools):
        result = await hello_tools.hello_world("Alice")
        assert result["success"] is True
        assert "Alice" in result["result"]
```

### Integration Tests (`tests/integration/`)

**Purpose**: Test components working together with mocked LLM

**Characteristics**:
- Moderate speed (~1s per test)
- Uses MockChatClient (no real API calls)
- Tests component interactions
- Target: Cover happy paths and major errors

**When to use**:
- Testing agent + tools together
- Testing middleware chains
- Testing session persistence
- Testing full request/response cycle

**Example**:
```python
@pytest.mark.integration
@pytest.mark.tools
class TestAgentToolIntegration:
    @pytest.mark.asyncio
    async def test_agent_with_tools(self, agent_with_tools):
        response = await agent_with_tools.run("test")
        assert response
```

### LLM Integration Tests (`tests/integration/llm/`)

**Purpose**: Test with REAL LLM APIs (opt-in, costs money)

**Characteristics**:
- Slow (>1s per test)
- Makes real API calls
- Costs money (~$0.005 per run)
- Automatically skips if no API key
- Opt-in only

**When to use**:
- Verifying tool invocation works with real LLMs
- Testing provider-specific behavior
- Validating prompts and instructions
- Testing conversation context

**Example**:
```python
@pytest.mark.llm
@pytest.mark.requires_openai
@pytest.mark.slow
class TestOpenAIToolInvocation:
    @pytest.mark.asyncio
    async def test_tool_invocation(self, openai_agent):
        \"\"\"Cost: ~$0.0005\"\"\"
        response = await openai_agent.run("Use hello_world tool")
        assert response
```

### Validation Tests (`tests/validation/`)

**Purpose**: Test CLI via subprocess (real process execution)

Validation tests execute the actual CLI as a subprocess (like a user would) and verify:
- CLI commands work correctly
- Help text is accurate
- Error messages are helpful
- Exit codes are correct
- Process behavior is as expected

**Characteristics**:
- Moderate speed (~1-5s per test)
- Tests via `subprocess.run("uv run agent ...")`
- Real process execution (not Python imports)
- YAML-based test configuration
- **Mixed cost**: Some tests free (CLI commands), some cost money (prompt execution)
  - Free tests (4): `--help`, `--version`, `--check`, `--config`
  - Paid tests (7): Tests that execute prompts (⚠️ make real LLM API calls if configured)
  - Paid tests automatically skip if `LLM_PROVIDER` not set

**When to use**:
- Testing CLI commands (`--help`, `--version`, `--check`, `--config`)
- Validating help text and documentation
- Testing error handling and exit codes
- Verifying output formatting for users
- Testing shell command integration (`!ls`, `!git status`)
- Ensuring CLI works as a standalone executable

**Example**:
```python
@pytest.mark.validation
def test_help_command(validator):
    """Test help command execution via subprocess."""
    result = validator.run_command("uv run agent --help", timeout=10)

    # Verify process behavior
    assert result["exit_code"] == 0
    assert "agent" in result["stdout"]
    assert "--prompt" in result["stdout"]
```

**YAML Configuration** (`agent_validation.yaml`):
```yaml
command_tests:
  - name: "Help command displays correctly"
    command: "uv run agent --help"
    timeout: 10
    expected:
      exit_code: 0
      stdout_contains:
        - "agent"
        - "--prompt"
        - "Examples:"

prompt_tests:
  - name: "Simple greeting"
    command: 'uv run agent -p "Say hello"'
    timeout: 30
    expected:
      exit_code: 0
      stdout_contains_any: ["Hello", "hello"]
```

**Running Validation Tests**:
```bash
# Run all validation tests
pytest -m validation

# Run using the YAML configuration
python tests/validation/run_validation.py

# Run specific validation test
pytest tests/validation/test_agent_validation.py -v
```

**Key Difference from Other Tests**:

| Aspect | Validation | Unit/Integration | LLM Integration |
|--------|-----------|------------------|-----------------|
| **Execution** | `subprocess.run()` | Python `import` | Python `import` |
| **Tests** | CLI process | Code logic | AI behavior |
| **API Calls** | **Mixed** (4 free, 7 paid*) | No (mocked) | Yes (real) |
| **Speed** | Moderate | Fast | Slow |
| **Verifies** | User experience | Code correctness | AI integration |

\* Validation tests that execute prompts make real LLM API calls if `LLM_PROVIDER` is configured. They skip automatically if not configured.

**Example Comparison**:

```python
# Unit test - Tests the function
@pytest.mark.unit
async def test_hello_world():
    tools = HelloTools(config)
    result = await tools.hello_world("Alice")
    assert result["success"] is True

# Integration test - Tests components together (mocked LLM)
@pytest.mark.integration
async def test_agent_with_tools():
    agent = Agent(config=config, chat_client=MockChatClient())
    response = await agent.run("test")
    assert response

# Validation test - Tests CLI as subprocess
@pytest.mark.validation
def test_cli_prompt():
    result = subprocess.run(["agent", "-p", "hello"], capture_output=True)
    assert result.returncode == 0
    assert result.stdout

# LLM integration test - Tests with REAL LLM
@pytest.mark.llm
async def test_openai_tool_invocation():
    agent = Agent(config)  # Real OpenAI client
    response = await agent.run("Use hello_world tool")  # REAL API call
    assert response
```

**Why Validation Tests Matter**:
1. **User perspective**: Tests what users actually run
2. **Process isolation**: Catches issues with imports, env vars, etc.
3. **CLI-specific**: Tests argument parsing, help text, formatting
4. **Real execution**: Not just Python unit tests
5. **Cross-platform**: Can test on different OSes

## Pytest Markers

### Test Type Markers
- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (mocked LLM)
- `@pytest.mark.validation` - CLI validation tests
- `@pytest.mark.llm` - Real LLM API calls (opt-in, costs money)

### Speed Markers
- `@pytest.mark.fast` - Tests < 100ms
- `@pytest.mark.slow` - Tests > 1s

### Feature Area Markers
- `@pytest.mark.agent` - Core agent functionality
- `@pytest.mark.tools` - Tool-related tests
- `@pytest.mark.display` - Display and rendering
- `@pytest.mark.cli` - CLI interface
- `@pytest.mark.middleware` - Middleware
- `@pytest.mark.persistence` - Session persistence
- `@pytest.mark.config` - Configuration
- `@pytest.mark.events` - Event bus

### Provider Markers (for LLM tests)
- `@pytest.mark.requires_openai` - Needs OpenAI API key
- `@pytest.mark.requires_anthropic` - Needs Anthropic API key
- `@pytest.mark.requires_azure` - Needs Azure credentials

### Using Markers

```bash
# Run fast tests only
pytest -m fast

# Run unit tests for tools
pytest -m "unit and tools"

# Run everything except LLM tests (default)
pytest -m "not llm"

# Run only OpenAI LLM tests
pytest -m "llm and requires_openai"

# Combine markers
pytest -m "integration and not slow"
```

## Writing New Tests

### 1. Choose Test Type

- **Testing a new tool?** → Use `tests/templates/test_tool_template.py`
- **Testing component integration?** → Use `tests/templates/test_integration_template.py`
- **Testing with real LLM?** → Use `tests/templates/test_llm_template.py`

### 2. Copy Template

```bash
# For a new tool
cp tests/templates/test_tool_template.py tests/unit/tools/test_my_tool.py

# For integration test
cp tests/templates/test_integration_template.py tests/integration/test_my_feature.py

# For LLM test
cp tests/templates/test_llm_template.py tests/integration/llm/test_my_llm_feature.py
```

### 3. Customize

Replace placeholders and follow the established patterns in the template.

### 4. Add Appropriate Markers

```python
# Unit test for a tool
@pytest.mark.unit
@pytest.mark.tools
class TestMyTool:
    pass

# Integration test
@pytest.mark.integration
@pytest.mark.middleware
class TestMyIntegration:
    pass

# LLM test (markers auto-added by conftest, but good to be explicit)
@pytest.mark.llm
@pytest.mark.requires_openai
@pytest.mark.slow
class TestMyLLMFeature:
    pass
```

## Common Patterns

### Using Fixtures

```python
def test_something(mock_config, mock_chat_client):
    """Use shared fixtures from conftest.py"""
    agent = Agent(config=mock_config, chat_client=mock_chat_client)
```

### Using Helpers

```python
from tests.helpers import assert_success_response, assert_error_response

async def test_tool(toolset):
    result = await toolset.my_tool("input")
    assert_success_response(result)  # Validates format
```

### Using Builders

```python
from tests.helpers.builders import build_test_config

def test_something():
    config = build_test_config(llm_provider="anthropic")
    # config is ready to use
```

## Running Tests

### Local Development

```bash
# Fast feedback - unit tests only
pytest -m unit

# Quick check before commit
pytest -m "unit and not slow"

# Full test suite (no LLM)
pytest

# With coverage
pytest --cov=src/agent --cov-fail-under=85

# Parallel execution (faster)
pytest -n auto
```

### CI/CD

Default CI runs:
```bash
pytest -m "not llm" --cov=src/agent --cov-fail-under=85
```

This excludes expensive LLM tests but ensures 85% coverage.

### Before Committing

```bash
# Code quality checks
uv run black src/ tests/
uv run ruff check --fix src/ tests/
uv run mypy src/agent/

# Run tests
pytest -m "not llm"
```

## Coverage

**Target**: 85% overall coverage (enforced by CI)

**Excluded from coverage**:
- `src/agent/__main__.py` - Wrapper only
- `src/agent/utils/__init__.py` - Imports only
- `src/agent/utils/errors.py` - Exception definitions
- `src/agent/cli/app.py` - CLI orchestration (hard to test)
- `src/agent/display/*` - Display logic (hard to test)

**Check coverage**:
```bash
pytest --cov=src/agent --cov-report=html
open htmlcov/index.html
```

## Troubleshooting

### Import Errors After Adding New Tests

**Solution**: Make sure `__init__.py` exists in the test directory

### Fixtures Not Found

**Solution**: Check that `conftest.py` imports the fixture or it's defined in a parent directory

### Tests Taking Too Long

**Solution**: Use markers to run only fast tests:
```bash
pytest -m "fast" -n auto
```

### LLM Tests Always Skip

**Solution**: Set API keys:
```bash
export OPENAI_API_KEY=your-key
pytest -m llm
```

## Best Practices

1. **One test, one assertion concept** - Test one thing per test method
2. **Descriptive names** - `test_hello_world_with_empty_name` not `test_1`
3. **Use fixtures** - Don't duplicate setup code
4. **Use helpers** - Reuse assertion logic
5. **Mark appropriately** - Use correct markers for test selection
6. **Document costs** - Add cost estimates to LLM test docstrings
7. **Keep tests independent** - Tests should not depend on each other
8. **Test errors** - Test error cases, not just happy paths

## Adding New Capabilities

### Adding a New Tool

1. Create tool in `src/agent/tools/your_tool.py`
2. Copy `tests/templates/test_tool_template.py` to `tests/unit/tools/test_your_tool.py`
3. Customize tests for your tool
4. Add integration test in `tests/integration/test_your_tool_integration.py`
5. Optionally add LLM test in `tests/integration/llm/test_your_tool_llm.py`

### Adding Observability

1. Create observability code in `src/agent/observability/`
2. Create `tests/unit/observability/` directory
3. Add unit tests for metrics, tracing, logging
4. Add integration tests for end-to-end observability

### Adding Workflows

1. Create workflow code in `src/agent/workflows/`
2. Create `tests/unit/workflows/` directory
3. Test workflow logic in isolation
4. Test workflow execution with mocked agents
5. Test real execution with LLM tests (optional)

### Adding Multi-Agent Features

1. Create multi-agent code in `src/agent/multiagent/`
2. Create `tests/unit/multiagent/` directory
3. Test agent coordination logic
4. Test message passing
5. Test with mocked agents first, real LLMs later

## Test Statistics

**Current Status**:
- Total Tests: 246
- Unit Tests: 199 (81%)
- Integration Tests: 25 (10%)
- LLM Tests: 22 (9%)
- Coverage: 85%+ (enforced)

**Test Execution Speed**:
- Unit tests: ~5-10 seconds
- Integration tests: ~10-15 seconds
- LLM tests: ~30-60 seconds (with real API calls)
- Total (excluding LLM): ~15-25 seconds

## Related Documentation

- [ADR-0008](../docs/decisions/0008-testing-strategy-and-coverage-targets.md) - Testing strategy decisions
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development guidelines
- [LLM Test Guide](integration/llm/README.md) - Real LLM testing guide
- [Test Templates](templates/) - Templates for new tests

## Getting Help

**Test not passing?**
1. Check the error message
2. Look at similar existing tests for patterns
3. Verify fixtures are correctly imported
4. Check markers are appropriate

**Not sure where to add a test?**
- Tool functionality → `tests/unit/tools/`
- Component integration → `tests/integration/`
- Real LLM behavior → `tests/integration/llm/`
- CLI commands → `tests/validation/`

**Need help with mocking?**
- See `tests/mocks/mock_client.py` for examples
- Check `tests/conftest.py` for available fixtures
- Review `tests/helpers/builders.py` for test data creation
