"""Display subsystem for execution visualization and context management.

This package provides:
- Event types for tracking agent execution (LLM requests, tool calls)
- Event emitter with asyncio queue for task-safe event propagation
- Execution context management for mode detection
- Display modes (MINIMAL, VERBOSE)
- Execution tree display with Rich Live

Usage:
    >>> from agent.display import (
    ...     ExecutionContext,
    ...     DisplayMode,
    ...     ExecutionTreeDisplay,
    ...     set_execution_context,
    ...     should_show_visualization
    ... )
    >>> ctx = ExecutionContext(
    ...     is_interactive=True,
    ...     show_visualization=True,
    ...     display_mode=DisplayMode.VERBOSE
    ... )
    >>> set_execution_context(ctx)
    >>> display = ExecutionTreeDisplay(display_mode=DisplayMode.VERBOSE)
    >>> async with display:
    ...     await agent.run("prompt")
"""

from agent.display.context import (
    DisplayMode,
    ExecutionContext,
    get_execution_context,
    is_interactive_mode,
    set_execution_context,
    should_show_visualization,
)
from agent.display.events import (
    EventEmitter,
    ExecutionEvent,
    LLMRequestEvent,
    LLMResponseEvent,
    ToolCompleteEvent,
    ToolErrorEvent,
    ToolStartEvent,
    get_current_tool_event_id,
    get_event_emitter,
    set_current_tool_event_id,
)
from agent.display.tree import ExecutionTreeDisplay

__all__ = [
    # Context management
    "DisplayMode",
    "ExecutionContext",
    "get_execution_context",
    "is_interactive_mode",
    "set_execution_context",
    "should_show_visualization",
    # Event types
    "EventEmitter",
    "ExecutionEvent",
    "LLMRequestEvent",
    "LLMResponseEvent",
    "ToolCompleteEvent",
    "ToolErrorEvent",
    "ToolStartEvent",
    # Event emitter
    "get_event_emitter",
    # Tool event context
    "get_current_tool_event_id",
    "set_current_tool_event_id",
    # Tree display
    "ExecutionTreeDisplay",
]
