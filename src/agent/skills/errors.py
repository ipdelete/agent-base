"""Custom exceptions for skill subsystem.

This module defines a hierarchy of domain-specific exceptions for the
skill plugin system.

Exception Hierarchy:
    SkillError (base)
    ├── SkillNotFoundError
    ├── SkillManifestError
    ├── SkillDependencyError
    └── SkillSecurityError
"""


class SkillError(Exception):
    """Base exception for all skill-related errors.

    All custom exceptions in the skill subsystem inherit from this base class,
    allowing for catch-all error handling when needed.

    Example:
        >>> try:
        ...     # some skill operation
        ...     pass
        ... except SkillError as e:
        ...     print(f"Skill error: {e}")
    """

    pass


class SkillNotFoundError(SkillError):
    """Skill not found in registry or filesystem.

    Raised when attempting to load or use a skill that doesn't exist
    or isn't installed.

    Example:
        >>> raise SkillNotFoundError("Skill 'kalshi-markets' not found")
    """

    pass


class SkillManifestError(SkillError):
    """Skill manifest (SKILL.md) validation or parsing errors.

    Raised when SKILL.md is missing, malformed, or contains invalid
    YAML front matter or required fields.

    Example:
        >>> raise SkillManifestError("Missing required field 'name' in SKILL.md")
    """

    pass


class SkillDependencyError(SkillError):
    """Skill dependency validation errors.

    Raised when a skill's Python dependencies are missing or incompatible,
    or when min/max version requirements aren't met.

    Example:
        >>> raise SkillDependencyError("Skill requires agent-base>=0.2.0, found 0.1.0")
    """

    pass


class SkillSecurityError(SkillError):
    """Skill security validation errors.

    Raised when skill name sanitization fails, path traversal is detected,
    or trust validation fails.

    Example:
        >>> raise SkillSecurityError("Invalid skill name: '../etc/passwd'")
    """

    pass
