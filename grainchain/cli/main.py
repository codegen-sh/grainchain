"""Main CLI entry point for Grainchain."""

import subprocess
import sys

import click

from .exceptions import DependencyError, handle_cli_error
from .utils import (
    accent,
    check_dependency,
    error,
    handle_keyboard_interrupt,
    info,
    muted,
    progress_spinner,
    success,
    verbose_echo,
    warning,
)


@click.group()
@click.version_option()
@click.option(
    "--verbose", "-v", is_flag=True, help="Enable verbose output for debugging"
)
@click.pass_context
def main(ctx: click.Context, verbose: bool):
    """Grainchain CLI for development and testing with ruff-powered code quality."""
    # Ensure context object exists and store verbose flag
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    if verbose:
        info("Verbose mode enabled")


def get_verbose_flag(ctx: click.Context | None = None) -> bool:
    """Get the verbose flag from the context."""
    if ctx is None:
        ctx = click.get_current_context(silent=True)
    return ctx.obj.get("verbose", False) if ctx and ctx.obj else False


@main.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
@click.option("--check", help="Check status of a specific provider")
@click.option("--available-only", is_flag=True, help="Show only available providers")
def providers(verbose: bool, check: str, available_only: bool):
    """Show available sandbox providers and their configuration status."""
    try:
        from grainchain.core.providers_info import ProviderDiscovery

        discovery = ProviderDiscovery()

        if check:
            # Check specific provider
            info = discovery.get_provider_info(check)
            _display_provider_info(info, verbose=True)
            return

        # Get all providers info
        all_providers = discovery.get_all_providers_info()

        if available_only:
            providers_to_show = {k: v for k, v in all_providers.items() if v.available}
        else:
            providers_to_show = all_providers

        if not providers_to_show:
            if available_only:
                click.echo("❌ No providers are currently available.")
                click.echo("Run 'grainchain providers' to see setup instructions.")
            else:
                click.echo("❌ No providers found.")
            return

        # Display header
        click.echo("🔧 Grainchain Sandbox Providers\n")

        # Show default provider info
        default_provider = discovery.config_manager.default_provider
        default_info = all_providers.get(default_provider)
        if default_info:
            status_icon = "✅" if default_info.available else "❌"
            click.echo(f"📌 Default provider: {default_provider} {status_icon}")
            click.echo()

        # Display providers
        for _name, info in providers_to_show.items():
            _display_provider_info(info, verbose)
            click.echo()

        # Count available providers
        available_count = 0
        for info in providers.values():
            if info.available:
                available_count += 1

        click.echo(
            f"📊 Summary: {available_count}/{len(providers)} providers available"
        )

        if not available_only:
            if available_count == 0:
                click.echo("\n💡 To get started:")
                click.echo(
                    "   1. Install provider dependencies (see install commands above)"
                )
                click.echo("   2. Set required environment variables")
                click.echo(
                    "   3. Run 'grainchain providers --available-only' to verify"
                )
            elif available_count < len(providers):
                click.echo(
                    "\n💡 Run 'grainchain providers --verbose' for setup instructions"
                )

    except ImportError as e:
        click.echo(f"❌ Error importing provider discovery: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error checking providers: {e}")
        sys.exit(1)


def _display_provider_info(info, verbose=False):
    """Display information about a single provider."""
    # Import here to avoid circular imports
    from grainchain.core.providers_info import ProviderDiscovery

    # Status icon
    if info.available:
        status_icon = "✅"
    elif info.dependencies_installed and not info.configured:
        status_icon = "⚠️"
    elif not info.dependencies_installed:
        status_icon = "❌"
    else:
        status_icon = "❌"

    # Provider header
    provider_meta = ProviderDiscovery.PROVIDERS.get(info.name, {})
    description = provider_meta.get("description", "")

    click.echo(f"{status_icon} {info.name.upper()}")
    if description and verbose:
        click.echo(f"   {description}")

    if verbose or not info.available:
        # Dependencies status
        deps_icon = "✅" if info.dependencies_installed else "❌"
        click.echo(f"   Dependencies: {deps_icon}")

        if not info.dependencies_installed and info.install_command:
            click.echo(f"   Install: {info.install_command}")

        # Configuration status
        config_icon = "✅" if info.configured else "❌"
        click.echo(f"   Configuration: {config_icon}")

        if info.missing_config:
            click.echo(f"   Missing: {', '.join(info.missing_config)}")

        # Configuration instructions
        if info.config_instructions and not info.configured:
            click.echo("   Setup:")
            for instruction in info.config_instructions:
                click.echo(f"     {instruction}")

    if info.error_message:
        click.echo(f"   Error: {info.error_message}")


@main.command()
@click.option("--cov", is_flag=True, help="Run with coverage")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.argument("path", default=".", type=click.Path())
@click.pass_context
def test(ctx: click.Context, cov: bool, verbose: bool, path: str):
    """Run tests using pytest."""
    global_verbose = get_verbose_flag(ctx)
    verbose = verbose or global_verbose

    try:
        cmd = ["python", "-m", "pytest"]

        if cov:
            cmd.extend(
                ["--cov=grainchain", "--cov-report=term-missing", "--cov-report=html"]
            )
            verbose_echo("Coverage reporting enabled", verbose)

        if verbose:
            cmd.append("-v")

        cmd.append(path)

        verbose_echo(f"Running command: {' '.join(cmd)}", verbose)

        with progress_spinner("Running tests", verbose):
            result = subprocess.run(cmd, capture_output=not verbose)

        if result.returncode == 0:
            success("Tests completed successfully!")
        else:
            error("Tests failed!")
            if not verbose:
                info("💡 Run with --verbose to see detailed output")

        sys.exit(result.returncode)

    except KeyboardInterrupt:
        handle_keyboard_interrupt()
    except Exception as e:
        handle_cli_error(e, verbose)


@main.command()
@click.option("--fix", is_flag=True, help="Auto-fix issues where possible")
@click.argument("path", default=".", type=click.Path())
@click.pass_context
def lint(ctx: click.Context, fix: bool, path: str):
    """Run linting checks with ruff."""
    verbose = get_verbose_flag(ctx)

    try:
        cmd = ["python", "-m", "ruff", "check"]

        if fix:
            cmd.append("--fix")
            verbose_echo("Auto-fix mode enabled", verbose)

        cmd.append(path)

        verbose_echo(f"Running command: {' '.join(cmd)}", verbose)

        action = "Fixing and checking" if fix else "Checking"
        with progress_spinner(f"{action} code style", verbose):
            result = subprocess.run(cmd, capture_output=not verbose)

        if result.returncode == 0:
            success("Linting completed successfully!")
        else:
            error("Linting issues found!")
            if not fix:
                info("💡 Run with --fix to automatically fix issues")

        sys.exit(result.returncode)

    except KeyboardInterrupt:
        handle_keyboard_interrupt()
    except Exception as e:
        handle_cli_error(e, verbose)


@main.command()
@click.argument("path", default=".", type=click.Path())
@click.pass_context
def format(ctx: click.Context, path: str):
    """Format code using ruff."""
    verbose = get_verbose_flag(ctx)

    try:
        commands = [
            (["python", "-m", "ruff", "check", "--fix", path], "Fixing style issues"),
            (["python", "-m", "ruff", "format", path], "Formatting code"),
        ]

        for cmd, description in commands:
            verbose_echo(f"Running command: {' '.join(cmd)}", verbose)

            with progress_spinner(description, verbose):
                result = subprocess.run(cmd, capture_output=not verbose)

            if result.returncode != 0:
                error(f"Command failed: {' '.join(cmd)}")
                sys.exit(result.returncode)

        success("Code formatting complete!")

    except KeyboardInterrupt:
        handle_keyboard_interrupt()
    except Exception as e:
        handle_cli_error(e, verbose)


@main.command()
@click.option(
    "--provider",
    default="local",
    help="Provider to benchmark (local, e2b, daytona, morph)",
)
@click.option("--config", help="Path to benchmark config file")
@click.option("--output", help="Output directory for results")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def benchmark(
    ctx: click.Context, provider: str, config: str, output: str, verbose: bool
):
    """Run performance benchmarks."""
    global_verbose = get_verbose_flag(ctx)
    verbose = verbose or global_verbose

    try:
        from grainchain.cli.benchmark import run_benchmark

        accent(f"🚀 Running benchmarks with {provider} provider...")
        verbose_echo(f"Config: {config or 'default'}", verbose)
        verbose_echo(f"Output: {output or 'console only'}", verbose)

        result = run_benchmark(
            provider=provider, config_path=config, output_dir=output, verbose=verbose
        )

        if result:
            success("Benchmarks completed successfully!")
        else:
            error("Benchmarks failed!")
            sys.exit(1)

    except ImportError as e:
        raise DependencyError(
            "Benchmark dependencies",
            install_command="uv sync --extra benchmark",
            docs_url="https://github.com/codegen-sh/grainchain#benchmark-setup",
        ) from e
    except KeyboardInterrupt:
        handle_keyboard_interrupt()
    except Exception as e:
        handle_cli_error(e, verbose)


@main.command()
@click.pass_context
def install_hooks(ctx: click.Context):
    """Install pre-commit hooks."""
    verbose = get_verbose_flag(ctx)

    try:
        if not check_dependency("pre-commit", "pre-commit", "pip install pre-commit"):
            raise DependencyError(
                "pre-commit", install_command="pip install pre-commit"
            )

        cmd = ["pre-commit", "install"]
        verbose_echo(f"Running command: {' '.join(cmd)}", verbose)

        with progress_spinner("Installing pre-commit hooks", verbose):
            result = subprocess.run(cmd, capture_output=not verbose)

        if result.returncode == 0:
            success("Pre-commit hooks installed!")
        else:
            error("Failed to install pre-commit hooks")
            sys.exit(result.returncode)

    except KeyboardInterrupt:
        handle_keyboard_interrupt()
    except Exception as e:
        handle_cli_error(e, verbose)


@main.command()
@click.option("--fix", is_flag=True, help="Automatically fix issues where possible")
@click.pass_context
def check(ctx: click.Context, fix: bool):
    """Run all quality checks (lint, format, test)."""
    verbose = get_verbose_flag(ctx)

    try:
        commands = [
            (
                ["python", "-m", "ruff", "check"] + (["--fix"] if fix else []) + ["."],
                "Linting",
            ),
            (
                ["python", "-m", "ruff", "format"]
                + ([] if fix else ["--check"])
                + ["."],
                "Code formatting",
            ),
            (["python", "-m", "pytest"], "Tests"),
        ]

        failed = []

        accent("🔍 Running quality checks...")

        for cmd, name in commands:
            verbose_echo(f"Running {name.lower()}: {' '.join(cmd)}", verbose)

            with progress_spinner(f"Running {name.lower()}", verbose):
                result = subprocess.run(cmd, capture_output=True)

            if result.returncode == 0:
                success(f"{name} passed")
            else:
                error(f"{name} failed")
                failed.append(name)

                if verbose and result.stderr:
                    verbose_echo(f"{name} stderr: {result.stderr.decode()}")

        # Note about skipped type checking
        warning("Type checking temporarily disabled")

        if failed:
            error(f"Failed checks: {', '.join(failed)}")
            if not fix and any(
                "format" in f.lower() or "lint" in f.lower() for f in failed
            ):
                info("💡 Run with --fix to automatically fix style issues")
            sys.exit(1)
        else:
            success("🎉 All checks passed!")

    except KeyboardInterrupt:
        handle_keyboard_interrupt()
    except Exception as e:
        handle_cli_error(e, verbose)


@main.command()
@click.argument("path", default=".", type=click.Path())
@click.pass_context
def typecheck(ctx: click.Context, path: str):
    """Run type checking with mypy."""
    verbose = get_verbose_flag(ctx)

    warning("Type checking temporarily disabled")
    muted("   Run 'mypy grainchain/' manually if needed")
    success("Skipped type checking")

    verbose_echo("Type checking is disabled due to unresolved typing issues", verbose)


if __name__ == "__main__":
    main()
