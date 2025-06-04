"""CLI utilities for enhanced user experience."""

import sys
import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import click


class CliColors:
    """Color constants for consistent CLI styling."""

    SUCCESS = "green"
    ERROR = "red"
    WARNING = "yellow"
    INFO = "blue"
    MUTED = "bright_black"
    ACCENT = "cyan"


def success(message: str, **kwargs) -> None:
    """Print a success message with green styling."""
    click.echo(click.style(f"✅ {message}", fg=CliColors.SUCCESS), **kwargs)


def error(message: str, **kwargs) -> None:
    """Print an error message with red styling."""
    click.echo(click.style(f"❌ {message}", fg=CliColors.ERROR), **kwargs)


def warning(message: str, **kwargs) -> None:
    """Print a warning message with yellow styling."""
    click.echo(click.style(f"⚠️  {message}", fg=CliColors.WARNING), **kwargs)


def info(message: str, **kwargs) -> None:
    """Print an info message with blue styling."""
    click.echo(click.style(f"ℹ️  {message}", fg=CliColors.INFO), **kwargs)


def muted(message: str, **kwargs) -> None:
    """Print a muted message with gray styling."""
    click.echo(click.style(message, fg=CliColors.MUTED), **kwargs)


def accent(message: str, **kwargs) -> None:
    """Print an accented message with cyan styling."""
    click.echo(click.style(message, fg=CliColors.ACCENT), **kwargs)


def verbose_echo(message: str, verbose: bool = False, **kwargs) -> None:
    """Print a message only if verbose mode is enabled."""
    if verbose:
        muted(f"[VERBOSE] {message}", **kwargs)


def format_duration(seconds: float) -> str:
    """Format duration in a human-readable way."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"


def confirm_action(message: str, default: bool = False, force: bool = False) -> bool:
    """
    Ask for user confirmation before proceeding with an action.

    Args:
        message: The confirmation message to display
        default: Default value if user just presses Enter
        force: If True, skip confirmation and return True

    Returns:
        True if user confirms, False otherwise
    """
    if force:
        return True

    return click.confirm(
        click.style(f"⚠️  {message}", fg=CliColors.WARNING), default=default
    )


@contextmanager
def progress_spinner(
    message: str, verbose: bool = False
) -> Generator[None, None, None]:
    """
    Context manager that shows a spinner for quick operations.

    Args:
        message: Message to display with the spinner
        verbose: Whether to show verbose output
    """
    if verbose:
        verbose_echo(f"Starting: {message}")
        start_time = time.time()

    with click.progressbar(
        length=1,
        label=message,
        show_eta=False,
        show_percent=False,
        item_show_func=lambda x: "",
    ) as bar:
        try:
            yield
            bar.update(1)
        finally:
            if verbose:
                duration = time.time() - start_time
                verbose_echo(f"Completed: {message} ({format_duration(duration)})")


@contextmanager
def progress_bar(
    items: list[Any], label: str = "Processing", verbose: bool = False
) -> Generator[click.progressbar, None, None]:
    """
    Context manager that provides a progress bar for iterating over items.

    Args:
        items: List of items to iterate over
        label: Label for the progress bar
        verbose: Whether to show verbose output

    Yields:
        Click progress bar object
    """
    if verbose:
        verbose_echo(f"Starting: {label} ({len(items)} items)")
        start_time = time.time()

    with click.progressbar(items, label=label, show_eta=True, show_percent=True) as bar:
        try:
            yield bar
        finally:
            if verbose:
                duration = time.time() - start_time
                verbose_echo(f"Completed: {label} ({format_duration(duration)})")


def format_table(
    headers: list[str], rows: list[list[str]], title: str | None = None
) -> str:
    """
    Format data as a simple ASCII table.

    Args:
        headers: Column headers
        rows: Data rows
        title: Optional table title

    Returns:
        Formatted table string
    """
    if not rows:
        return "No data to display"

    # Calculate column widths
    col_widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # Create format string
    row_format = " | ".join(f"{{:<{width}}}" for width in col_widths)
    separator = "-+-".join("-" * width for width in col_widths)

    # Build table
    lines = []

    if title:
        lines.append(click.style(title, fg=CliColors.ACCENT, bold=True))
        lines.append("")

    # Headers
    lines.append(row_format.format(*headers))
    lines.append(separator)

    # Data rows
    for row in rows:
        formatted_row = [str(cell) for cell in row]
        lines.append(row_format.format(*formatted_row))

    return "\n".join(lines)


def print_section(title: str, content: str = "", **kwargs) -> None:
    """Print a section with a styled title."""
    click.echo()
    click.echo(click.style(f"📋 {title}", fg=CliColors.ACCENT, bold=True), **kwargs)
    if content:
        click.echo(content, **kwargs)


def handle_keyboard_interrupt() -> None:
    """Handle Ctrl+C gracefully."""
    error("Operation cancelled by user")
    sys.exit(130)  # Standard exit code for SIGINT


def check_dependency(command: str, name: str, install_hint: str = "") -> bool:
    """
    Check if a command-line dependency is available.

    Args:
        command: Command to check (e.g., 'docker')
        name: Human-readable name of the dependency
        install_hint: Optional installation instructions

    Returns:
        True if dependency is available, False otherwise
    """
    import subprocess

    try:
        subprocess.run(
            [command, "--version"], capture_output=True, check=True, timeout=5
        )
        return True
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        error(f"{name} is not available or not working properly")
        if install_hint:
            info(f"💡 Try: {install_hint}")
        return False


def get_terminal_width() -> int:
    """Get the current terminal width, with a sensible default."""
    try:
        return click.get_terminal_size()[0]
    except OSError:
        return 80  # Default width if terminal size can't be determined
