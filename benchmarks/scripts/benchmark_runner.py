#!/usr/bin/env python3
"""
Outline Benchmark Runner

⚠️ IMPORTANT: Docker support is not currently available in Grainchain.
This benchmark runner is for future Docker provider development.

The local provider runs directly on your machine without Docker.
Docker provider support is coming soon!

For now, please use the local provider for benchmarking.
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


class BenchmarkRunner:
    """Main class for running Outline benchmarks"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.docker_client = docker.from_env()
        self.container = None
        self.results_dir = Path("benchmarks/results")
        self.results_dir.mkdir(exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.results_dir / "benchmark.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _load_config(self, config_path: str) -> dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "base_image": "ghcr.io/openai/codex-universal:latest",
            "outline_repo": "https://github.com/outline/outline.git",
            "outline_branch": "main",
            "container_name": "outline-benchmark",
            "workspace_path": "/workspace",
            "node_version": "20",
            "python_version": "3.12",
            "benchmark_iterations": 3,
            "trivial_changes": [
                {
                    "type": "comment",
                    "file": "README.md",
                    "content": "# Benchmark test comment",
                },
                {"type": "whitespace", "file": "package.json", "content": "\n"},
                {
                    "type": "log",
                    "file": "app/index.js",
                    "content": "console.log('benchmark test');",
                },
            ],
        }

        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def setup_container(self) -> bool:
        """Setup and start the Docker container with codex-universal base"""
        try:
            self.logger.info("Pulling codex-universal base image...")
            self.docker_client.images.pull(self.config["base_image"])

            self.logger.info("Starting container...")
            self.container = self.docker_client.containers.run(
                self.config["base_image"],
                command="sleep infinity",
                name=self.config["container_name"],
                detach=True,
                remove=True,
                environment={
                    "CODEX_ENV_NODE_VERSION": self.config["node_version"],
                    "CODEX_ENV_PYTHON_VERSION": self.config["python_version"],
                },
                working_dir=self.config["workspace_path"],
                volumes={str(Path.cwd()): {"bind": "/host", "mode": "rw"}},
            )

            # Wait for container to be ready
            time.sleep(5)
            self.logger.info(f"Container {self.container.id[:12]} is ready")
            return True

        except Exception as e:
            self.logger.error(f"Failed to setup container: {e}")
            return False

    def clone_and_install_outline(self) -> bool:
        """Clone Outline repository and install dependencies"""
        try:
            self.logger.info("Cloning Outline repository...")

            # Clone the repository
            clone_cmd = f"git clone {self.config['outline_repo']} outline"
            result = self.container.exec_run(
                clone_cmd, workdir=self.config["workspace_path"]
            )
            if result.exit_code != 0:
                self.logger.error(
                    f"Failed to clone repository: {result.output.decode()}"
                )
                return False

            # Checkout specific branch if needed
            if self.config["outline_branch"] != "main":
                checkout_cmd = f"git checkout {self.config['outline_branch']}"
                result = self.container.exec_run(
                    checkout_cmd, workdir=f"{self.config['workspace_path']}/outline"
                )
                if result.exit_code != 0:
                    self.logger.error(
                        f"Failed to checkout branch: {result.output.decode()}"
                    )
                    return False

            self.logger.info("Installing Outline dependencies...")

            # Install dependencies with yarn
            install_cmd = "yarn install --frozen-lockfile"
            result = self.container.exec_run(
                install_cmd,
                workdir=f"{self.config['workspace_path']}/outline",
                environment={"NODE_ENV": "development"},
            )

            if result.exit_code != 0:
                self.logger.error(
                    f"Failed to install dependencies: {result.output.decode()}"
                )
                return False

            self.logger.info("Outline installation completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to install Outline: {e}")
            return False

    def take_snapshot(self, snapshot_name: str) -> dict[str, Any]:
        """Take a performance snapshot of the current state"""
        try:
            self.logger.info(f"Taking snapshot: {snapshot_name}")

            snapshot = {
                "name": snapshot_name,
                "timestamp": datetime.now().isoformat(),
                "metrics": {},
            }

            # Container resource usage
            stats = self.container.stats(stream=False)
            snapshot["metrics"]["container"] = {
                "cpu_usage": stats["cpu_stats"]["cpu_usage"]["total_usage"],
                "memory_usage": stats["memory_stats"]["usage"],
                "memory_limit": stats["memory_stats"]["limit"],
                "network_rx": (
                    stats["networks"]["eth0"]["rx_bytes"] if "networks" in stats else 0
                ),
                "network_tx": (
                    stats["networks"]["eth0"]["tx_bytes"] if "networks" in stats else 0
                ),
            }

            # File system metrics
            result = self.container.exec_run(
                "du -sh outline", workdir=self.config["workspace_path"]
            )
            if result.exit_code == 0:
                size_output = result.output.decode().strip()
                snapshot["metrics"]["filesystem"] = {
                    "outline_size": size_output.split()[0]
                }

            # Node modules size
            result = self.container.exec_run(
                "du -sh outline/node_modules", workdir=self.config["workspace_path"]
            )
            if result.exit_code == 0:
                size_output = result.output.decode().strip()
                snapshot["metrics"]["filesystem"][
                    "node_modules_size"
                ] = size_output.split()[0]

            # Package count
            result = self.container.exec_run(
                "find outline/node_modules -name package.json | wc -l",
                workdir=self.config["workspace_path"],
            )
            if result.exit_code == 0:
                package_count = result.output.decode().strip()
                snapshot["metrics"]["filesystem"]["package_count"] = int(package_count)

            # Build time measurement
            start_time = time.time()
            result = self.container.exec_run(
                "yarn build", workdir=f"{self.config['workspace_path']}/outline"
            )
            build_time = time.time() - start_time

            snapshot["metrics"]["performance"] = {
                "build_time_seconds": build_time,
                "build_success": result.exit_code == 0,
            }

            if result.exit_code != 0:
                snapshot["metrics"]["performance"][
                    "build_error"
                ] = result.output.decode()

            # Test run time (if tests exist)
            start_time = time.time()
            result = self.container.exec_run(
                "yarn test --passWithNoTests",
                workdir=f"{self.config['workspace_path']}/outline",
            )
            test_time = time.time() - start_time

            snapshot["metrics"]["performance"]["test_time_seconds"] = test_time
            snapshot["metrics"]["performance"]["test_success"] = result.exit_code == 0

            self.logger.info(f"Snapshot {snapshot_name} completed")
            return snapshot

        except Exception as e:
            self.logger.error(f"Failed to take snapshot {snapshot_name}: {e}")
            return {"name": snapshot_name, "error": str(e)}

    def apply_trivial_change(self, change: dict[str, str]) -> bool:
        """Apply a trivial change to the codebase"""
        try:
            change_type = change["type"]
            file_path = change["file"]
            content = change["content"]

            self.logger.info(f"Applying {change_type} change to {file_path}")

            if change_type == "comment":
                # Add comment to file
                cmd = f"echo '{content}' >> {file_path}"
            elif change_type == "whitespace":
                # Add whitespace to file
                cmd = f"echo '{content}' >> {file_path}"
            elif change_type == "log":
                # Add log statement (for JS files)
                cmd = f"echo '{content}' >> {file_path}"
            else:
                self.logger.warning(f"Unknown change type: {change_type}")
                return False

            result = self.container.exec_run(
                cmd, workdir=f"{self.config['workspace_path']}/outline"
            )
            return result.exit_code == 0

        except Exception as e:
            self.logger.error(f"Failed to apply change: {e}")
            return False

    def revert_changes(self) -> bool:
        """Revert all changes to clean state"""
        try:
            self.logger.info("Reverting changes...")
            result = self.container.exec_run(
                "git checkout .", workdir=f"{self.config['workspace_path']}/outline"
            )
            return result.exit_code == 0
        except Exception as e:
            self.logger.error(f"Failed to revert changes: {e}")
            return False

    def run_benchmark(self) -> dict[str, Any]:
        """Run the complete benchmark suite"""
        benchmark_results = {
            "start_time": datetime.now().isoformat(),
            "config": self.config,
            "snapshots": [],
            "comparisons": [],
        }

        try:
            # Setup container and install Outline
            if not self.setup_container():
                raise Exception("Failed to setup container")

            if not self.clone_and_install_outline():
                raise Exception("Failed to install Outline")

            # Take baseline snapshot
            baseline_snapshot = self.take_snapshot("baseline")
            benchmark_results["snapshots"].append(baseline_snapshot)

            # Run benchmark iterations
            for i in range(self.config["benchmark_iterations"]):
                self.logger.info(
                    f"Running benchmark iteration {i + 1}/{self.config['benchmark_iterations']}"
                )

                for j, change in enumerate(self.config["trivial_changes"]):
                    # Apply change
                    if not self.apply_trivial_change(change):
                        self.logger.warning(f"Failed to apply change {j + 1}")
                        continue

                    # Take snapshot after change
                    snapshot_name = f"iteration_{i + 1}_change_{j + 1}_{change['type']}"
                    snapshot = self.take_snapshot(snapshot_name)
                    benchmark_results["snapshots"].append(snapshot)

                    # Compare with baseline
                    comparison = self._compare_snapshots(baseline_snapshot, snapshot)
                    benchmark_results["comparisons"].append(comparison)

                    # Revert changes for next iteration
                    self.revert_changes()

            benchmark_results["end_time"] = datetime.now().isoformat()
            benchmark_results["status"] = "completed"

        except Exception as e:
            self.logger.error(f"Benchmark failed: {e}")
            benchmark_results["error"] = str(e)
            benchmark_results["status"] = "failed"

        finally:
            self.cleanup()

        return benchmark_results

    def _compare_snapshots(
        self, baseline: dict[str, Any], current: dict[str, Any]
    ) -> dict[str, Any]:
        """Compare two snapshots and calculate differences"""
        comparison = {
            "baseline": baseline["name"],
            "current": current["name"],
            "differences": {},
        }

        if "metrics" in baseline and "metrics" in current:
            # Compare build times
            if (
                "performance" in baseline["metrics"]
                and "performance" in current["metrics"]
            ):
                baseline_build = baseline["metrics"]["performance"].get(
                    "build_time_seconds", 0
                )
                current_build = current["metrics"]["performance"].get(
                    "build_time_seconds", 0
                )

                comparison["differences"]["build_time_change"] = (
                    current_build - baseline_build
                )
                comparison["differences"]["build_time_percent_change"] = (
                    ((current_build - baseline_build) / baseline_build * 100)
                    if baseline_build > 0
                    else 0
                )

            # Compare memory usage
            if "container" in baseline["metrics"] and "container" in current["metrics"]:
                baseline_memory = baseline["metrics"]["container"].get(
                    "memory_usage", 0
                )
                current_memory = current["metrics"]["container"].get("memory_usage", 0)

                comparison["differences"]["memory_change"] = (
                    current_memory - baseline_memory
                )
                comparison["differences"]["memory_percent_change"] = (
                    ((current_memory - baseline_memory) / baseline_memory * 100)
                    if baseline_memory > 0
                    else 0
                )

        return comparison

    def generate_report(self, results: dict[str, Any]) -> str:
        """Generate HTML report from benchmark results"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Outline Benchmark Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .metric {{ margin: 20px 0; }}
        .error {{ color: red; }}
        .success {{ color: green; }}
    </style>
</head>
<body>
    <h1>Outline Benchmark Report</h1>
    <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <p><strong>Status:</strong> <span class="{"success" if results.get("status") == "completed" else "error"}">{results.get("status", "unknown")}</span></p>

    <h2>Configuration</h2>
    <table>
        <tr><th>Setting</th><th>Value</th></tr>
        <tr><td>Base Image</td><td>{results["config"]["base_image"]}</td></tr>
        <tr><td>Node Version</td><td>{results["config"]["node_version"]}</td></tr>
        <tr><td>Iterations</td><td>{results["config"]["benchmark_iterations"]}</td></tr>
    </table>

    <h2>Snapshot Results</h2>
    <table>
        <tr>
            <th>Snapshot</th>
            <th>Build Time (s)</th>
            <th>Memory Usage (MB)</th>
            <th>Package Count</th>
            <th>Status</th>
        </tr>
"""

        for snapshot in results.get("snapshots", []):
            if "metrics" in snapshot:
                build_time = (
                    snapshot["metrics"]
                    .get("performance", {})
                    .get("build_time_seconds", "N/A")
                )
                memory_mb = round(
                    snapshot["metrics"].get("container", {}).get("memory_usage", 0)
                    / 1024
                    / 1024,
                    2,
                )
                package_count = (
                    snapshot["metrics"]
                    .get("filesystem", {})
                    .get("package_count", "N/A")
                )
                build_success = (
                    snapshot["metrics"]
                    .get("performance", {})
                    .get("build_success", False)
                )
                status = "✅" if build_success else "❌"
            else:
                build_time = memory_mb = package_count = "Error"
                status = "❌"

            html_content += f"""
        <tr>
            <td>{snapshot["name"]}</td>
            <td>{build_time}</td>
            <td>{memory_mb}</td>
            <td>{package_count}</td>
            <td>{status}</td>
        </tr>"""

        html_content += """
    </table>

    <h2>Performance Comparisons</h2>
    <table>
        <tr>
            <th>Comparison</th>
            <th>Build Time Change (s)</th>
            <th>Build Time Change (%)</th>
            <th>Memory Change (MB)</th>
            <th>Memory Change (%)</th>
        </tr>
"""

        for comparison in results.get("comparisons", []):
            diffs = comparison.get("differences", {})
            build_change = round(diffs.get("build_time_change", 0), 3)
            build_percent = round(diffs.get("build_time_percent_change", 0), 2)
            memory_change = round(diffs.get("memory_change", 0) / 1024 / 1024, 2)
            memory_percent = round(diffs.get("memory_percent_change", 0), 2)

            html_content += f"""
        <tr>
            <td>{comparison["current"]} vs {comparison["baseline"]}</td>
            <td>{build_change:+}</td>
            <td>{build_percent:+}%</td>
            <td>{memory_change:+}</td>
            <td>{memory_percent:+}%</td>
        </tr>"""

        html_content += """
    </table>
</body>
</html>
"""
        return html_content

    def generate_markdown_report(self, results: dict[str, Any]) -> str:
        """Generate GitHub Flavored Markdown report"""
        md_content = f"""# Outline Benchmark Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Status:** {"✅ Completed" if results.get("status") == "completed" else "❌ Failed"}

## Configuration

| Setting | Value |
|---------|-------|
| Base Image | `{results["config"]["base_image"]}` |
| Node Version | `{results["config"]["node_version"]}` |
| Iterations | `{results["config"]["benchmark_iterations"]}` |

## Snapshot Results

| Snapshot | Build Time (s) | Memory Usage (MB) | Package Count | Status |
|----------|----------------|-------------------|---------------|--------|
"""

        for snapshot in results.get("snapshots", []):
            if "metrics" in snapshot:
                build_time = (
                    snapshot["metrics"]
                    .get("performance", {})
                    .get("build_time_seconds", "N/A")
                )
                memory_mb = round(
                    snapshot["metrics"].get("container", {}).get("memory_usage", 0)
                    / 1024
                    / 1024,
                    2,
                )
                package_count = (
                    snapshot["metrics"]
                    .get("filesystem", {})
                    .get("package_count", "N/A")
                )
                build_success = (
                    snapshot["metrics"]
                    .get("performance", {})
                    .get("build_success", False)
                )
                status = "✅" if build_success else "❌"
            else:
                build_time = memory_mb = package_count = "Error"
                status = "❌"

            md_content += f"| {snapshot['name']} | {build_time} | {memory_mb} | {package_count} | {status} |\n"

        md_content += """
## Performance Comparisons

| Comparison | Build Time Change (s) | Build Time Change (%) | Memory Change (MB) | Memory Change (%) |
|------------|----------------------|----------------------|-------------------|-------------------|
"""

        for comparison in results.get("comparisons", []):
            diffs = comparison.get("differences", {})
            build_change = round(diffs.get("build_time_change", 0), 3)
            build_percent = round(diffs.get("build_time_percent_change", 0), 2)
            memory_change = round(diffs.get("memory_change", 0) / 1024 / 1024, 2)
            memory_percent = round(diffs.get("memory_percent_change", 0), 2)

            md_content += f"| {comparison['current']} vs {comparison['baseline']} | {build_change:+} | {build_percent:+}% | {memory_change:+} | {memory_percent:+}% |\n"

        return md_content

    def save_results(self, results: dict[str, Any]) -> None:
        """Save benchmark results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON results
        json_file = self.results_dir / f"benchmark_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(results, f, indent=2)

        # Save HTML report
        html_content = self.generate_report(results)
        html_file = self.results_dir / f"benchmark_{timestamp}.html"
        with open(html_file, "w") as f:
            f.write(html_content)

        # Save Markdown report
        md_content = self.generate_markdown_report(results)
        md_file = self.results_dir / f"benchmark_{timestamp}.md"
        with open(md_file, "w") as f:
            f.write(md_content)

        # Update latest results
        latest_json = self.results_dir / "latest.json"
        latest_html = self.results_dir / "latest.html"
        latest_md = self.results_dir / "latest.md"

        with open(latest_json, "w") as f:
            json.dump(results, f, indent=2)
        with open(latest_html, "w") as f:
            f.write(html_content)
        with open(latest_md, "w") as f:
            f.write(md_content)

        self.logger.info(f"Results saved to {json_file}, {html_file}, {md_file}")

    def cleanup(self) -> None:
        """Clean up resources"""
        if self.container:
            try:
                self.container.stop()
                self.logger.info("Container stopped and cleaned up")
            except Exception as e:
                self.logger.error(f"Failed to cleanup container: {e}")


class DockerBenchmarkRunner:
    """
    ⚠️ IMPORTANT: Docker support is not currently available in Grainchain.
    This benchmark runner is for future Docker provider development.

    The local provider runs directly on your machine without Docker.
    Docker provider support is coming soon!

    For now, please use the local provider for benchmarking.
    """

    def __init__(self, config: dict[str, Any]):
        # Docker support coming soon - this will fail for now
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            raise RuntimeError(
                "❌ Docker support is not currently available in Grainchain.\n"
                "The local provider runs directly on your machine without Docker.\n"
                "Docker provider support is coming soon!\n"
                f"Original error: {e}"
            )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run Outline benchmarks")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--output-dir", help="Output directory for results")
    args = parser.parse_args()

    try:
        runner = BenchmarkRunner(args.config)

        if args.output_dir:
            runner.results_dir = Path(args.output_dir)
            runner.results_dir.mkdir(exist_ok=True)

        print("🚀 Starting Outline benchmark...")
        results = runner.run_benchmark()

        runner.save_results(results)

        if results.get("status") == "completed":
            print("✅ Benchmark completed successfully!")
            print(f"📊 Results saved to: {runner.results_dir}")
        else:
            print("❌ Benchmark failed!")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️  Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Benchmark failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
