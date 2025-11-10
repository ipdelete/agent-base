"""Memory management for Agent conversations.

This module provides in-memory storage capabilities for maintaining conversation
context across multiple interactions, enabling agents to remember preferences,
recall previous conversations, and provide personalized experiences.

Key Components:
    - MemoryManager: Abstract base class for memory operations
    - InMemoryStore: In-memory implementation of memory storage
    - MemoryPersistence: Serialization and persistence utilities

Example:
    >>> from agent.memory import create_memory_manager
    >>> memory = create_memory_manager(config)
    >>> await memory.add([{"role": "user", "content": "Hello"}])
"""

from typing import TYPE_CHECKING

from agent.memory.context_provider import MemoryContextProvider
from agent.memory.manager import MemoryManager
from agent.memory.store import InMemoryStore

if TYPE_CHECKING:
    from agent.config import AgentConfig

__all__ = ["MemoryManager", "InMemoryStore", "MemoryContextProvider", "create_memory_manager"]


def create_memory_manager(config: "AgentConfig") -> MemoryManager:
    """Factory function to create memory manager based on config.

    Args:
        config: AgentConfig instance with memory settings

    Returns:
        MemoryManager instance (InMemoryStore by default)

    Example:
        >>> config = AgentConfig(memory_enabled=True, memory_type="in_memory")
        >>> manager = create_memory_manager(config)
    """
    # For now, only in_memory is supported
    # Future: Add support for external memory services (mem0, langchain, etc.)
    return InMemoryStore(config)
