"""Tests for CLI sticky toolbar functionality."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from agent.cli import _get_status_bar_text
from agent.config import AgentConfig


def test_status_bar_returns_formatted_text(mock_config):
    """Test that status bar function returns FormattedText."""
    result = _get_status_bar_text(mock_config)

    # Should return list of (style, text) tuples
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(item, tuple) for item in result)
    assert all(len(item) == 2 for item in result)


def test_status_bar_includes_directory(mock_config):
    """Test that status bar includes current directory."""
    result = _get_status_bar_text(mock_config)

    # Convert FormattedText to string for content check
    text_content = "".join(text for _, text in result)

    # Should contain directory info (at least '/')
    assert "/" in text_content or "~" in text_content


@patch('subprocess.run')
def test_status_bar_includes_git_branch(mock_run, mock_config):
    """Test that git branch is included when available."""
    # Mock git command to return a branch name
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "main\n"
    mock_run.return_value = mock_result

    result = _get_status_bar_text(mock_config)
    text_content = "".join(text for _, text in result)

    # Should contain branch name
    assert "main" in text_content
    assert "⎇" in text_content  # Branch symbol


@patch('subprocess.run')
def test_status_bar_handles_no_git(mock_run, mock_config):
    """Test that status bar works when not in git repo."""
    # Mock git command to fail
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_run.return_value = mock_result

    # Should not raise exception
    result = _get_status_bar_text(mock_config)
    assert isinstance(result, list)


@patch('subprocess.run')
def test_status_bar_handles_git_exception(mock_run, mock_config):
    """Test that status bar handles git command exceptions."""
    # Mock git command to raise exception
    mock_run.side_effect = Exception("Git not found")

    # Should not raise exception
    result = _get_status_bar_text(mock_config)
    assert isinstance(result, list)

    # Should not contain branch info
    text_content = "".join(text for _, text in result)
    assert "⎇" not in text_content


def test_status_bar_includes_model_name(mock_config):
    """Test that model name is displayed."""
    result = _get_status_bar_text(mock_config)
    text_content = "".join(text for _, text in result)

    # Should contain model display name
    model_name = mock_config.get_model_display_name()
    assert model_name in text_content


def test_status_bar_includes_version(mock_config):
    """Test that version is displayed."""
    from agent.cli import __version__

    result = _get_status_bar_text(mock_config)
    text_content = "".join(text for _, text in result)

    # Should contain version
    assert __version__ in text_content


def test_status_bar_styling_classes(mock_config):
    """Test that correct styling classes are applied."""
    result = _get_status_bar_text(mock_config)

    # Check for expected style classes
    styles = [style for style, _ in result]
    assert 'class:toolbar.left' in styles
    assert 'class:toolbar.right' in styles
    assert 'class:toolbar.padding' in styles


def test_status_bar_has_padding(mock_config):
    """Test that status bar includes padding for alignment."""
    result = _get_status_bar_text(mock_config)

    # Should have padding section (middle element)
    assert len(result) == 3
    padding_style, padding_text = result[1]
    assert padding_style == 'class:toolbar.padding'
    assert len(padding_text) > 0  # Should have some padding


@patch('subprocess.run')
def test_status_bar_git_timeout(mock_run, mock_config):
    """Test that git command timeout is handled gracefully."""
    import subprocess

    # Mock git command to timeout
    mock_run.side_effect = subprocess.TimeoutExpired('git', 1)

    # Should not raise exception
    result = _get_status_bar_text(mock_config)
    assert isinstance(result, list)


def test_status_bar_directory_shortening(mock_config):
    """Test that home directory is shortened to ~/."""
    result = _get_status_bar_text(mock_config)
    text_content = "".join(text for _, text in result)

    # If we're in a subdirectory of home, should see ~/
    cwd = Path.cwd()
    try:
        cwd.relative_to(Path.home())
        # We're in home directory or subdirectory
        assert "~/" in text_content
    except ValueError:
        # We're outside home directory
        # Should show full path (will contain /)
        assert "/" in text_content
