#!/usr/bin/env python3
"""
Example usage of the benchmarking infrastructure

This script demonstrates how to use the BenchmarkRunner class
for custom benchmarking scenarios.
"""

import sys
from pathlib import Path

# Add the scripts directory to Python path
sys.path.append(str(Path(__file__).parent))
from benchmark_runner import BenchmarkRunner


def example_basic_benchmark():
    """Example: Run a basic benchmark with default settings"""
    print("🚀 Running basic benchmark example...")
    
    runner = BenchmarkRunner()
    results = runner.run_benchmark()
    
    if results.get("status") == "completed":
        print("✅ Benchmark completed successfully!")
        
        # Print some basic stats
        snapshots = results.get("snapshots", [])
        if snapshots:
            baseline = snapshots[0]
            if "metrics" in baseline:
                build_time = baseline["metrics"].get("performance", {}).get("build_time_seconds", "N/A")
                memory_mb = round(baseline["metrics"].get("container", {}).get("memory_usage", 0) / 1024 / 1024, 2)
                print(f"📊 Baseline build time: {build_time}s")
                print(f"💾 Baseline memory usage: {memory_mb}MB")
        
        runner.save_results(results)
        print(f"📁 Results saved to: {runner.results_dir}")
    else:
        print("❌ Benchmark failed!")
        if "error" in results:
            print(f"Error: {results['error']}")


def example_custom_config():
    """Example: Run benchmark with custom configuration"""
    print("🔧 Running custom configuration example...")
    
    # Create custom config
    custom_config = {
        "benchmark_iterations": 1,  # Faster for demo
        "trivial_changes": [
            {
                "type": "comment",
                "file": "README.md",
                "content": "# Custom benchmark comment"
            }
        ]
    }
    
    # Save custom config
    config_path = "benchmarks/configs/example.json"
    import json
    with open(config_path, 'w') as f:
        json.dump(custom_config, f, indent=2)
    
    # Run with custom config
    runner = BenchmarkRunner(config_path)
    results = runner.run_benchmark()
    
    if results.get("status") == "completed":
        print("✅ Custom benchmark completed!")
        runner.save_results(results)
    else:
        print("❌ Custom benchmark failed!")


def example_snapshot_only():
    """Example: Take a single snapshot without full benchmark"""
    print("📸 Taking snapshot example...")
    
    runner = BenchmarkRunner()
    
    # Setup container and install Outline
    if runner.setup_container() and runner.clone_and_install_outline():
        # Take a single snapshot
        snapshot = runner.take_snapshot("example_snapshot")
        
        if "metrics" in snapshot:
            print("✅ Snapshot taken successfully!")
            print(f"📊 Snapshot data: {snapshot['name']}")
            
            # Print metrics
            metrics = snapshot["metrics"]
            if "performance" in metrics:
                build_time = metrics["performance"].get("build_time_seconds", "N/A")
                print(f"⏱️  Build time: {build_time}s")
            
            if "filesystem" in metrics:
                package_count = metrics["filesystem"].get("package_count", "N/A")
                print(f"📦 Package count: {package_count}")
        else:
            print("❌ Snapshot failed!")
        
        runner.cleanup()
    else:
        print("❌ Failed to setup environment!")


def main():
    """Main example runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark usage examples")
    parser.add_argument("--basic", action="store_true", help="Run basic benchmark example")
    parser.add_argument("--custom", action="store_true", help="Run custom config example")
    parser.add_argument("--snapshot", action="store_true", help="Run snapshot-only example")
    parser.add_argument("--all", action="store_true", help="Run all examples")
    
    args = parser.parse_args()
    
    if args.all or args.basic:
        example_basic_benchmark()
        print()
    
    if args.all or args.custom:
        example_custom_config()
        print()
    
    if args.all or args.snapshot:
        example_snapshot_only()
        print()
    
    if not any([args.basic, args.custom, args.snapshot, args.all]):
        print("Please specify an example to run:")
        print("  --basic    Run basic benchmark")
        print("  --custom   Run with custom config")
        print("  --snapshot Take single snapshot")
        print("  --all      Run all examples")


if __name__ == "__main__":
    main()

