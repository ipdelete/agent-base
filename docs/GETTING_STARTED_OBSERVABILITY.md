# Getting Started with Observability (2 Minutes)

## For Non-Azure Users - Local Aspire Dashboard

### Step 1: Start Aspire Dashboard (from within agent)

```bash
uv run agent
```

Then in the agent:
```
> /telemetry start
✓ Aspire Dashboard started successfully!
📊 Dashboard: http://localhost:18888
🔌 OTLP Endpoint: http://localhost:4317
```

### Step 2: Enable telemetry

```bash
export ENABLE_OTEL=true
```

That's it! The endpoint defaults to `http://localhost:4317`.

### Step 3: Run your agent with telemetry

```bash
uv run agent -p "hello world"
```

### Step 4: View telemetry

1. Open http://localhost:18888 (no login required!)
2. Click **"Traces"** tab to see:
- Full execution hierarchy
- Token usage
- Duration metrics
- Tool executions

## What Each Tab Shows

**Traces:**
- Agent executions with parent-child relationships
- LLM API calls with token counts
- Tool executions with duration
- Filter by `session.id` to see full conversations

**Metrics:**
- Token usage histograms
- Duration metrics
- Request counts

**Structured Logs:**
- Application logs with trace correlation
- Search by session.id, trace_id, or keywords

## Query by Session

1. Go to Traces tab
2. Click "Add Filter"
3. Add: `session.id` = `2025-11-10-09-30-22`
4. See all messages from that chat session

## Manage Aspire Dashboard

**From CLI:**
```bash
uv run agent --telemetry start   # Start dashboard
uv run agent --telemetry stop    # Stop dashboard
uv run agent --telemetry status  # Check if running
uv run agent --telemetry url     # Show URLs
```

**From interactive mode:**
```
> /telemetry start
> /telemetry stop
> /telemetry status
```

## Next Level: Production with Application Insights

See [OBSERVABILITY.md](OBSERVABILITY.md) for Azure setup.

## Tips

**Cost tracking:**
- Filter by `gen_ai.request.model`
- Sum `gen_ai.usage.total_tokens`
- Multiply by model price per token

**Performance analysis:**
- Sort by duration
- Find slow operations
- Identify bottlenecks

**Debugging:**
- Use `session.id` to find matching log file
- See full trace hierarchy
- Identify which tool/LLM call failed
