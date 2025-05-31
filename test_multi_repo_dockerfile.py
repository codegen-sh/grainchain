#!/usr/bin/env python3
"""
E2B Custom Dockerfile Test Script - Multi-Repository Setup with Snapshots

This script demonstrates:
1. Custom Dockerfile creation for multiple language environments
2. E2B template building and usage
3. Repository cloning with streaming output for multiple repos
4. Dependency installation for different package managers
5. Trivial edits and snapshot simulation across repositories
6. Sandbox lifecycle management with timing

Usage: python test_multi_repo_dockerfile.py [--repo REPO_NAME]
Requires: E2B_API_KEY environment variable
"""

import asyncio
import json
import os
import sys
import tempfile
import time
from typing import Optional

try:
    from grainchain import Sandbox, SandboxConfig
except ImportError:
    print("❌ Error: grainchain not installed. Run: pip install grainchain[e2b]")
    sys.exit(1)


# ANSI color codes for pretty output
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    MAGENTA = "\033[0;35m"
    CYAN = "\033[0;36m"
    WHITE = "\033[1;37m"
    NC = "\033[0m"  # No Color


def print_step(step_num: int, description: str, color: str = Colors.CYAN):
    """Print a colored step header"""
    print(f"\n{color}{'=' * 60}")
    print(f"🔥 STEP {step_num}: {description}")
    print(f"{'=' * 60}{Colors.NC}")


def print_timing(description: str, duration: float, color: str = Colors.GREEN):
    """Print timing information"""
    print(f"{color}⏱️  {description}: {duration:.2f}s{Colors.NC}")


def print_substep(description: str, color: str = Colors.YELLOW):
    """Print a substep"""
    print(f"{color}  📌 {description}{Colors.NC}")


async def stream_command_output(sandbox, command: str, description: str) -> float:
    """Execute command and stream output with timing"""
    print_substep(f"{description}...")
    start_time = time.time()

    try:
        # Execute command and capture output
        result = await sandbox.run_command(command)
        duration = time.time() - start_time

        if result.exit_code == 0:
            print(f"{Colors.GREEN}✅ {description} completed{Colors.NC}")
            # Print last few lines of output for verification
            if result.stdout:
                lines = result.stdout.strip().split("\n")
                for line in lines[-3:]:  # Show last 3 lines
                    print(f"   {line}")
        else:
            print(
                f"{Colors.RED}❌ {description} failed (exit code: {result.exit_code}){Colors.NC}"
            )
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}...")

        return duration
    except Exception as e:
        duration = time.time() - start_time
        print(f"{Colors.RED}❌ {description} failed: {e}{Colors.NC}")
        return duration


def create_dockerfile_content() -> str:
    """Create Dockerfile content for multi-language support"""
    return """
FROM ghcr.io/openai/codex-universal:latest

# Install additional dependencies for multi-language support
RUN apt-get update && apt-get install -y \\
    curl \\
    git \\
    build-essential \\
    python3-dev \\
    python3-pip \\
    python3-venv \\
    nodejs \\
    npm \\
    yarn \\
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
RUN python3 -m pip install --upgrade pip setuptools wheel

# Set up Node.js environment
RUN npm install -g yarn

# Create workspace directory
RUN mkdir -p /workspace/projects
WORKDIR /workspace

# Set environment variables
ENV PYTHONPATH=/workspace
ENV NODE_ENV=development

# Default command
CMD ["bash"]
"""


async def create_custom_template() -> Optional[str]:
    """Create a custom E2B template (simulation)"""
    print_substep("Creating custom Dockerfile...")

    # Create temporary dockerfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".dockerfile", delete=False) as f:
        f.write(create_dockerfile_content())
        dockerfile_path = f.name

    try:
        print(f"📄 Dockerfile created at: {dockerfile_path}")
        print("📝 Dockerfile content preview:")
        with open(dockerfile_path) as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:10], 1):  # Show first 10 lines
                print(f"   {i:2d}: {line.rstrip()}")
            if len(lines) > 10:
                print(f"   ... ({len(lines) - 10} more lines)")

        # In practice, you'd run: e2b template build --name multi-repo-dev
        template_id = "multi-repo-dev-template"
        print("💡 In practice, run: e2b template build --name multi-repo-dev")
        print(f"🎯 Using simulated template ID: {template_id}")

        return template_id
    finally:
        # Clean up temporary file
        os.unlink(dockerfile_path)


async def setup_workspace_and_permissions(sandbox) -> float:
    """Set up workspace and permissions"""
    return await stream_command_output(
        sandbox,
        "mkdir -p ~/projects && chmod 755 ~/projects && ls -la ~",
        "Setting up workspace",
    )


def load_repo_config(repo_name: str) -> dict:
    """Load repository configuration"""
    config_path = f"benchmarks/configs/{repo_name}.json"
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration not found: {config_path}")

    with open(config_path) as f:
        return json.load(f)


async def setup_repository_environment(sandbox, repo_config: dict) -> dict[str, float]:
    """Set up environment for a specific repository"""
    repo_name = repo_config["repo_name"]
    timings = {}

    print_substep(f"Setting up {repo_name} environment...")

    # Clone repository
    clone_cmd = f"cd ~/projects && git clone {repo_config['repo_url']} {repo_name}"
    timings["clone"] = await stream_command_output(
        sandbox, clone_cmd, f"Cloning {repo_name} repository"
    )

    # Verify clone and show repo info
    verify_cmd = f"cd ~/projects/{repo_name} && ls -la && git log --oneline -5"
    timings["verify"] = await stream_command_output(
        sandbox, verify_cmd, f"Verifying {repo_name} clone"
    )

    return timings


async def install_dependencies(sandbox, repo_config: dict) -> float:
    """Install dependencies for the repository"""
    repo_name = repo_config["repo_name"]
    install_cmd = repo_config["install_command"]

    # Set up environment variables based on language
    env_setup = ""
    if repo_config.get("language") == "python":
        env_setup = "export PYTHONPATH=$PWD && "
    elif repo_config.get("language") == "typescript":
        env_setup = "export NODE_ENV=development && "

    full_cmd = f"cd ~/projects/{repo_name} && {env_setup}{install_cmd}"

    return await stream_command_output(
        sandbox, full_cmd, f"Installing {repo_name} dependencies"
    )


async def verify_installation(sandbox, repo_config: dict) -> float:
    """Verify the installation was successful"""
    repo_name = repo_config["repo_name"]

    if repo_config.get("language") == "python":
        verify_cmd = f"cd ~/projects/{repo_name} && python3 -c 'import sys; print(sys.path)' && ls -la"
    elif repo_config.get("language") == "typescript":
        verify_cmd = f"cd ~/projects/{repo_name} && ls -la node_modules/ | head -10 && yarn list --depth=0 | head -20"
    else:
        verify_cmd = f"cd ~/projects/{repo_name} && ls -la"

    return await stream_command_output(
        sandbox, verify_cmd, f"Verifying {repo_name} installation"
    )


async def make_trivial_edit(sandbox, repo_config: dict) -> float:
    """Make a trivial edit to test snapshot functionality"""
    repo_name = repo_config["repo_name"]

    # Use the first trivial change from config
    changes = repo_config.get("trivial_changes", [])
    if not changes:
        print_substep(f"No trivial changes configured for {repo_name}")
        return 0.0

    change = changes[0]  # Use first change
    edit_cmd = (
        f'cd ~/projects/{repo_name} && echo "{change["content"]}" >> {change["file"]}'
    )

    return await stream_command_output(
        sandbox, edit_cmd, f"Making trivial edit to {repo_name}"
    )


async def verify_edit(sandbox, repo_config: dict) -> float:
    """Verify the edit was applied"""
    repo_name = repo_config["repo_name"]
    changes = repo_config.get("trivial_changes", [])

    if not changes:
        return 0.0

    change = changes[0]
    verify_cmd = f"cd ~/projects/{repo_name} && tail -3 {change['file']}"

    return await stream_command_output(
        sandbox, verify_cmd, f"Verifying {repo_name} edit"
    )


async def create_snapshot_simulation(
    sandbox, repo_config: dict, snapshot_name: str
) -> float:
    """Simulate creating a snapshot"""
    repo_name = repo_config["repo_name"]

    snapshot_cmd = (
        f"cd ~/projects && tar -czf {snapshot_name}_{repo_name}_snapshot.tar.gz {repo_name}/ && "
        f'echo "Snapshot {snapshot_name}_{repo_name} created at $(date)" > {snapshot_name}_{repo_name}_snapshot.log'
    )

    return await stream_command_output(
        sandbox, snapshot_cmd, f"Creating {snapshot_name} snapshot for {repo_name}"
    )


async def run_tests(sandbox, repo_config: dict) -> float:
    """Run tests for the repository"""
    repo_name = repo_config["repo_name"]
    test_cmd = repo_config.get("test_command", "echo 'No tests configured'")

    full_cmd = f"cd ~/projects/{repo_name} && timeout 30s {test_cmd} || echo 'Tests completed or timed out'"

    return await stream_command_output(sandbox, full_cmd, f"Running {repo_name} tests")


async def benchmark_repository(
    sandbox, repo_name: str, template_id: str
) -> dict[str, float]:
    """Run complete benchmark for a single repository"""
    print_step(0, f"Benchmarking {repo_name.upper()}", Colors.MAGENTA)

    try:
        # Load repository configuration
        repo_config = load_repo_config(repo_name)
        print(f"📋 Loaded config for {repo_name}: {repo_config['repo_url']}")

        # Setup repository environment
        setup_timings = await setup_repository_environment(sandbox, repo_config)

        # Install dependencies
        install_time = await install_dependencies(sandbox, repo_config)

        # Verify installation
        verify_time = await verify_installation(sandbox, repo_config)

        # Take initial snapshot
        initial_snapshot_time = await create_snapshot_simulation(
            sandbox, repo_config, "initial"
        )

        # Make trivial edit
        edit_time = await make_trivial_edit(sandbox, repo_config)

        # Verify edit
        verify_edit_time = await verify_edit(sandbox, repo_config)

        # Take post-edit snapshot
        post_edit_snapshot_time = await create_snapshot_simulation(
            sandbox, repo_config, "post_edit"
        )

        # Run tests
        test_time = await run_tests(sandbox, repo_config)

        # Collect all timings
        all_timings = {
            **setup_timings,
            "install": install_time,
            "verify": verify_time,
            "initial_snapshot": initial_snapshot_time,
            "edit": edit_time,
            "verify_edit": verify_edit_time,
            "post_edit_snapshot": post_edit_snapshot_time,
            "tests": test_time,
        }

        return all_timings

    except Exception as e:
        print(f"{Colors.RED}❌ Failed to benchmark {repo_name}: {e}{Colors.NC}")
        return {"error": str(e)}


async def main():
    """Main function to orchestrate the multi-repo testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Test multi-repository Docker setup")
    parser.add_argument("--repo", help="Test specific repository only")
    args = parser.parse_args()

    # Check for E2B API key
    if not os.getenv("E2B_API_KEY"):
        print("❌ E2B_API_KEY environment variable not set")
        print("   Get your API key from: https://e2b.dev/dashboard")
        sys.exit(1)

    print(f"{Colors.WHITE}🚀 Multi-Repository E2B Dockerfile Test{Colors.NC}")
    print("   Testing grainchain integration with multiple repositories")

    # Determine which repositories to test
    available_repos = ["outline", "requests", "fastapi"]
    if args.repo:
        if args.repo not in available_repos:
            print(
                f"❌ Repository '{args.repo}' not found. Available: {available_repos}"
            )
            sys.exit(1)
        repos_to_test = [args.repo]
    else:
        repos_to_test = available_repos

    print(f"📋 Testing repositories: {repos_to_test}")

    total_start_time = time.time()
    all_results = {}

    try:
        # Step 1: Create custom template
        print_step(1, "Creating Custom Template", Colors.BLUE)
        template_id = await create_custom_template()

        # Step 2: Initialize sandbox
        print_step(2, "Initializing Sandbox", Colors.BLUE)
        print_substep("Creating sandbox with custom template...")

        config = SandboxConfig(
            template="e2b-code",  # Using default template for now
            timeout=300,  # 5 minutes
        )

        async with Sandbox(config) as sandbox:
            print(f"{Colors.GREEN}✅ Sandbox created successfully{Colors.NC}")

            # Step 3: Setup workspace
            print_step(3, "Setting Up Workspace", Colors.BLUE)
            workspace_time = await setup_workspace_and_permissions(sandbox)
            print_timing("Workspace setup", workspace_time)

            # Step 4: Test each repository
            for i, repo_name in enumerate(repos_to_test, 4):
                print_step(i, f"Testing {repo_name.upper()}", Colors.CYAN)
                repo_timings = await benchmark_repository(
                    sandbox, repo_name, template_id
                )
                all_results[repo_name] = repo_timings

                # Print repository summary
                if "error" not in repo_timings:
                    total_time = sum(repo_timings.values())
                    print_timing(
                        f"Total {repo_name} benchmark", total_time, Colors.MAGENTA
                    )
                else:
                    print(f"{Colors.RED}❌ {repo_name} benchmark failed{Colors.NC}")

    except Exception as e:
        print(f"{Colors.RED}❌ Test failed: {e}{Colors.NC}")
        sys.exit(1)

    # Final summary
    total_duration = time.time() - total_start_time
    print_step(len(repos_to_test) + 4, "Test Summary", Colors.GREEN)

    successful_repos = [
        repo for repo, results in all_results.items() if "error" not in results
    ]
    failed_repos = [repo for repo, results in all_results.items() if "error" in results]

    print("📊 Results:")
    print(f"   Total repositories tested: {len(repos_to_test)}")
    print(f"   Successful: {len(successful_repos)} {successful_repos}")
    print(f"   Failed: {len(failed_repos)} {failed_repos}")
    print_timing("Total test duration", total_duration, Colors.WHITE)

    print(f"\n{Colors.CYAN}🎯 Next Steps:{Colors.NC}")
    print(
        "  1. Create actual custom template: e2b template build --name multi-repo-dev"
    )
    print(
        "  2. Run production benchmarks with: python benchmarks/scripts/multi_repo_benchmark_runner.py"
    )
    print("  3. Analyze results in benchmarks/results/")

    if failed_repos:
        print(
            f"\n{Colors.YELLOW}⚠️  Some repositories failed. Check configurations in benchmarks/configs/{Colors.NC}"
        )


if __name__ == "__main__":
    asyncio.run(main())
