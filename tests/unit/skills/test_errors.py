"""Unit tests for skill error classes."""

import pytest

from agent.skills.errors import (
    SkillDependencyError,
    SkillError,
    SkillManifestError,
    SkillNotFoundError,
    SkillSecurityError,
)


class TestSkillError:
    """Test base SkillError exception."""

    def test_skill_error_is_exception(self):
        """SkillError should inherit from Exception."""
        assert issubclass(SkillError, Exception)

    def test_skill_error_can_be_raised(self):
        """SkillError should be raisable with a message."""
        with pytest.raises(SkillError, match="test error"):
            raise SkillError("test error")

    def test_skill_error_can_be_caught(self):
        """SkillError should be catchable."""
        try:
            raise SkillError("test error")
        except SkillError as e:
            assert str(e) == "test error"


class TestSkillNotFoundError:
    """Test SkillNotFoundError exception."""

    def test_inherits_from_skill_error(self):
        """SkillNotFoundError should inherit from SkillError."""
        assert issubclass(SkillNotFoundError, SkillError)

    def test_can_be_raised_with_message(self):
        """SkillNotFoundError should be raisable with a message."""
        with pytest.raises(SkillNotFoundError, match="Skill 'test' not found"):
            raise SkillNotFoundError("Skill 'test' not found")

    def test_can_be_caught_as_skill_error(self):
        """SkillNotFoundError should be catchable as SkillError."""
        try:
            raise SkillNotFoundError("test")
        except SkillError:
            pass  # Should catch


class TestSkillManifestError:
    """Test SkillManifestError exception."""

    def test_inherits_from_skill_error(self):
        """SkillManifestError should inherit from SkillError."""
        assert issubclass(SkillManifestError, SkillError)

    def test_can_be_raised_with_message(self):
        """SkillManifestError should be raisable with a message."""
        with pytest.raises(SkillManifestError, match="Invalid SKILL.md"):
            raise SkillManifestError("Invalid SKILL.md")

    def test_can_be_caught_as_skill_error(self):
        """SkillManifestError should be catchable as SkillError."""
        try:
            raise SkillManifestError("test")
        except SkillError:
            pass  # Should catch


class TestSkillDependencyError:
    """Test SkillDependencyError exception."""

    def test_inherits_from_skill_error(self):
        """SkillDependencyError should inherit from SkillError."""
        assert issubclass(SkillDependencyError, SkillError)

    def test_can_be_raised_with_message(self):
        """SkillDependencyError should be raisable with a message."""
        with pytest.raises(SkillDependencyError, match="Missing dependency"):
            raise SkillDependencyError("Missing dependency")

    def test_can_be_caught_as_skill_error(self):
        """SkillDependencyError should be catchable as SkillError."""
        try:
            raise SkillDependencyError("test")
        except SkillError:
            pass  # Should catch


class TestSkillSecurityError:
    """Test SkillSecurityError exception."""

    def test_inherits_from_skill_error(self):
        """SkillSecurityError should inherit from SkillError."""
        assert issubclass(SkillSecurityError, SkillError)

    def test_can_be_raised_with_message(self):
        """SkillSecurityError should be raisable with a message."""
        with pytest.raises(SkillSecurityError, match="Invalid skill name"):
            raise SkillSecurityError("Invalid skill name")

    def test_can_be_caught_as_skill_error(self):
        """SkillSecurityError should be catchable as SkillError."""
        try:
            raise SkillSecurityError("test")
        except SkillError:
            pass  # Should catch


class TestErrorHierarchy:
    """Test exception hierarchy behavior."""

    def test_all_skill_errors_catchable_as_skill_error(self):
        """All skill exception types should be catchable as SkillError."""
        exceptions = [
            SkillNotFoundError("test"),
            SkillManifestError("test"),
            SkillDependencyError("test"),
            SkillSecurityError("test"),
        ]

        for exc in exceptions:
            try:
                raise exc
            except SkillError:
                pass  # Should catch all

    def test_specific_errors_not_catchable_by_siblings(self):
        """Specific errors should not be caught by sibling exception types."""
        with pytest.raises(SkillManifestError):
            try:
                raise SkillManifestError("test")
            except SkillNotFoundError:
                pass  # Should NOT catch
