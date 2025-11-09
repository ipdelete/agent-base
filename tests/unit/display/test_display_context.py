"""Unit tests for agent.display.context module."""

import pytest

from agent.display.context import (
    DisplayMode,
    ExecutionContext,
    get_execution_context,
    is_interactive_mode,
    set_execution_context,
    should_show_visualization,
)
from agent.display.events import get_event_emitter


@pytest.mark.unit
@pytest.mark.display
class TestDisplayMode:
    """Tests for DisplayMode enum."""

    def test_display_mode_values(self):
        """Test DisplayMode has expected values."""
        assert DisplayMode.MINIMAL.value == "minimal"
        assert DisplayMode.VERBOSE.value == "verbose"


@pytest.mark.unit
@pytest.mark.display
class TestExecutionContext:
    """Tests for ExecutionContext dataclass."""

    def test_execution_context_defaults(self):
        """Test ExecutionContext has correct defaults."""
        ctx = ExecutionContext()

        assert ctx.is_interactive is False
        assert ctx.show_visualization is False
        assert ctx.display_mode == DisplayMode.MINIMAL

    def test_execution_context_with_values(self):
        """Test ExecutionContext can be created with values."""
        ctx = ExecutionContext(
            is_interactive=True, show_visualization=True, display_mode=DisplayMode.VERBOSE
        )

        assert ctx.is_interactive is True
        assert ctx.show_visualization is True
        assert ctx.display_mode == DisplayMode.VERBOSE


@pytest.mark.unit
@pytest.mark.display
class TestContextManagement:
    """Tests for context management functions."""

    @pytest.fixture(autouse=True)
    def reset_context(self):
        """Reset execution context before each test."""
        set_execution_context(None)
        # Also reset event emitter
        emitter = get_event_emitter()
        emitter.set_interactive_mode(False, False)
        yield
        # Clean up after test
        set_execution_context(None)

    def test_set_and_get_execution_context(self):
        """Test setting and getting execution context."""
        ctx = ExecutionContext(
            is_interactive=True, show_visualization=True, display_mode=DisplayMode.VERBOSE
        )

        set_execution_context(ctx)
        retrieved = get_execution_context()

        assert retrieved is ctx
        assert retrieved.is_interactive is True
        assert retrieved.show_visualization is True
        assert retrieved.display_mode == DisplayMode.VERBOSE

    def test_get_execution_context_returns_none_when_not_set(self):
        """Test get_execution_context returns None when not set."""
        set_execution_context(None)

        ctx = get_execution_context()

        assert ctx is None

    def test_set_execution_context_updates_event_emitter(self):
        """Test set_execution_context updates EventEmitter singleton."""
        ctx = ExecutionContext(is_interactive=True, show_visualization=True)

        set_execution_context(ctx)

        emitter = get_event_emitter()
        assert emitter.is_interactive_mode() is True
        assert emitter.should_show_visualization() is True

    def test_set_execution_context_none_clears_event_emitter(self):
        """Test setting context to None clears EventEmitter flags."""
        # First set a context
        ctx = ExecutionContext(is_interactive=True, show_visualization=True)
        set_execution_context(ctx)

        # Then clear it
        set_execution_context(None)

        emitter = get_event_emitter()
        assert emitter.is_interactive_mode() is False
        assert emitter.should_show_visualization() is False

    def test_is_interactive_mode_reads_from_emitter(self):
        """Test is_interactive_mode reads from EventEmitter."""
        ctx = ExecutionContext(is_interactive=True, show_visualization=True)
        set_execution_context(ctx)

        assert is_interactive_mode() is True

    def test_is_interactive_mode_false_when_not_set(self):
        """Test is_interactive_mode is False when context not set."""
        set_execution_context(None)

        assert is_interactive_mode() is False

    def test_is_interactive_mode_requires_both_flags(self):
        """Test is_interactive_mode requires both flags."""
        # Only interactive
        ctx1 = ExecutionContext(is_interactive=True, show_visualization=False)
        set_execution_context(ctx1)
        assert is_interactive_mode() is False

        # Only visualization
        ctx2 = ExecutionContext(is_interactive=False, show_visualization=True)
        set_execution_context(ctx2)
        assert is_interactive_mode() is False

        # Both
        ctx3 = ExecutionContext(is_interactive=True, show_visualization=True)
        set_execution_context(ctx3)
        assert is_interactive_mode() is True

    def test_should_show_visualization_reads_from_emitter(self):
        """Test should_show_visualization reads from EventEmitter."""
        ctx = ExecutionContext(show_visualization=True)
        set_execution_context(ctx)

        assert should_show_visualization() is True

    def test_should_show_visualization_false_when_not_set(self):
        """Test should_show_visualization is False when context not set."""
        set_execution_context(None)

        assert should_show_visualization() is False

    def test_should_show_visualization_independent_of_interactive(self):
        """Test should_show_visualization works regardless of interactive mode."""
        # CLI mode with visualization
        ctx1 = ExecutionContext(is_interactive=False, show_visualization=True)
        set_execution_context(ctx1)
        assert should_show_visualization() is True

        # Interactive mode with visualization
        ctx2 = ExecutionContext(is_interactive=True, show_visualization=True)
        set_execution_context(ctx2)
        assert should_show_visualization() is True

        # No visualization
        ctx3 = ExecutionContext(is_interactive=True, show_visualization=False)
        set_execution_context(ctx3)
        assert should_show_visualization() is False


@pytest.mark.unit
@pytest.mark.display
class TestContextIntegration:
    """Integration tests for context management."""

    @pytest.fixture(autouse=True)
    def reset_all(self):
        """Reset all state before each test."""
        set_execution_context(None)
        emitter = get_event_emitter()
        emitter.set_interactive_mode(False, False)
        yield
        set_execution_context(None)

    def test_cli_mode_with_verbose(self):
        """Test CLI mode with verbose visualization."""
        ctx = ExecutionContext(
            is_interactive=False, show_visualization=True, display_mode=DisplayMode.VERBOSE
        )
        set_execution_context(ctx)

        assert is_interactive_mode() is False
        assert should_show_visualization() is True
        assert get_execution_context().display_mode == DisplayMode.VERBOSE

    def test_interactive_mode_minimal(self):
        """Test interactive mode with minimal display."""
        ctx = ExecutionContext(
            is_interactive=True, show_visualization=True, display_mode=DisplayMode.MINIMAL
        )
        set_execution_context(ctx)

        assert is_interactive_mode() is True
        assert should_show_visualization() is True
        assert get_execution_context().display_mode == DisplayMode.MINIMAL

    def test_quiet_mode(self):
        """Test quiet mode (no visualization)."""
        ctx = ExecutionContext(
            is_interactive=False, show_visualization=False, display_mode=DisplayMode.MINIMAL
        )
        set_execution_context(ctx)

        assert is_interactive_mode() is False
        assert should_show_visualization() is False
