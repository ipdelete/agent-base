"""Unit tests for skill manifest parsing."""

from datetime import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from agent.skills.errors import SkillManifestError
from agent.skills.manifest import (
    SkillManifest,
    SkillRegistryEntry,
    extract_yaml_frontmatter,
    parse_skill_manifest,
)


class TestSkillManifest:
    """Test SkillManifest Pydantic model."""

    def test_minimal_valid_manifest(self):
        """Should accept minimal required fields."""
        manifest = SkillManifest(
            name="test-skill",
            description="A test skill for unit testing",
        )
        assert manifest.name == "test-skill"
        assert manifest.description == "A test skill for unit testing"
        assert manifest.version is None
        assert manifest.toolsets == []
        assert manifest.scripts is None

    def test_full_manifest(self):
        """Should accept all fields."""
        manifest = SkillManifest(
            name="kalshi-markets",
            description="Access Kalshi prediction market data",
            version="1.0.0",
            author="Test Author",
            repository="https://github.com/example/kalshi-markets",
            license="MIT",
            min_agent_base_version="0.1.0",
            max_agent_base_version="1.0.0",
            toolsets=["toolsets.hello:HelloExtended"],
            scripts=["status", "markets"],
            scripts_ignore=["*_test.py", "_*.py"],
            permissions={"env": ["KALSHI_API_KEY"]},
            instructions="# Usage instructions\n\nSome markdown here",
        )
        assert manifest.name == "kalshi-markets"
        assert manifest.version == "1.0.0"
        assert len(manifest.toolsets) == 1
        assert len(manifest.scripts) == 2
        assert len(manifest.scripts_ignore) == 2

    def test_name_validation_alphanumeric_hyphens(self):
        """Should accept alphanumeric + hyphens/underscores."""
        valid_names = [
            "skill",
            "my-skill",
            "my_skill",
            "skill-123",
            "Skill_Name_123",
        ]
        for name in valid_names:
            manifest = SkillManifest(name=name, description="test")
            assert manifest.name == name

    def test_name_validation_rejects_invalid(self):
        """Should reject invalid skill names."""
        invalid_names = [
            "../skill",  # Path traversal
            "/absolute/path",  # Absolute path
            "skill with spaces",  # Spaces
            "skill@special",  # Special chars
            "",  # Empty
            "a" * 65,  # Too long (>64 chars)
        ]
        for name in invalid_names:
            with pytest.raises(ValidationError):
                SkillManifest(name=name, description="test")

    def test_description_required(self):
        """Should reject missing description."""
        with pytest.raises(ValidationError):
            SkillManifest(name="test-skill")

    def test_description_max_length(self):
        """Should reject description >500 chars."""
        long_desc = "a" * 501
        with pytest.raises(ValidationError):
            SkillManifest(name="test-skill", description=long_desc)

    def test_toolsets_format_validation(self):
        """Should validate toolsets are in 'module:Class' format."""
        # Valid format
        manifest = SkillManifest(
            name="test",
            description="test",
            toolsets=["toolsets.hello:HelloExtended", "tools.utils:HelperTools"],
        )
        assert len(manifest.toolsets) == 2

        # Invalid format (missing colon)
        with pytest.raises(ValidationError, match="must be in 'module:Class' format"):
            SkillManifest(
                name="test",
                description="test",
                toolsets=["toolsets.hello"],  # Missing :Class
            )

    def test_scripts_accepts_both_formats(self):
        """Should accept both 'status' and 'status.py' formats."""
        manifest = SkillManifest(
            name="test",
            description="test",
            scripts=["status", "markets.py", "search"],
        )
        assert manifest.scripts == ["status", "markets.py", "search"]

    def test_scripts_none_means_auto_discover(self):
        """scripts=None should indicate auto-discovery."""
        manifest = SkillManifest(name="test", description="test")
        assert manifest.scripts is None


class TestSkillRegistryEntry:
    """Test SkillRegistryEntry Pydantic model."""

    def test_minimal_registry_entry(self):
        """Should create minimal registry entry."""
        entry = SkillRegistryEntry(
            name="test-skill",
            name_canonical="test-skill",
            installed_path=Path("/path/to/skill"),
        )
        assert entry.name == "test-skill"
        assert entry.name_canonical == "test-skill"
        assert entry.git_url is None
        assert entry.trusted is False
        assert isinstance(entry.installed_at, datetime)

    def test_full_registry_entry(self):
        """Should create full registry entry with all fields."""
        now = datetime.now()
        entry = SkillRegistryEntry(
            name="Kalshi-Markets",
            name_canonical="kalshi-markets",
            git_url="https://github.com/example/kalshi-markets",
            commit_sha="abc123def456",
            branch="main",
            tag="v1.0.0",
            installed_path=Path("/path/to/skill"),
            trusted=True,
            installed_at=now,
        )
        assert entry.name == "Kalshi-Markets"
        assert entry.name_canonical == "kalshi-markets"
        assert entry.commit_sha == "abc123def456"
        assert entry.trusted is True
        assert entry.installed_at == now

    def test_path_serialization(self):
        """Should serialize Path to string."""
        entry = SkillRegistryEntry(
            name="test",
            name_canonical="test",
            installed_path=Path("/path/to/skill"),
        )
        # Pydantic v2 uses model_dump for JSON serialization
        data = entry.model_dump(mode="json")
        assert isinstance(data["installed_path"], str)
        assert data["installed_path"] == "/path/to/skill"


class TestExtractYamlFrontmatter:
    """Test YAML front matter extraction."""

    def test_valid_frontmatter(self):
        """Should extract YAML and markdown correctly."""
        content = """---
name: test-skill
description: A test skill
version: 1.0.0
---

# Test Skill

This is the markdown content.
"""
        yaml_data, markdown = extract_yaml_frontmatter(content)

        assert yaml_data["name"] == "test-skill"
        assert yaml_data["description"] == "A test skill"
        assert yaml_data["version"] == "1.0.0"
        assert markdown.startswith("# Test Skill")

    def test_missing_frontmatter(self):
        """Should raise error if YAML front matter is missing."""
        content = "# Just markdown, no YAML"

        with pytest.raises(SkillManifestError, match="must start with YAML front matter"):
            extract_yaml_frontmatter(content)

    def test_malformed_yaml(self):
        """Should raise error for malformed YAML."""
        content = """---
name: test
  invalid: indentation:
description: bad
---

# Content
"""
        with pytest.raises(SkillManifestError, match="Invalid YAML front matter"):
            extract_yaml_frontmatter(content)

    def test_yaml_not_dict(self):
        """Should raise error if YAML is not a dictionary."""
        content = """---
- item1
- item2
---

# Content
"""
        with pytest.raises(SkillManifestError, match="must be a dictionary"):
            extract_yaml_frontmatter(content)

    def test_empty_markdown(self):
        """Should handle empty markdown section."""
        content = """---
name: test
description: test
---

"""
        yaml_data, markdown = extract_yaml_frontmatter(content)
        assert yaml_data["name"] == "test"
        assert markdown == ""

    def test_multiline_yaml_values(self):
        """Should handle multiline YAML values."""
        content = """---
name: test
description: |
  This is a multiline
  description value
---

# Content
"""
        yaml_data, markdown = extract_yaml_frontmatter(content)
        assert "multiline" in yaml_data["description"]


class TestParseSkillManifest:
    """Test parse_skill_manifest function."""

    def test_parse_valid_manifest(self, tmp_path):
        """Should parse valid SKILL.md file."""
        skill_path = tmp_path / "test-skill"
        skill_path.mkdir()

        manifest_content = """---
name: test-skill
description: A test skill for unit testing
version: 1.0.0
toolsets:
  - toolsets.hello:HelloExtended
---

# Test Skill

Usage instructions here.
"""
        (skill_path / "SKILL.md").write_text(manifest_content, encoding="utf-8")

        manifest = parse_skill_manifest(skill_path)

        assert manifest.name == "test-skill"
        assert manifest.description == "A test skill for unit testing"
        assert manifest.version == "1.0.0"
        assert len(manifest.toolsets) == 1
        assert "Usage instructions" in manifest.instructions

    def test_missing_skill_md(self, tmp_path):
        """Should raise error if SKILL.md doesn't exist."""
        skill_path = tmp_path / "no-manifest"
        skill_path.mkdir()

        with pytest.raises(SkillManifestError, match="SKILL.md not found"):
            parse_skill_manifest(skill_path)

    def test_non_utf8_encoding(self, tmp_path):
        """Should raise error for non-UTF-8 encoding."""
        skill_path = tmp_path / "bad-encoding"
        skill_path.mkdir()

        # Write with Latin-1 encoding containing non-UTF-8 bytes
        (skill_path / "SKILL.md").write_bytes(b"\xff\xfe Invalid UTF-8")

        with pytest.raises(SkillManifestError, match="must be UTF-8 encoded"):
            parse_skill_manifest(skill_path)

    def test_invalid_manifest_data(self, tmp_path):
        """Should raise error for invalid manifest fields."""
        skill_path = tmp_path / "invalid-manifest"
        skill_path.mkdir()

        # Missing required 'description' field
        manifest_content = """---
name: test-skill
---

# Content
"""
        (skill_path / "SKILL.md").write_text(manifest_content, encoding="utf-8")

        with pytest.raises(SkillManifestError, match="Invalid SKILL.md manifest"):
            parse_skill_manifest(skill_path)

    def test_kalshi_markets_example(self, tmp_path):
        """Should parse kalshi-markets style manifest."""
        skill_path = tmp_path / "kalshi-markets"
        skill_path.mkdir()

        manifest_content = """---
name: kalshi-markets
description: Access Kalshi prediction market data including market prices, orderbooks, trades, events, and series information.
version: 1.0.0
author: Example Author
repository: https://github.com/example/kalshi-markets-skill
---

# Kalshi Markets

Instructions for using this skill...

## Available Scripts

### `scripts/status.py`
**When to use:** Check if Kalshi exchange is operational
"""
        (skill_path / "SKILL.md").write_text(manifest_content, encoding="utf-8")

        manifest = parse_skill_manifest(skill_path)

        assert manifest.name == "kalshi-markets"
        assert "prediction market" in manifest.description
        assert manifest.version == "1.0.0"
        assert manifest.author == "Example Author"
        assert "Available Scripts" in manifest.instructions
