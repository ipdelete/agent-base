"""Aegis sandbox tools for secure Python code execution.

Execute Python code in an isolated Aegis sandbox with kernel-level security.
Streams output in real-time for immediate feedback.
"""

import logging
import os
from typing import Annotated

import grpc
from pydantic import Field

from agent.config.schema import AgentSettings
from agent.proto import aegis_pb2, aegis_pb2_grpc
from agent.tools.toolset import AgentToolset

logger = logging.getLogger(__name__)


class AegisTools(AgentToolset):
    """Execute Python code in Aegis hardened sandbox.

    Provides secure code execution with:
    - Namespace isolation (PID, network, mount, user, IPC)
    - Seccomp syscall filtering
    - Resource limits (CPU, memory, time)
    - Real-time streaming output

    Configuration via environment variables:
    - AEGIS_ENDPOINT: gRPC server address (default: 127.0.0.1:50051)
    - AEGIS_API_KEY: API key for authentication
    - AEGIS_ALLOW_INSECURE: Allow non-TLS connections (default: false)
    - AEGIS_CERT_PATH: Path to TLS certificate

    Example:
        >>> from agent.config import load_config
        >>> settings = load_config()
        >>> tools = AegisTools(settings)
        >>> result = await tools.execute_python("print('Hello!')")
        >>> print(result["result"])
        Hello!
    """

    def __init__(self, settings: AgentSettings):
        """Initialize AegisTools with settings.

        Args:
            settings: Agent settings instance
        """
        super().__init__(settings)
        self.endpoint = os.getenv("AEGIS_ENDPOINT", "127.0.0.1:50051")
        self.api_key = os.getenv("AEGIS_API_KEY")
        self.allow_insecure = os.getenv("AEGIS_ALLOW_INSECURE", "").lower() in (
            "1",
            "true",
            "yes",
        )
        self.cert_path = os.getenv("AEGIS_CERT_PATH")

        # Lazy channel creation
        self._channel: grpc.aio.Channel | None = None

        logger.debug(
            f"AegisTools initialized: endpoint={self.endpoint}, "
            f"insecure={self.allow_insecure}, has_api_key={bool(self.api_key)}"
        )

    def get_tools(self) -> list:
        """Get list of Aegis tools.

        Returns:
            List containing execute_python function
        """
        return [self.execute_python]

    async def _get_channel(self) -> grpc.aio.Channel:
        """Get or create gRPC channel.

        Returns:
            gRPC async channel connected to Aegis
        """
        if self._channel is None:
            if self.allow_insecure:
                logger.debug(f"Creating insecure channel to {self.endpoint}")
                self._channel = grpc.aio.insecure_channel(self.endpoint)
            else:
                if self.cert_path:
                    logger.debug(f"Creating secure channel with cert: {self.cert_path}")
                    with open(self.cert_path, "rb") as f:
                        credentials = grpc.ssl_channel_credentials(root_certificates=f.read())
                else:
                    logger.debug("Creating secure channel with system CA")
                    credentials = grpc.ssl_channel_credentials()
                self._channel = grpc.aio.secure_channel(self.endpoint, credentials)
        return self._channel

    async def execute_python(
        self,
        code: Annotated[str, Field(description="Python code to execute in the sandbox")],
        timeout_secs: Annotated[
            int, Field(description="Maximum execution time in seconds")
        ] = 30,
        memory_mb: Annotated[int, Field(description="Memory limit in megabytes")] = 256,
    ) -> dict:
        """Execute Python code in a secure Aegis sandbox.

        Runs code in an isolated environment with kernel-level security.
        Returns stdout, stderr, and exit code. Output streams in real-time.

        Security: Code runs in isolated namespaces with no network access,
        restricted syscalls, and resource limits. Safe for untrusted code.
        """
        try:
            channel = await self._get_channel()
            stub = aegis_pb2_grpc.AegisControllerStub(channel)

            # Build request
            request = aegis_pb2.ExecuteRequest(
                code=code,
                timeout_secs=timeout_secs,
                memory_mb=memory_mb,
            )

            # Build metadata with API key if configured
            metadata = []
            if self.api_key:
                metadata.append(("x-api-key", self.api_key))

            logger.debug(f"Executing code ({len(code)} chars) with timeout={timeout_secs}s")

            # Stream execution output
            stdout_parts: list[str] = []
            stderr_parts: list[str] = []
            exit_code = 0
            error_message: str | None = None

            async for chunk in stub.ExecuteStream(request, metadata=metadata or None):
                if chunk.type == aegis_pb2.ExecutionChunk.ChunkType.STDOUT:
                    text = chunk.data.decode("utf-8", errors="replace")
                    stdout_parts.append(text)
                    logger.debug(f"stdout chunk: {text!r}")
                elif chunk.type == aegis_pb2.ExecutionChunk.ChunkType.STDERR:
                    text = chunk.data.decode("utf-8", errors="replace")
                    stderr_parts.append(text)
                    logger.debug(f"stderr chunk: {text!r}")
                elif chunk.type == aegis_pb2.ExecutionChunk.ChunkType.EXIT_CODE:
                    exit_code = chunk.exit_code
                    logger.debug(f"exit_code: {exit_code}")
                elif chunk.type == aegis_pb2.ExecutionChunk.ChunkType.ERROR:
                    error_message = chunk.error.message if chunk.error else "Unknown error"
                    logger.warning(f"execution error: {error_message}")

            stdout = "".join(stdout_parts)
            stderr = "".join(stderr_parts)

            if error_message:
                return self._create_error_response(
                    error="execution_failed",
                    message=f"{error_message}\nstderr: {stderr}" if stderr else error_message,
                )

            if exit_code != 0:
                return self._create_error_response(
                    error="nonzero_exit",
                    message=(
                        f"Code exited with status {exit_code}\nstderr: {stderr}"
                        if stderr
                        else f"Exit code: {exit_code}"
                    ),
                )

            return self._create_success_response(
                result=stdout.strip() if stdout else "(no output)",
                message=f"Executed successfully (exit code {exit_code})",
            )

        except grpc.aio.AioRpcError as e:
            logger.error(f"gRPC error: {e.code().name} - {e.details()}")
            return self._create_error_response(
                error="grpc_error",
                message=f"Aegis connection failed: {e.code().name} - {e.details()}",
            )
        except FileNotFoundError as e:
            logger.error(f"Certificate file not found: {e}")
            return self._create_error_response(
                error="cert_not_found",
                message=f"TLS certificate not found: {self.cert_path}",
            )
        except Exception as e:
            logger.exception(f"Unexpected error during code execution: {e}")
            return self._create_error_response(
                error="unexpected_error",
                message=f"Unexpected error: {e!s}",
            )

    async def close(self) -> None:
        """Close gRPC channel.

        Call this when done with the toolset to clean up resources.
        """
        if self._channel:
            await self._channel.close()
            self._channel = None
            logger.debug("Closed Aegis gRPC channel")
