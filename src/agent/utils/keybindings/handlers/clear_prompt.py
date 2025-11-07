"""Clear prompt keybinding handler.

Provides ESC key handler to clear the current prompt text.
Adapted from butler-agent for agent-template.
"""

from typing import Any

from agent.utils.keybindings.handler import KeybindingHandler


class ClearPromptHandler(KeybindingHandler):
    """Handler for clearing prompt text with ESC key.

    Example:
        >>> handler = ClearPromptHandler()
        >>> handler.trigger_key
        'escape'
    """

    @property
    def trigger_key(self) -> str:
        """ESC key clears prompt.

        Returns:
            'escape' key identifier
        """
        return "escape"

    @property
    def description(self) -> str:
        """Description of handler behavior.

        Returns:
            Description string
        """
        return "Clear the current prompt text"

    def handle(self, event: Any) -> None:
        """Clear the current buffer text.

        Args:
            event: prompt_toolkit key event with app.current_buffer
        """
        event.app.current_buffer.text = ""
