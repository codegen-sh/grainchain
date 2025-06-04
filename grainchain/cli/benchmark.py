"""Benchmark CLI module for Grainchain."""

import asyncio
import json
import time
from pathlib import Path

import click

from .exceptions import BenchmarkError, ProviderError, handle_cli_error
from .utils import (
    accent,
    error,
    format_duration,
    format_table,
    info,
    muted,
    print_section,
    success,
    verbose_echo,
)


def run_benchmark(
    provider: str = "local",
    config_path: str | None = None,
    output_dir: str | None = None,
    verbose: bool = False,
) -> bool:
    """
    Run a simple benchmark against the specified provider.

    Args:
        provider: Provider to benchmark (local, e2b, daytona, morph)
        config_path: Path to config file (optional)
        output_dir: Output directory for results (optional)
        verbose: Enable verbose output

    Returns:
        True if benchmark succeeded, False otherwise
    """
    try:
        return asyncio.run(
            _run_benchmark_async(provider, config_path, output_dir, verbose)
        )
    except KeyboardInterrupt:
        error("Benchmark cancelled by user")
        return False
    except Exception as e:
        handle_cli_error(e, verbose)
        return False


async def _run_benchmark_async(
    provider: str, config_path: str | None, output_dir: str | None, verbose: bool
) -> bool:
    """Async benchmark runner."""
    from grainchain import Sandbox
    from grainchain.core.interfaces import SandboxConfig

    # Create benchmark config
    config = SandboxConfig(timeout=60, working_directory="~", auto_cleanup=True)
    verbose_echo(
        f"Using config: timeout={config.timeout}s, working_dir={config.working_directory}",
        verbose,
    )

    results = {
        "provider": provider,
        "timestamp": time.time(),
        "tests": [],
        "summary": {},
    }

    # Define test cases
    test_cases = [
        ("basic_echo", "echo 'Hello, Grainchain!'", "Basic command execution"),
        (
            "python_execution",
            "python3 -c \"print('Python works!')\"",
            "Python interpreter test",
        ),
        ("file_operations", None, "File upload and read test"),  # Special case
    ]

    print_section(
        f"🚀 Benchmark: {provider} provider", f"Running {len(test_cases)} tests..."
    )

    start_time = time.time()

    try:
        async with Sandbox(provider=provider, config=config) as sandbox:
            verbose_echo(f"Successfully connected to {provider} sandbox", verbose)

            # Run tests with progress tracking
            for i, (test_name, command, description) in enumerate(test_cases, 1):
                info(f"[{i}/{len(test_cases)}] {description}")

                test_start = time.time()

                try:
                    if test_name == "file_operations":
                        # Special handling for file operations test
                        verbose_echo("Uploading test file...", verbose)
                        await sandbox.upload_file("test.txt", "Hello from file!")

                        verbose_echo("Reading uploaded file...", verbose)
                        result = await sandbox.execute("cat test.txt")

                        test_success = (
                            result.success and "Hello from file!" in result.stdout
                        )
                        stdout = result.stdout.strip()
                    else:
                        verbose_echo(f"Executing: {command}", verbose)
                        result = await sandbox.execute(command)
                        test_success = result.success
                        stdout = result.stdout.strip()

                    exec_time = time.time() - test_start

                    test_result = {
                        "name": test_name,
                        "description": description,
                        "duration": exec_time,
                        "success": test_success,
                        "stdout": stdout,
                        "stderr": result.stderr.strip()
                        if hasattr(result, "stderr")
                        else "",
                    }
                    results["tests"].append(test_result)

                    if test_success:
                        success(f"✓ {description} ({format_duration(exec_time)})")
                        verbose_echo(f"Output: {stdout}", verbose)
                    else:
                        error(f"✗ {description} failed")
                        if hasattr(result, "stderr") and result.stderr:
                            verbose_echo(f"Error: {result.stderr}", verbose)

                        raise BenchmarkError(
                            test_name,
                            provider,
                            result.stderr
                            if hasattr(result, "stderr")
                            else "Unknown error",
                        )

                except Exception as e:
                    exec_time = time.time() - test_start
                    error(f"✗ {description} failed ({format_duration(exec_time)})")

                    if isinstance(e, BenchmarkError):
                        raise
                    else:
                        raise BenchmarkError(test_name, provider, str(e)) from e

    except Exception as e:
        if isinstance(e, BenchmarkError):
            raise
        else:
            raise ProviderError(provider, "benchmark execution", str(e)) from e

    # Calculate summary statistics
    total_duration = time.time() - start_time
    successful_tests = sum(1 for test in results["tests"] if test["success"])
    avg_duration = sum(test["duration"] for test in results["tests"]) / len(
        results["tests"]
    )

    results["summary"] = {
        "total_duration": total_duration,
        "successful_tests": successful_tests,
        "total_tests": len(results["tests"]),
        "success_rate": (successful_tests / len(results["tests"])) * 100,
        "avg_test_duration": avg_duration,
    }

    # Display results
    _display_benchmark_results(results, verbose)

    # Save results if output directory specified
    if output_dir:
        _save_benchmark_results(results, output_dir, provider)

    return successful_tests == len(results["tests"])


def _display_benchmark_results(results: dict, verbose: bool) -> None:
    """Display benchmark results in a formatted table."""
    print_section("📊 Benchmark Results")

    # Test results table
    headers = ["Test", "Status", "Duration", "Description"]
    rows = []

    for test in results["tests"]:
        status = "✅ PASS" if test["success"] else "❌ FAIL"
        duration = format_duration(test["duration"])
        rows.append([test["name"], status, duration, test["description"]])

    table = format_table(headers, rows)
    click.echo(table)

    # Summary statistics
    summary = results["summary"]
    click.echo()
    accent("📈 Summary Statistics:")
    click.echo(f"  Provider: {results['provider']}")
    click.echo(f"  Total Duration: {format_duration(summary['total_duration'])}")
    click.echo(
        f"  Success Rate: {summary['success_rate']:.1f}% ({summary['successful_tests']}/{summary['total_tests']})"
    )
    click.echo(
        f"  Average Test Duration: {format_duration(summary['avg_test_duration'])}"
    )

    if verbose:
        click.echo()
        muted("Detailed test output:")
        for test in results["tests"]:
            if test["stdout"]:
                muted(f"  {test['name']}: {test['stdout']}")


def _save_benchmark_results(results: dict, output_dir: str, provider: str) -> None:
    """Save benchmark results to a JSON file."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    timestamp = int(results["timestamp"])
    results_file = output_path / f"benchmark_{provider}_{timestamp}.json"

    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    info(f"📄 Results saved to {results_file}")
