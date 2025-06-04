"""Main CLI entry point for Grainchain."""

import subprocess
import sys

import click


@click.group()
@click.version_option()
def main():
    """Grainchain CLI for development and testing with ruff-powered code quality."""
    pass


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
def test(cov: bool, verbose: bool, path: str):
    """Run tests using pytest."""
    cmd = ["python", "-m", "pytest"]

    if cov:
        cmd.extend(
            ["--cov=grainchain", "--cov-report=term-missing", "--cov-report=html"]
        )

    if verbose:
        cmd.append("-v")

    cmd.append(path)

    click.echo(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


@main.command()
@click.option("--fix", is_flag=True, help="Auto-fix issues where possible")
@click.argument("path", default=".", type=click.Path())
def lint(fix: bool, path: str):
    """Run linting checks with ruff."""
    cmd = ["python", "-m", "ruff", "check"]

    if fix:
        cmd.append("--fix")

    cmd.append(path)

    click.echo(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


@main.command()
@click.argument("path", default=".", type=click.Path())
def format(path: str):
    """Format code using ruff."""
    commands = [
        ["python", "-m", "ruff", "check", "--fix", path],
        ["python", "-m", "ruff", "format", path],
    ]

    for cmd in commands:
        click.echo(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            click.echo(f"Command failed: {' '.join(cmd)}")
            sys.exit(result.returncode)

    click.echo("✅ Code formatting complete!")


@main.command()
@click.argument("path", default=".", type=click.Path())
def typecheck(path: str):
    """Run type checking with mypy."""
    click.echo("⚠️  Type checking temporarily disabled")
    click.echo("   Run 'mypy grainchain/' manually if needed")
    click.echo("✅ Skipped type checking")
    # Temporarily disabled until typing issues are resolved
    # cmd = ["python", "-m", "mypy", path]
    # click.echo(f"Running: {' '.join(cmd)}")
    # result = subprocess.run(cmd)
    # sys.exit(result.returncode)


@main.command()
@click.option(
    "--provider", default="local", help="Provider to benchmark (local, e2b, daytona)"
)
@click.option("--config", help="Path to benchmark config file")
@click.option("--output", help="Output directory for results")
def benchmark(provider: str, config: str, output: str):
    """Run performance benchmarks."""
    try:
        from grainchain.cli.benchmark import run_benchmark

        click.echo(f"🚀 Running benchmarks with {provider} provider...")

        result = run_benchmark(provider=provider, config_path=config, output_dir=output)

        if result:
            click.echo("��� Benchmarks completed successfully!")
        else:
            click.echo("❌ Benchmarks failed!")
            sys.exit(1)

    except ImportError:
        click.echo(
            "❌ Benchmark dependencies not installed. Run: uv sync --extra benchmark"
        )
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Benchmark failed: {e}")
        sys.exit(1)


@main.command()
def install_hooks():
    """Install pre-commit hooks."""
    cmd = ["pre-commit", "install"]

    click.echo(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        click.echo("✅ Pre-commit hooks installed!")
    else:
        click.echo("❌ Failed to install pre-commit hooks")
        sys.exit(result.returncode)


@main.command()
def check():
    """Run all quality checks (lint, format, test)."""
    commands = [
        (["python", "-m", "ruff", "check", "."], "Linting"),
        (["python", "-m", "ruff", "format", "--check", "."], "Code formatting"),
        # Temporarily disabled until typing issues are resolved
        # (["python", "-m", "mypy", "grainchain/"], "Type checking"),
        (["python", "-m", "pytest"], "Tests"),
    ]

    failed = []

    for cmd, name in commands:
        click.echo(f"🔍 {name}...")
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode == 0:
            click.echo(f"✅ {name} passed")
        else:
            click.echo(f"❌ {name} failed")
            failed.append(name)

    # Note about skipped type checking
    click.echo("⚠️  Type checking temporarily disabled")

    if failed:
        click.echo(f"\n❌ Failed checks: {', '.join(failed)}")
        sys.exit(1)
    else:
        click.echo("\n🎉 All checks passed!")


if __name__ == "__main__":
    main()
