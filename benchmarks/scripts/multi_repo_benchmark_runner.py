#!/usr/bin/env python3
"""
Multi-Repository Benchmarking Infrastructure

This script orchestrates the benchmarking process for multiple repositories:
1. Boots up a VM using the codex-universal base image
2. Installs applications based on their language and package manager
3. Takes performance snapshots before and after making trivial changes
4. Stores results per repository and generates reports
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import docker


class MultiRepoBenchmarkRunner:
    """Main class for running benchmarks across multiple repositories"""

    def __init__(self, config_paths: list[str] = None):
        self.configs = self._load_configs(config_paths or [])
        self.docker_client = docker.from_env()
        self.containers = {}
        self.results_dir = Path("benchmarks/results")
        self.results_dir.mkdir(exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.results_dir / "multi_benchmark.log"),
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

    def setup_container(self, repo_name: str, config: dict[str, Any]) -> bool:
        """Setup and start the Docker container for a specific repository"""
        try:
            self.logger.info(f"Setting up container for {repo_name}...")
            self.docker_client.images.pull(config["base_image"])

            environment = {}
            if config.get("language") == "typescript":
                environment["CODEX_ENV_NODE_VERSION"] = config.get("node_version", "20")
            if config.get("python_version"):
                environment["CODEX_ENV_PYTHON_VERSION"] = config["python_version"]

            container = self.docker_client.containers.run(
                config["base_image"],
                command="sleep infinity",
                name=config["container_name"],
                detach=True,
                remove=True,
                environment=environment,
                working_dir=config["workspace_path"],
                volumes={str(Path.cwd()): {"bind": "/host", "mode": "rw"}},
            )

            # Wait for container to be ready
            time.sleep(5)

            # Test container connectivity
            result = container.exec_run("echo 'Container ready'")
            if result.exit_code != 0:
                self.logger.error(f"Container setup failed for {repo_name}")
                return False

            self.containers[repo_name] = container
            self.logger.info(f"Container setup completed for {repo_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to setup container for {repo_name}: {e}")
            return False

    def clone_and_install_repo(self, repo_name: str, config: dict[str, Any]) -> bool:
        """Clone repository and install dependencies"""
        container = self.containers[repo_name]

        try:
            self.logger.info(f"Cloning {repo_name} repository...")

            # Clone the repository
            clone_cmd = f"git clone {config['repo_url']} {repo_name}"
            result = container.exec_run(clone_cmd, workdir=config["workspace_path"])
            if result.exit_code != 0:
                self.logger.error(
                    f"Failed to clone {repo_name}: {result.output.decode()}"
                )
                return False

            # Checkout specific branch if needed
            if config["repo_branch"] != "main" and config["repo_branch"] != "master":
                checkout_cmd = f"git checkout {config['repo_branch']}"
                result = container.exec_run(
                    checkout_cmd, workdir=f"{config['workspace_path']}/{repo_name}"
                )
                if result.exit_code != 0:
                    self.logger.error(
                        f"Failed to checkout branch for {repo_name}: {result.output.decode()}"
                    )
                    return False

            self.logger.info(f"Installing {repo_name} dependencies...")

            # Install dependencies based on package manager
            install_cmd = config["install_command"]
            environment = {}

            if config.get("language") == "typescript":
                environment["NODE_ENV"] = "development"
            elif config.get("language") == "python":
                environment["PYTHONPATH"] = f"{config['workspace_path']}/{repo_name}"

            result = container.exec_run(
                install_cmd,
                workdir=f"{config['workspace_path']}/{repo_name}",
                environment=environment,
            )

            if result.exit_code != 0:
                self.logger.error(
                    f"Failed to install dependencies for {repo_name}: {result.output.decode()}"
                )
                return False

            self.logger.info(f"{repo_name} installation completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to install {repo_name}: {e}")
            return False

    def take_snapshot(
        self, repo_name: str, config: dict[str, Any], snapshot_name: str
    ) -> dict[str, Any]:
        """Take a performance snapshot of the repository"""
        container = self.containers[repo_name]
        snapshot_data = {
            "timestamp": datetime.now().isoformat(),
            "snapshot_name": snapshot_name,
            "repo_name": repo_name,
        }

        try:
            # Collect filesystem stats
            if config.get("metrics", {}).get("collect_filesystem_stats", True):
                result = container.exec_run(
                    f"du -sh {config['workspace_path']}/{repo_name}",
                    workdir=config["workspace_path"],
                )
                if result.exit_code == 0:
                    snapshot_data["filesystem_size"] = (
                        result.output.decode().strip().split()[0]
                    )

            # Collect memory usage
            if config.get("metrics", {}).get("collect_memory_usage", True):
                result = container.exec_run("free -m")
                if result.exit_code == 0:
                    memory_info = result.output.decode().strip()
                    snapshot_data["memory_info"] = memory_info

            # Run tests if configured
            if config.get("metrics", {}).get("run_tests", True):
                test_start = time.time()
                result = container.exec_run(
                    config.get("test_command", "echo 'No test command configured'"),
                    workdir=f"{config['workspace_path']}/{repo_name}",
                )
                test_duration = time.time() - test_start

                snapshot_data["test_results"] = {
                    "exit_code": result.exit_code,
                    "duration": test_duration,
                    "output_length": len(result.output.decode())
                    if result.output
                    else 0,
                }

            self.logger.info(f"Snapshot '{snapshot_name}' completed for {repo_name}")
            return snapshot_data

        except Exception as e:
            self.logger.error(f"Failed to take snapshot for {repo_name}: {e}")
            snapshot_data["error"] = str(e)
            return snapshot_data

    def apply_trivial_change(
        self, repo_name: str, config: dict[str, Any], change: dict[str, str]
    ) -> bool:
        """Apply a trivial change to the repository"""
        container = self.containers[repo_name]

        try:
            file_path = f"{config['workspace_path']}/{repo_name}/{change['file']}"

            if change["type"] == "comment":
                cmd = f"echo '{change['content']}' >> {file_path}"
            elif change["type"] == "whitespace":
                cmd = f"echo '{change['content']}' >> {file_path}"
            elif change["type"] == "log":
                cmd = f"echo '{change['content']}' >> {file_path}"
            else:
                self.logger.warning(f"Unknown change type: {change['type']}")
                return False

            result = container.exec_run(cmd)
            if result.exit_code != 0:
                self.logger.error(
                    f"Failed to apply change to {repo_name}: {result.output.decode()}"
                )
                return False

            return True

        except Exception as e:
            self.logger.error(f"Failed to apply trivial change to {repo_name}: {e}")
            return False

    def revert_changes(self, repo_name: str, config: dict[str, Any]) -> bool:
        """Revert all changes in the repository"""
        container = self.containers[repo_name]

        try:
            result = container.exec_run(
                "git checkout .", workdir=f"{config['workspace_path']}/{repo_name}"
            )
            return result.exit_code == 0
        except Exception as e:
            self.logger.error(f"Failed to revert changes for {repo_name}: {e}")
            return False

    def run_benchmark_for_repo(
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
            # Setup container
            if not self.setup_container(repo_name, config):
                results["status"] = "failed"
                results["error"] = "Container setup failed"
                return results

            # Clone and install
            if not self.clone_and_install_repo(repo_name, config):
                results["status"] = "failed"
                results["error"] = "Repository setup failed"
                return results

            # Take initial snapshot
            initial_snapshot = self.take_snapshot(repo_name, config, "initial")
            results["snapshots"]["initial"] = initial_snapshot

            # Apply trivial changes and take snapshots
            for i, change in enumerate(config.get("trivial_changes", [])):
                change_name = f"change_{i+1}_{change['type']}"

                if self.apply_trivial_change(repo_name, config, change):
                    results["changes_applied"].append(change)
                    snapshot = self.take_snapshot(repo_name, config, change_name)
                    results["snapshots"][change_name] = snapshot
                else:
                    self.logger.warning(
                        f"Failed to apply change {change_name} for {repo_name}"
                    )

            # Take final snapshot
            final_snapshot = self.take_snapshot(repo_name, config, "final")
            results["snapshots"]["final"] = final_snapshot

            results["status"] = "completed"
            results["end_time"] = datetime.now().isoformat()

        except Exception as e:
            self.logger.error(f"Benchmark failed for {repo_name}: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
            results["end_time"] = datetime.now().isoformat()

        return results

    def run_all_benchmarks(self) -> dict[str, Any]:
        """Run benchmarks for all configured repositories"""
        self.logger.info("Starting multi-repository benchmarks...")

        all_results = {
            "start_time": datetime.now().isoformat(),
            "repositories": {},
            "summary": {},
        }

        for repo_name, config in self.configs.items():
            self.logger.info(f"Running benchmark for {repo_name}...")
            repo_results = self.run_benchmark_for_repo(repo_name, config)
            all_results["repositories"][repo_name] = repo_results

            # Cleanup container for this repo
            self.cleanup_repo(repo_name)

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
        results_file = self.results_dir / f"multi_benchmark_results_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        # Save per-repository results
        for repo_name, repo_results in results["repositories"].items():
            repo_file = self.results_dir / f"{repo_name}_benchmark_{timestamp}.json"
            with open(repo_file, "w") as f:
                json.dump(repo_results, f, indent=2)

        self.logger.info(f"Results saved to {results_file}")

    def cleanup_repo(self, repo_name: str) -> None:
        """Cleanup container for a specific repository"""
        if repo_name in self.containers:
            try:
                container = self.containers[repo_name]
                container.stop()
                container.remove()
                del self.containers[repo_name]
                self.logger.info(f"Cleaned up container for {repo_name}")
            except Exception as e:
                self.logger.error(f"Failed to cleanup container for {repo_name}: {e}")

    def cleanup_all(self) -> None:
        """Cleanup all containers"""
        for repo_name in list(self.containers.keys()):
            self.cleanup_repo(repo_name)


def main():
    parser = argparse.ArgumentParser(description="Run multi-repository benchmarks")
    parser.add_argument(
        "--configs",
        nargs="*",
        help="Paths to configuration files (default: all configs in benchmarks/configs/)",
    )
    parser.add_argument("--repo", help="Run benchmark for a specific repository only")

    args = parser.parse_args()

    try:
        runner = MultiRepoBenchmarkRunner(args.configs)

        if args.repo:
            if args.repo not in runner.configs:
                print(f"❌ Repository '{args.repo}' not found in configurations")
                print(f"Available repositories: {list(runner.configs.keys())}")
                sys.exit(1)

            print(f"🚀 Starting benchmark for {args.repo}...")
            config = runner.configs[args.repo]
            results = runner.run_benchmark_for_repo(args.repo, config)
            all_results = {
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "repositories": {args.repo: results},
                "summary": runner._generate_summary({args.repo: results}),
            }
        else:
            print("🚀 Starting multi-repository benchmarks...")
            all_results = runner.run_all_benchmarks()

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
    finally:
        if "runner" in locals():
            runner.cleanup_all()


if __name__ == "__main__":
    main()
