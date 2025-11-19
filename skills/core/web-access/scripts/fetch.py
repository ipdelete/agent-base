#!/usr/bin/env python3
# /// script
# dependencies = [
#     "httpx",
#     "beautifulsoup4",
#     "markdownify",
#     "click",
# ]
# ///

"""
Web Fetch Script

Fetch and parse web page content, converting HTML to clean markdown.
Supports timeout configuration and size limits.

Usage:
    uv run fetch.py --url "https://example.com"
    uv run fetch.py --url "https://example.com" --json
    uv run fetch.py --url "https://example.com" --timeout 60
"""

import json
import os
import sys
from urllib.parse import urlparse

import click
import httpx
from bs4 import BeautifulSoup  # type: ignore
from markdownify import markdownify as md  # type: ignore

# Configuration defaults
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_MAX_SIZE = 1048576  # 1MB


def is_valid_url(url: str) -> bool:
    """Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if URL is valid (http/https), False otherwise
    """
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def html_to_markdown(html: str) -> str:
    """Convert HTML content to clean markdown.

    Removes scripts, styles, and other non-content elements before conversion.

    Args:
        html: HTML content to convert

    Returns:
        Markdown representation of the content
    """
    # Parse HTML
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style elements
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()

    # Convert to markdown
    markdown = md(str(soup), heading_style="ATX", strip=["img"])

    # Clean up excessive whitespace
    lines = [line.strip() for line in markdown.split("\n")]
    clean_lines = [line for line in lines if line]  # Remove empty lines

    return "\n\n".join(clean_lines)


def fetch_web_page(url: str, timeout: int, max_size: int) -> dict:
    """Fetch and parse web page content.

    Args:
        url: URL to fetch content from
        timeout: Request timeout in seconds
        max_size: Maximum response size in bytes

    Returns:
        Dict with success, result/error, and message
    """
    # Validate URL
    if not is_valid_url(url):
        return {
            "success": False,
            "error": "invalid_url",
            "message": f"URL must start with http:// or https://. Got: {url}",
        }

    try:
        # Fetch content with timeout
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()

            # Check content size
            content_length = len(response.content)
            if content_length > max_size:
                return {
                    "success": False,
                    "error": "content_too_large",
                    "message": f"Response size ({content_length} bytes) exceeds maximum ({max_size} bytes)",
                }

            # Parse HTML to markdown
            markdown_content = html_to_markdown(response.text)

            return {
                "success": True,
                "result": markdown_content,
                "message": f"Successfully fetched {len(markdown_content)} characters from {url}",
            }

    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "timeout",
            "message": f"Request timed out after {timeout} seconds",
        }

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": "http_error",
            "message": f"HTTP {e.response.status_code}: {e.response.reason_phrase}",
        }

    except httpx.RequestError as e:
        return {
            "success": False,
            "error": "request_error",
            "message": f"Request failed: {str(e)}",
        }

    except Exception as e:
        return {
            "success": False,
            "error": "unknown_error",
            "message": f"Unexpected error: {str(e)}",
        }


def format_markdown_output(url: str, markdown: str) -> str:
    """Format markdown for human-readable output.

    Args:
        url: Source URL
        markdown: Markdown content

    Returns:
        Formatted string for display
    """
    lines = []
    lines.append("\n" + "=" * 60)
    lines.append(f"📄 Content from {url}")
    lines.append("=" * 60)
    lines.append("")
    lines.append(markdown)
    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


@click.command()
@click.option("--url", required=True, help="URL to fetch content from")
@click.option(
    "--timeout",
    default=None,
    type=int,
    help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})",
)
@click.option(
    "--max-size",
    default=None,
    type=int,
    help=f"Maximum response size in bytes (default: {DEFAULT_MAX_SIZE})",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output as JSON instead of human-readable format",
)
def main(url: str, timeout: int | None, max_size: int | None, output_json: bool) -> None:
    """
    Fetch and parse web page content.

    Retrieves HTML content from the specified URL and converts it to clean
    markdown format. Handles timeouts, HTTP errors, and invalid URLs gracefully.

    Environment variables:
        WEB_FETCH_TIMEOUT - Default timeout in seconds
        WEB_FETCH_MAX_SIZE - Default max response size in bytes

    Examples:
        uv run fetch.py --url "https://example.com"
        uv run fetch.py --url "https://example.com" --json
        uv run fetch.py --url "https://example.com" --timeout 60
    """
    try:
        # Get timeout from env or use default
        if timeout is None:
            timeout = int(os.getenv("WEB_FETCH_TIMEOUT", str(DEFAULT_TIMEOUT)))

        # Get max_size from env or use default
        if max_size is None:
            max_size = int(os.getenv("WEB_FETCH_MAX_SIZE", str(DEFAULT_MAX_SIZE)))

        # Fetch and parse
        result = fetch_web_page(url, timeout, max_size)

        # Output results
        if output_json:
            click.echo(json.dumps(result, indent=2))
        else:
            if result["success"]:
                formatted = format_markdown_output(url, result["result"])
                click.echo(formatted)
            else:
                click.echo(f"❌ Error ({result['error']}): {result['message']}", err=True)

        sys.exit(0 if result["success"] else 1)

    except Exception as e:
        if output_json:
            error_data = {"success": False, "error": "script_error", "message": str(e)}
            click.echo(json.dumps(error_data, indent=2))
        else:
            click.echo(f"❌ Script Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
