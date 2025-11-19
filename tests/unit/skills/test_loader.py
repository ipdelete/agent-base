"""Unit tests for skill loader."""

from unittest.mock import Mock

import pytest

from agent.skills.errors import SkillManifestError
from agent.skills.loader import SkillLoader
from agent.skills.manifest import SkillManifest


@pytest.fixture
def mock_config():
    """Create mock AgentConfig."""
    config = Mock()
    config.enabled_skills = []
    config.core_skills_dir = None
    config.agent_skills_dir = None
    return config


class TestSkillLoader:
    """Test SkillLoader class."""

    def test_init(self, mock_config):
        """Should initialize with config."""
        loader = SkillLoader(mock_config)
        assert loader.config == mock_config
        assert loader._loaded_scripts == {}

    def test_scan_skill_directory_nonexistent(self, mock_config, tmp_path):
        """Should return empty list for nonexistent directory."""
        loader = SkillLoader(mock_config)
        nonexistent = tmp_path / "nonexistent"
        result = loader.scan_skill_directory(nonexistent)
        assert result == []

    def test_scan_skill_directory_with_skills(self, mock_config, tmp_path):
        """Should find skills with SKILL.md."""
        loader = SkillLoader(mock_config)

        # Create skill directories
        skill1 = tmp_path / "skill1"
        skill1.mkdir()
        (skill1 / "SKILL.md").write_text("---\nname: skill1\ndescription: test\n---\n")

        skill2 = tmp_path / "skill2"
        skill2.mkdir()
        (skill2 / "SKILL.md").write_text("---\nname: skill2\ndescription: test\n---\n")

        # Create directory without SKILL.md (should be ignored)
        no_manifest = tmp_path / "no_manifest"
        no_manifest.mkdir()

        result = loader.scan_skill_directory(tmp_path)
        assert len(result) == 2
        assert skill1 in result
        assert skill2 in result

    def test_discover_scripts_auto_discover(self, mock_config, tmp_path):
        """Should auto-discover scripts from scripts/ directory."""
        loader = SkillLoader(mock_config)

        skill_path = tmp_path / "test-skill"
        scripts_dir = skill_path / "scripts"
        scripts_dir.mkdir(parents=True)

        # Create script files
        (scripts_dir / "status.py").write_text("# status script")
        (scripts_dir / "markets.py").write_text("# markets script")

        manifest = SkillManifest(name="test-skill", description="test", scripts=None)

        scripts = loader.discover_scripts(skill_path, manifest)

        assert len(scripts) == 2
        script_names = [s["name"] for s in scripts]
        assert "status" in script_names
        assert "markets" in script_names

    def test_discover_scripts_explicit_list(self, mock_config, tmp_path):
        """Should use explicit script list from manifest."""
        loader = SkillLoader(mock_config)

        skill_path = tmp_path / "test-skill"
        scripts_dir = skill_path / "scripts"
        scripts_dir.mkdir(parents=True)

        # Create scripts
        (scripts_dir / "status.py").write_text("# status")
        (scripts_dir / "markets.py").write_text("# markets")
        (scripts_dir / "extra.py").write_text("# extra")

        # Manifest only specifies status and markets
        manifest = SkillManifest(
            name="test-skill", description="test", scripts=["status", "markets"]
        )

        scripts = loader.discover_scripts(skill_path, manifest)

        assert len(scripts) == 2
        script_names = [s["name"] for s in scripts]
        assert "status" in script_names
        assert "markets" in script_names
        assert "extra" not in script_names

    def test_discover_scripts_with_ignore_patterns(self, mock_config, tmp_path):
        """Should exclude scripts matching ignore patterns."""
        loader = SkillLoader(mock_config)

        skill_path = tmp_path / "test-skill"
        scripts_dir = skill_path / "scripts"
        scripts_dir.mkdir(parents=True)

        # Create scripts
        (scripts_dir / "status.py").write_text("# status")
        (scripts_dir / "status_test.py").write_text("# test")
        (scripts_dir / "_private.py").write_text("# private")

        manifest = SkillManifest(
            name="test-skill",
            description="test",
            scripts=None,
            scripts_ignore=["*_test.py", "_*.py"],
        )

        scripts = loader.discover_scripts(skill_path, manifest)

        assert len(scripts) == 1
        assert scripts[0]["name"] == "status"

    def test_discover_scripts_no_scripts_dir(self, mock_config, tmp_path):
        """Should return empty list if scripts/ doesn't exist."""
        loader = SkillLoader(mock_config)

        skill_path = tmp_path / "test-skill"
        skill_path.mkdir()

        manifest = SkillManifest(name="test-skill", description="test")

        scripts = loader.discover_scripts(skill_path, manifest)
        assert scripts == []

    def test_load_skill_minimal(self, mock_config, tmp_path):
        """Should load skill with minimal manifest."""
        loader = SkillLoader(mock_config)

        skill_path = tmp_path / "test-skill"
        skill_path.mkdir()
        (skill_path / "SKILL.md").write_text(
            """---
name: test-skill
description: A test skill
---

# Test Skill
"""
        )

        manifest, toolsets, scripts = loader.load_skill(skill_path)

        assert manifest.name == "test-skill"
        assert toolsets == []
        assert scripts == []

    def test_load_skill_with_scripts(self, mock_config, tmp_path):
        """Should load skill with scripts."""
        loader = SkillLoader(mock_config)

        skill_path = tmp_path / "test-skill"
        skill_path.mkdir()
        scripts_dir = skill_path / "scripts"
        scripts_dir.mkdir()

        (skill_path / "SKILL.md").write_text(
            """---
name: test-skill
description: A test skill
---

# Test Skill
"""
        )

        (scripts_dir / "status.py").write_text("# status script")

        manifest, toolsets, scripts = loader.load_skill(skill_path)

        assert manifest.name == "test-skill"
        assert len(scripts) == 1
        assert scripts[0]["name"] == "status"

    def test_load_skill_invalid_manifest(self, mock_config, tmp_path):
        """Should raise SkillManifestError for invalid manifest."""
        loader = SkillLoader(mock_config)

        skill_path = tmp_path / "test-skill"
        skill_path.mkdir()
        (skill_path / "SKILL.md").write_text("Invalid YAML")

        with pytest.raises(SkillManifestError):
            loader.load_skill(skill_path)

    def test_load_enabled_skills_none(self, mock_config):
        """Should return empty lists if no skills enabled."""
        mock_config.enabled_skills = []

        loader = SkillLoader(mock_config)
        toolsets, script_wrapper = loader.load_enabled_skills()

        assert toolsets == []
        assert script_wrapper is None

    def test_load_enabled_skills_none_marker(self, mock_config):
        """Should return empty lists for 'none' marker."""
        mock_config.enabled_skills = ["none"]

        loader = SkillLoader(mock_config)
        toolsets, script_wrapper = loader.load_enabled_skills()

        assert toolsets == []
        assert script_wrapper is None


class TestScriptNameNormalization:
    """Test script name normalization in loader."""

    def test_accepts_both_formats(self, mock_config, tmp_path):
        """Should accept both 'status' and 'status.py' in manifest."""
        loader = SkillLoader(mock_config)

        skill_path = tmp_path / "test-skill"
        scripts_dir = skill_path / "scripts"
        scripts_dir.mkdir(parents=True)

        (scripts_dir / "status.py").write_text("# status")

        # Manifest lists without .py extension
        manifest = SkillManifest(name="test-skill", description="test", scripts=["status"])

        scripts = loader.discover_scripts(skill_path, manifest)

        assert len(scripts) == 1
        assert scripts[0]["name"] == "status"
        assert scripts[0]["path"] == scripts_dir / "status.py"
