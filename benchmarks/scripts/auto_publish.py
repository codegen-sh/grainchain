#!/usr/bin/env python3
"""
Automated benchmark execution and result publishing script

This script:
1. Runs the benchmark suite
2. Commits results to the repository
3. Can be scheduled to run periodically
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
import logging

# Add the scripts directory to Python path
sys.path.append(str(Path(__file__).parent))
from benchmark_runner import BenchmarkRunner


class AutoPublisher:
    """Handles automated benchmark execution and publishing"""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent.parent
        self.results_dir = self.repo_root / "benchmarks" / "results"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def run_benchmark_and_publish(self) -> bool:
        """Run benchmark and publish results"""
        try:
            # Run the benchmark
            self.logger.info("Starting automated benchmark run...")
            runner = BenchmarkRunner()
            results = runner.run_benchmark()
            
            if results.get("status") != "completed":
                self.logger.error("Benchmark failed, not publishing results")
                return False
            
            # Save results
            runner.save_results(results)
            
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
            subprocess.run(["git", "config", "user.email", "benchmark@grainchain.dev"], check=True)
            
            # Add results files
            subprocess.run(["git", "add", "benchmarks/results/"], check=True)
            
            # Check if there are changes to commit
            result = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
            if result.returncode == 0:
                self.logger.info("No new benchmark results to commit")
                return True
            
            # Commit results
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
            # Find all result files
            result_files = list(self.results_dir.glob("benchmark_*.json"))
            result_files.sort()
            
            if not result_files:
                self.logger.warning("No benchmark results found")
                return
            
            # Load all results
            all_results = []
            for file_path in result_files:
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        all_results.append(data)
                except Exception as e:
                    self.logger.warning(f"Failed to load {file_path}: {e}")
            
            # Generate summary markdown
            summary_md = self._generate_summary_markdown(all_results)
            
            # Save summary
            summary_file = self.results_dir / "SUMMARY.md"
            with open(summary_file, 'w') as f:
                f.write(summary_md)
            
            self.logger.info(f"Summary report generated: {summary_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary report: {e}")
    
    def _generate_summary_markdown(self, results: list) -> str:
        """Generate summary markdown from all results"""
        md_content = f"""# Outline Benchmark Summary

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Benchmark Runs:** {len(results)}

## Recent Results

| Date | Status | Avg Build Time (s) | Avg Memory (MB) | Notes |
|------|--------|-------------------|-----------------|-------|
"""
        
        # Show last 10 results
        recent_results = results[-10:] if len(results) > 10 else results
        
        for result in reversed(recent_results):
            date = result.get("start_time", "Unknown")[:10]  # Extract date part
            status = "✅" if result.get("status") == "completed" else "❌"
            
            # Calculate averages
            snapshots = result.get("snapshots", [])
            build_times = []
            memory_usages = []
            
            for snapshot in snapshots:
                if "metrics" in snapshot and "performance" in snapshot["metrics"]:
                    build_time = snapshot["metrics"]["performance"].get("build_time_seconds")
                    if build_time and isinstance(build_time, (int, float)):
                        build_times.append(build_time)
                
                if "metrics" in snapshot and "container" in snapshot["metrics"]:
                    memory = snapshot["metrics"]["container"].get("memory_usage")
                    if memory and isinstance(memory, (int, float)):
                        memory_usages.append(memory / 1024 / 1024)  # Convert to MB
            
            avg_build = round(sum(build_times) / len(build_times), 2) if build_times else "N/A"
            avg_memory = round(sum(memory_usages) / len(memory_usages), 2) if memory_usages else "N/A"
            
            notes = "Failed" if result.get("status") != "completed" else "OK"
            
            md_content += f"| {date} | {status} | {avg_build} | {avg_memory} | {notes} |\n"
        
        md_content += f"""
## Configuration

The benchmarks use the following configuration:
- **Base Image:** `ghcr.io/openai/codex-universal:latest`
- **Node Version:** 20
- **Benchmark Iterations:** 3
- **Trivial Changes:** Comment addition, whitespace, log statements

## Metrics Collected

- **Build Time:** Time to run `yarn build`
- **Memory Usage:** Container memory consumption
- **File System:** Package count and directory sizes
- **Test Time:** Time to run test suite

## Automation

This summary is automatically updated when new benchmark results are available.
Results are committed to the repository for historical tracking.
"""
        
        return md_content


def main():
    """Main entry point for automated publishing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automated benchmark publishing")
    parser.add_argument("--run-benchmark", action="store_true", help="Run benchmark and publish results")
    parser.add_argument("--generate-summary", action="store_true", help="Generate summary report only")
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

