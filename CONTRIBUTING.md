# Contributing

Development guide for Agent Base contributors.

## Development Setup

**Requirements:**
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Git
- LLM provider access (OpenAI, Anthropic, or Azure)

**Install:**

```bash
git clone https://github.com/danielscholl/agent-base.git
cd agent-base
uv sync --all-extras
```

**Configure:**

Copy `.env.example` to `.env` and add your provider credentials:

```bash
cp .env.example .env
```

**OpenAI:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

**Anthropic:**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

**Azure:**
```bash
LLM_PROVIDER=azure_ai_foundry
AZURE_PROJECT_ENDPOINT=https://...
AZURE_MODEL_DEPLOYMENT=gpt-4o
```
Then authenticate: `az login`

See `.env.example` for all options.

**Verify:**

```bash
uv run agent --check
```

## Code Quality

Run quality checks before submitting:

```bash
# Format and lint
uv run black src/agent/ tests/
uv run ruff check --fix src/agent/ tests/

# Type check
uv run mypy src/agent/

# Test with coverage
uv run pytest --cov=src/agent --cov-fail-under=85
```

CI requires all checks to pass:
- Black (formatting)
- Ruff (linting)
- MyPy (type checking)
- PyTest (85% minimum coverage)
- CodeQL (security)

## Testing

See [tests/README.md](tests/README.md) for comprehensive testing guide.

**Quick reference:**

```bash
uv run pytest                    # All tests
uv run pytest -m unit            # Unit tests only
uv run pytest -m tools           # Tool tests
uv run pytest --cov=src/agent    # With coverage
uv run pytest -n auto            # Parallel execution
```

**Requirements:**
- Overall coverage ≥ 85%
- Use appropriate test markers
- Follow templates in `tests/templates/`

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>
```

**Types:**
- `feat` - New feature (minor version)
- `fix` - Bug fix (patch version)
- `docs` - Documentation only
- `refactor` - Code refactoring
- `test` - Add/update tests
- `chore` - Maintenance

**Scopes:** `agent`, `config`, `tools`, `cli`, `events`, `memory`, `tests`

**Examples:**

```bash
git commit -m "feat(tools): add language support to greet_user"
git commit -m "fix(agent): handle empty tool list"
git commit -m "docs: add architecture decision record"
```

**Breaking changes:**

```bash
git commit -m "feat(config)!: redesign configuration system

BREAKING CHANGE: Configuration now uses dataclasses.
Update code to use AgentConfig.from_env() instead of load_config()."
```

## Pull Request Process

1. Create feature branch: `git checkout -b feat/feature-name`
2. Make changes following code style guidelines
3. Run quality checks (see above)
4. Commit using conventional format
5. Push and create PR
6. Address review feedback

**Review requirements:**
- All CI checks pass
- Coverage ≥ 85%
- Type hints on public functions
- Docstrings for public APIs
- Conventional commit format

## Code Style

**Python style:**
- Line length: 100 characters
- Type hints required for public APIs
- Google-style docstrings for public functions/classes

**Docstring example:**

```python
def hello_world(name: str = "World") -> dict:
    """Say hello to someone.

    Args:
        name: Name of person to greet

    Returns:
        Success response with greeting message

    Raises:
        ValueError: If name is empty
    """
    ...
```

**Type hints:**

```python
# Public APIs require type hints
def process_data(data: list[dict[str, Any]]) -> tuple[int, list[str]]:
    ...

# Use Protocol for interfaces
from typing import Protocol

class ToolProvider(Protocol):
    def get_tools(self) -> list[Callable]: ...
```

## Architecture

Agent Template uses Microsoft Agent Framework with modular components:

**Core:** Agent class, configuration, CLI interface
**Tools:** Base toolset class and implementations
**Display:** Execution visualization and event handling
**Memory:** In-memory storage with persistence
**Persistence:** Session management

See `docs/design/architecture.md` for details.

### Adding a New Tool

1. Create tool class inheriting from `AgentToolset`
2. Add type hints and docstrings
3. Write unit tests
4. Update documentation

See `src/agent/tools/hello.py` for reference implementation.

### Architecture Decisions

For significant architectural changes, document decisions in `docs/decisions/`. See `docs/decisions/README.md` for the ADR template.

## Releases

Releases use [release-please](https://github.com/googleapis/release-please) with automatic versioning from conventional commits:
- `feat:` → minor version
- `fix:` → patch version
- `BREAKING CHANGE:` → major version

Merging the release PR triggers automated release creation.

## Getting Help

- **Questions**: Open a [Discussion](https://github.com/danielscholl/agent-base/discussions)
- **Bugs**: Open an [Issue](https://github.com/danielscholl/agent-base/issues)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
