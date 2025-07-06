#!/usr/bin/env python3
"""
Automated benchmark execution and result publishing script

This script:
1. Runs the benchmark suite
2. Commits results to the repository
3. Can be scheduled to run periodically
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add the scripts directory to Python path
sys.path.append(str(Path(__file__).parent))


class AutoPublisher:
    """Handles automated benchmark execution and publishing"""

    def __init__(self):
        self.repo_root = Path(__file__).parent.parent.parent
        self.results_dir = self.repo_root / "benchmarks" / "results"

        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def run_benchmark_and_publish(self) -> bool:
        """Run benchmark and publish results"""
        try:
            # Run the grainchain benchmark instead of Docker-based benchmark
            self.logger.info("Starting automated grainchain benchmark run...")

            import subprocess
            import sys

            # Run the grainchain benchmark script
            result = subprocess.run(
                [
                    sys.executable,
                    "benchmarks/scripts/grainchain_benchmark.py",
                    "--providers",
                    "local",
                    "--iterations",
                    "3",
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
            )

            if result.returncode != 0:
                self.logger.error(f"Grainchain benchmark failed: {result.stderr}")
                return False

            self.logger.info("Grainchain benchmark completed successfully")

            # Commit and push results
            return self._commit_and_push_results()

        except Exception as e:
            self.logger.error(f"Failed to run benchmark and publish: {e}")
            return False

    def _commit_and_push_results(self) -> bool:
        """Commit and push benchmark results to repository"""
        try:
            os.chdir(self.repo_root)

            # Configure git if needed
            subprocess.run(["git", "config", "user.name", "Benchmark Bot"], check=True)
            subprocess.run(
                ["git", "config", "user.email", "benchmark@grainchain.dev"], check=True
            )

            # Add results files
            subprocess.run(["git", "add", "benchmarks/results/"], check=True)

            # Check if there are changes to commit
            result = subprocess.run(
                ["git", "diff", "--cached", "--quiet"], capture_output=True
            )
            if result.returncode == 0:
                self.logger.info("No new benchmark results to commit")
                return True

            # Commit results
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"📊 Automated benchmark results - {timestamp}"
            subprocess.run(["git", "commit", "-m", commit_message], check=True)

            # Push to remote (if configured)
            try:
                subprocess.run(["git", "push"], check=True)
                self.logger.info("Successfully pushed benchmark results")
            except subprocess.CalledProcessError:
                self.logger.warning("Failed to push results (no remote configured?)")

            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git operation failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to commit results: {e}")
            return False

    def generate_summary_report(self) -> None:
        """Generate a summary report from all historical results"""
        try:
            # Find all grainchain result files
            result_files = list(self.results_dir.glob("grainchain_benchmark_*.json"))
            result_files.sort()

            if not result_files:
                self.logger.warning("No grainchain benchmark results found")
                return

            # Load all results
            all_results = []
            for file_path in result_files:
                try:
                    with open(file_path) as f:
                        data = json.load(f)
                        all_results.append(data)
                except Exception as e:
                    self.logger.warning(f"Failed to load {file_path}: {e}")

            # Generate summary markdown
            summary_md = self._generate_grainchain_summary_markdown(all_results)

            # Save summary
            summary_file = self.results_dir / "SUMMARY.md"
            with open(summary_file, "w") as f:
                f.write(summary_md)

            self.logger.info(f"Summary report generated: {summary_file}")

        except Exception as e:
            self.logger.error(f"Failed to generate summary report: {e}")

    def _generate_grainchain_summary_markdown(self, results: list) -> str:
        """Generate summary markdown from grainchain benchmark results"""
        md_content = f"""# Grainchain Benchmark Summary

**Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Benchmark Runs:** {len(results)}

## Recent Results

| Date | Status | Success Rate | Avg Time (s) | Providers | Notes |
|------|--------|--------------|--------------|-----------|-------|
"""

        # Show last 10 results
        recent_results = results[-10:] if len(results) > 10 else results

        for result in reversed(recent_results):
            # Extract date from benchmark_info
            start_time = result.get("benchmark_info", {}).get("start_time", "Unknown")
            date = start_time[:10] if start_time != "Unknown" else "Unknown"

            status = "✅" if result.get("status") == "completed" else "❌"

            # Calculate overall success rate and average time
            provider_results = result.get("provider_results", {})
            success_rates = []
            avg_times = []
            providers = []

            for provider, provider_data in provider_results.items():
                providers.append(provider)
                if provider_data.get("status") == "completed":
                    overall_metrics = provider_data.get("overall_metrics", {})
                    success_rate = overall_metrics.get("overall_success_rate", 0)
                    avg_time = overall_metrics.get("avg_scenario_time", 0)
                    success_rates.append(success_rate)
                    avg_times.append(avg_time)

            overall_success = (
                round((sum(success_rates) / len(success_rates)) * 100, 1)
                if success_rates
                else 0
            )
            overall_avg_time = (
                round(sum(avg_times) / len(avg_times), 2) if avg_times else 0
            )
            providers_str = ", ".join(providers) if providers else "None"

            notes = "Failed" if result.get("status") != "completed" else "OK"

            md_content += f"| {date} | {status} | {overall_success}% | {overall_avg_time} | {providers_str} | {notes} |\n"

        md_content += """
## Configuration

The benchmarks use the following configuration:
- **Providers:** Local, E2B, Modal, Daytona, Morph (when available)
- **Test Scenarios:** Basic commands, Python execution, File operations, Computational tasks, Snapshot lifecycle
- **Default Iterations:** 3
- **Timeout:** 30 seconds per scenario

## Metrics Collected

- **Sandbox Creation Time:** Time to create a new sandbox
- **Command Execution Time:** Time to execute individual commands
- **Success Rate:** Percentage of successful operations
- **File Operations:** Upload/download performance
- **Snapshot Lifecycle:** Git clone, snapshot creation, and restoration

## Test Scenarios

1. **Basic Commands:** Shell commands (echo, pwd, ls, whoami, date)
2. **Python Execution:** Python script execution and version checks
3. **File Operations:** File upload/download with various sizes
4. **Computational Tasks:** CPU-intensive Python operations
5. **Snapshot Lifecycle:** Git clone, file creation, snapshot, kill, and restore

## Automation

This summary is automatically updated when new benchmark results are available.
Results are committed to the repository for historical tracking.
"""

        return md_content


def main():
    """Main entry point for automated publishing"""
    import argparse

    parser = argparse.ArgumentParser(description="Automated benchmark publishing")
    parser.add_argument(
        "--run-benchmark", action="store_true", help="Run benchmark and publish results"
    )
    parser.add_argument(
        "--generate-summary", action="store_true", help="Generate summary report only"
    )
    args = parser.parse_args()

    publisher = AutoPublisher()

    if args.run_benchmark:
        success = publisher.run_benchmark_and_publish()
        if not success:
            sys.exit(1)

    if args.generate_summary or not args.run_benchmark:
        publisher.generate_summary_report()

    print("✅ Automated publishing completed!")


if __name__ == "__main__":
    main()
