"""CLI entry point for Agent."""

import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import typer
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.console import Console

from agent import __version__
from agent.agent import Agent
from agent.config import AgentConfig
from agent.display import (
    DisplayMode,
    ExecutionContext,
    ExecutionTreeDisplay,
    set_execution_context,
)
from agent.persistence import ThreadPersistence
from agent.utils.keybindings import ClearPromptHandler, KeybindingManager
from agent.utils.terminal import TIMEOUT_EXIT_CODE, clear_screen, execute_shell_command

app = typer.Typer(help="Agent - AI-powered conversational assistant with extensible tools")
console = Console()


def _save_last_session(session_name: str) -> None:
    """Save the last session name for --continue.

    Args:
        session_name: Name of the session to track
    """
    try:
        last_session_file = Path.home() / ".agent" / "last_session"
        last_session_file.parent.mkdir(parents=True, exist_ok=True)

        with open(last_session_file, "w") as f:
            f.write(session_name)

    except Exception as e:
        import logging

        logging.warning(f"Failed to save last session marker: {e}")


def _get_last_session() -> str | None:
    """Get the last session name for --continue.

    Returns:
        Last session name or None if not found
    """
    try:
        last_session_file = Path.home() / ".agent" / "last_session"
        if last_session_file.exists():
            with open(last_session_file) as f:
                return f.read().strip()
    except Exception as e:
        import logging

        logging.warning(f"Failed to read last session marker: {e}")

    return None


def _render_startup_banner(config: AgentConfig) -> None:
    """Render startup banner with branding.

    Args:
        config: Agent configuration
    """
    console.print()
    console.print("[bold cyan]Agent[/bold cyan] - AI-powered conversational assistant")
    # Use markup=False to prevent Rich from interpreting hyphens in model name as markup
    console.print(f"Version {__version__} • {config.get_model_display_name()}", style="dim", markup=False)


def _get_status_bar_text() -> str:
    """Get status bar text without printing.

    Returns:
        Status bar text as string (path and branch, right-justified)
    """
    # Get current directory
    cwd = Path.cwd()
    try:
        cwd_display = f"~/{cwd.relative_to(Path.home())}"
    except ValueError:
        cwd_display = str(cwd)

    # Get git branch
    branch_display = ""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=1,
            cwd=cwd,
        )
        if result.returncode == 0 and result.stdout.strip():
            branch = result.stdout.strip()
            branch_display = f" [⎇ {branch}]"
    except Exception:
        pass

    # Right-justify the path and branch
    status = f"{cwd_display}{branch_display}"
    padding = max(0, console.width - len(status))

    return f"{' ' * padding}{status}"


def _show_help() -> None:
    """Show help message in interactive mode."""
    console.print("\n[bold]Available Commands:[/bold]")
    console.print("  [cyan]/clear[/cyan]     - Clear screen and start new conversation")
    console.print("  [cyan]/continue[/cyan]  - Resume a previous session")
    console.print("  [cyan]/purge[/cyan]     - Delete all saved sessions")
    console.print("  [cyan]/help[/cyan]      - Show this help message")
    console.print("  [cyan]exit[/cyan]       - Exit interactive mode")
    console.print()
    console.print("[bold]Shell Commands:[/bold]")
    console.print("  [cyan]!<command>[/cyan] - Execute shell command")
    console.print()
    console.print("[bold]Keyboard Shortcuts:[/bold]")
    console.print("  [cyan]ESC[/cyan]        - Clear current prompt")
    console.print("  [cyan]Ctrl+D[/cyan]     - Exit interactive mode")
    console.print("  [cyan]Ctrl+C[/cyan]     - Interrupt current operation")
    console.print()


async def _auto_save_session(
    persistence: ThreadPersistence,
    thread: Any,
    message_count: int,
    quiet: bool,
    messages: list[dict] | None = None,
) -> None:
    """Auto-save session on exit if it has messages.

    Args:
        persistence: ThreadPersistence instance
        thread: Conversation thread (can be None for some providers)
        message_count: Number of messages in session
        quiet: Whether to suppress output
        messages: Optional list of tracked messages for providers without thread support
    """
    if message_count > 0:
        try:
            # Generate auto-save name with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            session_name = timestamp

            await persistence.save_thread(
                thread,
                session_name,
                description="Auto-saved session",
                messages=messages,
            )

            # Save as last session for --continue
            _save_last_session(session_name)

            if not quiet:
                console.print(f"[dim]Session auto-saved as '{session_name}'[/dim]")
        except Exception as e:
            if not quiet:
                console.print(f"\n[yellow]Failed to auto-save session: {e}[/yellow]")


@app.command()
def main(
    prompt: str = typer.Option(None, "-p", "--prompt", help="Execute a single prompt and exit"),
    check: bool = typer.Option(False, "--check", help="Run health check for configuration"),
    config_flag: bool = typer.Option(False, "--config", help="Show current configuration"),
    version_flag: bool = typer.Option(False, "--version", help="Show version"),
    verbose: bool = typer.Option(
        False, "--verbose", help="Verbose output with detailed execution tree"
    ),
    quiet: bool = typer.Option(False, "--quiet", help="Minimal output mode"),
    resume: bool = typer.Option(False, "--continue", help="Resume last saved session"),
):
    """Agent - Generic chatbot agent with extensible tools.

    Examples:
        # Interactive mode
        agent

        # Run health check
        agent --check

        # Show configuration
        agent --config

        # Execute single prompt
        agent -p "Say hello to Alice"

        # Execute with verbose visualization
        agent -p "Say hello to Alice" --verbose

        # Resume previous session
        agent --continue

        # Show version
        agent --version
    """
    if version_flag:
        console.print(f"Agent version {__version__}")
        return

    if check:
        run_health_check()
        return

    if config_flag:
        show_configuration()
        return

    if prompt:
        # Single-prompt mode with optional visualization
        asyncio.run(run_single_prompt(prompt, verbose=verbose, quiet=quiet))
    else:
        # Interactive chat mode
        # Handle --continue flag: resume last session
        resume_session = None
        if resume:
            resume_session = _get_last_session()
            if not resume_session:
                console.print("[yellow]No previous session found. Starting new session.[/yellow]\n")

        asyncio.run(run_chat_mode(quiet=quiet, verbose=verbose, resume_session=resume_session))


def run_health_check():
    """Run health check for dependencies and configuration."""
    console.print("\n[bold]Agent Health Check[/bold]\n")

    try:
        config = AgentConfig.from_env()
        config.validate()

        console.print("[green]✓[/green] Configuration valid")
        console.print(f"  Provider: {config.llm_provider}")
        console.print(f"  Model: {config.get_model_display_name()}")

        if config.agent_data_dir:
            console.print(f"  Data Dir: {config.agent_data_dir}")

        console.print("\n[green]✓ All checks passed![/green]\n")

    except ValueError as e:
        console.print(f"[red]✗[/red] Configuration error: {e}")
        console.print("\n[yellow]See .env.example for configuration template[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗[/red] Unexpected error: {e}")
        raise typer.Exit(1)


def show_configuration():
    """Show current configuration."""
    console.print("\n[bold]Agent Configuration[/bold]\n")

    try:
        config = AgentConfig.from_env()

        console.print("[bold]LLM Provider:[/bold]")
        console.print(f" • Provider: {config.llm_provider}")
        console.print(f" • Model: {config.get_model_display_name()}")

        if config.llm_provider == "openai" and config.openai_api_key:
            masked_key = f"****{config.openai_api_key[-6:]}"
            console.print(f" • API Key: {masked_key}")
        elif config.llm_provider == "anthropic" and config.anthropic_api_key:
            masked_key = f"****{config.anthropic_api_key[-6:]}"
            console.print(f" • API Key: {masked_key}")
        elif config.llm_provider == "azure":
            console.print(f" • Endpoint: {config.azure_openai_endpoint}")
            if config.azure_openai_api_key:
                masked_key = f"****{config.azure_openai_api_key[-6:]}"
                console.print(f" • API Key: {masked_key}")
        elif config.llm_provider == "azure_ai_foundry":
            console.print(f" • Endpoint: {config.azure_project_endpoint}")

        console.print("\n[bold]Agent Settings:[/bold]")
        console.print(f" • Data Directory: {config.agent_data_dir}")
        if config.agent_session_dir:
            console.print(f" • Session Directory: {config.agent_session_dir}")

        console.print()

    except Exception as e:
        console.print(f"[red]Error loading configuration:[/red] {e}")
        raise typer.Exit(1)


async def run_single_prompt(prompt: str, verbose: bool = False, quiet: bool = False):
    """Run single prompt and display response.

    Args:
        prompt: User prompt to execute
        verbose: Show verbose execution tree
        quiet: Minimal output mode
    """
    try:
        config = AgentConfig.from_env()
        config.validate()

        agent = Agent(config=config)

        # Setup execution context for visualization
        display_mode = DisplayMode.VERBOSE if verbose else DisplayMode.MINIMAL
        ctx = ExecutionContext(
            is_interactive=False,
            show_visualization=not quiet,
            display_mode=display_mode,
        )
        set_execution_context(ctx)

        # Use execution tree display if visualization enabled
        if not quiet:
            execution_display = ExecutionTreeDisplay(
                console=console,
                display_mode=display_mode,
                show_completion_summary=True,
            )
            await execution_display.start()

            try:
                # Run agent (non-streaming for better visualization)
                response = await agent.run(prompt)

                # Stop display (shows completion summary with timing)
                await execution_display.stop()

            except KeyboardInterrupt:
                # User interrupted - stop display cleanly
                await execution_display.stop()
                console.print("\n[yellow]Interrupted by user[/yellow]\n")
                raise typer.Exit(130)
        else:
            # Quiet mode - no visualization
            response = await agent.run(prompt)

        # Display response after completion summary
        if response:
            console.print(f"\n{response}\n")
            console.print(f"[dim]{'─' * console.width}[/dim]")

    except ValueError as e:
        console.print(f"\n[red]Configuration error:[/red] {e}")
        console.print("[yellow]Run 'agent --check' to diagnose issues[/yellow]")
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        raise typer.Exit(1)


async def run_chat_mode(
    quiet: bool = False,
    verbose: bool = False,
    resume_session: str | None = None,
) -> None:
    """Run interactive chat mode.

    Args:
        quiet: Minimal output mode
        verbose: Verbose output mode with detailed execution tree
        resume_session: Session name to resume (from --continue flag)
    """
    try:
        # Load configuration
        config = AgentConfig.from_env()
        config.validate()

        # Show startup banner
        if not quiet:
            _render_startup_banner(config)

        # Create agent
        agent = Agent(config=config)

        # Initialize persistence manager
        persistence = ThreadPersistence()

        # Create or resume conversation thread
        thread = None
        message_count = 0
        conversation_messages: list[dict] = []  # Track messages for providers without thread support

        if resume_session:
            try:
                thread, context_summary = await persistence.load_thread(agent, resume_session)

                # If we have a context summary, restore AI context silently
                if context_summary:
                    if not quiet:
                        with console.status("[bold blue]Restoring context...", spinner="dots"):
                            # Send context summary to AI to restore understanding
                            await agent.run(context_summary, thread=thread)
                            message_count += 1
                    else:
                        await agent.run(context_summary, thread=thread)
                        message_count += 1

                # Show single clean status message after restore
                if not quiet:
                    console.print("[green]✓ Ready[/green]\n")
                    console.print(f"[dim]{'─' * console.width}[/dim]")

            except FileNotFoundError:
                console.print(
                    f"[yellow]Session '{resume_session}' not found. Starting new session.[/yellow]\n"
                )
                thread = agent.get_new_thread()
            except Exception as e:
                console.print(
                    f"[yellow]Failed to resume session: {e}. Starting new session.[/yellow]\n"
                )
                thread = agent.get_new_thread()

        if thread is None:
            thread = agent.get_new_thread()

        # Setup keybinding manager
        keybinding_manager = KeybindingManager()
        keybinding_manager.register_handler(ClearPromptHandler())
        key_bindings = keybinding_manager.create_keybindings()

        # Setup prompt session with history
        history_file = Path.home() / ".agent_history"

        session: PromptSession = PromptSession(
            history=FileHistory(str(history_file)),
            key_bindings=key_bindings,
        )

        # Interactive loop
        while True:
            try:
                # Print status bar before prompt
                if not quiet:
                    status_text = _get_status_bar_text()
                    console.print(f"\n[dim]{status_text}[/dim]")
                    console.print(f"[dim]{'─' * console.width}[/dim]")

                # Get user input
                user_input = await session.prompt_async("> ")

                if not user_input or not user_input.strip():
                    continue

                # Handle shell commands (lines starting with !)
                if user_input.strip().startswith("!"):
                    command = user_input.strip()[1:].strip()

                    if not command:
                        console.print(
                            "\n[yellow]No command specified. Type !<command> to execute shell commands.[/yellow]\n"
                        )
                        continue

                    # Show what we're executing
                    console.print(f"\n[dim]$ {command}[/dim]")

                    # Execute the command
                    exit_code, stdout, stderr = execute_shell_command(command)

                    # Display output
                    if stdout:
                        console.print(stdout, end="")
                    if stderr:
                        console.print(f"[red]{stderr}[/red]", end="")

                    # Display exit code
                    if exit_code == 0:
                        console.print(f"\n[dim][green]Exit code: {exit_code}[/green][/dim]")
                    elif exit_code == TIMEOUT_EXIT_CODE:
                        console.print(
                            f"\n[dim][yellow]Exit code: {exit_code} (timeout)[/yellow][/dim]"
                        )
                    else:
                        console.print(f"\n[dim][red]Exit code: {exit_code}[/red][/dim]")

                    console.print()
                    continue

                # Handle special commands
                cmd = user_input.strip().lower()

                if cmd in ["exit", "quit", "q"]:
                    # Auto-save session before exit
                    await _auto_save_session(
                        persistence, thread, message_count, quiet, conversation_messages
                    )
                    console.print("\n[dim]Goodbye![/dim]")
                    break

                if cmd in ["help", "?", "/help"]:
                    _show_help()
                    continue

                # Handle /clear command
                if cmd in ["/clear", "clear"]:
                    if not clear_screen():
                        console.print("[yellow]Warning: Failed to clear the screen.[/yellow]")

                    # Reset conversation context
                    thread = agent.get_new_thread()
                    message_count = 0

                    continue

                # Handle /continue command
                if cmd == "/continue":
                    sessions = persistence.list_sessions()
                    if not sessions:
                        console.print("\n[yellow]No saved sessions available[/yellow]\n")
                        continue

                    # Show session picker
                    console.print("\n[bold]Available Sessions:[/bold]")
                    for i, sess in enumerate(sessions, 1):
                        created = sess.get("created_at", "")
                        # Calculate time ago
                        try:
                            created_dt = datetime.fromisoformat(created)
                            now = datetime.now()
                            delta = now - created_dt
                            if delta.days > 0:
                                time_ago = f"{delta.days}d ago"
                            elif delta.seconds > 3600:
                                time_ago = f"{delta.seconds // 3600}h ago"
                            else:
                                time_ago = f"{delta.seconds // 60}m ago"
                        except Exception:
                            time_ago = "unknown"

                        # Get first message preview
                        first_msg = sess.get("first_message", "")
                        if len(first_msg) > 50:
                            first_msg = first_msg[:47] + "..."

                        console.print(
                            f"  {i}. [cyan]{sess['name']}[/cyan] [dim]({time_ago})[/dim] \"{first_msg}\""
                        )

                    # Get user selection
                    try:
                        choice = await session.prompt_async(
                            f"\nSelect session [1-{len(sessions)}]: "
                        )
                        choice_num = int(choice.strip())
                        if 1 <= choice_num <= len(sessions):
                            selected = sessions[choice_num - 1]
                            thread, context_summary = await persistence.load_thread(
                                agent, selected["name"]
                            )

                            # Restore context if needed
                            if context_summary:
                                with console.status(
                                    "[bold blue]Restoring context...", spinner="dots"
                                ):
                                    await agent.run(context_summary, thread=thread)
                                    message_count += 1

                            # Show single clean status with separator
                            console.print("\n[green]✓ Ready[/green]\n")
                            console.print(f"[dim]{'─' * console.width}[/dim]")
                        else:
                            console.print("[red]Invalid selection[/red]\n")
                    except (ValueError, EOFError, KeyboardInterrupt):
                        console.print("\n[yellow]Cancelled[/yellow]\n")
                    continue

                # Handle /purge command
                if cmd == "/purge":
                    sessions = persistence.list_sessions()
                    if not sessions:
                        console.print("\n[yellow]No sessions to purge[/yellow]\n")
                        continue

                    # Confirm deletion
                    console.print(
                        f"\n[yellow]⚠ This will delete ALL {len(sessions)} saved sessions.[/yellow]"
                    )
                    try:
                        confirm = await session.prompt_async("Continue? (y/n): ")
                        if confirm.strip().lower() == "y":
                            deleted = 0
                            for sess in sessions:
                                try:
                                    persistence.delete_session(sess["name"])
                                    deleted += 1
                                except Exception as e:
                                    console.print(
                                        f"[yellow]Failed to delete {sess['name']}: {e}[/yellow]"
                                    )

                            console.print(f"\n[green]✓ Deleted {deleted} sessions[/green]\n")
                        else:
                            console.print("\n[yellow]Cancelled[/yellow]\n")
                    except (EOFError, KeyboardInterrupt):
                        console.print("\n[yellow]Cancelled[/yellow]\n")
                    continue

                # Move past the old status bar with a newline
                console.print()

                # Execute agent query with visualization
                display_mode = DisplayMode.VERBOSE if verbose else DisplayMode.MINIMAL
                ctx = ExecutionContext(
                    is_interactive=True,
                    show_visualization=not quiet,
                    display_mode=display_mode,
                )
                set_execution_context(ctx)

                # Use execution tree display if visualization enabled
                if not quiet:
                    execution_display = ExecutionTreeDisplay(
                        console=console,
                        display_mode=display_mode,
                        show_completion_summary=True,  # Show completion summary in interactive mode
                    )

                    await execution_display.start()

                    try:
                        # Run agent (non-streaming for better visualization)
                        response = await agent.run(user_input, thread=thread)
                        message_count += 1

                        # Track messages for session persistence
                        conversation_messages.append({"role": "user", "content": user_input})
                        response_text = (
                            response.text if hasattr(response, "text") else str(response)
                        )
                        conversation_messages.append(
                            {"role": "assistant", "content": response_text}
                        )

                        # Stop display (shows completion summary)
                        await execution_display.stop()

                        # Print response after completion summary
                        console.print(f"{response}")

                    except KeyboardInterrupt:
                        # User pressed Ctrl+C - cancel operation
                        await execution_display.stop()
                        console.print(
                            "\n[yellow]Operation cancelled[/yellow] - Press Ctrl+C again to exit\n"
                        )
                        continue
                else:
                    # Quiet mode - no visualization
                    try:
                        response = await agent.run(user_input, thread=thread)
                        message_count += 1

                        # Track messages for session persistence
                        conversation_messages.append({"role": "user", "content": user_input})
                        response_text = (
                            response.text if hasattr(response, "text") else str(response)
                        )
                        conversation_messages.append(
                            {"role": "assistant", "content": response_text}
                        )

                        console.print(f"{response}")
                    except KeyboardInterrupt:
                        console.print("\n[yellow]Operation cancelled[/yellow]\n")
                        continue

            except KeyboardInterrupt:
                console.print("\n[yellow]Use Ctrl+D to exit or type 'exit'[/yellow]")
                continue
            except EOFError:
                # Ctrl+D - exit gracefully
                await _auto_save_session(
                    persistence, thread, message_count, quiet, conversation_messages
                )
                console.print("\n[dim]Goodbye![/dim]")
                break

    except ValueError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        console.print("[yellow]Run 'agent --check' to diagnose issues[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
