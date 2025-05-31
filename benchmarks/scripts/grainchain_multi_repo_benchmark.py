#!/usr/bin/env python3
"""
Multi-Repository Benchmarking Infrastructure using Grainchain

This script orchestrates the benchmarking process for multiple repositories:
1. Uses grainchain Sandbox for environment management
2. Installs applications based on their language and package manager
3. Takes performance snapshots before and after making trivial changes
4. Stores results per repository and generates reports
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add the project root to the path so we can import grainchain
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from grainchain import Sandbox, SandboxConfig
except ImportError as e:
    print(f"❌ Error importing grainchain: {e}")
    print("Make sure you're in the virtual environment: source .venv/bin/activate")
    sys.exit(1)


class GrainchainMultiRepoBenchmark:
    """Main class for running benchmarks across multiple repositories using grainchain"""

    def __init__(self, config_paths: list[str] = None):
        self.configs = self._load_configs(config_paths or [])
        self.results_dir = Path("benchmarks/results")
        self.results_dir.mkdir(exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(
                    self.results_dir / "grainchain_multi_benchmark.log"
                ),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _load_configs(self, config_paths: list[str]) -> dict[str, dict[str, Any]]:
        """Load configurations from files"""
        configs = {}

        # If no config paths provided, load all configs from configs directory
        if not config_paths:
            config_dir = Path("benchmarks/configs")
            config_paths = [
                str(f) for f in config_dir.glob("*.json") if f.name != "default.json"
            ]

        for config_path in config_paths:
            if os.path.exists(config_path):
                with open(config_path) as f:
                    config = json.load(f)
                    repo_name = config.get("repo_name", Path(config_path).stem)
                    configs[repo_name] = config
                    self.logger.info(f"Loaded config for {repo_name}")
            else:
                self.logger.warning(f"Config file not found: {config_path}")

        return configs

    async def clone_and_install_repo(
        self, sandbox, repo_name: str, config: dict[str, Any]
    ) -> bool:
        """Clone repository and install dependencies"""
        try:
            self.logger.info(f"Cloning {repo_name} repository...")

            # Clone the repository
            clone_cmd = f"git clone {config['repo_url']} {repo_name}"
            result = await sandbox.run_command(clone_cmd)

            if result.exit_code != 0:
                self.logger.error(f"Failed to clone {repo_name}: {result.stderr}")
                return False

            # Checkout specific branch if needed
            if config["repo_branch"] not in ["main", "master"]:
                checkout_cmd = f"cd {repo_name} && git checkout {config['repo_branch']}"
                result = await sandbox.run_command(checkout_cmd)
                if result.exit_code != 0:
                    self.logger.error(
                        f"Failed to checkout branch for {repo_name}: {result.stderr}"
                    )
                    return False

            self.logger.info(f"Installing {repo_name} dependencies...")

            # Install dependencies based on package manager
            install_cmd = f"cd {repo_name} && {config['install_command']}"
            result = await sandbox.run_command(install_cmd)

            if result.exit_code != 0:
                self.logger.error(
                    f"Failed to install dependencies for {repo_name}: {result.stderr}"
                )
                return False

            self.logger.info(f"{repo_name} installation completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to install {repo_name}: {e}")
            return False

    async def take_snapshot(
        self, sandbox, repo_name: str, config: dict[str, Any], snapshot_name: str
    ) -> dict[str, Any]:
        """Take a performance snapshot of the repository"""
        snapshot_data = {
            "timestamp": datetime.now().isoformat(),
            "snapshot_name": snapshot_name,
            "repo_name": repo_name,
        }

        try:
            # Collect filesystem stats
            if config.get("metrics", {}).get("collect_filesystem_stats", True):
                result = await sandbox.run_command(f"du -sh {repo_name}")
                if result.exit_code == 0:
                    snapshot_data["filesystem_size"] = result.stdout.strip().split()[0]

            # Collect memory usage
            if config.get("metrics", {}).get("collect_memory_usage", True):
                result = await sandbox.run_command("free -m")
                if result.exit_code == 0:
                    snapshot_data["memory_info"] = result.stdout.strip()

            # Run tests if configured
            if config.get("metrics", {}).get("run_tests", True):
                test_start = time.time()
                test_cmd = f"cd {repo_name} && timeout 30s {config.get('test_command', 'echo \"No test command configured\"')}"
                result = await sandbox.run_command(test_cmd)
                test_duration = time.time() - test_start

                snapshot_data["test_results"] = {
                    "exit_code": result.exit_code,
                    "duration": test_duration,
                    "stdout_length": len(result.stdout) if result.stdout else 0,
                    "stderr_length": len(result.stderr) if result.stderr else 0,
                }

            self.logger.info(f"Snapshot '{snapshot_name}' completed for {repo_name}")
            return snapshot_data

        except Exception as e:
            self.logger.error(f"Failed to take snapshot for {repo_name}: {e}")
            snapshot_data["error"] = str(e)
            return snapshot_data

    async def apply_trivial_change(
        self, sandbox, repo_name: str, config: dict[str, Any], change: dict[str, str]
    ) -> bool:
        """Apply a trivial change to the repository"""
        try:
            file_path = f"{repo_name}/{change['file']}"

            if change["type"] == "comment":
                cmd = f"echo '{change['content']}' >> {file_path}"
            elif change["type"] == "whitespace":
                cmd = f"echo '{change['content']}' >> {file_path}"
            elif change["type"] == "log":
                cmd = f"echo '{change['content']}' >> {file_path}"
            else:
                self.logger.warning(f"Unknown change type: {change['type']}")
                return False

            result = await sandbox.run_command(cmd)
            if result.exit_code != 0:
                self.logger.error(
                    f"Failed to apply change to {repo_name}: {result.stderr}"
                )
                return False

            return True

        except Exception as e:
            self.logger.error(f"Failed to apply trivial change to {repo_name}: {e}")
            return False

    async def revert_changes(self, sandbox, repo_name: str) -> bool:
        """Revert all changes in the repository"""
        try:
            result = await sandbox.run_command(f"cd {repo_name} && git checkout .")
            return result.exit_code == 0
        except Exception as e:
            self.logger.error(f"Failed to revert changes for {repo_name}: {e}")
            return False

    async def run_benchmark_for_repo(
        self, repo_name: str, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Run benchmark for a single repository"""
        self.logger.info(f"Starting benchmark for {repo_name}...")

        results = {
            "repo_name": repo_name,
            "config": config,
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "snapshots": {},
            "changes_applied": [],
        }

        try:
            # Create sandbox configuration
            sandbox_config = SandboxConfig(
                template="e2b-code",
                timeout=300,  # 5 minutes
            )

            async with Sandbox(sandbox_config) as sandbox:
                self.logger.info(f"Sandbox created for {repo_name}")

                # Clone and install
                if not await self.clone_and_install_repo(sandbox, repo_name, config):
                    results["status"] = "failed"
                    results["error"] = "Repository setup failed"
                    return results

                # Take initial snapshot
                initial_snapshot = await self.take_snapshot(
                    sandbox, repo_name, config, "initial"
                )
                results["snapshots"]["initial"] = initial_snapshot

                # Apply trivial changes and take snapshots
                for i, change in enumerate(config.get("trivial_changes", [])):
                    change_name = f"change_{i+1}_{change['type']}"

                    if await self.apply_trivial_change(
                        sandbox, repo_name, config, change
                    ):
                        results["changes_applied"].append(change)
                        snapshot = await self.take_snapshot(
                            sandbox, repo_name, config, change_name
                        )
                        results["snapshots"][change_name] = snapshot
                    else:
                        self.logger.warning(
                            f"Failed to apply change {change_name} for {repo_name}"
                        )

                # Take final snapshot
                final_snapshot = await self.take_snapshot(
                    sandbox, repo_name, config, "final"
                )
                results["snapshots"]["final"] = final_snapshot

                results["status"] = "completed"
                results["end_time"] = datetime.now().isoformat()

        except Exception as e:
            self.logger.error(f"Benchmark failed for {repo_name}: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
            results["end_time"] = datetime.now().isoformat()

        return results

    async def run_all_benchmarks(self) -> dict[str, Any]:
        """Run benchmarks for all configured repositories"""
        self.logger.info("Starting multi-repository benchmarks...")

        all_results = {
            "start_time": datetime.now().isoformat(),
            "repositories": {},
            "summary": {},
        }

        for repo_name, config in self.configs.items():
            self.logger.info(f"Running benchmark for {repo_name}...")
            repo_results = await self.run_benchmark_for_repo(repo_name, config)
            all_results["repositories"][repo_name] = repo_results

        all_results["end_time"] = datetime.now().isoformat()

        # Generate summary
        all_results["summary"] = self._generate_summary(all_results["repositories"])

        return all_results

    def _generate_summary(self, repo_results: dict[str, Any]) -> dict[str, Any]:
        """Generate summary statistics across all repositories"""
        summary = {
            "total_repos": len(repo_results),
            "successful": 0,
            "failed": 0,
            "by_language": {},
        }

        for _repo_name, results in repo_results.items():
            if results["status"] == "completed":
                summary["successful"] += 1
            else:
                summary["failed"] += 1

            language = results["config"].get("language", "unknown")
            if language not in summary["by_language"]:
                summary["by_language"][language] = {"count": 0, "successful": 0}

            summary["by_language"][language]["count"] += 1
            if results["status"] == "completed":
                summary["by_language"][language]["successful"] += 1

        return summary

    def save_results(self, results: dict[str, Any]) -> None:
        """Save benchmark results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save overall results
        results_file = self.results_dir / f"grainchain_multi_benchmark_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        # Save per-repository results
        for repo_name, repo_results in results["repositories"].items():
            repo_file = (
                self.results_dir / f"{repo_name}_grainchain_benchmark_{timestamp}.json"
            )
            with open(repo_file, "w") as f:
                json.dump(repo_results, f, indent=2)

        self.logger.info(f"Results saved to {results_file}")


async def main():
    parser = argparse.ArgumentParser(
        description="Run multi-repository benchmarks with grainchain"
    )
    parser.add_argument(
        "--configs",
        nargs="*",
        help="Paths to configuration files (default: all configs in benchmarks/configs/)",
    )
    parser.add_argument("--repo", help="Run benchmark for a specific repository only")

    args = parser.parse_args()

    try:
        runner = GrainchainMultiRepoBenchmark(args.configs)

        if args.repo:
            if args.repo not in runner.configs:
                print(f"❌ Repository '{args.repo}' not found in configurations")
                print(f"Available repositories: {list(runner.configs.keys())}")
                sys.exit(1)

            print(f"🚀 Starting grainchain benchmark for {args.repo}...")
            config = runner.configs[args.repo]
            results = await runner.run_benchmark_for_repo(args.repo, config)
            all_results = {
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "repositories": {args.repo: results},
                "summary": runner._generate_summary({args.repo: results}),
            }
        else:
            print("🚀 Starting grainchain multi-repository benchmarks...")
            all_results = await runner.run_all_benchmarks()

        runner.save_results(all_results)

        # Print summary
        summary = all_results["summary"]
        print("\n📊 Benchmark Summary:")
        print(f"   Total repositories: {summary['total_repos']}")
        print(f"   Successful: {summary['successful']}")
        print(f"   Failed: {summary['failed']}")

        for language, stats in summary["by_language"].items():
            print(f"   {language}: {stats['successful']}/{stats['count']} successful")

    except KeyboardInterrupt:
        print("\n⚠️ Benchmark interrupted by user")
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
