"""Memory fixtures for testing."""

import pytest

from agent.config import AgentConfig
from agent.memory import InMemoryStore, create_memory_manager
from agent.memory.persistence import MemoryPersistence


@pytest.fixture
def memory_config():
    """Create config with memory enabled."""
    return AgentConfig(
        llm_provider="openai",
        openai_api_key="test-key",
        memory_enabled=True,
        memory_type="in_memory",
    )


@pytest.fixture
def memory_store(memory_config):
    """Create InMemoryStore instance."""
    return InMemoryStore(memory_config)


@pytest.fixture
def memory_manager(memory_config):
    """Create memory manager via factory."""
    return create_memory_manager(memory_config)


@pytest.fixture
def sample_messages():
    """Sample messages for testing."""
    return [
        {"role": "user", "content": "My name is Alice"},
        {"role": "assistant", "content": "Nice to meet you, Alice!"},
        {"role": "user", "content": "I like Python programming"},
        {"role": "assistant", "content": "Python is a great language!"},
    ]


@pytest.fixture
def memory_persistence(tmp_path):
    """Create MemoryPersistence with temporary storage."""
    storage_dir = tmp_path / "memory"
    return MemoryPersistence(storage_dir=storage_dir)
