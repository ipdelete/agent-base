"""Integration tests for session persistence.

Tests save/load cycle with real agent and thread operations.
"""

from pathlib import Path
from typing import Any

import pytest

from agent.agent import Agent
from agent.config import AgentConfig
from agent.persistence import ThreadPersistence


@pytest.fixture
def temp_session_dir(tmp_path: Path) -> Path:
    """Create temporary session directory."""
    session_dir = tmp_path / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


@pytest.fixture
def persistence(temp_session_dir: Path) -> ThreadPersistence:
    """Create ThreadPersistence with temporary directory."""
    return ThreadPersistence(storage_dir=temp_session_dir)


@pytest.fixture
def agent_instance(mock_config: AgentConfig, mock_chat_client: Any) -> Agent:
    """Create agent instance for testing."""
    return Agent(config=mock_config, chat_client=mock_chat_client)


@pytest.mark.asyncio
async def test_delete_session(
    persistence: ThreadPersistence,
):
    """Test session deletion without requiring thread creation."""
    # Create a dummy session file directly (bypass thread requirement)
    import json
    from datetime import datetime

    session_name = "session-to-delete"
    session_file = persistence.storage_dir / f"{session_name}.json"

    dummy_data = {
        "name": session_name,
        "created_at": datetime.now().isoformat(),
        "message_count": 1,
        "first_message": "Test",
        "thread": {"metadata": {}, "messages": []},
    }

    with open(session_file, "w") as f:
        json.dump(dummy_data, f)

    # Update metadata
    persistence.metadata["conversations"][session_name] = {
        "created_at": dummy_data["created_at"],
        "message_count": 1,
    }
    persistence._save_metadata()

    # Verify it exists
    sessions = persistence.list_sessions()
    assert len(sessions) == 1, "Should have one session"

    # Delete it
    persistence.delete_session(session_name)

    # Verify it's gone
    sessions = persistence.list_sessions()
    assert len(sessions) == 0, "Should have no sessions"

    # Verify file is deleted
    assert not session_file.exists(), "Session file should be deleted"


@pytest.mark.asyncio
async def test_load_nonexistent_session(
    agent_instance: Agent,
    persistence: ThreadPersistence,
):
    """Test loading a session that doesn't exist."""
    with pytest.raises(FileNotFoundError):
        await persistence.load_thread(agent_instance, "nonexistent-session")
