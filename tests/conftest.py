"""Shared test fixtures for all tests.

This file imports and re-exports fixtures from the fixtures/ module
to maintain backward compatibility while organizing fixtures by component.

All tests can continue using fixtures as before - they are automatically
discovered by pytest through this conftest.py file.
"""

# Import all fixtures from organized modules
from tests.fixtures.agent import agent_instance, mock_chat_client  # noqa: F401
from tests.fixtures.config import (  # noqa: F401
    mock_anthropic_config,
    mock_azure_foundry_config,
    mock_config,
    mock_openai_config,
)
from tests.fixtures.memory import (  # noqa: F401
    memory_config,
    memory_manager,
    memory_persistence,
    memory_store,
    sample_messages,
)

# Future: Add more fixture imports as needed
# from tests.fixtures.tools import tool_specific_fixtures
# from tests.fixtures.middleware import middleware_fixtures
