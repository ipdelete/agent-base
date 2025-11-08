# Contributing to Agent Template

Thank you for your interest in contributing to Agent Template!

## Development Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Git
- One of the supported LLM providers (OpenAI, Anthropic, or Azure AI Foundry)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/danielscholl/agent-template.git
cd agent-template

# Install dependencies with dev extras
uv sync --all-extras

# Configure environment
cp .env.example .env
# Edit .env with required values for your LLM provider

# Verify installation
uv run agent --help
uv run agent --check
```

### Environment Configuration

Create a `.env` file with your configuration:

```bash
cp .env.example .env
```

**For OpenAI:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your-api-key
```

**For Anthropic:**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-api-key
```

**For Azure AI Foundry:**
```bash
LLM_PROVIDER=azure_ai_foundry
AZURE_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-id
AZURE_MODEL_DEPLOYMENT=gpt-4o
# Then run: az login
```

## Code Quality

### Quality Checks

Before submitting a pull request, ensure all quality checks pass:

```bash
# Auto-fix formatting and linting
uv run black src/agent/ tests/
uv run ruff check --fix src/agent/ tests/

# Verify checks pass
uv run black --check src/agent/ tests/
uv run ruff check src/agent/ tests/
uv run mypy src/agent/
uv run pytest --cov=src/agent --cov-fail-under=85
```

### CI Pipeline

Our GitHub Actions CI runs the following checks:

1. **Black**: Code formatting (strict)
2. **Ruff**: Linting and code quality
3. **MyPy**: Type checking
4. **PyTest**: Test suite with 85% minimum coverage
5. **CodeQL**: Security scanning

All checks must pass for PRs to be merged.

### Testing

#### Run All Tests

```bash
# Full test suite
uv run pytest

# With verbose output
uv run pytest -v

# With coverage report
uv run pytest --cov=src/agent --cov-report=term-missing
```

#### Run Specific Tests

```bash
# Test a specific file
uv run pytest tests/unit/test_agent.py

# Test a specific class
uv run pytest tests/unit/test_cli.py::TestInteractiveMode

# Test a specific function
uv run pytest tests/unit/test_config.py::test_openai_provider_validation
```

#### Coverage

```bash
# Generate HTML coverage report
uv run pytest --cov=src/agent --cov-report=html
open htmlcov/index.html
```

## Commit Guidelines

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning and changelog generation.

### Commit Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Commit Types

| Type | Description | Version Bump | Example |
|------|-------------|--------------|---------|
| `feat` | New feature | Minor (0.x.0) | `feat(tools): add WebTools for scraping` |
| `fix` | Bug fix | Patch (0.0.x) | `fix(config): handle missing env vars` |
| `docs` | Documentation only | None | `docs: update USAGE.md examples` |
| `style` | Code style changes | None | `style: format with black` |
| `refactor` | Code refactoring | None | `refactor(agent): extract session logic` |
| `test` | Add/update tests | None | `test: add HelloTools edge cases` |
| `chore` | Maintenance | None | `chore: update dependencies` |
| `ci` | CI/CD changes | None | `ci: add CodeQL workflow` |
| `perf` | Performance improvements | Patch | `perf(tools): cache API responses` |

### Scopes

Common scopes in this project:
- `agent`: Agent class and core functionality
- `config`: Configuration management
- `tools`: Tool implementations
- `cli`: CLI interface
- `events`: Event bus
- `tests`: Test infrastructure

### Breaking Changes

For breaking changes, add `!` after type and include `BREAKING CHANGE:` in footer:

```
feat(config)!: redesign configuration system

BREAKING CHANGE: Configuration now uses dataclasses instead of dict.
Update code to use AgentConfig.from_env() instead of load_config().
```

### Examples

```bash
# New feature
git commit -m "feat(tools): add greet_user tool with language support"

# Bug fix
git commit -m "fix(agent): handle empty tool list gracefully"

# Documentation
git commit -m "docs: add architecture decision record for event bus"

# Multiple changes
git commit -m "feat(cli): add interactive mode

- Implement prompt_toolkit shell
- Add session management
- Support command history"

# Breaking change
git commit -m "feat(config)!: switch to pydantic for validation

BREAKING CHANGE: AgentConfig now requires pydantic models.
Update imports from agent.config import AgentConfig."
```

## Pull Request Process

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes** following code style guidelines

3. **Run quality checks**:
   ```bash
   uv run black src/agent/ tests/
   uv run ruff check --fix src/agent/ tests/
   uv run mypy src/agent/
   uv run pytest --cov=src/agent
   ```

4. **Commit using aipr** (if available):
   ```bash
   git add .
   git commit -m "$(aipr commit -s -m claude)"
   ```

   Or manually with conventional commits:
   ```bash
   git commit -m "feat(scope): add new feature"
   ```

5. **Push and create PR**:
   ```bash
   git push -u origin feat/your-feature-name
   gh pr create --title "feat: add new feature" --body "Description"
   ```

6. **Address review comments** and ensure CI passes

### Code Review Checklist

Reviewers will verify:

- [ ] All CI checks pass (Black, Ruff, MyPy, PyTest, CodeQL)
- [ ] Test coverage ≥ 85%
- [ ] Type hints on all public functions
- [ ] Docstrings for public APIs
- [ ] Conventional commit format
- [ ] No breaking changes without `BREAKING CHANGE:` footer
- [ ] Documentation updated if needed

## Architecture

Agent Template follows a modular architecture built on Microsoft Agent Framework.

### Core Components

#### Agent Layer (`src/agent/`)
- **agent.py**: Main Agent class with LLM orchestration
- **config.py**: Multi-provider configuration management
- **cli.py**: CLI interface and interactive chat mode
- **middleware.py**: Agent and function-level middleware for event emission

#### Tools (`src/agent/tools/`)
- **toolset.py**: Base class for toolsets
- **hello.py**: HelloTools (reference implementation)

#### Display & Events
- **display/**: Execution visualization with Rich Live
- **events.py**: Event bus for loose coupling
- **middleware.py**: Event emission during execution
- **persistence.py**: Session save/load management

#### Utilities
- **utils/keybindings/**: Extensible keybinding system
- **utils/terminal.py**: Shell command execution
- **utils/errors.py**: Custom exception hierarchy

## Architecture Decision Records

For significant architectural decisions, create an ADR in `docs/decisions/`:

### When to Create an ADR

Create an ADR when deciding:
- Architecture patterns (tool registration, event bus, etc.)
- Technology choices (frameworks, libraries)
- Design patterns (observer, factory, dependency injection)
- API designs (method signatures, response formats)
- Testing strategies (mocking patterns, coverage targets)

### ADR Process

1. **Copy template:**
   ```bash
   cp docs/decisions/adr-template.md docs/decisions/0XXX-your-decision.md
   ```

2. **Fill in content:**
   - Status: `proposed`
   - Context and problem statement
   - Decision drivers
   - Considered options
   - Decision outcome
   - Consequences

3. **Include in PR:**
   - ADRs should be included in the same PR as the implementation
   - Update status to `accepted` once PR is merged

4. **Example ADRs:**
   - See existing ADRs in `docs/decisions/`
   - Follow the template structure

See [docs/decisions/README.md](docs/decisions/README.md) for complete ADR documentation.

## Code Style

### Python Style Guide

We follow PEP 8 with these specifications:

- **Line length**: 100 characters (configured in black/ruff)
- **Imports**: Sorted by isort via ruff
- **Type hints**: Required for public APIs
- **Docstrings**: Google style for public functions/classes

### Docstring Example

```python
def hello_world(name: str = "World") -> dict:
    """Say hello to someone.

    Args:
        name: Name of person to greet (default: "World")

    Returns:
        Success response with greeting message

    Raises:
        ValueError: If name is empty string

    Example:
        >>> tools = HelloTools(config)
        >>> result = await tools.hello_world("Alice")
        >>> print(result)
        {'success': True, 'result': 'Hello, Alice!', 'message': ''}
    """
    ...
```

### Type Hints

```python
# Required for public APIs
def process_data(data: list[dict[str, Any]]) -> tuple[int, list[str]]:
    ...

# Optional for private functions (but recommended)
def _helper(x: int) -> int:
    ...

# Use Protocol for interfaces
from typing import Protocol

class ToolProvider(Protocol):
    def get_tools(self) -> list[Callable]: ...
```

## Development Workflows

### Adding a New Tool

1. Create tool class in `src/agent/tools/`
2. Inherit from `AgentToolset`
3. Add type hints and comprehensive docstring
4. Add unit tests in `tests/unit/`
5. Update documentation

### Modifying Display

Display code is in `src/agent/cli.py` and `src/agent/display/`:
- Banner and status bar: `_render_startup_banner()`, `_render_status_bar()`
- Execution tree: `src/agent/display/tree.py`
- Keep consistent with ◉‿◉ branding
- Use `highlight=False` to prevent Rich auto-highlighting

## Testing Guidelines

### Test Organization

```
tests/
├── unit/              # Isolated component tests
│   ├── test_agent.py
│   ├── test_config.py
│   └── test_hello_tools.py
├── integration/       # Full stack tests
│   └── test_hello_integration.py
├── mocks/            # Test mocks
│   └── mock_client.py
└── conftest.py       # Shared fixtures
```

### Writing Tests

```python
import pytest

@pytest.mark.asyncio
async def test_hello_world_default(hello_tools):
    """Test hello_world with default name."""
    result = await hello_tools.hello_world()

    assert result["success"] is True
    assert result["result"] == "Hello, World! ◉‿◉"
```

### Test Coverage

- **Overall**: Minimum 85% coverage (enforced by CI)
- **Unit tests**: 100% for business logic
- **Integration tests**: Cover happy path and error cases

## Release Process

Releases are automated using [release-please](https://github.com/googleapis/release-please):

1. **Commit with conventional commits** - Version bumps calculated automatically
2. **PR created automatically** - Merge to trigger release
3. **GitHub Release created** - Changelog generated from commits
4. **Package published** - Artifacts uploaded to GitHub Releases

### Version Bumping

Based on commit types:
- `feat:` → Minor version (0.x.0)
- `fix:` → Patch version (0.0.x)
- `feat!:` or `BREAKING CHANGE:` → Major version (x.0.0)

## Getting Help

- **Questions**: Open a [Discussion](https://github.com/danielscholl/agent-template/discussions)
- **Bugs**: Open an [Issue](https://github.com/danielscholl/agent-template/issues)
- **Security**: Email security@example.com (private disclosure)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). By participating, you agree to uphold this code.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
