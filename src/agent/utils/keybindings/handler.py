"""Abstract base class for keybinding handlers.

Provides extensible keybinding system for prompt_toolkit integration.
Adapted from butler-agent for agent-template.
"""

from abc import ABC, abstractmethod
from typing import Any


class KeybindingHandler(ABC):
    """Abstract base class for keybinding handlers.

    Handlers define:
    - trigger_key: Which key activates this handler
    - description: Human-readable description
    - handle: What happens when key is pressed

    Example:
        >>> class MyHandler(KeybindingHandler):
        ...     @property
        ...     def trigger_key(self) -> str:
        ...         return "c-x"  # Ctrl+X
        ...     @property
        ...     def description(self) -> str:
        ...         return "Exit application"
        ...     def handle(self, event: Any) -> None:
        ...         event.app.exit()
    """

    @property
    @abstractmethod
    def trigger_key(self) -> str:
        """prompt_toolkit key name (e.g., 'escape', 'c-x', 'f1').

        Returns:
            Key identifier string

        Common keys:
            - 'escape' - ESC key
            - 'c-x' - Ctrl+X
            - 'c-c' - Ctrl+C
            - 'f1' through 'f12' - Function keys
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this handler does.

        Returns:
            Description string

        Example:
            "Clear the current prompt text"
        """
        pass

    @abstractmethod
    def handle(self, event: Any) -> None:
        """Handle the key press event.

        Args:
            event: prompt_toolkit key event

        Example:
            >>> def handle(self, event):
            ...     event.app.current_buffer.text = ""
        """
        pass
