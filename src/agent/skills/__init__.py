"""Skill subsystem for agent-base.

This module provides a plugin system enabling domain-specific capabilities
through git-based skill packages. Skills support both:
- Structured Python Toolsets: Testable, type-safe tool classes
- Standalone PEP 723 Scripts: Context-efficient, progressive disclosure

Example:
    >>> from agent.skills import SkillLoader
    >>> from agent.config import load_config
    >>> config = load_config()
    >>> loader = SkillLoader(config)
    >>> skill_toolsets, script_tools, skill_instructions = loader.load_enabled_skills()
"""

from agent.skills.errors import (
    SkillDependencyError,
    SkillError,
    SkillManifestError,
    SkillNotFoundError,
    SkillSecurityError,
)
from agent.skills.loader import SkillLoader
from agent.skills.manager import SkillManager
from agent.skills.registry import SkillRegistry

__all__ = [
    "SkillError",
    "SkillNotFoundError",
    "SkillManifestError",
    "SkillDependencyError",
    "SkillSecurityError",
    "SkillLoader",
    "SkillManager",
    "SkillRegistry",
]
