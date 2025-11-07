"""Activity tracking for Agent.

This module provides a singleton for tracking the current activity/operation
being performed by the agent. Useful for status displays and progress tracking.

Adapted from butler-agent for agent-template.
"""

from typing import Optional


class ActivityTracker:
    """Singleton for tracking current agent activity.

    Example:
        >>> from agent.activity import activity_tracker
        >>> activity_tracker.set_activity("Executing tool: hello_world")
        >>> activity_tracker.get_current()
        'Executing tool: hello_world'
        >>> activity_tracker.reset()
    """

    _instance: Optional["ActivityTracker"] = None
    _current_activity: str | None = None

    def __new__(cls) -> "ActivityTracker":
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_activity(self, message: str) -> None:
        """Set the current activity message.

        Args:
            message: Description of current activity

        Example:
            >>> activity_tracker.set_activity("Processing request")
        """
        self._current_activity = message

    def get_current(self) -> str | None:
        """Get the current activity message.

        Returns:
            Current activity message or None if no activity set

        Example:
            >>> activity_tracker.get_current()
            'Processing request'
        """
        return self._current_activity

    def reset(self) -> None:
        """Reset the current activity.

        Example:
            >>> activity_tracker.reset()
            >>> activity_tracker.get_current()
            None
        """
        self._current_activity = None


# Global instance
activity_tracker = ActivityTracker()
