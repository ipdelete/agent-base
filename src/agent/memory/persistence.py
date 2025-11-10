"""Memory persistence utilities.

This module provides serialization and persistence for memory state.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class MemoryPersistence:
    """Helper class for memory serialization and persistence.

    Provides JSON-based serialization for memory state with version
    compatibility handling. Follows ThreadPersistence patterns.

    Example:
        >>> persistence = MemoryPersistence()
        >>> await persistence.save(memory_data, Path("memory.json"))
    """

    VERSION = "1.0"

    def __init__(self, storage_dir: Path | None = None):
        """Initialize memory persistence helper.

        Args:
            storage_dir: Directory for memory storage (default: ~/.agent/memory)
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".agent" / "memory"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Memory persistence initialized: {self.storage_dir}")

    async def save(self, memory_data: list[dict], file_path: Path) -> None:
        """Save memory state to file.

        Args:
            memory_data: List of memory entries to serialize
            file_path: Path to save file

        Raises:
            Exception: If serialization or save fails

        Example:
            >>> memories = [{"role": "user", "content": "Hello"}]
            >>> await persistence.save(memories, Path("session-1-memory.json"))
        """
        try:
            # Build memory state with metadata
            state = {
                "version": self.VERSION,
                "saved_at": datetime.now().isoformat(),
                "memory_count": len(memory_data),
                "memories": memory_data,
            }

            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Save to file
            with open(file_path, "w") as f:
                json.dump(state, f, indent=2)

            logger.info(f"Saved {len(memory_data)} memories to {file_path}")

        except Exception as e:
            logger.error(f"Failed to save memory state: {e}")
            raise

    async def load(self, file_path: Path) -> list[dict] | None:
        """Load memory state from file.

        Args:
            file_path: Path to memory file

        Returns:
            List of memory entries or None if file doesn't exist

        Raises:
            Exception: If deserialization fails

        Example:
            >>> memories = await persistence.load(Path("session-1-memory.json"))
        """
        if not file_path.exists():
            logger.debug(f"Memory file not found: {file_path}")
            return None

        try:
            with open(file_path) as f:
                state = json.load(f)

            # Version compatibility check
            version = state.get("version", "unknown")
            if version != self.VERSION:
                logger.warning(f"Memory version mismatch: {version} != {self.VERSION}")
                # Future: Handle version migrations here

            memories: list[dict] = state.get("memories", [])
            logger.info(f"Loaded {len(memories)} memories from {file_path}")

            return memories

        except Exception as e:
            logger.error(f"Failed to load memory state: {e}")
            raise

    def get_memory_path(self, session_name: str) -> Path:
        """Get memory file path for a session.

        Args:
            session_name: Name of the session

        Returns:
            Path to memory file for the session

        Example:
            >>> path = persistence.get_memory_path("session-1")
            >>> str(path)
            '~/.agent/memory/session-1-memory.json'
        """
        return self.storage_dir / f"{session_name}-memory.json"
