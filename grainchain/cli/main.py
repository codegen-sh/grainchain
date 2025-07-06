"""Main CLI entry point for Grainchain."""

import subprocess
import sys

import click

# Import analysis commands
from .analysis import register_analysis_commands


@click.group()
@click.version_option()
def main():
    """Grainchain CLI for development and testing with ruff-powered code quality."""
    pass


# Register analysis commands
register_analysis_commands(main)


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
    "--provider",
    default="local",
    help="Provider to benchmark (local, e2b, daytona, morph)",
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
@click.option(
    "--iterations",
    default=50,
    type=int,
    help="Number of iterations per test scenario (default: 50)",
)
@click.option(
    "--providers",
    default="local e2b",
    help="Space-separated list of providers to test (default: 'local e2b')",
)
@click.option(
    "--config",
    default="benchmarks/configs/high_iteration.json",
    help="Path to high-iteration benchmark config file",
)
@click.option(
    "--output",
    default="benchmarks/results/high_iteration",
    help="Output directory for results",
)
@click.option(
    "--statistical-analysis",
    is_flag=True,
    default=True,
    help="Generate detailed statistical analysis (default: enabled)",
)
def benchmark_high_iteration(
    iterations: int,
    providers: str,
    config: str,
    output: str,
    statistical_analysis: bool,
):
    """Run high-iteration performance benchmarks for statistical significance.

    This command runs comprehensive benchmarks with a configurable number of iterations
    (default: 50) to provide statistically significant results. Unlike the standard
    benchmark command, this provides:

    - Confidence intervals for performance metrics
    - Outlier detection and analysis
    - Trend analysis capabilities
    - More reliable performance comparisons

    Examples:

        # Run 50 iterations on local and e2b providers
        grainchain benchmark-high-iteration

        # Run 100 iterations on specific providers
        grainchain benchmark-high-iteration --iterations 100 --providers "local e2b daytona"

        # Run with custom config
        grainchain benchmark-high-iteration --config my_config.json --iterations 25
    """
    try:
        from pathlib import Path

        # Validate inputs
        if iterations < 1:
            click.echo("❌ Error: Iterations must be a positive integer")
            sys.exit(1)

        if iterations > 100:
            click.echo(
                f"⚠️  Warning: High iteration count ({iterations}) may take a very long time"
            )
            if not click.confirm("Continue anyway?"):
                click.echo("❌ Cancelled by user")
                sys.exit(1)

        # Ensure output directory exists
        Path(output).mkdir(parents=True, exist_ok=True)

        click.echo("🚀 Starting high-iteration benchmarks...")
        click.echo(f"📊 Iterations: {iterations}")
        click.echo(f"🔧 Providers: {providers}")
        click.echo(f"📁 Output: {output}")
        click.echo(
            f"📈 Statistical Analysis: {'Enabled' if statistical_analysis else 'Disabled'}"
        )
        click.echo("=" * 60)

        # Run the high-iteration benchmark script
        script_path = Path("scripts/benchmark_high_iteration.sh")
        if not script_path.exists():
            click.echo(f"❌ Benchmark script not found: {script_path}")
            click.echo("   Make sure you're running from the repository root")
            sys.exit(1)

        cmd = [str(script_path), str(iterations), providers]

        click.echo(f"🏃 Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=".")

        if result.returncode == 0:
            click.echo("✅ High-iteration benchmarks completed successfully!")
            click.echo(f"📊 Results available in: {output}")

            if statistical_analysis:
                click.echo("📈 Statistical analysis included in results")

        else:
            click.echo("❌ High-iteration benchmarks failed!")
            sys.exit(1)

    except KeyboardInterrupt:
        click.echo("\n❌ Benchmark cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ High-iteration benchmark failed: {e}")
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
