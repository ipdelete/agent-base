"""In-memory implementation of memory storage.

This module provides the default in-memory storage for agent memories.
"""

import logging
from datetime import datetime

from agent.config.schema import AgentSettings
from agent.memory.manager import MemoryManager

logger = logging.getLogger(__name__)


class InMemoryStore(MemoryManager):
    """In-memory storage implementation for agent memories.

    Stores messages with metadata in memory, providing search, filtering,
    and retrieval capabilities without external dependencies.

    Attributes:
        config: Agent configuration
        memories: List of stored memory entries

    Example:
        >>> config = AgentConfig(memory_enabled=True)
        >>> store = InMemoryStore(config)
        >>> await store.add([{"role": "user", "content": "Hello"}])
    """

    def __init__(self, config: AgentSettings):
        """Initialize in-memory store.

        Args:
            config: Agent configuration with memory settings
        """
        super().__init__(config)
        self.memories: list[dict] = []

    async def add(self, messages: list[dict]) -> dict:
        """Add messages to memory storage.

        Each message is stored with metadata including timestamp, type, and content.
        Messages are stored in chronological order.

        Args:
            messages: List of message dicts with role and content

        Returns:
            Structured response dict with success status and added memory IDs

        Example:
            >>> await store.add([
            ...     {"role": "user", "content": "My name is Alice"},
            ...     {"role": "assistant", "content": "Nice to meet you, Alice!"}
            ... ])
        """
        if not messages:
            return self._create_error_response(
                error="invalid_input", message="No messages provided"
            )

        added_memories = []

        for msg in messages:
            # Validate message structure
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                logger.warning(f"Skipping invalid message: {msg}")
                continue

            # Create memory entry with metadata (timestamp per message for accuracy)
            memory_entry = {
                "id": len(self.memories),  # Simple incrementing ID
                "role": msg.get("role", "unknown"),
                "content": msg.get("content", ""),
                "timestamp": datetime.now().isoformat(),
                "metadata": msg.get("metadata", {}),
            }

            self.memories.append(memory_entry)
            added_memories.append(memory_entry["id"])

        logger.debug(f"Added {len(added_memories)} messages to memory")

        return self._create_success_response(
            result=added_memories, message=f"Added {len(added_memories)} messages to memory"
        )

    async def search(self, query: str, limit: int = 5) -> dict:
        """Search memories by keyword query.

        Performs case-insensitive keyword search across message content.
        Returns memories ranked by relevance (number of keyword matches).

        Args:
            query: Search query string (keywords)
            limit: Maximum number of results

        Returns:
            Structured response dict with matching memories

        Example:
            >>> result = await store.search("Alice name", limit=5)
        """
        if not query or not query.strip():
            return self._create_error_response(
                error="invalid_query", message="Search query cannot be empty"
            )

        query_lower = query.lower()
        keywords = query_lower.split()

        # Search and rank by relevance
        matches = []
        for memory in self.memories:
            content_lower = memory.get("content", "").lower()

            # Count keyword matches
            match_count = sum(1 for keyword in keywords if keyword in content_lower)

            if match_count > 0:
                matches.append((memory, match_count))

        # Sort by relevance (match count) and recency
        matches.sort(key=lambda x: (x[1], x[0].get("timestamp", "")), reverse=True)

        # Extract top matches
        results = [match[0] for match in matches[:limit]]

        logger.debug(f"Search for '{query}' returned {len(results)} results")

        return self._create_success_response(
            result=results,
            message=f"Found {len(results)} matching memories for query: {query}",
        )

    async def get_all(self) -> dict:
        """Get all memories from storage.

        Returns:
            Structured response dict with all memories
        """
        return self._create_success_response(result=self.memories, message="Retrieved all memories")

    async def get_recent(self, limit: int = 10) -> dict:
        """Get recent memories.

        Returns the most recent memories based on storage order (chronological).
        More recent memories are at the end of the list.

        Args:
            limit: Number of recent memories to retrieve

        Returns:
            Structured response dict with recent memories
        """
        recent = self.memories[-limit:] if self.memories else []
        return self._create_success_response(
            result=recent, message=f"Retrieved {len(recent)} recent memories"
        )

    async def clear(self) -> dict:
        """Clear all memories from storage.

        Returns:
            Structured response dict with success status
        """
        count = len(self.memories)
        self.memories = []
        return self._create_success_response(result=None, message=f"Cleared {count} memories")
