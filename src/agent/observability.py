"""Observability helpers for Agent Base.

This module provides helper utilities for OpenTelemetry integration.
The main observability setup is handled by agent_framework.observability.setup_observability().

For full observability setup, see:
- agent_framework.observability.setup_observability()
- Examples: examples/observability_example.py
- Documentation: docs/decisions/0014-observability-integration.md
"""

import contextvars
from typing import Any

# Context var to hold the current agent span for cross-task propagation
_current_agent_span: contextvars.ContextVar[Any] = contextvars.ContextVar(
    "_current_agent_span", default=None
)


def set_current_agent_span(span: Any) -> None:
    """Record the current agent span in a context variable.

    This helps preserve parent-child relationships for tool spans when
    asynchronous task boundaries might lose the active span context.

    Args:
        span: The agent-level span to set as current
    """
    try:
        _current_agent_span.set(span)
    except Exception:
        # Best-effort: ignore issues with context vars in constrained envs
        pass


def get_current_agent_span() -> Any:
    """Retrieve the current agent span from the context variable.

    Returns:
        The agent span if set, otherwise None.
    """
    try:
        return _current_agent_span.get()
    except Exception:
        return None
