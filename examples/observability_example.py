"""Example demonstrating observability integration with OpenTelemetry.

This example shows how to:
1. Setup observability with console output
2. Setup observability with OTLP endpoint (Aspire Dashboard, Jaeger, etc.)
3. Setup observability with Azure Application Insights
4. Use custom spans for additional instrumentation

Prerequisites:
    - Set OPENAI_API_KEY or ANTHROPIC_API_KEY in your environment
    - For OTLP: Run Aspire Dashboard locally (see commands below)
    - For App Insights: Create Application Insights resource in Azure

Running Aspire Dashboard locally:
    docker run --rm -it -p 18888:18888 -p 4317:18889 \\
        mcr.microsoft.com/dotnet/aspire-dashboard:latest

    Then open: http://localhost:18888
"""

import asyncio
import os

from agent_framework.observability import get_tracer, setup_observability

from agent.agent import Agent
from agent.config import AgentConfig


async def example_console_output() -> None:
    """Example 1: Console output (development/debugging).

    This is the simplest setup - telemetry is printed to console.
    Useful for local development and debugging.
    """
    print("\n" + "=" * 70)
    print("Example 1: Console Output")
    print("=" * 70)

    # Setup observability with console output (no endpoint needed)
    result = setup_observability()
    print(f"Setup result: {result}")

    # Create agent
    config = AgentConfig.from_env()
    config.enable_otel = True
    agent = Agent(config=config)

    # Run agent - telemetry will be printed to console
    print("\nRunning agent with console telemetry...")
    response = await agent.run("Say hello")
    print(f"Response: {response}\n")


async def example_otlp_endpoint() -> None:
    """Example 2: OTLP endpoint (Aspire Dashboard, Jaeger, etc.).

    This sends telemetry to an OTLP-compatible endpoint.
    Great for local development with Aspire Dashboard or connecting to
    observability platforms like Jaeger, Prometheus, or Grafana.

    Prerequisites:
        Run Aspire Dashboard:
        docker run --rm -it -p 18888:18888 -p 4317:18889 \\
            mcr.microsoft.com/dotnet/aspire-dashboard:latest
    """
    print("\n" + "=" * 70)
    print("Example 2: OTLP Endpoint (Aspire Dashboard)")
    print("=" * 70)

    # Check if OTLP endpoint is configured
    otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
    print(f"OTLP endpoint: {otlp_endpoint}")

    # Setup observability with OTLP endpoint
    result = setup_observability(otlp_endpoint=otlp_endpoint)
    print(f"Setup result: {result}")

    # Create agent
    config = AgentConfig.from_env()
    config.enable_otel = True
    agent = Agent(config=config)

    # Run agent - telemetry will be sent to OTLP endpoint
    print("\nRunning agent with OTLP telemetry...")
    print("View telemetry at: http://localhost:18888")
    response = await agent.run("Say hello and tell me a fun fact")
    print(f"Response: {response}\n")


async def example_application_insights() -> None:
    """Example 3: Azure Application Insights.

    This sends telemetry to Azure Application Insights for production monitoring.

    Prerequisites:
        1. Create Application Insights resource in Azure Portal
        2. Get connection string from: Overview > Connection String
        3. Set APPLICATIONINSIGHTS_CONNECTION_STRING environment variable
    """
    print("\n" + "=" * 70)
    print("Example 3: Azure Application Insights")
    print("=" * 70)

    # Check if App Insights is configured
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not connection_string:
        print("APPLICATIONINSIGHTS_CONNECTION_STRING not set. Skipping example.")
        return

    print("Application Insights connection string configured")

    # Setup observability with Application Insights
    result = setup_observability(appinsights_connection_string=connection_string)
    print(f"Setup result: {result}")

    # Create agent
    config = AgentConfig.from_env()
    config.enable_otel = True
    agent = Agent(config=config)

    # Run agent - telemetry will be sent to App Insights
    print("\nRunning agent with Application Insights telemetry...")
    print("View telemetry in Azure Portal > Application Insights > Transaction search")
    response = await agent.run("Say hello and explain what observability is")
    print(f"Response: {response}\n")


async def example_custom_spans() -> None:
    """Example 4: Custom spans for additional instrumentation.

    Shows how to create custom spans to instrument your own code.
    This is useful for tracking specific operations or business logic.
    """
    print("\n" + "=" * 70)
    print("Example 4: Custom Spans")
    print("=" * 70)

    # Setup observability (console output for this example)
    result = setup_observability()
    print(f"Setup result: {result}")

    # Get tracer for creating custom spans
    tracer = get_tracer(__name__)

    # Create a custom span for a business operation
    with tracer.start_as_current_span("custom_business_operation") as span:
        print("\nInside custom span...")

        # Set custom attributes
        span.set_attribute("business.operation", "user_greeting")
        span.set_attribute("business.priority", "high")

        # Create agent
        config = AgentConfig.from_env()
        config.enable_otel = True
        agent = Agent(config=config)

        # Agent operations will be child spans of our custom span
        response = await agent.run("Say hello")
        print(f"Response: {response}")

        # Add result to span
        span.set_attribute("business.success", True)
        span.set_attribute("business.response_length", len(response))

    print("\nCustom span completed\n")


async def example_multiple_exporters() -> None:
    """Example 5: Multiple exporters (OTLP + Application Insights).

    Shows how to send telemetry to multiple destinations simultaneously.
    Useful for combining local development (Aspire) with production monitoring (App Insights).
    """
    print("\n" + "=" * 70)
    print("Example 5: Multiple Exporters")
    print("=" * 70)

    # Check if both are configured
    otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    if not connection_string:
        print("APPLICATIONINSIGHTS_CONNECTION_STRING not set. Skipping example.")
        return

    print(f"OTLP endpoint: {otlp_endpoint}")
    print("Application Insights: configured")

    # Setup observability with both exporters
    result = setup_observability(
        otlp_endpoint=otlp_endpoint, appinsights_connection_string=connection_string
    )
    print(f"Setup result: {result}")

    # Create agent
    config = AgentConfig.from_env()
    config.enable_otel = True
    agent = Agent(config=config)

    # Run agent - telemetry will be sent to both destinations
    print("\nRunning agent with multiple exporters...")
    print("View in Aspire: http://localhost:18888")
    print("View in Azure: Portal > Application Insights > Transaction search")
    response = await agent.run("Say hello and tell me about distributed tracing")
    print(f"Response: {response}\n")


async def main() -> None:
    """Run all observability examples."""
    print("\n" + "=" * 70)
    print("Agent Base - Observability Examples")
    print("=" * 70)

    # Run examples based on what's configured
    examples_to_run = []

    # Example 1: Always run console example
    examples_to_run.append(("Console Output", example_console_output()))

    # Example 2: Run if OTLP endpoint is available
    if os.getenv("OTLP_ENDPOINT"):
        examples_to_run.append(("OTLP Endpoint", example_otlp_endpoint()))

    # Example 3: Run if App Insights is configured
    if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
        examples_to_run.append(("Application Insights", example_application_insights()))

    # Example 4: Custom spans
    examples_to_run.append(("Custom Spans", example_custom_spans()))

    # Example 5: Multiple exporters (if both configured)
    if os.getenv("OTLP_ENDPOINT") and os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
        examples_to_run.append(("Multiple Exporters", example_multiple_exporters()))

    # Run all examples
    for name, example in examples_to_run:
        try:
            await example
        except Exception as e:
            print(f"\n❌ Example '{name}' failed: {e}\n")

    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    # Ensure ENABLE_OTEL is set for this example
    os.environ["ENABLE_OTEL"] = "true"

    # Run examples
    asyncio.run(main())
