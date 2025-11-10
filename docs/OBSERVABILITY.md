# Observability Quick Start

Simple guide to get observability working locally in under 2 minutes.

## Local Development (Telemetry Dashboard)

**Step 1: Start telemetry dashboard**
```bash
uv run agent --telemetry start
```

**Step 2: Configure environment**
```bash
# Copy local config
cp .env.local .env

# Add your API key
# Edit .env and set OPENAI_API_KEY or ANTHROPIC_API_KEY
```

**Step 3: Run your agent**
```bash
uv run agent -p "hello world"
```

**Step 4: View telemetry**

Open http://localhost:18888 in your browser

You'll see:
- **Traces**: Full execution hierarchy (agent → LLM calls → tool executions)
- **Metrics**: Token usage, duration, request counts
- **Structured Logs**: Application logs with correlation

## What You'll See

### Single-Prompt Mode
```
agent-base.cli.single-prompt (5.4s)
  └─ invoke_agent Agent (5.4s)
      ├─ chat gpt-5-mini (3.5s) - 898 tokens
      ├─ execute_tool hello_world (0.001s)
      └─ chat gpt-5-mini (1.9s) - 887 tokens
```

### Interactive Mode
Each message creates a trace:
```
agent-base.message (7.0s)
  └─ invoke_agent Agent (7.0s)
      ├─ chat gpt-5-mini (5.6s)
      └─ execute_tool hello_world (0.001s)
```

All messages share the same `session.id` for correlation.

## Key Attributes

Every trace includes:
- `session.id`: Correlates with log file (`~/.agent/logs/session-YYYY-MM-DD-HH-MM-SS.log`)
- `mode`: "interactive" or "single-prompt"
- `gen_ai.system`: "openai", "anthropic", etc.
- `gen_ai.request.model`: "gpt-5-mini", "claude-sonnet-4-5", etc.
- `gen_ai.usage.input_tokens`: Input token count
- `gen_ai.usage.output_tokens`: Output token count
- `gen_ai.usage.total_tokens`: Total tokens (for cost tracking)

## Query Examples in Aspire

**All traces for a session:**
- Filter by `session.id = "2025-11-10-09-30-22"`

**Token usage by model:**
- Group by `gen_ai.request.model`
- Sum `gen_ai.usage.total_tokens`

**Interactive vs Single-prompt:**
- Filter by `mode = "interactive"` or `mode = "single-prompt"`

## Stopping Dashboard

```bash
# Stop the dashboard
uv run agent --telemetry stop
```

## Troubleshooting

**Port already in use?**
```bash
# Check what's using the port
lsof -i :4317
lsof -i :18888

# Stop any conflicting containers
docker ps
docker stop <container-id>
```

**Not seeing traces?**
- Make sure `ENABLE_OTEL=true` is set
- Check `OTLP_ENDPOINT=http://localhost:4317` (not https!)
- Verify Aspire is running: `docker ps | grep aspire`
- Wait 1-2 seconds for async export

**Telemetry to console instead:**
```bash
# Set only ENABLE_OTEL, no endpoint
ENABLE_OTEL=true uv run agent -p "hello"
# Spans will be printed to console
```

## Production: Azure Application Insights

For production monitoring, switch to Application Insights:

```bash
# In .env
ENABLE_OTEL=true
APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=xxx;IngestionEndpoint=https://xxx"

# Can use both simultaneously!
ENABLE_OTEL=true
OTLP_ENDPOINT=http://localhost:4317
APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=xxx"
```

## More Information

- Architecture Decision: [docs/decisions/0014-observability-integration.md](decisions/0014-observability-integration.md)
- Full spec: [docs/specs/observability-integration.md](specs/observability-integration.md)
- Examples: [examples/observability_example.py](../examples/observability_example.py)
- OpenTelemetry docs: https://opentelemetry.io/docs/
- Aspire Dashboard: https://learn.microsoft.com/en-us/dotnet/aspire/fundamentals/dashboard
