"""Unit tests for skill security validation."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent.skills.errors import SkillManifestError, SkillSecurityError
from agent.skills.security import (
    confirm_untrusted_install,
    normalize_script_name,
    normalize_skill_name,
    pin_commit_sha,
    sanitize_skill_name,
    validate_manifest,
)


class TestSanitizeSkillName:
    """Test sanitize_skill_name function."""

    def test_valid_names(self):
        """Should accept valid skill names."""
        valid_names = [
            "skill",
            "my-skill",
            "my_skill",
            "skill-123",
            "Skill_Name_123",
            "a",  # Single char
            "a" * 64,  # Max length
        ]
        for name in valid_names:
            assert sanitize_skill_name(name) == name

    def test_reject_reserved_names(self):
        """Should reject reserved names."""
        reserved_names = [".", "..", "~", "__pycache__", ""]

        for name in reserved_names:
            with pytest.raises(SkillSecurityError, match="Reserved skill name"):
                sanitize_skill_name(name)

    def test_reject_path_traversal(self):
        """Should reject path traversal patterns."""
        invalid_names = [
            "../skill",
            "../../etc/passwd",
            "skill/../other",
            "../",
        ]

        for name in invalid_names:
            with pytest.raises(SkillSecurityError, match="path traversal"):
                sanitize_skill_name(name)

    def test_reject_absolute_paths(self):
        """Should reject absolute paths."""
        invalid_names = [
            "/etc/passwd",
            "/absolute/path",
            "\\windows\\path",
        ]

        for name in invalid_names:
            with pytest.raises(SkillSecurityError):
                sanitize_skill_name(name)

    def test_reject_special_characters(self):
        """Should reject names with special characters."""
        invalid_names = [
            "skill@special",
            "skill$name",
            "skill!",
            "skill&name",
            "skill*",
        ]

        for name in invalid_names:
            with pytest.raises(SkillSecurityError):
                sanitize_skill_name(name)

    def test_reject_spaces(self):
        """Should reject names with spaces."""
        with pytest.raises(SkillSecurityError, match="spaces not allowed"):
            sanitize_skill_name("skill with spaces")

    def test_reject_too_long(self):
        """Should reject names >64 characters."""
        long_name = "a" * 65
        with pytest.raises(SkillSecurityError):
            sanitize_skill_name(long_name)

    def test_reject_empty_string(self):
        """Should reject empty string as reserved."""
        with pytest.raises(SkillSecurityError, match="Reserved"):
            sanitize_skill_name("")


class TestNormalizeSkillName:
    """Test normalize_skill_name function."""

    def test_lowercase_conversion(self):
        """Should convert to lowercase."""
        assert normalize_skill_name("Kalshi-Markets") == "kalshi-markets"
        assert normalize_skill_name("MY_SKILL") == "my-skill"
        assert normalize_skill_name("MixedCase") == "mixedcase"

    def test_underscore_to_hyphen(self):
        """Should replace underscores with hyphens."""
        assert normalize_skill_name("my_skill") == "my-skill"
        assert normalize_skill_name("skill_123") == "skill-123"
        assert normalize_skill_name("a_b_c") == "a-b-c"

    def test_already_canonical(self):
        """Should handle already-canonical names."""
        canonical = "my-skill-123"
        assert normalize_skill_name(canonical) == canonical

    def test_mixed_transformations(self):
        """Should handle both case and underscore conversion."""
        assert normalize_skill_name("Kalshi_Markets") == "kalshi-markets"
        assert normalize_skill_name("My_Skill_Name") == "my-skill-name"

    def test_validates_before_normalizing(self):
        """Should validate name before normalizing."""
        with pytest.raises(SkillSecurityError):
            normalize_skill_name("../invalid")

        with pytest.raises(SkillSecurityError):
            normalize_skill_name("skill with spaces")


class TestNormalizeScriptName:
    """Test normalize_script_name function."""

    def test_adds_py_extension(self):
        """Should add .py extension if missing."""
        assert normalize_script_name("status") == "status.py"
        assert normalize_script_name("markets") == "markets.py"

    def test_preserves_py_extension(self):
        """Should preserve existing .py extension."""
        assert normalize_script_name("status.py") == "status.py"
        assert normalize_script_name("markets.py") == "markets.py"

    def test_lowercase_conversion(self):
        """Should convert to lowercase."""
        assert normalize_script_name("Status") == "status.py"
        assert normalize_script_name("Markets.py") == "markets.py"
        assert normalize_script_name("SCRIPT") == "script.py"

    def test_combined_transformations(self):
        """Should handle case conversion and extension."""
        assert normalize_script_name("Status") == "status.py"
        assert normalize_script_name("Markets.PY") == "markets.py"


class TestConfirmUntrustedInstall:
    """Test confirm_untrusted_install function."""

    def test_bundled_skills_auto_trusted(self):
        """Should auto-trust bundled skills (no git_url)."""
        result = confirm_untrusted_install("kalshi-markets", None)
        assert result is True

    def test_git_skills_not_auto_trusted(self):
        """Should not auto-trust git skills (Phase 1)."""
        result = confirm_untrusted_install("external-skill", "https://github.com/example/skill")
        assert result is False

    # Phase 2 will add interactive confirmation tests


class TestPinCommitSha:
    """Test pin_commit_sha function."""

    @patch("agent.skills.security.Repo")
    def test_get_sha_from_branch(self, mock_repo_class):
        """Should get commit SHA from branch HEAD."""
        # Mock repository
        mock_repo = MagicMock()
        mock_repo.head.is_detached = False
        mock_repo.head.commit = "abc123def456"
        mock_repo_class.return_value = mock_repo

        repo_path = Path("/fake/repo")
        sha = pin_commit_sha(repo_path)

        assert sha == "abc123def456"
        mock_repo_class.assert_called_once_with(repo_path)

    @patch("agent.skills.security.Repo")
    def test_get_sha_from_detached_head(self, mock_repo_class):
        """Should get commit SHA from detached HEAD."""
        # Mock detached HEAD
        mock_repo = MagicMock()
        mock_repo.head.is_detached = True
        mock_repo.head.commit = "detached123"
        mock_repo_class.return_value = mock_repo

        repo_path = Path("/fake/repo")
        sha = pin_commit_sha(repo_path)

        assert sha == "detached123"

    @patch("agent.skills.security.Repo")
    def test_invalid_repo_raises_error(self, mock_repo_class):
        """Should raise SkillSecurityError for invalid repo."""
        mock_repo_class.side_effect = Exception("Not a git repository")

        repo_path = Path("/not/a/repo")
        with pytest.raises(SkillSecurityError, match="Failed to get commit SHA"):
            pin_commit_sha(repo_path)


class TestValidateManifest:
    """Test validate_manifest function."""

    def test_valid_manifest(self, tmp_path):
        """Should validate a correct SKILL.md."""
        manifest_path = tmp_path / "SKILL.md"
        manifest_path.write_text(
            """---
name: test-skill
description: Test skill
---

# Content
""",
            encoding="utf-8",
        )

        # Should not raise
        validate_manifest(manifest_path)

    def test_missing_file_raises_error(self, tmp_path):
        """Should raise error if SKILL.md doesn't exist."""
        manifest_path = tmp_path / "SKILL.md"

        with pytest.raises(SkillManifestError, match="SKILL.md not found"):
            validate_manifest(manifest_path)

    def test_directory_not_file_raises_error(self, tmp_path):
        """Should raise error if SKILL.md is a directory."""
        manifest_path = tmp_path / "SKILL.md"
        manifest_path.mkdir()

        with pytest.raises(SkillManifestError, match="not a file"):
            validate_manifest(manifest_path)

    def test_non_utf8_encoding_raises_error(self, tmp_path):
        """Should raise error for non-UTF-8 encoding."""
        manifest_path = tmp_path / "SKILL.md"
        # Write invalid UTF-8 bytes
        manifest_path.write_bytes(b"\xff\xfe Invalid UTF-8")

        with pytest.raises(SkillManifestError, match="must be UTF-8 encoded"):
            validate_manifest(manifest_path)

    def test_missing_yaml_frontmatter_raises_error(self, tmp_path):
        """Should raise error if YAML front matter is missing."""
        manifest_path = tmp_path / "SKILL.md"
        manifest_path.write_text(
            """# Just markdown, no YAML

Some content here.
""",
            encoding="utf-8",
        )

        with pytest.raises(SkillManifestError, match="must start with YAML front matter"):
            validate_manifest(manifest_path)


class TestSecurityPatterns:
    """Test comprehensive security patterns."""

    def test_name_equivalence_patterns(self):
        """Test that different formats normalize to same canonical form."""
        # All these should normalize to the same canonical name
        variations = [
            "Kalshi-Markets",
            "kalshi-markets",
            "Kalshi_Markets",
            "kalshi_markets",
            "KALSHI-MARKETS",
        ]

        canonical_names = [normalize_skill_name(v) for v in variations]
        assert len(set(canonical_names)) == 1  # All should be identical
        assert canonical_names[0] == "kalshi-markets"

    def test_script_name_equivalence(self):
        """Test that script names normalize consistently."""
        variations = ["status", "Status", "status.py", "Status.py", "STATUS"]

        canonical_names = [normalize_script_name(v) for v in variations]
        assert len(set(canonical_names)) == 1
        assert canonical_names[0] == "status.py"

    def test_path_injection_attempts(self):
        """Test various path injection attempts are blocked."""
        injection_attempts = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/shadow",
            "\\\\network\\share",
            "skill/../../../secret",
        ]

        for attempt in injection_attempts:
            with pytest.raises(SkillSecurityError):
                sanitize_skill_name(attempt)

    def test_reserved_names_comprehensive(self):
        """Test all reserved names are rejected."""
        reserved = [".", "..", "~", "__pycache__", ""]

        for name in reserved:
            with pytest.raises(SkillSecurityError):
                sanitize_skill_name(name)
