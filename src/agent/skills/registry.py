"""Skill registry for tracking installed skills.

This module provides persistence and lookup for installed skills with
atomic file operations and canonical name matching.
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from agent.skills.errors import SkillNotFoundError
from agent.skills.manifest import SkillRegistryEntry
from agent.skills.security import normalize_skill_name


class SkillRegistry:
    """Registry for tracking installed skills with JSON persistence.

    Provides atomic writes and case-insensitive lookups by canonical name.

    Attributes:
        registry_path: Path to registry.json file

    Example:
        >>> registry = SkillRegistry()
        >>> entry = SkillRegistryEntry(
        ...     name="kalshi-markets",
        ...     name_canonical="kalshi-markets",
        ...     installed_path=Path("/path/to/skill"),
        ...     trusted=True
        ... )
        >>> registry.register(entry)
        >>> skill = registry.get("kalshi-markets")
    """

    def __init__(self, registry_path: Path | None = None):
        """Initialize skill registry.

        Args:
            registry_path: Custom registry path (defaults to ~/.agent/skills/registry.json)
        """
        if registry_path is None:
            registry_path = Path.home() / ".agent" / "skills" / "registry.json"

        self.registry_path = registry_path
        self._ensure_registry_dir()

    def _ensure_registry_dir(self) -> None:
        """Ensure registry directory exists."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_registry(self) -> dict[str, Any]:
        """Load registry from JSON file.

        Returns:
            Dictionary mapping canonical names to skill data
        """
        if not self.registry_path.exists():
            return {}

        try:
            with open(self.registry_path, encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)
                # Convert ISO datetime strings back to datetime objects
                for entry in data.values():
                    if "installed_at" in entry:
                        entry["installed_at"] = datetime.fromisoformat(entry["installed_at"])
                    if "installed_path" in entry:
                        entry["installed_path"] = Path(entry["installed_path"])
                return data
        except (json.JSONDecodeError, KeyError):
            # Corrupted registry, start fresh
            return {}

    def _save_registry(self, data: dict[str, Any]) -> None:
        """Save registry to JSON file atomically.

        Uses temp file + os.replace() for atomic writes to prevent corruption.

        Args:
            data: Registry data to save
        """
        # Convert to JSON-serializable format
        serializable = {}
        for canonical_name, entry in data.items():
            entry_copy = entry.copy()
            if "installed_at" in entry_copy and isinstance(entry_copy["installed_at"], datetime):
                entry_copy["installed_at"] = entry_copy["installed_at"].isoformat()
            if "installed_path" in entry_copy and isinstance(entry_copy["installed_path"], Path):
                entry_copy["installed_path"] = str(entry_copy["installed_path"])
            serializable[canonical_name] = entry_copy

        # Atomic write via temp file + os.replace()
        fd, temp_path = tempfile.mkstemp(
            dir=self.registry_path.parent, prefix=".registry-", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(serializable, f, indent=2)
            # Atomic replace (cross-platform safe)
            os.replace(temp_path, self.registry_path)
        except Exception:
            # Clean up temp file on error
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                # Safe to ignore if temp file doesn't exist (already deleted or never created)
                pass
            raise

    def register(self, entry: SkillRegistryEntry) -> None:
        """Register a new skill.

        Args:
            entry: SkillRegistryEntry to add

        Raises:
            ValueError: If skill with canonical name already exists
        """
        data = self._load_registry()

        if entry.name_canonical in data:
            raise ValueError(f"Skill '{entry.name_canonical}' already registered")

        # Convert to dict for storage
        entry_dict = entry.model_dump()
        data[entry.name_canonical] = entry_dict

        self._save_registry(data)

    def unregister(self, canonical_name: str) -> None:
        """Unregister a skill.

        Args:
            canonical_name: Canonical skill name

        Raises:
            SkillNotFoundError: If skill not found in registry
        """
        data = self._load_registry()

        if canonical_name not in data:
            raise SkillNotFoundError(f"Skill '{canonical_name}' not found in registry")

        del data[canonical_name]
        self._save_registry(data)

    def get(self, name: str) -> SkillRegistryEntry:
        """Get skill by name (case-insensitive).

        Args:
            name: Skill name (any case/format)

        Returns:
            SkillRegistryEntry for the skill

        Raises:
            SkillNotFoundError: If skill not found
        """
        canonical_name = normalize_skill_name(name)
        data = self._load_registry()

        if canonical_name not in data:
            raise SkillNotFoundError(f"Skill '{name}' not found in registry")

        return SkillRegistryEntry(**data[canonical_name])

    def get_by_canonical_name(self, canonical_name: str) -> SkillRegistryEntry:
        """Get skill by canonical name (already normalized).

        Args:
            canonical_name: Canonical skill name (lowercase, hyphens)

        Returns:
            SkillRegistryEntry for the skill

        Raises:
            SkillNotFoundError: If skill not found
        """
        data = self._load_registry()

        if canonical_name not in data:
            raise SkillNotFoundError(f"Skill '{canonical_name}' not found in registry")

        return SkillRegistryEntry(**data[canonical_name])

    def list(self) -> list[SkillRegistryEntry]:
        """List all registered skills.

        Returns:
            List of SkillRegistryEntry, sorted by canonical name (stable order)
        """
        data = self._load_registry()

        # Sort by canonical name for stable ordering
        sorted_names = sorted(data.keys())

        return [SkillRegistryEntry(**data[name]) for name in sorted_names]

    def update_sha(self, canonical_name: str, commit_sha: str) -> None:
        """Update commit SHA for a skill.

        Args:
            canonical_name: Canonical skill name
            commit_sha: New commit SHA

        Raises:
            SkillNotFoundError: If skill not found
        """
        data = self._load_registry()

        if canonical_name not in data:
            raise SkillNotFoundError(f"Skill '{canonical_name}' not found in registry")

        data[canonical_name]["commit_sha"] = commit_sha
        self._save_registry(data)

    def exists(self, name: str) -> bool:
        """Check if skill exists in registry.

        Args:
            name: Skill name (any case/format)

        Returns:
            True if skill is registered, False otherwise
        """
        try:
            canonical_name = normalize_skill_name(name)
            data = self._load_registry()
            return canonical_name in data
        except Exception:
            return False
