"""Benchmark CLI module for Grainchain."""

import asyncio
import json
import time
from pathlib import Path
from typing import Optional

import click


def run_benchmark(
    provider: str = "local",
    config_path: Optional[str] = None,
    output_dir: Optional[str] = None,
    codegen_benchmark: Optional[str] = None,
) -> bool:
    """
    Run a simple benchmark against the specified provider.

    Args:
        provider: Provider to benchmark (local, e2b, daytona)
        config_path: Path to config file (optional)
        output_dir: Output directory for results (optional)
        codegen_benchmark: Special codegen benchmark type (e.g., 'outline')

    Returns:
        True if benchmark succeeded, False otherwise
    """
    try:
        if codegen_benchmark:
            return asyncio.run(
                _run_codegen_benchmark_async(
                    codegen_benchmark, provider, config_path, output_dir
                )
            )
        else:
            return asyncio.run(_run_benchmark_async(provider, config_path, output_dir))
    except Exception as e:
        click.echo(f"Benchmark failed: {e}")
        return False


async def _run_benchmark_async(
    provider: str, config_path: Optional[str], output_dir: Optional[str]
) -> bool:
    """Async benchmark runner."""
    from grainchain import Sandbox
    from grainchain.core.interfaces import SandboxConfig

    # Create benchmark config
    config = SandboxConfig(timeout=60, working_directory="~", auto_cleanup=True)

    results = {"provider": provider, "timestamp": time.time(), "tests": []}

    click.echo(f"🏃 Starting benchmark with {provider} provider...")

    try:
        async with Sandbox(provider=provider, config=config) as sandbox:
            # Test 1: Basic command execution
            start_time = time.time()
            result = await sandbox.execute("echo 'Hello, Grainchain!'")
            exec_time = time.time() - start_time

            test_result = {
                "name": "basic_echo",
                "duration": exec_time,
                "success": result.success,
                "stdout": result.stdout.strip(),
            }
            results["tests"].append(test_result)

            if result.success:
                click.echo(f"✅ Basic echo test: {exec_time:.3f}s")
            else:
                click.echo(f"❌ Basic echo test failed: {result.stderr}")
                return False

            # Test 2: Python execution
            start_time = time.time()
            result = await sandbox.execute("python3 -c \"print('Python works!')\"")
            exec_time = time.time() - start_time

            test_result = {
                "name": "python_execution",
                "duration": exec_time,
                "success": result.success,
                "stdout": result.stdout.strip(),
            }
            results["tests"].append(test_result)

            if result.success:
                click.echo(f"✅ Python test: {exec_time:.3f}s")
            else:
                click.echo(f"❌ Python test failed: {result.stderr}")
                return False

            # Test 3: File operations
            start_time = time.time()
            await sandbox.upload_file("test.txt", "Hello from file!")
            result = await sandbox.execute("cat test.txt")
            exec_time = time.time() - start_time

            test_result = {
                "name": "file_operations",
                "duration": exec_time,
                "success": result.success and "Hello from file!" in result.stdout,
                "stdout": result.stdout.strip(),
            }
            results["tests"].append(test_result)

            if test_result["success"]:
                click.echo(f"✅ File operations test: {exec_time:.3f}s")
            else:
                click.echo("❌ File operations test failed")
                return False

    except Exception as e:
        click.echo(f"❌ Benchmark failed during execution: {e}")
        return False

    # Save results if output directory specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        results_file = output_path / f"benchmark_{provider}_{int(time.time())}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        click.echo(f"📊 Results saved to {results_file}")

    # Print summary
    total_duration = sum(test["duration"] for test in results["tests"])
    click.echo("\n📈 Benchmark Summary:")
    click.echo(f"   Provider: {provider}")
    click.echo(f"   Total time: {total_duration:.3f}s")
    click.echo(f"   Tests passed: {len(results['tests'])}")

    return True


async def _run_codegen_benchmark_async(
    codegen_benchmark: str,
    provider: str,
    config_path: Optional[str],
    output_dir: Optional[str],
) -> bool:
    """Async benchmark runner for codegen benchmarks."""
    from grainchain.cli.codegen_benchmark import run_codegen_outline_benchmark

    if codegen_benchmark.lower() == "outline":
        # For codegen outline benchmark, we test both E2B and Daytona by default
        # unless a specific provider is requested
        if provider == "local":
            click.echo(
                "⚠️  Codegen outline benchmark is designed for E2B and Daytona providers"
            )
            click.echo("   Switching to E2B and Daytona for comparison...")
            providers = ["e2b", "daytona"]
        else:
            providers = [provider]

        return await run_codegen_outline_benchmark(
            providers=providers, config_path=config_path, output_dir=output_dir
        )
    else:
        click.echo(f"❌ Unknown codegen benchmark type: {codegen_benchmark}")
        click.echo("   Available types: outline")
        return False
