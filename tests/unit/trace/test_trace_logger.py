"""Unit tests for trace logger."""

import json
from pathlib import Path

import pytest

from agent.trace_logger import TraceLogger


@pytest.mark.unit
class TestTraceLoggerInitialization:
    """Test TraceLogger initialization and file setup."""

    def test_init_creates_trace_logger(self, tmp_path: Path):
        """Test trace logger initializes with correct attributes."""
        trace_file = tmp_path / "test-trace.log"
        logger = TraceLogger(trace_file=trace_file, include_messages=False)

        assert logger.trace_file == trace_file
        assert logger.include_messages is False

    def test_init_creates_directory_and_file(self, tmp_path: Path):
        """Test trace logger creates directory and file on init."""
        trace_file = tmp_path / "subdir" / "trace.log"
        assert not trace_file.parent.exists()

        TraceLogger(trace_file=trace_file, include_messages=False)

        assert trace_file.parent.exists()
        assert trace_file.exists()

    def test_init_with_existing_file(self, tmp_path: Path):
        """Test trace logger works with existing file."""
        trace_file = tmp_path / "existing.log"
        trace_file.write_text("existing content\n")

        logger = TraceLogger(trace_file=trace_file)

        assert logger.trace_file == trace_file
        assert trace_file.exists()
        # Should not overwrite existing content
        assert "existing content" in trace_file.read_text()

    def test_init_include_messages_defaults_to_false(self, tmp_path: Path):
        """Test include_messages defaults to False."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        assert logger.include_messages is False

    def test_init_include_messages_can_be_enabled(self, tmp_path: Path):
        """Test include_messages can be set to True."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file, include_messages=True)

        assert logger.include_messages is True


@pytest.mark.unit
class TestLogInteraction:
    """Test log_interaction method."""

    def test_log_interaction_basic_data(self, tmp_path: Path):
        """Test logging basic interaction data."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file, include_messages=False)

        logger.log_interaction(
            request_id="test-123",
            model="gpt-4o-mini",
            provider="openai",
        )

        # Read and parse log entry
        log_entries = trace_file.read_text().strip().split("\n")
        assert len(log_entries) == 1

        entry = json.loads(log_entries[0])
        assert entry["request_id"] == "test-123"
        assert entry["model"] == "gpt-4o-mini"
        assert entry["provider"] == "openai"
        assert "timestamp" in entry

    def test_log_interaction_with_messages_excluded(self, tmp_path: Path):
        """Test logging interaction without message content (include_messages=False)."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file, include_messages=False)

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        logger.log_interaction(
            request_id="test-123",
            messages=messages,
            response_content="Response text",
            model="gpt-4o-mini",
        )

        entry = json.loads(trace_file.read_text().strip())
        # Should include message count but not content
        assert entry["message_count"] == 2
        assert "messages" not in entry
        # Should include response length but not content
        assert entry["response_length"] == len("Response text")
        assert "response" not in entry

    def test_log_interaction_with_messages_included(self, tmp_path: Path):
        """Test logging interaction with full message content (include_messages=True)."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file, include_messages=True)

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        logger.log_interaction(
            request_id="test-123",
            messages=messages,
            response_content="Response text",
            model="gpt-4o-mini",
        )

        entry = json.loads(trace_file.read_text().strip())
        # Should include full message content
        assert entry["message_count"] == 2
        assert entry["messages"] == messages
        # Should include full response content
        assert entry["response"] == "Response text"
        assert "response_length" not in entry

    def test_log_interaction_with_token_usage(self, tmp_path: Path):
        """Test logging interaction with token usage data."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        logger.log_interaction(
            request_id="test-123",
            model="gpt-4o-mini",
            input_tokens=150,
            output_tokens=75,
            total_tokens=225,
        )

        entry = json.loads(trace_file.read_text().strip())
        assert "tokens" in entry
        assert entry["tokens"]["input"] == 150
        assert entry["tokens"]["output"] == 75
        assert entry["tokens"]["total"] == 225

    def test_log_interaction_with_partial_token_usage(self, tmp_path: Path):
        """Test logging interaction with partial token data."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        logger.log_interaction(
            request_id="test-123",
            model="gpt-4o-mini",
            input_tokens=150,
            output_tokens=None,
            total_tokens=150,
        )

        entry = json.loads(trace_file.read_text().strip())
        assert "tokens" in entry
        assert entry["tokens"]["input"] == 150
        assert entry["tokens"]["total"] == 150
        assert "output" not in entry["tokens"]

    def test_log_interaction_with_latency(self, tmp_path: Path):
        """Test logging interaction with latency data."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        logger.log_interaction(
            request_id="test-123",
            model="gpt-4o-mini",
            latency_ms=1234.5678,
        )

        entry = json.loads(trace_file.read_text().strip())
        # Latency should be rounded to 2 decimal places
        assert entry["latency_ms"] == 1234.57

    def test_log_interaction_with_error(self, tmp_path: Path):
        """Test logging interaction with error."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        logger.log_interaction(
            request_id="test-123",
            model="gpt-4o-mini",
            error="API rate limit exceeded",
        )

        entry = json.loads(trace_file.read_text().strip())
        assert entry["error"] == "API rate limit exceeded"

    def test_log_interaction_with_all_fields(self, tmp_path: Path):
        """Test logging interaction with all possible fields."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file, include_messages=True)

        messages = [{"role": "user", "content": "Test"}]

        logger.log_interaction(
            request_id="test-123",
            messages=messages,
            response_content="Response",
            model="gpt-4o-mini",
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
            latency_ms=500.123,
            provider="openai",
            error=None,
        )

        entry = json.loads(trace_file.read_text().strip())
        assert entry["request_id"] == "test-123"
        assert entry["messages"] == messages
        assert entry["response"] == "Response"
        assert entry["model"] == "gpt-4o-mini"
        assert entry["tokens"]["input"] == 10
        assert entry["tokens"]["output"] == 5
        assert entry["tokens"]["total"] == 15
        assert entry["latency_ms"] == 500.12
        assert entry["provider"] == "openai"
        assert "error" not in entry  # None values not logged

    def test_log_interaction_handles_write_failure(self, tmp_path: Path, caplog):
        """Test logging interaction handles file write failures gracefully."""
        import logging

        caplog.set_level(logging.ERROR)

        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        # Make file read-only to cause write failure
        trace_file.chmod(0o444)

        # Should not raise exception
        logger.log_interaction(request_id="test-123", model="gpt-4o-mini")

        # Should log error
        assert any("Failed to write trace log" in record.message for record in caplog.records)

        # Restore permissions
        trace_file.chmod(0o644)


@pytest.mark.unit
class TestLogRequest:
    """Test log_request method."""

    def test_log_request_basic_data(self, tmp_path: Path):
        """Test logging request data."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file, include_messages=False)

        messages = [{"role": "user", "content": "Hello"}]

        logger.log_request(
            request_id="req-123",
            messages=messages,
            model="gpt-4o-mini",
            provider="openai",
        )

        entry = json.loads(trace_file.read_text().strip())
        assert entry["request_id"] == "req-123"
        assert entry["type"] == "request"
        assert entry["model"] == "gpt-4o-mini"
        assert entry["provider"] == "openai"
        assert entry["message_count"] == 1
        assert "timestamp" in entry

    def test_log_request_without_messages_content(self, tmp_path: Path):
        """Test logging request without message content (include_messages=False)."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file, include_messages=False)

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]

        logger.log_request(request_id="req-123", messages=messages)

        entry = json.loads(trace_file.read_text().strip())
        assert entry["message_count"] == 2
        assert "messages" not in entry

    def test_log_request_with_messages_content(self, tmp_path: Path):
        """Test logging request with full message content (include_messages=True)."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file, include_messages=True)

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]

        logger.log_request(request_id="req-123", messages=messages)

        entry = json.loads(trace_file.read_text().strip())
        assert entry["message_count"] == 2
        assert entry["messages"] == messages

    def test_log_request_handles_write_failure(self, tmp_path: Path, caplog):
        """Test logging request handles file write failures gracefully."""
        import logging

        caplog.set_level(logging.ERROR)

        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        trace_file.chmod(0o444)

        messages = [{"role": "user", "content": "Test"}]
        logger.log_request(request_id="req-123", messages=messages)

        assert any("Failed to write trace log" in record.message for record in caplog.records)

        trace_file.chmod(0o644)


@pytest.mark.unit
class TestLogResponse:
    """Test log_response method."""

    def test_log_response_basic_data(self, tmp_path: Path):
        """Test logging response data."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file, include_messages=False)

        logger.log_response(
            request_id="resp-123",
            response_content="Hello there!",
            model="gpt-4o-mini",
        )

        entry = json.loads(trace_file.read_text().strip())
        assert entry["request_id"] == "resp-123"
        assert entry["type"] == "response"
        assert entry["model"] == "gpt-4o-mini"
        assert entry["response_length"] == len("Hello there!")
        assert "response" not in entry
        assert "timestamp" in entry

    def test_log_response_with_content_included(self, tmp_path: Path):
        """Test logging response with full content (include_messages=True)."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file, include_messages=True)

        logger.log_response(
            request_id="resp-123",
            response_content="Hello there!",
            model="gpt-4o-mini",
        )

        entry = json.loads(trace_file.read_text().strip())
        assert entry["response"] == "Hello there!"
        assert "response_length" not in entry

    def test_log_response_with_token_usage(self, tmp_path: Path):
        """Test logging response with token usage."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        logger.log_response(
            request_id="resp-123",
            response_content="Response",
            model="gpt-4o-mini",
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
        )

        entry = json.loads(trace_file.read_text().strip())
        assert "tokens" in entry
        assert entry["tokens"]["input"] == 100
        assert entry["tokens"]["output"] == 50
        assert entry["tokens"]["total"] == 150

    def test_log_response_with_latency(self, tmp_path: Path):
        """Test logging response with latency."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        logger.log_response(
            request_id="resp-123",
            response_content="Response",
            latency_ms=2345.6789,
        )

        entry = json.loads(trace_file.read_text().strip())
        assert entry["latency_ms"] == 2345.68

    def test_log_response_with_error(self, tmp_path: Path):
        """Test logging response with error."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        logger.log_response(
            request_id="resp-123",
            response_content="",
            error="Connection timeout",
        )

        entry = json.loads(trace_file.read_text().strip())
        assert entry["error"] == "Connection timeout"
        assert entry["response_length"] == 0

    def test_log_response_handles_write_failure(self, tmp_path: Path, caplog):
        """Test logging response handles file write failures gracefully."""
        import logging

        caplog.set_level(logging.ERROR)

        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        trace_file.chmod(0o444)

        logger.log_response(request_id="resp-123", response_content="Test")

        assert any("Failed to write trace log" in record.message for record in caplog.records)

        trace_file.chmod(0o644)


@pytest.mark.unit
class TestMultipleEntries:
    """Test logging multiple entries to same file."""

    def test_multiple_log_entries_json_per_line(self, tmp_path: Path):
        """Test multiple log entries are written one per line."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        # Log multiple interactions
        logger.log_request(request_id="req-1", messages=[{"role": "user", "content": "First"}])
        logger.log_response(request_id="req-1", response_content="Response 1")
        logger.log_request(request_id="req-2", messages=[{"role": "user", "content": "Second"}])
        logger.log_response(request_id="req-2", response_content="Response 2")

        # Read all entries
        log_entries = trace_file.read_text().strip().split("\n")
        assert len(log_entries) == 4

        # Verify each line is valid JSON
        for line in log_entries:
            entry = json.loads(line)
            assert "timestamp" in entry
            assert "request_id" in entry

        # Verify request IDs
        assert json.loads(log_entries[0])["request_id"] == "req-1"
        assert json.loads(log_entries[1])["request_id"] == "req-1"
        assert json.loads(log_entries[2])["request_id"] == "req-2"
        assert json.loads(log_entries[3])["request_id"] == "req-2"

    def test_log_interaction_and_separate_calls(self, tmp_path: Path):
        """Test mixing log_interaction and separate log_request/log_response calls."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        # Log complete interaction
        logger.log_interaction(request_id="int-1", model="gpt-4o-mini")

        # Log separate request and response
        logger.log_request(request_id="req-1", messages=[{"role": "user", "content": "Test"}])
        logger.log_response(request_id="req-1", response_content="Test response")

        log_entries = trace_file.read_text().strip().split("\n")
        assert len(log_entries) == 3

        # First entry is complete interaction (no type field)
        entry1 = json.loads(log_entries[0])
        assert entry1["request_id"] == "int-1"
        assert "type" not in entry1

        # Second and third entries are request/response
        entry2 = json.loads(log_entries[1])
        assert entry2["request_id"] == "req-1"
        assert entry2["type"] == "request"

        entry3 = json.loads(log_entries[2])
        assert entry3["request_id"] == "req-1"
        assert entry3["type"] == "response"


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_log_with_empty_messages(self, tmp_path: Path):
        """Test logging with empty messages list."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        logger.log_request(request_id="req-1", messages=[])

        entry = json.loads(trace_file.read_text().strip())
        assert entry["message_count"] == 0

    def test_log_with_none_messages(self, tmp_path: Path):
        """Test logging with None messages."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        logger.log_interaction(request_id="req-1", messages=None)

        entry = json.loads(trace_file.read_text().strip())
        assert "message_count" not in entry
        assert "messages" not in entry

    def test_log_with_empty_response(self, tmp_path: Path):
        """Test logging with empty response content."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        logger.log_response(request_id="resp-1", response_content="")

        entry = json.loads(trace_file.read_text().strip())
        assert entry["response_length"] == 0

    def test_log_with_none_values(self, tmp_path: Path):
        """Test logging with None values for optional fields."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        logger.log_interaction(
            request_id="req-1",
            model=None,
            provider=None,
            input_tokens=None,
            output_tokens=None,
            total_tokens=None,
            latency_ms=None,
            error=None,
        )

        entry = json.loads(trace_file.read_text().strip())
        assert entry["request_id"] == "req-1"
        # None values should not be included
        assert entry["model"] is None
        assert entry["provider"] is None
        assert "tokens" not in entry
        assert "latency_ms" not in entry
        assert "error" not in entry

    def test_log_with_zero_latency(self, tmp_path: Path):
        """Test logging with zero latency (very fast response)."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file)

        logger.log_response(request_id="resp-1", response_content="Fast", latency_ms=0.0)

        entry = json.loads(trace_file.read_text().strip())
        assert entry["latency_ms"] == 0.0

    def test_log_with_special_characters(self, tmp_path: Path):
        """Test logging with special characters in content."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file, include_messages=True)

        messages = [{"role": "user", "content": 'Test with "quotes" and\nnewlines\t\ttabs'}]

        logger.log_request(request_id="req-1", messages=messages)

        entry = json.loads(trace_file.read_text().strip())
        # JSON should handle special characters
        assert entry["messages"][0]["content"] == 'Test with "quotes" and\nnewlines\t\ttabs'

    def test_log_with_unicode_characters(self, tmp_path: Path):
        """Test logging with unicode characters."""
        trace_file = tmp_path / "trace.log"
        logger = TraceLogger(trace_file=trace_file, include_messages=True)

        messages = [{"role": "user", "content": "Hello 世界 🌍"}]

        logger.log_request(request_id="req-1", messages=messages)

        entry = json.loads(trace_file.read_text().strip())
        assert entry["messages"][0]["content"] == "Hello 世界 🌍"
