"""Utility functions for mem0 integration.

This module provides helper functions for mem0 client management,
health checks, and connection handling.
"""

import logging
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from agent.config import AgentConfig

logger = logging.getLogger(__name__)


def check_mem0_endpoint(endpoint: str | None = None, timeout: float = 1.0) -> bool:
    """Health check for mem0 endpoint availability.

    Makes an actual HTTP request to verify the service is responding,
    not just checking if the port is open.

    Args:
        endpoint: Endpoint URL (e.g., "http://localhost:8000")
        timeout: Request timeout in seconds (default: 1s)

    Returns:
        True if endpoint is reachable and responding, False otherwise

    Example:
        >>> check_mem0_endpoint("http://localhost:8000")
        True
    """
    if not endpoint:
        endpoint = "http://localhost:8000"

    try:
        # Make actual HTTP request to root endpoint
        req = Request(endpoint + "/", method="GET")
        with urlopen(req, timeout=timeout) as response:
            # Service is responding if we get any HTTP response
            status_code: int = int(response.status)
            return status_code < 500

    except URLError as e:
        logger.debug(f"Mem0 endpoint check failed (HTTP error): {e}")
        return False
    except Exception as e:
        logger.debug(f"Mem0 endpoint check failed: {e}")
        return False


def get_mem0_client(config: AgentConfig) -> Any:
    """Factory function to create mem0 client based on configuration.

    Routes to self-hosted or cloud client based on config settings.

    Args:
        config: Agent configuration with mem0 settings

    Returns:
        Configured mem0 MemoryClient instance

    Raises:
        ValueError: If configuration is invalid or incomplete
        ImportError: If mem0ai package is not installed

    Example:
        >>> config = AgentConfig.from_env()
        >>> client = get_mem0_client(config)
    """
    try:
        from mem0 import MemoryClient  # type: ignore[import-untyped]
    except ImportError:
        raise ImportError(
            "mem0ai package not installed. "
            "Install with: uv pip install -e '.[mem0]' (or pip install -e '.[mem0]')"
        )

    # Validate configuration
    if not config.mem0_host and not (config.mem0_api_key and config.mem0_org_id):
        raise ValueError(
            "Invalid mem0 configuration. Provide either:\n"
            "  - Self-hosted: MEM0_HOST\n"
            "  - Cloud: MEM0_API_KEY + MEM0_ORG_ID"
        )

    # Route to appropriate client
    if config.mem0_host:
        # Self-hosted mode
        logger.info(f"Initializing mem0 self-hosted client: {config.mem0_host}")
        try:
            client = MemoryClient(host=config.mem0_host)
            logger.debug("Mem0 self-hosted client initialized successfully")
            return client
        except Exception as e:
            raise ValueError(f"Failed to initialize mem0 self-hosted client: {e}")
    else:
        # Cloud mode
        logger.info("Initializing mem0 cloud client")
        try:
            client = MemoryClient(api_key=config.mem0_api_key, org_id=config.mem0_org_id)
            logger.debug("Mem0 cloud client initialized successfully")
            return client
        except Exception as e:
            raise ValueError(f"Failed to initialize mem0 cloud client: {e}")
