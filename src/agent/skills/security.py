"""Security validation for skill subsystem.

This module provides security functions for skill name sanitization,
path validation, and trust management.
"""

import re
from pathlib import Path

from git import Repo

from agent.skills.errors import SkillManifestError, SkillSecurityError


def sanitize_skill_name(name: str) -> str:
    """Validate skill name for security.

    Ensures skill names are safe to use in filesystem paths and prevent
    directory traversal attacks.

    Args:
        name: Skill name to validate

    Returns:
        The validated name (unchanged if valid)

    Raises:
        SkillSecurityError: If name contains invalid characters or patterns

    Examples:
        >>> sanitize_skill_name("kalshi-markets")
        'kalshi-markets'
        >>> sanitize_skill_name("../etc/passwd")
        Traceback (most recent call last):
        ...
        SkillSecurityError: Invalid skill name: '../etc/passwd'
    """
    # Reserved names
    reserved = {".", "..", "~", "__pycache__", ""}
    if name in reserved:
        raise SkillSecurityError(f"Reserved skill name: '{name}'")

    # Reject path traversal patterns (check before regex)
    if ".." in name or name.startswith("/") or name.startswith("\\"):
        raise SkillSecurityError(f"Invalid skill name: '{name}' (path traversal detected)")

    # Reject spaces (check before regex for clearer error)
    if " " in name:
        raise SkillSecurityError(f"Invalid skill name: '{name}' (spaces not allowed)")

    # Must be alphanumeric + hyphens/underscores, 1-64 chars
    if not re.match(r"^[a-zA-Z0-9_-]{1,64}$", name):
        raise SkillSecurityError(
            f"Invalid skill name: '{name}' "
            "(must be alphanumeric with hyphens/underscores, 1-64 chars)"
        )

    return name


def normalize_skill_name(name: str) -> str:
    """Normalize skill name to canonical form.

    Converts to lowercase and replaces underscores with hyphens for
    case-insensitive, format-agnostic matching.

    Args:
        name: Skill name to normalize

    Returns:
        Canonical skill name (lowercase, hyphens)

    Examples:
        >>> normalize_skill_name("Kalshi-Markets")
        'kalshi-markets'
        >>> normalize_skill_name("My_Skill_Name")
        'my-skill-name'
        >>> normalize_skill_name("skill_123")
        'skill-123'
    """
    # First validate (will raise if invalid)
    sanitize_skill_name(name)

    # Convert to lowercase and replace underscores with hyphens
    canonical = name.lower().replace("_", "-")

    return canonical


def normalize_script_name(name: str) -> str:
    """Normalize script name to canonical form.

    Accepts both "status" and "status.py" formats, always returns with .py extension.

    Args:
        name: Script name with or without .py extension

    Returns:
        Canonical script name (lowercase, .py extension)

    Examples:
        >>> normalize_script_name("status")
        'status.py'
        >>> normalize_script_name("Status.py")
        'status.py'
        >>> normalize_script_name("markets")
        'markets.py'
    """
    # Convert to lowercase
    name = name.lower()

    # Add .py extension if missing
    if not name.endswith(".py"):
        name = f"{name}.py"

    return name


def confirm_untrusted_install(skill_name: str, git_url: str) -> bool:
    """Prompt user for confirmation to install untrusted skill.

    Args:
        skill_name: Name of the skill to install
        git_url: Git repository URL

    Returns:
        True if user confirms, False otherwise

    Note:
        This is a placeholder for Phase 2. In Phase 1, bundled skills
        are automatically trusted.
    """
    # Phase 2 implementation: Interactive prompt
    # For now, return True for bundled skills (no git_url)
    # and False for git installs (require explicit --trusted flag)
    if git_url is None:
        return True  # Bundled skills are trusted

    # Phase 2: Use rich.prompt.Confirm for interactive confirmation
    # For now, require explicit trust flag in CLI
    return False


def pin_commit_sha(repo_path: Path) -> str:
    """Get current commit SHA from a git repository.

    Args:
        repo_path: Path to git repository

    Returns:
        Current commit SHA (40-character hex string)

    Raises:
        SkillSecurityError: If repository is invalid or not a git repo

    Examples:
        >>> repo_path = Path("/path/to/skill")
        >>> sha = pin_commit_sha(repo_path)  # doctest: +SKIP
        >>> len(sha)  # doctest: +SKIP
        40
    """
    try:
        repo = Repo(repo_path)
        if repo.head.is_detached:
            # Detached HEAD, use current commit
            return str(repo.head.commit)
        else:
            # On a branch, use branch head
            return str(repo.head.commit)
    except Exception as e:
        raise SkillSecurityError(f"Failed to get commit SHA from {repo_path}: {e}")


def validate_manifest(manifest_path: Path) -> None:
    """Validate SKILL.md manifest file.

    Checks that:
    - File exists
    - Is UTF-8 encoded
    - Has valid YAML front matter
    - Contains required fields

    Args:
        manifest_path: Path to SKILL.md file

    Raises:
        SkillManifestError: If manifest is invalid

    Examples:
        >>> from pathlib import Path
        >>> manifest_path = Path("/path/to/SKILL.md")
        >>> validate_manifest(manifest_path)  # doctest: +SKIP
    """
    if not manifest_path.exists():
        raise SkillManifestError(f"SKILL.md not found at {manifest_path}")

    if not manifest_path.is_file():
        raise SkillManifestError(f"SKILL.md is not a file: {manifest_path}")

    # Check UTF-8 encoding
    try:
        content = manifest_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise SkillManifestError(f"SKILL.md must be UTF-8 encoded: {manifest_path}")

    # Check YAML front matter exists
    if not content.startswith("---"):
        raise SkillManifestError(f"SKILL.md must start with YAML front matter: {manifest_path}")

    # Further validation happens in manifest.parse_skill_manifest()
    # This is just a quick check for file existence and encoding
