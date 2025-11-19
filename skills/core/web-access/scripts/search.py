#!/usr/bin/env python3
# /// script
# dependencies = [
#     "httpx",
#     "click",
# ]
# ///

"""
Web Search Script using Brave Search API

Search the internet using Brave Search API.
Requires BRAVE_API_KEY environment variable.

Usage:
    uv run search.py --query "anthropic claude"
    uv run search.py --query "python" --count 10
    uv run search.py --query "keyword" --json
"""

import json
import os
import sys

import click
import httpx

# Configuration
API_BASE_URL = "https://api.search.brave.com/res/v1"
API_TIMEOUT = 30.0  # seconds
USER_AGENT = "agent-base-web-access/1.0"


class BraveSearchClient:
    """HTTP client for Brave Search API"""

    def __init__(self, api_key: str):
        """Initialize Brave Search client

        Args:
            api_key: Brave Search API key
        """
        self.api_key = api_key
        self.client = httpx.Client(
            base_url=API_BASE_URL,
            timeout=API_TIMEOUT,
            headers={
                "User-Agent": USER_AGENT,
                "X-Subscription-Token": api_key,
                "Accept": "application/json",
            },
        )

    def __enter__(self) -> "BraveSearchClient":
        """Context manager entry"""
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Context manager exit - cleanup"""
        self.client.close()

    def search(self, query: str, count: int = 10) -> list[dict]:
        """Search using Brave Search API

        Args:
            query: Search query
            count: Number of results to return (max 20)

        Returns:
            List of search results with title, url, description

        Raises:
            Exception if API call fails
        """
        try:
            params = {
                "q": query,
                "count": str(min(count, 20)),  # Brave API max is 20
            }

            response = self.client.get("/web/search", params=params)
            response.raise_for_status()
            data = response.json()

            # Extract web results
            web_results = data.get("web", {}).get("results", [])

            # Format results
            results = []
            for result in web_results:
                results.append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "description": result.get("description", ""),
                    }
                )

            return results

        except httpx.HTTPStatusError as e:
            raise Exception(f"API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")


def format_search_result(result: dict, index: int) -> str:
    """Format a single search result"""
    title = result.get("title", "N/A")
    url = result.get("url", "N/A")
    description = result.get("description", "")

    lines = []
    lines.append(f"{index}. {title}")
    lines.append(f"   {url}")

    if description:
        # Truncate long descriptions
        desc = description[:200] + "..." if len(description) > 200 else description
        lines.append(f"   {desc}")

    return "\n".join(lines)


def format_search_results(query: str, results: list[dict]) -> str:
    """Format search results for human-readable output

    Args:
        query: Search query
        results: List of search results

    Returns:
        Formatted string for display
    """
    lines = []
    lines.append("\n" + "=" * 60)
    lines.append(f"🔍 Web Search Results for '{query}'")
    lines.append("=" * 60)

    if not results:
        lines.append("\nNo results found for your search.")
        lines.append("\nTip: Try different keywords.")
    else:
        lines.append(f"Found {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            lines.append(format_search_result(result, i))
            lines.append("")

        lines.append("─" * 60)
        lines.append("Powered by Brave Search API")

    lines.append("=" * 60)
    return "\n".join(lines)


@click.command()
@click.option("--query", required=True, help="Search query")
@click.option("--count", default=10, type=int, help="Number of results (max 20)")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output as JSON instead of human-readable format",
)
def main(query: str, count: int, output_json: bool) -> None:
    """
    Search the web using Brave Search API.

    Requires BRAVE_API_KEY environment variable.

    Examples:
        uv run search.py --query "anthropic claude"
        uv run search.py --query "python" --count 5 --json
    """
    try:
        # Get API key from environment
        api_key = os.getenv("BRAVE_API_KEY")
        if not api_key:
            raise ValueError(
                "BRAVE_API_KEY environment variable is required. "
                "Get a free API key at https://brave.com/search/api/"
            )

        if not query.strip():
            raise ValueError("Query cannot be empty")

        # Search via API
        with BraveSearchClient(api_key) as client:
            results = client.search(query, count)

        # Output results
        if output_json:
            click.echo(json.dumps(results, indent=2))
        else:
            formatted = format_search_results(query, results)
            click.echo(formatted)

        sys.exit(0)

    except Exception as e:
        if output_json:
            error_data = {"error": str(e)}
            click.echo(json.dumps(error_data, indent=2))
        else:
            click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
