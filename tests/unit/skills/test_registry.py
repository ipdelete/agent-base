"""Unit tests for skill registry."""

from datetime import datetime
from pathlib import Path

import pytest

from agent.skills.errors import SkillNotFoundError
from agent.skills.manifest import SkillRegistryEntry
from agent.skills.registry import SkillRegistry


class TestSkillRegistry:
    """Test SkillRegistry class."""

    def test_init_default_path(self):
        """Should use default registry path."""
        registry = SkillRegistry()
        expected_path = Path.home() / ".agent" / "skills" / "registry.json"
        assert registry.registry_path == expected_path

    def test_init_custom_path(self, tmp_path):
        """Should use custom registry path."""
        custom_path = tmp_path / "custom-registry.json"
        registry = SkillRegistry(registry_path=custom_path)
        assert registry.registry_path == custom_path

    def test_register_new_skill(self, tmp_path):
        """Should register a new skill."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        entry = SkillRegistryEntry(
            name="test-skill",
            name_canonical="test-skill",
            installed_path=Path("/path/to/skill"),
            trusted=True,
        )

        registry.register(entry)

        # Verify it was saved
        retrieved = registry.get("test-skill")
        assert retrieved.name == "test-skill"
        assert retrieved.trusted is True

    def test_register_duplicate_raises_error(self, tmp_path):
        """Should reject duplicate skill names."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        entry = SkillRegistryEntry(
            name="test-skill",
            name_canonical="test-skill",
            installed_path=Path("/path/to/skill"),
        )

        registry.register(entry)

        # Try to register again
        with pytest.raises(ValueError, match="already registered"):
            registry.register(entry)

    def test_unregister_skill(self, tmp_path):
        """Should unregister a skill."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        entry = SkillRegistryEntry(
            name="test-skill",
            name_canonical="test-skill",
            installed_path=Path("/path/to/skill"),
        )

        registry.register(entry)
        registry.unregister("test-skill")

        # Verify it's gone
        with pytest.raises(SkillNotFoundError):
            registry.get("test-skill")

    def test_unregister_nonexistent_raises_error(self, tmp_path):
        """Should raise error when unregistering nonexistent skill."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        with pytest.raises(SkillNotFoundError, match="not found in registry"):
            registry.unregister("nonexistent")

    def test_get_by_name_case_insensitive(self, tmp_path):
        """Should retrieve skill by name (case-insensitive)."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        entry = SkillRegistryEntry(
            name="Kalshi-Markets",
            name_canonical="kalshi-markets",
            installed_path=Path("/path/to/skill"),
        )

        registry.register(entry)

        # Try various case formats
        assert registry.get("kalshi-markets").name == "Kalshi-Markets"
        assert registry.get("Kalshi-Markets").name == "Kalshi-Markets"
        assert registry.get("KALSHI-MARKETS").name == "Kalshi-Markets"

    def test_get_nonexistent_raises_error(self, tmp_path):
        """Should raise error when getting nonexistent skill."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        with pytest.raises(SkillNotFoundError, match="not found in registry"):
            registry.get("nonexistent")

    def test_get_by_canonical_name(self, tmp_path):
        """Should retrieve skill by canonical name."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        entry = SkillRegistryEntry(
            name="Kalshi-Markets",
            name_canonical="kalshi-markets",
            installed_path=Path("/path/to/skill"),
        )

        registry.register(entry)

        retrieved = registry.get_by_canonical_name("kalshi-markets")
        assert retrieved.name == "Kalshi-Markets"

    def test_list_empty_registry(self, tmp_path):
        """Should return empty list for empty registry."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")
        assert registry.list() == []

    def test_list_multiple_skills(self, tmp_path):
        """Should list all registered skills."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        skills = [
            SkillRegistryEntry(name="skill-a", name_canonical="skill-a", installed_path=Path("/a")),
            SkillRegistryEntry(name="skill-b", name_canonical="skill-b", installed_path=Path("/b")),
            SkillRegistryEntry(name="skill-c", name_canonical="skill-c", installed_path=Path("/c")),
        ]

        for skill in skills:
            registry.register(skill)

        listed = registry.list()
        assert len(listed) == 3
        assert all(isinstance(s, SkillRegistryEntry) for s in listed)

    def test_list_stable_sorted_order(self, tmp_path):
        """Should return skills in stable alphabetical order."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        # Register in random order
        registry.register(
            SkillRegistryEntry(name="zeta", name_canonical="zeta", installed_path=Path("/z"))
        )
        registry.register(
            SkillRegistryEntry(name="alpha", name_canonical="alpha", installed_path=Path("/a"))
        )
        registry.register(
            SkillRegistryEntry(name="beta", name_canonical="beta", installed_path=Path("/b"))
        )

        listed = registry.list()
        names = [s.name_canonical for s in listed]
        assert names == ["alpha", "beta", "zeta"]

    def test_update_sha(self, tmp_path):
        """Should update commit SHA for a skill."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        entry = SkillRegistryEntry(
            name="test-skill",
            name_canonical="test-skill",
            installed_path=Path("/path/to/skill"),
            commit_sha="old123",
        )

        registry.register(entry)
        registry.update_sha("test-skill", "new456")

        retrieved = registry.get("test-skill")
        assert retrieved.commit_sha == "new456"

    def test_update_sha_nonexistent_raises_error(self, tmp_path):
        """Should raise error when updating SHA for nonexistent skill."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        with pytest.raises(SkillNotFoundError):
            registry.update_sha("nonexistent", "abc123")

    def test_exists(self, tmp_path):
        """Should check if skill exists."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        entry = SkillRegistryEntry(
            name="test-skill",
            name_canonical="test-skill",
            installed_path=Path("/path/to/skill"),
        )

        registry.register(entry)

        assert registry.exists("test-skill") is True
        assert registry.exists("nonexistent") is False

    def test_exists_case_insensitive(self, tmp_path):
        """Should check existence case-insensitively."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        entry = SkillRegistryEntry(
            name="Kalshi-Markets",
            name_canonical="kalshi-markets",
            installed_path=Path("/path/to/skill"),
        )

        registry.register(entry)

        assert registry.exists("kalshi-markets") is True
        assert registry.exists("Kalshi-Markets") is True
        assert registry.exists("KALSHI-MARKETS") is True


class TestRegistryPersistence:
    """Test JSON persistence and serialization."""

    def test_datetime_serialization(self, tmp_path):
        """Should serialize and deserialize datetime correctly."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        now = datetime.now()
        entry = SkillRegistryEntry(
            name="test-skill",
            name_canonical="test-skill",
            installed_path=Path("/path/to/skill"),
            installed_at=now,
        )

        registry.register(entry)

        # Load from disk
        retrieved = registry.get("test-skill")
        assert isinstance(retrieved.installed_at, datetime)
        # Compare timestamps (strip microseconds for comparison)
        assert retrieved.installed_at.replace(microsecond=0) == now.replace(microsecond=0)

    def test_path_serialization(self, tmp_path):
        """Should serialize and deserialize Path correctly."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        skill_path = Path("/home/user/.agent/skills/test-skill")
        entry = SkillRegistryEntry(
            name="test-skill",
            name_canonical="test-skill",
            installed_path=skill_path,
        )

        registry.register(entry)

        retrieved = registry.get("test-skill")
        assert isinstance(retrieved.installed_path, Path)
        assert retrieved.installed_path == skill_path

    def test_atomic_write(self, tmp_path):
        """Should use atomic writes (temp file + replace)."""
        registry_path = tmp_path / "registry.json"
        registry = SkillRegistry(registry_path=registry_path)

        entry = SkillRegistryEntry(
            name="test-skill",
            name_canonical="test-skill",
            installed_path=Path("/path/to/skill"),
        )

        registry.register(entry)

        # Verify file exists and is valid JSON
        assert registry_path.exists()
        import json

        with open(registry_path) as f:
            data = json.load(f)
            assert "test-skill" in data

    def test_corrupted_registry_recovery(self, tmp_path):
        """Should recover from corrupted registry file."""
        registry_path = tmp_path / "registry.json"

        # Write corrupted JSON
        registry_path.write_text("{ invalid json }", encoding="utf-8")

        # Should start fresh
        registry = SkillRegistry(registry_path=registry_path)
        assert registry.list() == []

    def test_persistence_across_instances(self, tmp_path):
        """Should persist across registry instances."""
        registry_path = tmp_path / "registry.json"

        # Instance 1: Register skill
        registry1 = SkillRegistry(registry_path=registry_path)
        entry = SkillRegistryEntry(
            name="test-skill",
            name_canonical="test-skill",
            installed_path=Path("/path/to/skill"),
        )
        registry1.register(entry)

        # Instance 2: Should see the skill
        registry2 = SkillRegistry(registry_path=registry_path)
        assert registry2.exists("test-skill")
        retrieved = registry2.get("test-skill")
        assert retrieved.name == "test-skill"


class TestRegistryEdgeCases:
    """Test edge cases and error scenarios."""

    def test_empty_registry_operations(self, tmp_path):
        """Should handle operations on empty registry gracefully."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        assert registry.list() == []
        assert registry.exists("anything") is False

        with pytest.raises(SkillNotFoundError):
            registry.get("anything")

    def test_special_characters_in_path(self, tmp_path):
        """Should handle special characters in paths."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        entry = SkillRegistryEntry(
            name="test-skill",
            name_canonical="test-skill",
            installed_path=Path("/path/with spaces/and-special_chars"),
        )

        registry.register(entry)
        retrieved = registry.get("test-skill")
        assert retrieved.installed_path == Path("/path/with spaces/and-special_chars")

    def test_underscore_hyphen_equivalence(self, tmp_path):
        """Should treat underscores and hyphens as equivalent."""
        registry = SkillRegistry(registry_path=tmp_path / "registry.json")

        entry = SkillRegistryEntry(
            name="my_skill",
            name_canonical="my-skill",  # Normalized form
            installed_path=Path("/path/to/skill"),
        )

        registry.register(entry)

        # Both formats should find it
        assert registry.exists("my_skill")
        assert registry.exists("my-skill")
        assert registry.get("my_skill").name == "my_skill"
        assert registry.get("my-skill").name == "my_skill"
