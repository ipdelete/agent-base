"""Unit tests for agent.tools.aegis module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agent.config.schema import AgentSettings
from agent.proto import aegis_pb2
from agent.tools.aegis import AegisTools


@pytest.fixture
def mock_settings():
    """Create mock AgentSettings for testing."""
    return AgentSettings(llm_provider="openai", openai_api_key="test-key")


@pytest.fixture
def aegis_tools(mock_settings, monkeypatch):
    """Create AegisTools instance for testing with insecure mode."""
    monkeypatch.setenv("AEGIS_ENDPOINT", "localhost:50051")
    monkeypatch.setenv("AEGIS_ALLOW_INSECURE", "true")
    return AegisTools(mock_settings)


@pytest.fixture
def aegis_tools_with_key(mock_settings, monkeypatch):
    """Create AegisTools instance with API key."""
    monkeypatch.setenv("AEGIS_ENDPOINT", "localhost:50051")
    monkeypatch.setenv("AEGIS_API_KEY", "test-api-key")
    monkeypatch.setenv("AEGIS_ALLOW_INSECURE", "true")
    return AegisTools(mock_settings)


class AsyncIteratorMock:
    """Mock async iterator for gRPC streaming responses."""

    def __init__(self, items):
        self.items = items
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item


def make_chunk(chunk_type: int, data: bytes = b"", exit_code: int = 0, error=None):
    """Create a mock ExecutionChunk."""
    chunk = MagicMock()
    chunk.type = chunk_type
    chunk.data = data
    chunk.exit_code = exit_code
    chunk.error = error
    return chunk


@pytest.mark.unit
@pytest.mark.tools
class TestAegisToolsInitialization:
    """Tests for AegisTools initialization."""

    def test_initialization_default_endpoint(self, mock_settings, monkeypatch):
        """Test AegisTools uses default endpoint when not set."""
        monkeypatch.delenv("AEGIS_ENDPOINT", raising=False)
        monkeypatch.delenv("AEGIS_API_KEY", raising=False)
        monkeypatch.setenv("AEGIS_ALLOW_INSECURE", "true")

        tools = AegisTools(mock_settings)

        assert tools.endpoint == "127.0.0.1:50051"
        assert tools.api_key is None
        assert tools.allow_insecure is True

    def test_initialization_custom_endpoint(self, mock_settings, monkeypatch):
        """Test AegisTools uses custom endpoint from env."""
        monkeypatch.setenv("AEGIS_ENDPOINT", "aegis.example.com:50051")
        monkeypatch.setenv("AEGIS_ALLOW_INSECURE", "false")

        tools = AegisTools(mock_settings)

        assert tools.endpoint == "aegis.example.com:50051"
        assert tools.allow_insecure is False

    def test_initialization_with_api_key(self, mock_settings, monkeypatch):
        """Test AegisTools reads API key from env."""
        monkeypatch.setenv("AEGIS_ENDPOINT", "localhost:50051")
        monkeypatch.setenv("AEGIS_API_KEY", "my-secret-key")
        monkeypatch.setenv("AEGIS_ALLOW_INSECURE", "true")

        tools = AegisTools(mock_settings)

        assert tools.api_key == "my-secret-key"

    def test_initialization_with_cert_path(self, mock_settings, monkeypatch):
        """Test AegisTools reads cert path from env."""
        monkeypatch.setenv("AEGIS_ENDPOINT", "localhost:50051")
        monkeypatch.setenv("AEGIS_CERT_PATH", "/path/to/cert.pem")

        tools = AegisTools(mock_settings)

        assert tools.cert_path == "/path/to/cert.pem"
        assert tools.allow_insecure is False

    def test_get_tools_returns_execute_python(self, aegis_tools):
        """Test get_tools returns execute_python function."""
        tools_list = aegis_tools.get_tools()

        assert len(tools_list) == 1
        assert aegis_tools.execute_python in tools_list


@pytest.mark.unit
@pytest.mark.tools
class TestAegisToolsExecution:
    """Tests for AegisTools execute_python method."""

    @pytest.mark.asyncio
    async def test_execute_python_success(self, aegis_tools):
        """Test successful code execution."""
        mock_chunks = [
            make_chunk(aegis_pb2.ExecutionChunk.ChunkType.STDOUT, b"Hello, World!\n"),
            make_chunk(aegis_pb2.ExecutionChunk.ChunkType.EXIT_CODE, exit_code=0),
        ]

        mock_stub = MagicMock()
        mock_stub.ExecuteStream = MagicMock(return_value=AsyncIteratorMock(mock_chunks))

        with patch.object(aegis_tools, "_get_channel") as mock_channel:
            mock_channel.return_value = MagicMock()
            with patch(
                "agent.tools.aegis.aegis_pb2_grpc.AegisControllerStub",
                return_value=mock_stub,
            ):
                result = await aegis_tools.execute_python("print('Hello, World!')")

        assert result["success"] is True
        assert "Hello, World!" in result["result"]
        assert "exit code 0" in result["message"]

    @pytest.mark.asyncio
    async def test_execute_python_no_output(self, aegis_tools):
        """Test code execution with no output."""
        mock_chunks = [
            make_chunk(aegis_pb2.ExecutionChunk.ChunkType.EXIT_CODE, exit_code=0),
        ]

        mock_stub = MagicMock()
        mock_stub.ExecuteStream = MagicMock(return_value=AsyncIteratorMock(mock_chunks))

        with patch.object(aegis_tools, "_get_channel") as mock_channel:
            mock_channel.return_value = MagicMock()
            with patch(
                "agent.tools.aegis.aegis_pb2_grpc.AegisControllerStub",
                return_value=mock_stub,
            ):
                result = await aegis_tools.execute_python("x = 1 + 1")

        assert result["success"] is True
        assert result["result"] == "(no output)"

    @pytest.mark.asyncio
    async def test_execute_python_nonzero_exit(self, aegis_tools):
        """Test code execution with non-zero exit code."""
        mock_chunks = [
            make_chunk(aegis_pb2.ExecutionChunk.ChunkType.STDERR, b"NameError: name 'x' is not defined\n"),
            make_chunk(aegis_pb2.ExecutionChunk.ChunkType.EXIT_CODE, exit_code=1),
        ]

        mock_stub = MagicMock()
        mock_stub.ExecuteStream = MagicMock(return_value=AsyncIteratorMock(mock_chunks))

        with patch.object(aegis_tools, "_get_channel") as mock_channel:
            mock_channel.return_value = MagicMock()
            with patch(
                "agent.tools.aegis.aegis_pb2_grpc.AegisControllerStub",
                return_value=mock_stub,
            ):
                result = await aegis_tools.execute_python("print(x)")

        assert result["success"] is False
        assert result["error"] == "nonzero_exit"
        assert "exit" in result["message"].lower()
        assert "NameError" in result["message"]

    @pytest.mark.asyncio
    async def test_execute_python_execution_error(self, aegis_tools):
        """Test code execution with execution error chunk."""
        mock_error = MagicMock()
        mock_error.message = "Timeout exceeded"

        mock_chunks = [
            make_chunk(
                aegis_pb2.ExecutionChunk.ChunkType.ERROR,
                error=mock_error,
            ),
        ]

        mock_stub = MagicMock()
        mock_stub.ExecuteStream = MagicMock(return_value=AsyncIteratorMock(mock_chunks))

        with patch.object(aegis_tools, "_get_channel") as mock_channel:
            mock_channel.return_value = MagicMock()
            with patch(
                "agent.tools.aegis.aegis_pb2_grpc.AegisControllerStub",
                return_value=mock_stub,
            ):
                result = await aegis_tools.execute_python("while True: pass")

        assert result["success"] is False
        assert result["error"] == "execution_failed"
        assert "Timeout" in result["message"]

    @pytest.mark.asyncio
    async def test_execute_python_grpc_error(self, aegis_tools):
        """Test handling of gRPC connection errors."""
        import grpc

        mock_stub = MagicMock()
        mock_error = grpc.aio.AioRpcError(
            code=grpc.StatusCode.UNAVAILABLE,
            initial_metadata=None,
            trailing_metadata=None,
            details="Connection refused",
            debug_error_string=None,
        )
        mock_stub.ExecuteStream = MagicMock(side_effect=mock_error)

        with patch.object(aegis_tools, "_get_channel") as mock_channel:
            mock_channel.return_value = MagicMock()
            with patch(
                "agent.tools.aegis.aegis_pb2_grpc.AegisControllerStub",
                return_value=mock_stub,
            ):
                result = await aegis_tools.execute_python("print('test')")

        assert result["success"] is False
        assert result["error"] == "grpc_error"
        assert "UNAVAILABLE" in result["message"]

    @pytest.mark.asyncio
    async def test_execute_python_multiple_stdout_chunks(self, aegis_tools):
        """Test code execution with multiple stdout chunks."""
        mock_chunks = [
            make_chunk(aegis_pb2.ExecutionChunk.ChunkType.STDOUT, b"Line 1\n"),
            make_chunk(aegis_pb2.ExecutionChunk.ChunkType.STDOUT, b"Line 2\n"),
            make_chunk(aegis_pb2.ExecutionChunk.ChunkType.STDOUT, b"Line 3\n"),
            make_chunk(aegis_pb2.ExecutionChunk.ChunkType.EXIT_CODE, exit_code=0),
        ]

        mock_stub = MagicMock()
        mock_stub.ExecuteStream = MagicMock(return_value=AsyncIteratorMock(mock_chunks))

        with patch.object(aegis_tools, "_get_channel") as mock_channel:
            mock_channel.return_value = MagicMock()
            with patch(
                "agent.tools.aegis.aegis_pb2_grpc.AegisControllerStub",
                return_value=mock_stub,
            ):
                result = await aegis_tools.execute_python("for i in range(3): print(f'Line {i+1}')")

        assert result["success"] is True
        assert "Line 1" in result["result"]
        assert "Line 2" in result["result"]
        assert "Line 3" in result["result"]

    @pytest.mark.asyncio
    async def test_execute_python_with_api_key(self, aegis_tools_with_key):
        """Test that API key is passed in metadata."""
        mock_chunks = [
            make_chunk(aegis_pb2.ExecutionChunk.ChunkType.EXIT_CODE, exit_code=0),
        ]

        mock_stub = MagicMock()
        mock_stub.ExecuteStream = MagicMock(return_value=AsyncIteratorMock(mock_chunks))

        with patch.object(aegis_tools_with_key, "_get_channel") as mock_channel:
            mock_channel.return_value = MagicMock()
            with patch(
                "agent.tools.aegis.aegis_pb2_grpc.AegisControllerStub",
                return_value=mock_stub,
            ):
                await aegis_tools_with_key.execute_python("pass")

        # Verify ExecuteStream was called with metadata containing API key
        call_args = mock_stub.ExecuteStream.call_args
        metadata = call_args.kwargs.get("metadata") or call_args[1].get("metadata")
        assert metadata is not None
        assert ("x-api-key", "test-api-key") in metadata


@pytest.mark.unit
@pytest.mark.tools
class TestAegisToolsDocstrings:
    """Tests for AegisTools docstrings and LLM compatibility."""

    def test_execute_python_has_docstring(self, aegis_tools):
        """Test execute_python has docstring for LLM."""
        docstring = aegis_tools.execute_python.__doc__

        assert docstring is not None
        assert "sandbox" in docstring.lower()
        assert "security" in docstring.lower() or "secure" in docstring.lower()

    def test_response_format_consistency(self, aegis_tools):
        """Test response helpers follow consistent format."""
        success = aegis_tools._create_success_response("test", "msg")
        assert "success" in success
        assert "result" in success
        assert "message" in success
        assert success["success"] is True

        error = aegis_tools._create_error_response("code", "msg")
        assert "success" in error
        assert "error" in error
        assert "message" in error
        assert error["success"] is False


@pytest.mark.unit
@pytest.mark.tools
class TestAegisToolsChannel:
    """Tests for gRPC channel management."""

    @pytest.mark.asyncio
    async def test_channel_lazy_creation(self, aegis_tools):
        """Test channel is created lazily on first use."""
        assert aegis_tools._channel is None

        with patch("grpc.aio.insecure_channel") as mock_insecure:
            mock_insecure.return_value = MagicMock()
            channel = await aegis_tools._get_channel()

            assert channel is not None
            mock_insecure.assert_called_once_with("localhost:50051")

    @pytest.mark.asyncio
    async def test_channel_reused(self, aegis_tools):
        """Test channel is reused on subsequent calls."""
        with patch("grpc.aio.insecure_channel") as mock_insecure:
            mock_channel = MagicMock()
            mock_insecure.return_value = mock_channel

            channel1 = await aegis_tools._get_channel()
            channel2 = await aegis_tools._get_channel()

            assert channel1 is channel2
            mock_insecure.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_channel(self, aegis_tools):
        """Test close releases channel."""
        mock_channel = AsyncMock()
        aegis_tools._channel = mock_channel

        await aegis_tools.close()

        mock_channel.close.assert_called_once()
        assert aegis_tools._channel is None

    @pytest.mark.asyncio
    async def test_close_no_channel(self, aegis_tools):
        """Test close is safe when no channel exists."""
        assert aegis_tools._channel is None

        await aegis_tools.close()  # Should not raise

        assert aegis_tools._channel is None
