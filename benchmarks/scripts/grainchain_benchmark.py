#!/usr/bin/env python3
"""
Grainchain Sandbox Provider Benchmarking

This script benchmarks different sandbox providers (Local, E2B, Modal, Daytona) to measure:
1. Sandbox creation time
2. Command execution performance
3. File operation speed
4. Memory usage and resource consumption
5. Error rates and reliability
"""

import argparse
import asyncio
import json
import logging
import os
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add the parent directory to Python path to import grainchain
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from grainchain import Sandbox  # noqa: E402


class GrainchainBenchmark:
    """Benchmarking suite for Grainchain sandbox providers"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.results_dir = Path("benchmarks/results")
        self.results_dir.mkdir(exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.results_dir / "grainchain_benchmark.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

        # Test scenarios
        self.test_scenarios = [
            {
                "name": "basic_commands",
                "description": "Basic shell commands",
                "commands": ["echo 'Hello, World!'", "pwd", "ls -la", "whoami", "date"],
            },
            {
                "name": "python_execution",
                "description": "Python script execution",
                "commands": [
                    "python3 --version",
                    "python3 -c 'print(\"Hello from Python\")'",
                    "python3 -c 'import sys; print(sys.version)'",
                    "python3 -c 'import json; print(json.dumps({\"test\": True}))'",
                ],
            },
            {
                "name": "file_operations",
                "description": "File upload/download operations",
                "files": [
                    {
                        "name": "test.txt",
                        "content": "Hello, Grainchain!",
                        "size": "small",
                    },
                    {
                        "name": "data.json",
                        "content": '{"benchmark": true, "timestamp": "'
                        + datetime.now().isoformat()
                        + '"}',
                        "size": "small",
                    },
                    {
                        "name": "large_file.txt",
                        "content": "x" * 10000,
                        "size": "medium",
                    },
                ],
            },
            {
                "name": "computational_tasks",
                "description": "CPU-intensive tasks",
                "commands": [
                    "python3 -c 'sum(range(100000))'",
                    "python3 -c 'import math; [math.factorial(i) for i in range(100)]'",
                    "python3 -c 'import hashlib; hashlib.sha256(b\"test\" * 1000).hexdigest()'",
                ],
            },
            {
                "name": "snapshot_lifecycle",
                "description": "Git clone, file creation, snapshot, kill, and restore operations",
                "type": "snapshot_lifecycle",
                "commands": [
                    "git clone https://github.com/codegen-sh/outline.git /tmp/outline",
                    "ls -la /tmp/outline",
                ],
                "files": [
                    {
                        "name": "codegen-test.md",
                        "content": "# Codegen Test File\n\nThis is a minimal test file created during benchmarking.\n\nTimestamp: "
                        + datetime.now().isoformat(),
                        "size": "small",
                    }
                ],
            },
        ]

    def _load_config(self, config_path: str) -> dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "providers": [
                "local",
                "e2b",
                "modal",
                "daytona",
            ],  # Add "modal" when available
            "iterations": 3,
            "timeout": 30,
            "parallel_tests": False,
            "detailed_metrics": True,
            "export_formats": ["json", "markdown", "html"],
        }

        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    async def run_full_benchmark(self) -> dict[str, Any]:
        """Run complete benchmark suite across all providers"""
        self.logger.info("🚀 Starting Grainchain Provider Benchmark Suite")

        start_time = time.time()
        results = {
            "benchmark_info": {
                "start_time": datetime.now().isoformat(),
                "config": self.config,
                "test_scenarios": len(self.test_scenarios),
                "providers": self.config["providers"],
            },
            "provider_results": {},
            "summary": {},
            "status": "running",
        }

        # Test each provider
        for provider in self.config["providers"]:
            self.logger.info(f"📊 Benchmarking provider: {provider}")
            try:
                provider_results = await self._benchmark_provider(provider)
                results["provider_results"][provider] = provider_results
                self.logger.info(f"✅ Completed benchmarking {provider}")
            except Exception as e:
                self.logger.error(f"❌ Failed to benchmark {provider}: {e}")
                results["provider_results"][provider] = {
                    "status": "failed",
                    "error": str(e),
                    "scenarios": {},
                }

        # Generate summary
        results["summary"] = self._generate_summary(results["provider_results"])
        results["benchmark_info"]["end_time"] = datetime.now().isoformat()
        results["benchmark_info"]["duration_seconds"] = time.time() - start_time
        results["status"] = "completed"

        self.logger.info(
            f"🎉 Benchmark completed in {results['benchmark_info']['duration_seconds']:.2f} seconds"
        )
        return results

    async def _benchmark_provider(self, provider: str) -> dict[str, Any]:
        """Benchmark a specific provider"""
        provider_results = {
            "provider": provider,
            "status": "running",
            "scenarios": {},
            "overall_metrics": {},
        }

        # Test provider availability
        try:
            async with Sandbox(provider=provider):
                self.logger.info(f"✅ {provider} provider is available")
        except Exception as e:
            self.logger.error(f"❌ {provider} provider unavailable: {e}")
            provider_results["status"] = "unavailable"
            provider_results["error"] = str(e)
            return provider_results

        # Run each test scenario
        for scenario in self.test_scenarios:
            scenario_name = scenario["name"]
            self.logger.info(f"  🧪 Running scenario: {scenario_name}")

            scenario_results = []
            for iteration in range(self.config["iterations"]):
                try:
                    result = await self._run_scenario(provider, scenario, iteration)
                    scenario_results.append(result)
                except Exception as e:
                    self.logger.warning(f"    ⚠️  Iteration {iteration + 1} failed: {e}")
                    scenario_results.append(
                        {"iteration": iteration, "status": "failed", "error": str(e)}
                    )

            # Aggregate scenario results
            provider_results["scenarios"][scenario_name] = {
                "description": scenario["description"],
                "iterations": scenario_results,
                "aggregated": self._aggregate_scenario_results(scenario_results),
            }

        # Calculate overall metrics
        provider_results["overall_metrics"] = self._calculate_overall_metrics(
            provider_results["scenarios"]
        )
        provider_results["status"] = "completed"

        return provider_results

    async def _run_scenario(
        self, provider: str, scenario: dict[str, Any], iteration: int
    ) -> dict[str, Any]:
        """Run a single test scenario"""
        # Check if this is a special snapshot lifecycle scenario
        if scenario.get("type") == "snapshot_lifecycle":
            return await self._run_snapshot_lifecycle_scenario(
                provider, scenario, iteration
            )

        start_time = time.time()
        result = {
            "iteration": iteration,
            "scenario": scenario["name"],
            "provider": provider,
            "status": "running",
            "metrics": {
                "sandbox_creation_time": 0,
                "command_execution_times": [],
                "file_operation_times": [],
                "total_time": 0,
                "memory_usage": [],
                "success_rate": 0,
            },
        }

        try:
            # Measure sandbox creation time
            creation_start = time.time()
            async with Sandbox(provider=provider) as sandbox:
                result["metrics"]["sandbox_creation_time"] = (
                    time.time() - creation_start
                )

                # Run commands if present
                if "commands" in scenario:
                    for cmd in scenario["commands"]:
                        cmd_start = time.time()
                        try:
                            exec_result = await sandbox.execute(
                                cmd, timeout=self.config["timeout"]
                            )
                            cmd_time = time.time() - cmd_start
                            result["metrics"]["command_execution_times"].append(
                                {
                                    "command": cmd,
                                    "time": cmd_time,
                                    "success": exec_result.success,
                                    "return_code": exec_result.return_code,
                                }
                            )
                        except Exception as e:
                            result["metrics"]["command_execution_times"].append(
                                {
                                    "command": cmd,
                                    "time": time.time() - cmd_start,
                                    "success": False,
                                    "error": str(e),
                                }
                            )

                # Run file operations if present
                if "files" in scenario:
                    for file_info in scenario["files"]:
                        # Upload file
                        upload_start = time.time()
                        try:
                            await sandbox.upload_file(
                                file_info["name"], file_info["content"]
                            )
                            upload_time = time.time() - upload_start

                            # Download file
                            download_start = time.time()
                            downloaded_content = await sandbox.download_file(
                                file_info["name"]
                            )
                            download_time = time.time() - download_start

                            # Verify content
                            content_match = (
                                downloaded_content.strip()
                                == file_info["content"].strip()
                            )

                            result["metrics"]["file_operation_times"].append(
                                {
                                    "file": file_info["name"],
                                    "size": file_info["size"],
                                    "upload_time": upload_time,
                                    "download_time": download_time,
                                    "total_time": upload_time + download_time,
                                    "content_verified": content_match,
                                }
                            )
                        except Exception as e:
                            result["metrics"]["file_operation_times"].append(
                                {
                                    "file": file_info["name"],
                                    "size": file_info["size"],
                                    "upload_time": time.time() - upload_start,
                                    "download_time": 0,
                                    "total_time": time.time() - upload_start,
                                    "error": str(e),
                                    "content_verified": False,
                                }
                            )

                # Calculate success rate
                total_operations = len(
                    result["metrics"]["command_execution_times"]
                ) + len(result["metrics"]["file_operation_times"])
                successful_operations = sum(
                    1
                    for cmd in result["metrics"]["command_execution_times"]
                    if cmd.get("success", False)
                ) + sum(
                    1
                    for file_op in result["metrics"]["file_operation_times"]
                    if file_op.get("content_verified", False)
                )
                result["metrics"]["success_rate"] = (
                    successful_operations / total_operations
                    if total_operations > 0
                    else 1.0
                )

            result["metrics"]["total_time"] = time.time() - start_time
            result["status"] = "completed"

        except Exception as e:
            result["metrics"]["total_time"] = time.time() - start_time
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    async def _run_snapshot_lifecycle_scenario(
        self, provider: str, scenario: dict[str, Any], iteration: int
    ) -> dict[str, Any]:
        """Run the special snapshot lifecycle scenario"""
        start_time = time.time()
        result = {
            "iteration": iteration,
            "scenario": scenario["name"],
            "provider": provider,
            "status": "running",
            "metrics": {
                "sandbox_creation_time": 0,
                "git_clone_time": 0,
                "file_write_time": 0,
                "snapshot_creation_time": 0,
                "sandbox_kill_time": 0,
                "sandbox_restore_time": 0,
                "verification_time": 0,
                "total_time": 0,
                "success_rate": 0,
                "operations_completed": 0,
                "operations_total": 6,  # git clone, file write, snapshot, kill, restore, verify
            },
        }

        operations_completed = 0

        try:
            # Step 1: Create initial sandbox and measure creation time
            creation_start = time.time()
            sandbox = Sandbox(provider=provider)
            await sandbox.__aenter__()
            result["metrics"]["sandbox_creation_time"] = time.time() - creation_start
            operations_completed += 1

            # Step 2: Git clone the outline repo
            clone_start = time.time()
            try:
                clone_result = await sandbox.execute(
                    "git clone https://github.com/codegen-sh/outline.git /tmp/outline",
                    timeout=self.config["timeout"],
                )
                result["metrics"]["git_clone_time"] = time.time() - clone_start
                if clone_result.success:
                    operations_completed += 1
                    self.logger.info(f"Git clone successful for {provider}")
                else:
                    self.logger.warning(
                        f"Git clone failed for {provider}: {clone_result.stderr}"
                    )
            except Exception as e:
                result["metrics"]["git_clone_time"] = time.time() - clone_start
                self.logger.error(f"Git clone error for {provider}: {e}")

            # Step 3: Write codegen-test.md file
            file_start = time.time()
            try:
                file_content = scenario["files"][0]["content"]
                await sandbox.upload_file("codegen-test.md", file_content)
                result["metrics"]["file_write_time"] = time.time() - file_start
                operations_completed += 1
                self.logger.info(f"File write successful for {provider}")
            except Exception as e:
                result["metrics"]["file_write_time"] = time.time() - file_start
                self.logger.error(f"File write error for {provider}: {e}")

            # Step 4: Create snapshot
            snapshot_start = time.time()
            snapshot_id = None
            try:
                snapshot_id = await sandbox.create_snapshot()
                result["metrics"]["snapshot_creation_time"] = (
                    time.time() - snapshot_start
                )
                operations_completed += 1
                self.logger.info(f"Snapshot created for {provider}: {snapshot_id}")
            except Exception as e:
                result["metrics"]["snapshot_creation_time"] = (
                    time.time() - snapshot_start
                )
                self.logger.error(f"Snapshot creation error for {provider}: {e}")

            # Step 5: Kill/close the original sandbox
            kill_start = time.time()
            try:
                await sandbox.__aexit__(None, None, None)
                result["metrics"]["sandbox_kill_time"] = time.time() - kill_start
                operations_completed += 1
                self.logger.info(f"Sandbox killed for {provider}")
            except Exception as e:
                result["metrics"]["sandbox_kill_time"] = time.time() - kill_start
                self.logger.error(f"Sandbox kill error for {provider}: {e}")

            # Step 6: Create new sandbox and restore from snapshot
            restore_start = time.time()
            try:
                new_sandbox = Sandbox(provider=provider)
                await new_sandbox.__aenter__()

                if snapshot_id:
                    await new_sandbox.restore_snapshot(snapshot_id)

                # Verify the restoration by checking if files exist
                verify_start = time.time()
                outline_check = await new_sandbox.execute(
                    "ls -la /tmp/outline", timeout=self.config["timeout"]
                )
                file_check = await new_sandbox.execute(
                    "ls -la codegen-test.md", timeout=self.config["timeout"]
                )

                result["metrics"]["sandbox_restore_time"] = verify_start - restore_start
                result["metrics"]["verification_time"] = time.time() - verify_start

                if outline_check.success and file_check.success:
                    operations_completed += 1
                    self.logger.info(
                        f"Snapshot restore and verification successful for {provider}"
                    )
                else:
                    self.logger.warning(
                        f"Snapshot restore verification failed for {provider}"
                    )

                await new_sandbox.__aexit__(None, None, None)

            except Exception as e:
                result["metrics"]["sandbox_restore_time"] = time.time() - restore_start
                result["metrics"]["verification_time"] = 0
                self.logger.error(f"Sandbox restore error for {provider}: {e}")

            # Calculate success rate
            result["metrics"]["operations_completed"] = operations_completed
            result["metrics"]["success_rate"] = (
                operations_completed / result["metrics"]["operations_total"]
            )
            result["metrics"]["total_time"] = time.time() - start_time
            result["status"] = "completed"

        except Exception as e:
            result["metrics"]["total_time"] = time.time() - start_time
            result["status"] = "failed"
            result["error"] = str(e)
            self.logger.error(f"Snapshot lifecycle scenario failed for {provider}: {e}")

        return result

    def _aggregate_scenario_results(
        self, scenario_results: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Aggregate results from multiple iterations of a scenario"""
        successful_results = [
            r for r in scenario_results if r.get("status") == "completed"
        ]

        if not successful_results:
            return {
                "success_rate": 0,
                "avg_total_time": 0,
                "avg_sandbox_creation_time": 0,
                "error_rate": 1.0,
            }

        # Calculate averages
        total_times = [r["metrics"]["total_time"] for r in successful_results]
        creation_times = [
            r["metrics"]["sandbox_creation_time"] for r in successful_results
        ]
        success_rates = [r["metrics"]["success_rate"] for r in successful_results]

        return {
            "iterations_completed": len(successful_results),
            "iterations_total": len(scenario_results),
            "success_rate": statistics.mean(success_rates) if success_rates else 0,
            "avg_total_time": statistics.mean(total_times) if total_times else 0,
            "min_total_time": min(total_times) if total_times else 0,
            "max_total_time": max(total_times) if total_times else 0,
            "avg_sandbox_creation_time": (
                statistics.mean(creation_times) if creation_times else 0
            ),
            "error_rate": 1 - (len(successful_results) / len(scenario_results)),
        }

    def _calculate_overall_metrics(self, scenarios: dict[str, Any]) -> dict[str, Any]:
        """Calculate overall metrics across all scenarios"""
        all_success_rates = []
        all_total_times = []
        all_creation_times = []

        for scenario_data in scenarios.values():
            agg = scenario_data.get("aggregated", {})
            if agg.get("success_rate") is not None:
                all_success_rates.append(agg["success_rate"])
            if agg.get("avg_total_time") is not None:
                all_total_times.append(agg["avg_total_time"])
            if agg.get("avg_sandbox_creation_time") is not None:
                all_creation_times.append(agg["avg_sandbox_creation_time"])

        return {
            "overall_success_rate": (
                statistics.mean(all_success_rates) if all_success_rates else 0
            ),
            "avg_scenario_time": (
                statistics.mean(all_total_times) if all_total_times else 0
            ),
            "avg_sandbox_creation_time": (
                statistics.mean(all_creation_times) if all_creation_times else 0
            ),
            "scenarios_completed": len(
                [
                    s
                    for s in scenarios.values()
                    if s.get("aggregated", {}).get("success_rate", 0) > 0
                ]
            ),
        }

    def _generate_summary(self, provider_results: dict[str, Any]) -> dict[str, Any]:
        """Generate summary comparison across providers"""
        summary = {
            "provider_comparison": {},
            "best_performer": {},
            "recommendations": [],
        }

        # Compare providers
        for provider, results in provider_results.items():
            if results.get("status") == "completed":
                overall = results.get("overall_metrics", {})
                summary["provider_comparison"][provider] = {
                    "success_rate": overall.get("overall_success_rate", 0),
                    "avg_time": overall.get("avg_scenario_time", 0),
                    "creation_time": overall.get("avg_sandbox_creation_time", 0),
                    "scenarios_completed": overall.get("scenarios_completed", 0),
                }

        # Find best performers
        if summary["provider_comparison"]:
            # Best success rate
            best_success = max(
                summary["provider_comparison"].items(),
                key=lambda x: x[1]["success_rate"],
            )
            summary["best_performer"]["reliability"] = best_success[0]

            # Fastest average time
            fastest = min(
                summary["provider_comparison"].items(),
                key=lambda x: (
                    x[1]["avg_time"] if x[1]["avg_time"] > 0 else float("inf")
                ),
            )
            summary["best_performer"]["speed"] = fastest[0]

            # Fastest creation time
            fastest_creation = min(
                summary["provider_comparison"].items(),
                key=lambda x: (
                    x[1]["creation_time"] if x[1]["creation_time"] > 0 else float("inf")
                ),
            )
            summary["best_performer"]["startup"] = fastest_creation[0]

        return summary

    def save_results(self, results: dict[str, Any]) -> None:
        """Save benchmark results in multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON
        json_file = self.results_dir / f"grainchain_benchmark_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Save as latest
        latest_json = self.results_dir / "latest_grainchain.json"
        with open(latest_json, "w") as f:
            json.dump(results, f, indent=2, default=str)

        # Generate markdown report
        if "markdown" in self.config["export_formats"]:
            md_content = self._generate_markdown_report(results)
            md_file = self.results_dir / f"grainchain_benchmark_{timestamp}.md"
            with open(md_file, "w") as f:
                f.write(md_content)

            # Save as latest
            latest_md = self.results_dir / "latest_grainchain.md"
            with open(latest_md, "w") as f:
                f.write(md_content)

        self.logger.info(f"📁 Results saved to {json_file}")

    def _generate_markdown_report(self, results: dict[str, Any]) -> str:
        """Generate a markdown report from benchmark results"""
        md = f"""# Grainchain Provider Benchmark Report

**Generated:** {results["benchmark_info"]["start_time"]}
**Duration:** {results["benchmark_info"]["duration_seconds"]:.2f} seconds
**Providers Tested:** {", ".join(results["benchmark_info"]["providers"])}
**Test Scenarios:** {results["benchmark_info"]["test_scenarios"]}

## Executive Summary

"""

        # Add summary table
        if results["summary"]["provider_comparison"]:
            md += "| Provider | Success Rate | Avg Time (s) | Creation Time (s) | Status |\n"
            md += "|----------|--------------|--------------|-------------------|--------|\n"

            for provider, metrics in results["summary"]["provider_comparison"].items():
                status = (
                    "✅"
                    if metrics["success_rate"] > 0.8
                    else "⚠️"
                    if metrics["success_rate"] > 0.5
                    else "❌"
                )
                md += f"| {provider} | {metrics['success_rate']:.1%} | {metrics['avg_time']:.2f} | {metrics['creation_time']:.2f} | {status} |\n"

        # Best performers
        if results["summary"]["best_performer"]:
            md += "\n## 🏆 Best Performers\n\n"
            best = results["summary"]["best_performer"]
            if "reliability" in best:
                md += f"- **Most Reliable:** {best['reliability']}\n"
            if "speed" in best:
                md += f"- **Fastest Execution:** {best['speed']}\n"
            if "startup" in best:
                md += f"- **Fastest Startup:** {best['startup']}\n"

        # Detailed results
        md += "\n## Detailed Results\n\n"

        for provider, provider_data in results["provider_results"].items():
            md += f"### {provider.upper()} Provider\n\n"

            if provider_data.get("status") != "completed":
                md += f"❌ **Status:** {provider_data.get('status', 'unknown')}\n"
                if "error" in provider_data:
                    md += f"**Error:** {provider_data['error']}\n\n"
                continue

            overall = provider_data.get("overall_metrics", {})
            md += f"- **Overall Success Rate:** {overall.get('overall_success_rate', 0):.1%}\n"
            md += f"- **Average Scenario Time:** {overall.get('avg_scenario_time', 0):.2f}s\n"
            md += f"- **Average Creation Time:** {overall.get('avg_sandbox_creation_time', 0):.2f}s\n\n"

            # Scenario details
            for scenario_name, scenario_data in provider_data["scenarios"].items():
                agg = scenario_data.get("aggregated", {})
                md += f"#### {scenario_name.replace('_', ' ').title()}\n"
                md += f"- **Success Rate:** {agg.get('success_rate', 0):.1%}\n"
                md += f"- **Average Time:** {agg.get('avg_total_time', 0):.2f}s\n"
                md += f"- **Iterations:** {agg.get('iterations_completed', 0)}/{agg.get('iterations_total', 0)}\n\n"

        # Configuration
        md += "## Configuration\n\n"
        md += f"```json\n{json.dumps(results['benchmark_info']['config'], indent=2)}\n```\n"

        return md


async def main():
    """Main entry point for Grainchain benchmarking"""
    parser = argparse.ArgumentParser(description="Grainchain Provider Benchmarking")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument(
        "--providers",
        nargs="+",
        help="Providers to test",
        choices=["local", "e2b", "modal", "daytona"],
        default=["local", "e2b"],
    )
    parser.add_argument(
        "--iterations", type=int, default=3, help="Number of iterations per test"
    )
    parser.add_argument("--output-dir", help="Output directory for results")
    args = parser.parse_args()

    # Create custom config if needed
    config = {}
    if args.providers:
        config["providers"] = args.providers
    if args.iterations:
        config["iterations"] = args.iterations

    # Save temporary config if needed
    config_path = None
    if config:
        config_path = "temp_benchmark_config.json"
        with open(config_path, "w") as f:
            json.dump(config, f)

    try:
        # Run benchmark
        benchmark = GrainchainBenchmark(config_path or args.config)
        results = await benchmark.run_full_benchmark()
        benchmark.save_results(results)

        print("\n🎉 Grainchain benchmark completed successfully!")
        print(f"📊 Results saved to: {benchmark.results_dir}")

        # Print quick summary
        if results["summary"]["provider_comparison"]:
            print("\n📈 Quick Summary:")
            for provider, metrics in results["summary"]["provider_comparison"].items():
                print(
                    f"  {provider}: {metrics['success_rate']:.1%} success, {metrics['avg_time']:.2f}s avg"
                )

    finally:
        # Cleanup temporary config
        if config_path and os.path.exists(config_path):
            os.remove(config_path)


if __name__ == "__main__":
    asyncio.run(main())
