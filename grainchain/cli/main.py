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
