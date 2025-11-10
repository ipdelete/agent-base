# Feature: Observability Integration with OpenTelemetry and Application Insights

## Feature Description

Enable comprehensive observability for the Agent Base application using OpenTelemetry standard with support for multiple telemetry backends including Azure Application Insights, OTLP endpoints, and Aspire Dashboard. This feature will instrument the agent framework to emit traces, logs, and metrics that provide visibility into agent performance, token usage, response times, and error patterns.

## User Story

As a developer using Agent Base
I want comprehensive observability through OpenTelemetry
So that I can monitor agent performance, track token consumption, debug issues, and gain insights into agent behavior in production environments

## Problem Statement

Currently, Agent Base lacks comprehensive observability capabilities, making it difficult to:
- Monitor agent performance and response times in production
- Track token usage and costs across conversations
- Debug issues and understand agent behavior
- Analyze tool execution patterns and failures
- Gain insights into LLM provider interactions

## Solution Statement

Implement OpenTelemetry-based observability following the Microsoft Agent Framework patterns, providing:
- Automatic instrumentation for agent operations, tool executions, and LLM interactions
- Support for multiple telemetry backends (Application Insights, OTLP, Aspire Dashboard, Console)
- Environment-based configuration with `setup_observability()` helper function
- Semantic conventions for GenAI telemetry following OpenTelemetry standards
- Optional sensitive data capture (prompts/responses) for development environments

## Related Documentation

### Requirements
- [Architecture](../design/architecture.md) - System architecture and component design
- [Requirements](../design/requirements.md) - Core project requirements

### Architecture Decisions
- [ADR-0005: Event Bus Pattern](../decisions/0005-event-bus-pattern-for-loose-coupling.md) - Event-driven architecture that observability will integrate with
- [ADR-0006: Class-Based Toolset Architecture](../decisions/0006-class-based-toolset-architecture.md) - Tool system that needs instrumentation
- [ADR-0012: Middleware Integration Strategy](../decisions/0012-middleware-integration-strategy.md) - Middleware pattern for cross-cutting concerns

### Reference Implementation
- Microsoft Agent Framework: `ai-examples/agent-framework/python/packages/core/agent_framework/observability.py`
- ADR-0003: Agent OpenTelemetry Instrumentation (reference framework)

## Codebase Analysis Findings

### Architecture Patterns to Follow
- **Dependency Injection**: All observability components should be injected, not global
- **Event-Driven Design**: Leverage existing EventBus for telemetry event emission
- **Configuration from Environment**: Use AgentConfig pattern for observability settings
- **Class-Based Architecture**: Create ObservabilityTools toolset following AgentToolset pattern
- **Structured Responses**: All telemetry helpers return `{"success": bool, "result": any, "message": str}`

### Naming Conventions
- Module: `src/agent/observability.py` (snake_case)
- Classes: `ObservabilitySettings`, `ObservabilityManager` (PascalCase)
- Functions: `setup_observability()`, `get_tracer()`, `get_meter()` (snake_case)
- Constants: `OTEL_ENABLED`, `OBSERVABILITY_SETTINGS` (UPPER_SNAKE_CASE)

### Similar Implementations
- Middleware pipeline in `src/agent/middleware.py` - Shows how to wrap agent operations
- EventBus in `src/agent/events.py` - Pattern for emitting telemetry events
- Config management in `src/agent/config.py` - Pattern for settings with validation

### Integration Patterns
The observability module will integrate with existing components:
1. **Agent class** (`src/agent/agent.py`) - Instrument `run()` method
2. **Toolsets** (`src/agent/tools/`) - Instrument tool execution
3. **Middleware** (`src/agent/middleware.py`) - Add telemetry middleware
4. **Config** (`src/agent/config.py`) - Add observability configuration fields

## Relevant Files

### Existing Files to Modify
- `src/agent/config.py` - Add observability configuration fields
- `src/agent/agent.py` - Add telemetry instrumentation hooks
- `src/agent/middleware.py` - Add observability middleware
- `src/agent/tools/toolset.py` - Add base instrumentation for tools
- `.env.example` - Document observability environment variables
- `pyproject.toml` - Add OpenTelemetry dependencies

### New Files to Create
- `src/agent/observability.py` - Core observability module with setup and helpers
- `tests/unit/test_observability.py` - Unit tests for observability module
- `tests/integration/test_observability_integration.py` - Integration tests
- `docs/decisions/0014-observability-integration.md` - ADR for this feature
- `examples/observability_example.py` - Usage example

## Implementation Plan

### Phase 1: Foundation (Configuration & Module Structure)
Set up the basic infrastructure for observability without active instrumentation.

**Tasks:**
1. Verify OpenTelemetry dependencies (already installed via `agent-framework`)
2. Create `ObservabilitySettings` configuration class
3. Update `AgentConfig` to include observability settings
4. Create basic observability module structure
5. Add environment variable documentation to `.env.example`

**Deliverables:**
- Dependencies verified and available (via `agent-framework>=1.0.0b251007`)
- Configuration classes defined
- No active instrumentation yet (feature disabled by default)

### Phase 2: Core Implementation (Telemetry Infrastructure)
Implement the core observability functionality following Microsoft Agent Framework patterns.

**Tasks:**
1. Implement `setup_observability()` function with exporter creation
2. Create tracer and meter provider configuration
3. Implement `get_tracer()` and `get_meter()` helper functions
4. Add support for OTLP, Application Insights, and Console exporters
5. Implement telemetry attribute constants following OpenTelemetry conventions

**Deliverables:**
- Functional `setup_observability()` with multiple backend support
- Provider configuration for traces, logs, and metrics
- Helper functions for accessing telemetry APIs

### Phase 3: Agent & Tool Instrumentation
Add instrumentation to agent operations and tool executions.

**Tasks:**
1. Create telemetry middleware for agent operations
2. Instrument agent `run()` method with span creation
3. Add tool execution instrumentation to `AgentToolset` base class
4. Implement token usage and duration metric collection
5. Add error and exception tracking

**Deliverables:**
- Agent operations emit spans with appropriate attributes
- Tool executions tracked with timing and results
- Metrics captured for tokens and duration

## Step by Step Tasks

### Task 1: Verify OpenTelemetry Dependencies (Already Installed)
- **Description**: Verify that OpenTelemetry packages are available through `agent-framework` dependency
- **Files to verify**:
  - `pyproject.toml` (confirm `agent-framework>=1.0.0b251007` is present)
- **Details**:
  - OpenTelemetry packages are already included as transitive dependencies of `agent-framework-core`
  - Included packages: `opentelemetry-api>=1.24`, `opentelemetry-sdk>=1.24`, `opentelemetry-exporter-otlp-proto-grpc>=1.36.0`, `opentelemetry-semantic-conventions-ai>=0.4.13`
  - Optional: `azure-monitor-opentelemetry-exporter` (for Application Insights support)
  - **No changes to `pyproject.toml` required** - dependencies already present
- **Validation**:
  ```bash
  # Verify OpenTelemetry packages are available
  uv run python -c "import opentelemetry; from agent_framework.observability import setup_observability; print('✓ OpenTelemetry available')"
  ```

### Task 2: Create ObservabilitySettings Configuration Class
- **Description**: Create Pydantic settings class for observability configuration following existing AgentConfig pattern
- **Files to create**:
  - `src/agent/observability.py` (initial structure)
- **Details**:
  - Create `ObservabilitySettings` class inheriting from Pydantic BaseSettings
  - Add fields: `enable_otel`, `enable_sensitive_data`, `applicationinsights_connection_string`, `otlp_endpoint`, `vs_code_extension_port`
  - Implement `from_env()` class method
  - Add `ENABLED` and `SENSITIVE_DATA_ENABLED` properties
  - Include docstrings with examples
- **Validation**: Settings can be loaded from environment variables

### Task 3: Update AgentConfig with Observability Settings
- **Description**: Extend `AgentConfig` to include observability configuration
- **Files to modify**:
  - `src/agent/config.py`
- **Details**:
  - Add observability-related fields to `AgentConfig` dataclass
  - Add validation for observability settings
  - Update `from_env()` to load observability config
  - Maintain backward compatibility (observability disabled by default)
- **Validation**: Existing tests pass, config loads observability settings

### Task 4: Implement setup_observability() Function
- **Description**: Create main setup function for configuring OpenTelemetry providers and exporters
- **Files to modify**:
  - `src/agent/observability.py`
- **Details**:
  - Implement `setup_observability()` with parameters for OTLP endpoint, App Insights connection string, exporters, credential
  - Create helper functions: `_get_otlp_exporters()`, `_get_azure_monitor_exporters()`, `_create_resource()`
  - Configure TracerProvider, LoggerProvider, and MeterProvider
  - Support multiple exporters simultaneously
  - Add console fallback when no exporters configured
  - Implement singleton pattern to prevent multiple setup calls
- **Validation**: Function creates providers correctly with different configurations

### Task 5: Implement get_tracer() and get_meter() Helpers
- **Description**: Create convenience functions for accessing OpenTelemetry APIs
- **Files to modify**:
  - `src/agent/observability.py`
- **Details**:
  - Implement `get_tracer()` with default instrumenting module name
  - Implement `get_meter()` with histogram bucket boundaries for token usage and duration
  - Add type hints and comprehensive docstrings
  - Include usage examples in docstrings
- **Validation**: Functions return working Tracer and Meter instances

### Task 6: Create OpenTelemetry Attribute Constants
- **Description**: Define constants for telemetry attribute names following OpenTelemetry semantic conventions
- **Files to modify**:
  - `src/agent/observability.py`
- **Details**:
  - Create `OtelAttr` enum with GenAI semantic convention attributes
  - Include attributes for: operation, provider, model, tokens, tool execution, agent metadata
  - Add role-to-event mapping for messages
  - Define bucket boundaries for histograms (tokens, duration)
  - Follow naming from `opentelemetry.semconv_ai`
- **Validation**: Constants match OpenTelemetry GenAI conventions

### Task 7: Create Observability Middleware
- **Description**: Implement middleware that instruments agent operations with tracing
- **Files to modify**:
  - `src/agent/middleware.py` or create new `src/agent/observability_middleware.py`
- **Details**:
  - Create middleware class that wraps agent operations
  - Start span on operation entry, set attributes from context
  - Capture operation duration and token usage
  - Record exceptions with proper error attributes
  - End span on operation completion
  - Emit events through EventBus for loose coupling
  - Follow existing middleware pattern in codebase
- **Validation**: Middleware emits spans for agent operations

### Task 8: Instrument AgentToolset Base Class
- **Description**: Add telemetry instrumentation to tool execution in base toolset class
- **Files to modify**:
  - `src/agent/tools/toolset.py`
- **Details**:
  - Add optional `_trace_tool_execution()` decorator/wrapper
  - Create span for tool execution with tool name and arguments (if sensitive data enabled)
  - Capture execution duration metric
  - Record tool results (if sensitive data enabled)
  - Handle errors and exceptions with proper attributes
  - Make instrumentation conditional on observability settings
- **Validation**: Tool executions create child spans under agent operation spans

### Task 9: Instrument Agent.run() Method
- **Description**: Add telemetry to core agent run method following Microsoft Agent Framework patterns
- **Files to modify**:
  - `src/agent/agent.py`
- **Details**:
  - Wrap `run()` method to create root span for agent invocation
  - Set span attributes: agent name, model, provider, instructions
  - Capture input messages (if sensitive data enabled)
  - Record token usage from response
  - Capture output messages (if sensitive data enabled)
  - Record operation duration metric
  - Use context manager pattern for span lifecycle
- **Validation**: Agent runs create spans with all expected attributes

### Task 10: Add Token Usage and Duration Metrics
- **Description**: Implement metrics collection for token usage and operation duration
- **Files to modify**:
  - `src/agent/observability.py`, `src/agent/agent.py`
- **Details**:
  - Create histogram metrics for input/output tokens
  - Create histogram metric for operation duration
  - Use appropriate bucket boundaries from Microsoft Agent Framework
  - Tag metrics with operation type, provider, model
  - Record metrics in agent and tool instrumentation
  - Follow OpenTelemetry Metrics API patterns
- **Validation**: Metrics are recorded and exported correctly

### Task 11: Implement Error and Exception Tracking
- **Description**: Add comprehensive error tracking to telemetry
- **Files to modify**:
  - `src/agent/observability.py`, middleware and instrumentation files
- **Details**:
  - Implement `capture_exception()` helper function
  - Set error attributes on spans (error.type)
  - Record exceptions with stack traces
  - Set span status to ERROR with description
  - Add error events to spans
  - Capture error metrics/counters
- **Validation**: Errors create proper span status and events

### Task 12: Update .env.example Documentation
- **Description**: Document all observability environment variables with examples
- **Files to modify**:
  - `.env.example`
- **Details**:
  - Add section for observability configuration
  - Document: ENABLE_OTEL, ENABLE_SENSITIVE_DATA, APPLICATIONINSIGHTS_CONNECTION_STRING, OTLP_ENDPOINT, VS_CODE_EXTENSION_PORT
  - Provide example values for each backend
  - Add security warning for ENABLE_SENSITIVE_DATA
  - Include links to relevant documentation
- **Validation**: Documentation is clear and complete

### Task 13: Create Unit Tests for Observability Module
- **Description**: Write comprehensive unit tests for all observability functions
- **Files to create**:
  - `tests/unit/test_observability.py`
- **Details**:
  - Test `ObservabilitySettings` loading from environment
  - Test `setup_observability()` with different configurations
  - Test exporter creation functions
  - Test `get_tracer()` and `get_meter()` helpers
  - Test span creation and attribute setting
  - Test metric recording
  - Mock OpenTelemetry components to avoid actual telemetry
  - Achieve >85% code coverage
- **Validation**: `uv run pytest tests/unit/test_observability.py --cov=src/agent/observability --cov-fail-under=85`

### Task 14: Create Integration Tests
- **Description**: Write integration tests that verify end-to-end telemetry flow
- **Files to create**:
  - `tests/integration/test_observability_integration.py`
- **Details**:
  - Test agent execution with observability enabled
  - Test tool execution creates child spans
  - Test metrics are recorded correctly
  - Test error scenarios create proper telemetry
  - Use in-memory span exporter for verification
  - Test with mock LLM to avoid API costs
  - Follow existing integration test patterns
- **Validation**: Integration tests pass showing complete telemetry flow

### Task 15: Create Usage Example
- **Description**: Create example script demonstrating observability usage
- **Files to create**:
  - `examples/observability_example.py`
- **Details**:
  - Show basic setup with `setup_observability()`
  - Demonstrate console output configuration
  - Show OTLP endpoint configuration
  - Show Application Insights configuration
  - Include example of using custom spans
  - Add comments explaining each section
  - Follow coding style from existing examples
- **Validation**: Example runs successfully and emits telemetry

### Task 16: Create Architecture Decision Record
- **Description**: Document the observability implementation decisions
- **Files to create**:
  - `docs/decisions/0014-observability-integration.md`
- **Details**:
  - Document context and problem statement
  - List decision drivers (compliance, alignment with Microsoft patterns, non-intrusive design)
  - Describe considered options
  - Explain chosen approach and rationale
  - Document consequences (good, neutral, bad)
  - Include validation approach
  - Reference Microsoft Agent Framework patterns
  - Follow ADR template
- **Validation**: ADR is complete and follows template

### Task 17: Run Validation Commands
- **Description**: Execute all validation commands to ensure quality
- **Files**: All modified files
- **Commands**:
  ```bash
  # Run tests with coverage
  uv run pytest -m "not llm" -n auto --cov=src/agent --cov-fail-under=85

  # Format code
  uv run black src/agent/ tests/ examples/

  # Lint code
  uv run ruff check --fix src/agent/ tests/ examples/

  # Type check
  uv run mypy src/agent/

  # Verify observability with console output
  uv run python examples/observability_example.py
  ```
- **Validation**: All commands pass without errors

## Testing Strategy

### Unit Tests
Tests for individual observability components in isolation:

- **ObservabilitySettings**
  - Test loading from environment variables
  - Test validation of connection strings and endpoints
  - Test ENABLED property logic
  - Test default values

- **setup_observability()**
  - Test with OTLP endpoint configuration
  - Test with Application Insights configuration
  - Test with multiple exporters
  - Test with custom exporters
  - Test with no configuration (console fallback)
  - Test singleton behavior (multiple calls)

- **Tracer and Meter Helpers**
  - Test `get_tracer()` returns valid tracer
  - Test `get_meter()` returns valid meter
  - Test default parameters
  - Test custom parameters

- **Exporter Creation**
  - Test `_get_otlp_exporters()` creates correct exporters
  - Test `_get_azure_monitor_exporters()` with connection string
  - Test `_get_azure_monitor_exporters()` with credential
  - Test exporter deduplication

### Integration Tests
Tests verifying end-to-end telemetry flow:

- **Agent Instrumentation**
  - Test agent run creates root span
  - Test span attributes include agent metadata
  - Test token usage metrics recorded
  - Test duration metrics recorded
  - Test sensitive data capture (when enabled)

- **Tool Instrumentation**
  - Test tool execution creates child span
  - Test tool span includes tool name and description
  - Test tool duration recorded
  - Test tool errors captured

- **Error Handling**
  - Test exceptions create error spans
  - Test error attributes set correctly
  - Test span status set to ERROR
  - Test exception details recorded

- **Multiple Exporters**
  - Test telemetry sent to multiple backends
  - Test console + OTLP configuration
  - Test Application Insights + OTLP configuration

### Edge Cases
- Empty/invalid connection strings
- Missing environment variables
- Observability disabled (no performance impact)
- Observability enabled but no exporters configured
- Concurrent agent executions (trace context propagation)
- Very long tool executions (span timeout handling)
- Large token counts (metric bucket boundaries)
- Sensitive data toggle mid-execution

## Acceptance Criteria

- [ ] OpenTelemetry dependencies verified (already available via `agent-framework>=1.0.0b251007`)
- [ ] `ObservabilitySettings` class loads from environment variables
- [ ] `setup_observability()` function creates providers for traces, logs, and metrics
- [ ] Support for OTLP endpoint exporters
- [ ] Support for Azure Application Insights exporters
- [ ] Support for console exporters (fallback)
- [ ] `get_tracer()` and `get_meter()` helper functions work correctly
- [ ] Agent operations create spans with proper attributes
- [ ] Tool executions create child spans
- [ ] Token usage metrics recorded (input/output)
- [ ] Operation duration metrics recorded
- [ ] Errors and exceptions tracked with proper attributes
- [ ] Sensitive data capture can be toggled via environment variable
- [ ] Observability can be disabled (default state)
- [ ] Unit tests achieve >85% code coverage
- [ ] Integration tests verify end-to-end telemetry flow
- [ ] Code formatted with Black (line length 100)
- [ ] Code passes Ruff linting
- [ ] Code passes Mypy type checking
- [ ] Documentation in `.env.example` is complete
- [ ] Usage example demonstrates all major features
- [ ] ADR documents the implementation decisions

## Validation Commands

```bash
# Run all tests (excludes LLM tests to avoid API costs)
uv run pytest -m "not llm" -n auto

# Run tests with coverage (must meet 85% threshold)
uv run pytest --cov=src/agent --cov-fail-under=85 -m "not llm"

# Run only observability tests
uv run pytest tests/unit/test_observability.py tests/integration/test_observability_integration.py -v

# Code quality checks
uv run black src/agent/ tests/ examples/
uv run ruff check --fix src/agent/ tests/ examples/
uv run mypy src/agent/

# Test with console output
ENABLE_OTEL=true uv run python examples/observability_example.py

# Test with Aspire Dashboard (requires Docker)
# 1. Start Aspire Dashboard:
docker run --rm -it -d -p 18888:18888 -p 4317:18889 --name aspire-dashboard mcr.microsoft.com/dotnet/aspire-dashboard:latest
# 2. Run example:
ENABLE_OTEL=true OTLP_ENDPOINT=http://localhost:4317 uv run python examples/observability_example.py
# 3. View at http://localhost:18888

# Test with Application Insights (requires Azure resource)
ENABLE_OTEL=true APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=..." uv run python examples/observability_example.py
```

## Notes

### Implementation Guidelines
1. **Follow Microsoft Agent Framework patterns exactly** - The reference implementation in `ai-examples/agent-framework` provides proven patterns
2. **Non-intrusive design** - Observability must be optional and have zero performance impact when disabled
3. **Leverage existing patterns** - Use EventBus for telemetry events, follow middleware pattern for instrumentation
4. **Semantic conventions** - Follow OpenTelemetry GenAI semantic conventions strictly
5. **Security first** - Sensitive data (prompts/responses) only in dev environments, default to disabled

### Future Considerations
- Support for additional APM vendors (Prometheus, Jaeger, etc.)
- Custom span processors for advanced filtering
- Distributed tracing across multiple agents
- Performance optimization for high-throughput scenarios
- Automatic sampling configuration
- Context propagation for async operations
- Integration with VS Code AI Toolkit
- Grafana dashboard templates

### Dependencies on Other Features
- Event Bus (ADR-0005) - Used for emitting telemetry events
- Middleware (ADR-0012) - Pattern for instrumentation
- Configuration (src/agent/config.py) - Settings management

### Performance Considerations
- Observability disabled: Zero overhead (no-op tracer/meter)
- Observability enabled: Minimal overhead (<5% in Microsoft Agent Framework benchmarks)
- Batch processors for exporters (reduce I/O)
- Histogram bucket boundaries optimized for GenAI workloads
- Async export to avoid blocking agent operations

## Execution

This spec can be implemented using: `/implement docs/specs/observability-integration.md`
