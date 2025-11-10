"""Middleware functions for Agent execution pipeline.

This module provides middleware functions for logging and event emission
in the agent request/response pipeline. Middleware allows automatic event
tracking without modifying individual tools.

Middleware Types:
    - Agent-level: Wrap entire agent execution (LLM calls)
    - Function-level: Wrap individual tool calls

Event Emission:
    Middleware emits execution events for display visualization when
    should_show_visualization() returns True. This enables real-time
    execution tree display without coupling tools to display logic.
"""

import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any, cast

from agent_framework import (
    AgentRunContext,
    FunctionInvocationContext,
    FunctionMiddleware,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Agent-Level Middleware
# ============================================================================


async def agent_run_logging_middleware(
    context: AgentRunContext,
    next: Callable[[AgentRunContext], Awaitable[None]],
) -> None:
    """Log agent execution lifecycle and emit LLM request/response events.

    This middleware:
    - Logs agent execution start/complete
    - Emits LLMRequestEvent before LLM call
    - Emits LLMResponseEvent after LLM call with duration
    - Only emits events if should_show_visualization() is True

    Args:
        context: Agent run context containing messages and state
        next: Next middleware in chain

    Example:
        >>> middleware = {"agent": [agent_run_logging_middleware]}
        >>> agent = chat_client.create_agent(..., middleware=middleware)
    """
    from agent.display import (
        LLMRequestEvent,
        LLMResponseEvent,
        get_event_emitter,
        should_show_visualization,
    )

    logger.debug("Agent run starting...")

    # Emit LLM request event
    llm_event_id = None
    if should_show_visualization():
        message_count = len(context.messages) if hasattr(context, "messages") else 0
        event = LLMRequestEvent(message_count=message_count)
        llm_event_id = event.event_id
        get_event_emitter().emit(event)
        logger.debug(f"Emitted LLM request event with {message_count} messages")

    start_time = time.time()

    try:
        await next(context)
        duration = time.time() - start_time
        logger.debug("Agent run completed successfully")

        # Emit LLM response event
        if should_show_visualization() and llm_event_id:
            response_event = LLMResponseEvent(duration=duration, event_id=llm_event_id)
            get_event_emitter().emit(response_event)
            logger.debug(f"Emitted LLM response event ({duration:.2f}s)")

    except Exception as e:
        logger.error(f"Agent run failed: {e}")
        raise


async def agent_observability_middleware(
    context: AgentRunContext,
    next: Callable[[AgentRunContext], Awaitable[None]],
) -> None:
    """Track agent execution metrics and timing.

    This middleware logs execution duration and can be extended to send
    metrics to observability platforms (Application Insights, Prometheus, etc.).

    Args:
        context: Agent run context
        next: Next middleware in chain

    Example:
        >>> middleware = {"agent": [agent_observability_middleware]}
        >>> agent = chat_client.create_agent(..., middleware=middleware)
    """
    start_time = time.time()

    try:
        await next(context)
    finally:
        duration = time.time() - start_time
        logger.info(f"Agent execution took {duration:.2f}s")

        # Future: Send to observability platform
        # if config.applicationinsights_connection_string:
        #     track_metric("agent_execution_duration", duration)


# ============================================================================
# Function-Level Middleware
# ============================================================================


async def logging_function_middleware(
    context: FunctionInvocationContext,
    next: Callable,
) -> Any:
    """Middleware to log function/tool calls and emit execution events.

    This middleware:
    - Logs tool execution start/complete/error
    - Emits ToolStartEvent before tool execution
    - Emits ToolCompleteEvent on success with result summary
    - Emits ToolErrorEvent on failure
    - Sets tool context for nested event tracking
    - Only emits events if should_show_visualization() is True

    Args:
        context: Function invocation context with function metadata and arguments
        next: Next middleware in chain

    Returns:
        Result from tool execution

    Example:
        >>> middleware = {"function": [logging_function_middleware]}
        >>> agent = chat_client.create_agent(..., middleware=middleware)
    """
    from agent.display import (
        ToolCompleteEvent,
        ToolErrorEvent,
        ToolStartEvent,
        get_current_tool_event_id,
        get_event_emitter,
        set_current_tool_event_id,
        should_show_visualization,
    )

    tool_name = context.function.name
    args = context.arguments

    logger.info(f"Tool call: {tool_name}")

    # Emit tool start event (if visualization enabled)
    tool_event_id = None
    parent_id = None
    if should_show_visualization():
        # Get parent event ID for nested tools
        parent_id = get_current_tool_event_id()

        # Convert args to dict for event (using Pydantic v2 model_dump)
        if hasattr(args, "model_dump"):
            args_dict = args.model_dump()
        elif hasattr(args, "dict"):
            # Fallback for Pydantic v1 compatibility
            args_dict = args.dict()
        elif isinstance(args, dict):
            args_dict = args
        else:
            args_dict = {}

        # Sanitize (remove sensitive keys)
        safe_args = {
            k: v
            for k, v in args_dict.items()
            if k not in ["token", "api_key", "password", "secret"]
        }

        event = ToolStartEvent(tool_name=tool_name, arguments=safe_args, parent_id=parent_id)
        tool_event_id = event.event_id
        get_event_emitter().emit(event)

        # Set tool context for child operations (enables nested event display)
        set_current_tool_event_id(tool_event_id)
        logger.debug(f"Set tool context: {tool_name} (event_id: {tool_event_id[:8]}...)")

    start_time = time.time()

    try:
        result = await next(context)
        duration = time.time() - start_time
        logger.info(f"Tool call {tool_name} completed successfully ({duration:.2f}s)")

        # Emit tool complete event
        if should_show_visualization() and tool_event_id:
            # Extract summary from result
            summary = _extract_tool_summary(tool_name, result)
            complete_event = ToolCompleteEvent(
                tool_name=tool_name,
                result_summary=summary,
                duration=duration,
                event_id=tool_event_id,
            )
            get_event_emitter().emit(complete_event)

        return result
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Tool call {tool_name} failed: {e}")

        # Emit tool error event
        if should_show_visualization() and tool_event_id:
            error_event = ToolErrorEvent(
                tool_name=tool_name,
                error_message=str(e),
                duration=duration,
                event_id=tool_event_id,
            )
            get_event_emitter().emit(error_event)

        raise
    finally:
        # Clear tool context when exiting tool (restore parent)
        if should_show_visualization():
            set_current_tool_event_id(parent_id)
            if parent_id:
                logger.debug("Restored parent tool context")
            else:
                logger.debug(f"Cleared tool context: {tool_name}")


def _extract_tool_summary(tool_name: str, result: Any) -> str:
    """Extract human-readable summary from tool result.

    Attempts to extract meaningful summary from common result patterns:
    - Dict with "message" key
    - Dict with "summary" key
    - String result (truncated to 100 chars)
    - Other types return "Complete"

    Args:
        tool_name: Name of the tool
        result: Tool result

    Returns:
        Brief summary string (max 100 chars)

    Example:
        >>> _extract_tool_summary("hello_world", {"message": "Hello, Alice!"})
        'Hello, Alice!'
        >>> _extract_tool_summary("greet_user", "Long result...")
        'Long result...'  # (truncated if > 100 chars)
    """
    if isinstance(result, dict):
        if "message" in result:
            msg = str(result["message"])
            return msg[:100] if len(msg) > 100 else msg
        elif "summary" in result:
            summary = str(result["summary"])
            return summary[:100] if len(summary) > 100 else summary
    elif isinstance(result, str):
        return result[:100] if len(result) > 100 else result

    return "Complete"


# ============================================================================
# Middleware Factory
# ============================================================================


def create_middleware() -> list:
    """Create default middleware for agent and function levels.

    Returns:
        List of middleware (framework auto-categorizes by type)

    Note:
        Memory is handled via ContextProvider, not middleware.
        See MemoryContextProvider for memory management.

    Example:
        >>> from agent.middleware import create_middleware
        >>> middleware = create_middleware()
        >>> agent = chat_client.create_agent(
        ...     name="Agent",
        ...     instructions="...",
        ...     tools=tools,
        ...     middleware=middleware
        ... )
    """
    return [
        agent_run_logging_middleware,
        agent_observability_middleware,
        logging_function_middleware,
    ]


# Backward compatibility
def create_function_middleware() -> list[FunctionMiddleware]:
    """Create list of function middleware (legacy).

    Provided for backward compatibility. Use create_middleware() instead.

    Returns:
        List of function middleware

    Example:
        >>> from agent.middleware import create_function_middleware
        >>> function_mw = create_function_middleware()
    """
    return [cast(FunctionMiddleware, logging_function_middleware)]
