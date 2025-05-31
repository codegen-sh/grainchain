#!/usr/bin/env python3
"""
Test runner script for Grainchain.

This script provides convenient commands for running different types of tests
and generating coverage reports.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors."""
    if description:
        print(f"\n🔄 {description}")
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        return False
    else:
        print(f"✅ {description or 'Command'} completed successfully")
        return True


def main():
    parser = argparse.ArgumentParser(description="Run Grainchain tests")
    parser.add_argument(
        "test_type",
        choices=["unit", "integration", "all", "e2b", "modal", "local", "coverage"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run tests in parallel"
    )
    parser.add_argument(
        "--no-cov",
        action="store_true",
        help="Disable coverage reporting"
    )
    parser.add_argument(
        "--html-cov",
        action="store_true",
        help="Generate HTML coverage report"
    )
    parser.add_argument(
        "--fail-fast", "-x",
        action="store_true",
        help="Stop on first failure"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Add fail-fast
    if args.fail_fast:
        cmd.append("-x")
    
    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", "auto"])
    
    # Configure coverage
    if not args.no_cov:
        cmd.extend([
            "--cov=grainchain",
            "--cov-report=term-missing"
        ])
        
        if args.html_cov:
            cmd.append("--cov-report=html")
    
    # Configure test selection based on type
    if args.test_type == "unit":
        cmd.extend(["-m", "not integration", "tests/unit/"])
        description = "Running unit tests"
    
    elif args.test_type == "integration":
        cmd.extend(["-m", "integration", "tests/integration/"])
        description = "Running integration tests"
    
    elif args.test_type == "e2b":
        cmd.extend(["-m", "e2b", "tests/integration/test_e2b_provider.py"])
        description = "Running E2B integration tests"
        
        # Check for E2B credentials
        if not os.getenv("E2B_API_KEY"):
            print("⚠️  Warning: E2B_API_KEY not set. E2B tests will be skipped.")
    
    elif args.test_type == "modal":
        cmd.extend(["-m", "modal", "tests/integration/test_modal_provider.py"])
        description = "Running Modal integration tests"
        
        # Check for Modal credentials
        if not (os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET")):
            print("⚠️  Warning: MODAL_TOKEN_ID and MODAL_TOKEN_SECRET not set. Modal tests will be skipped.")
    
    elif args.test_type == "local":
        cmd.append("tests/integration/test_local_provider.py")
        description = "Running Local provider integration tests"
    
    elif args.test_type == "all":
        cmd.append("tests/")
        description = "Running all tests"
    
    elif args.test_type == "coverage":
        # Run all tests with detailed coverage
        cmd.extend([
            "--cov=grainchain",
            "--cov-report=term-missing",
            "--cov-report=html",
            "--cov-report=xml",
            "--cov-fail-under=90",
            "tests/"
        ])
        description = "Running all tests with coverage analysis"
    
    # Run the tests
    success = run_command(cmd, description)
    
    if args.test_type == "coverage" or args.html_cov:
        if Path("htmlcov/index.html").exists():
            print(f"\n📊 HTML coverage report generated: htmlcov/index.html")
    
    # Print summary
    if success:
        print(f"\n🎉 {description} completed successfully!")
        
        if args.test_type in ["all", "coverage"]:
            print("\n📋 Test Summary:")
            print("  ✅ Unit tests: Core functionality")
            print("  ✅ Integration tests: Real provider interactions")
            print("  📊 Coverage report: Available in htmlcov/")
            
            print("\n🔧 To run specific test types:")
            print("  python run_tests.py unit          # Unit tests only")
            print("  python run_tests.py integration   # Integration tests only")
            print("  python run_tests.py e2b           # E2B provider tests")
            print("  python run_tests.py modal         # Modal provider tests")
            print("  python run_tests.py local         # Local provider tests")
    else:
        print(f"\n❌ {description} failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

