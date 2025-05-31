#!/usr/bin/env python3
"""
E2B Custom Dockerfile Test Script - Outline Setup with Snapshots

This script demonstrates:
1. Custom Dockerfile creation for Node.js/Outline environment
2. E2B template building and usage
3. Repository cloning with streaming output
4. Dependency installation (yarn install)
5. Trivial edits and snapshot simulation
6. Sandbox lifecycle management with timing

Usage: python test_dockerfile_simple
Requires: E2B_API_KEY environment variable
"""

import asyncio
import os
import sys
import tempfile
import time
from pathlib import Path
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
    print(f"{color}⏱️  {description}: {duration:.3f}s{Colors.NC}")


def print_substep(description: str, color: str = Colors.YELLOW):
    """Print a substep"""
    print(f"{color}  🔸 {description}{Colors.NC}")


async def stream_command_output(sandbox, command: str, description: str) -> float:
    """Execute command and stream output with timing"""
    print_substep(f"Running: {command}")

    start_time = time.time()

    # For now, we'll execute the command normally
    # In a real implementation, you might want to implement streaming
    result = await sandbox.execute(command, timeout=300)

    duration = time.time() - start_time

    if result.stdout:
        print(f"{Colors.WHITE}📤 STDOUT:{Colors.NC}")
        for line in result.stdout.split("\n")[:20]:  # Show first 20 lines
            if line.strip():
                print(f"  {line}")
        if len(result.stdout.split("\n")) > 20:
            print(f"  ... ({len(result.stdout.split('\n')) - 20} more lines)")

    if result.stderr:
        print(f"{Colors.RED}📥 STDERR:{Colors.NC}")
        for line in result.stderr.split("\n")[:10]:  # Show first 10 lines
            if line.strip():
                print(f"  {line}")

    if not result.success:
        print(
            f"{Colors.RED}❌ Command failed with return code: {result.return_code}{Colors.NC}"
        )
    else:
        print(f"{Colors.GREEN}✅ Command completed successfully{Colors.NC}")

    print_timing(description, duration)
    return duration


def create_dockerfile_content() -> str:
    """Create custom Dockerfile content for Outline setup"""
    return """# Custom E2B Dockerfile for Outline development
FROM e2bdev/code-interpreter:latest

# Install Node.js 18 and Yarn
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && \\
    apt-get install -y nodejs

# Install Yarn
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add - && \\
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list && \\
    apt-get update && apt-get install -y yarn

# Install Git (should already be available)
RUN apt-get update && apt-get install -y git

# Install additional development tools
RUN apt-get install -y build-essential python3 make g++

# Set working directory and ensure proper permissions
RUN mkdir -p /home/user/workspace && chown -R user:user /home/user/workspace
WORKDIR /home/user/workspace

# Install common global packages
RUN npm install -g npm@latest

# Set environment variables
ENV NODE_ENV=development
ENV WORKSPACE=/home/user/workspace

# Switch to user for security
USER user
"""


async def create_custom_template() -> Optional[str]:
    """Create custom E2B template with Dockerfile"""
    print_step(1, "Creating Custom E2B Template", Colors.MAGENTA)

    # Create temporary directory for template
    with tempfile.TemporaryDirectory() as temp_dir:
        dockerfile_path = Path(temp_dir) / "e2b.Dockerfile"

        print_substep("Writing custom Dockerfile")
        with open(dockerfile_path, "w") as f:
            f.write(create_dockerfile_content())

        print_substep("Dockerfile created with Node.js 18 + Yarn + Git")
        print(f"📁 Location: {dockerfile_path}")

        # For this demo, we'll use a pre-built template
        # In practice, you'd run: e2b template build --name outline-dev
        # and get back a template ID

        print_substep("Using base template (will create workspace dynamically)")
        print("💡 In practice, run: e2b template build --name outline-dev")

        # Return a placeholder template - in practice this would be your custom template ID
        return "base"  # Use base template for this demo


async def setup_workspace_and_permissions(sandbox) -> float:
    """Set up workspace with proper permissions"""
    print_step(2, "Setting Up Workspace and Permissions", Colors.BLUE)

    # Check current user and create accessible workspace
    setup_duration = await stream_command_output(
        sandbox,
        "whoami && pwd && mkdir -p ~/projects && cd ~/projects && pwd",
        "Workspace setup",
    )

    return setup_duration


async def setup_outline_environment(sandbox, template_id: str) -> dict[str, float]:
    """Set up Outline development environment"""
    timings = {}

    print_step(3, "Setting Up Outline Development Environment", Colors.BLUE)

    # Clone Outline repository to home directory
    print_substep("Cloning Outline repository")
    clone_duration = await stream_command_output(
        sandbox,
        "cd ~/projects && git clone https://github.com/outline/outline.git",
        "Git clone operation",
    )
    timings["clone"] = clone_duration

    # Check repo status
    info_duration = await stream_command_output(
        sandbox,
        "cd ~/projects/outline && ls -la && git log --oneline -5",
        "Repository inspection",
    )
    timings["inspect"] = info_duration

    return timings


async def install_dependencies(sandbox) -> float:
    """Install Outline dependencies with yarn"""
    print_step(4, "Installing Dependencies with Yarn", Colors.CYAN)

    # Check if yarn is available and install dependencies
    install_duration = await stream_command_output(
        sandbox,
        "cd ~/projects/outline && yarn --version && yarn install --frozen-lockfile",
        "Yarn install operation",
    )

    # Verify installation
    verify_duration = await stream_command_output(
        sandbox,
        "cd ~/projects/outline && ls -la node_modules/ | head -10 && yarn list --depth=0 | head -20",
        "Dependency verification",
    )

    return install_duration + verify_duration


async def make_trivial_edit(sandbox) -> float:
    """Make a trivial edit to demonstrate file modification"""
    print_step(5, "Making Trivial Edit", Colors.YELLOW)

    # Create a simple benchmark comment
    edit_duration = await stream_command_output(
        sandbox,
        'cd ~/projects/outline && echo "/* Grainchain E2B benchmark test - $(date) */" >> README.md',
        "Adding benchmark comment",
    )

    # Verify the edit
    verify_duration = await stream_command_output(
        sandbox, "cd ~/projects/outline && tail -3 README.md", "Verifying edit"
    )

    return edit_duration + verify_duration


async def create_snapshot_simulation(sandbox, snapshot_name: str) -> float:
    """Simulate snapshot creation (E2B doesn't support true snapshots)"""
    print_step(6, f"Creating Snapshot Simulation: {snapshot_name}", Colors.MAGENTA)

    # Create a marker file with current state
    snapshot_duration = await stream_command_output(
        sandbox,
        f'cd ~/projects && tar -czf {snapshot_name}_snapshot.tar.gz outline/ && echo "Snapshot {snapshot_name} created at $(date)" > {snapshot_name}_snapshot.log',
        "Creating snapshot archive",
    )

    # Verify snapshot
    verify_duration = await stream_command_output(
        sandbox,
        f"cd ~/projects && ls -lh {snapshot_name}_snapshot.* && cat {snapshot_name}_snapshot.log",
        "Verifying snapshot creation",
    )

    return snapshot_duration + verify_duration


async def main():
    """Main execution flow"""
    start_time = time.time()

    print(f"{Colors.WHITE}{'=' * 80}")
    print("🚀 GRAINCHAIN E2B DOCKERFILE TESTING SUITE")
    print("📦 Testing: Custom Docker Images + Outline Setup + Snapshots")
    print(f"{'=' * 80}{Colors.NC}")

    # Check E2B API key
    if not os.getenv("E2B_API_KEY"):
        print(
            f"{Colors.RED}❌ Error: E2B_API_KEY environment variable not set{Colors.NC}"
        )
        print("💡 Get your API key from: https://e2b.dev/")
        return

    # Create custom template
    template_id = await create_custom_template()
    if not template_id:
        print(f"{Colors.RED}❌ Failed to create custom template{Colors.NC}")
        return

    timings = {}

    try:
        # Configure sandbox with accessible working directory
        config = SandboxConfig(
            timeout=600,  # 10 minutes for yarn install
            working_directory="/home/user",  # Use home directory
            environment_vars={
                "NODE_ENV": "development",
                "YARN_CACHE_FOLDER": "/tmp/yarn-cache",
            },
        )

        # Step 1: Create first sandbox
        print_step(7, "Creating E2B Sandbox", Colors.GREEN)
        creation_start = time.time()

        # Use base template
        async with Sandbox(provider="e2b", config=config) as sandbox:
            creation_duration = time.time() - creation_start
            timings["sandbox_creation"] = creation_duration
            print_timing("Sandbox creation", creation_duration)

            # Verify environment
            env_duration = await stream_command_output(
                sandbox,
                "node --version && npm --version && yarn --version && git --version",
                "Environment verification",
            )
            timings["env_check"] = env_duration

            # Setup workspace with proper permissions
            workspace_duration = await setup_workspace_and_permissions(sandbox)
            timings["workspace_setup"] = workspace_duration

            # Setup Outline environment
            setup_timings = await setup_outline_environment(sandbox, template_id)
            timings.update(setup_timings)

            # Install dependencies
            install_duration = await install_dependencies(sandbox)
            timings["install"] = install_duration

            # Make trivial edit
            edit_duration = await make_trivial_edit(sandbox)
            timings["edit"] = edit_duration

            # Create snapshot simulation
            snapshot_duration = await create_snapshot_simulation(
                sandbox, "outline_configured"
            )
            timings["snapshot"] = snapshot_duration

            print_step(8, "Killing First Sandbox", Colors.RED)
            print_substep("Sandbox will be destroyed when context exits")

        # Step 2: Create new sandbox from "snapshot"
        print_step(9, "Creating New Sandbox from 'Snapshot'", Colors.GREEN)

        restore_start = time.time()
        async with Sandbox(provider="e2b", config=config) as new_sandbox:
            restore_duration = time.time() - restore_start
            timings["sandbox_restore"] = restore_duration
            print_timing("New sandbox creation", restore_duration)

            # Simulate snapshot restoration
            print_substep("Simulating snapshot restoration")

            # In a real scenario, you'd have persistent storage or
            # a custom template with the pre-configured environment
            restore_sim_duration = await stream_command_output(
                new_sandbox,
                "echo 'In practice, this would restore from persistent storage or use a pre-configured template' && mkdir -p ~/projects",
                "Snapshot restoration simulation",
            )
            timings["restore_simulation"] = restore_sim_duration

            # Verify new environment
            verify_duration = await stream_command_output(
                new_sandbox,
                "whoami && pwd && ls -la ~/projects/",
                "New sandbox verification",
            )
            timings["verification"] = verify_duration

    except Exception as e:
        print(f"{Colors.RED}❌ Error during execution: {e}{Colors.NC}")
        import traceback

        traceback.print_exc()
        return

    # Final summary
    total_duration = time.time() - start_time

    print_step(10, "EXECUTION SUMMARY", Colors.WHITE)

    print(f"{Colors.CYAN}📊 DETAILED TIMINGS:{Colors.NC}")
    for operation, duration in timings.items():
        print(f"  {operation.replace('_', ' ').title()}: {duration:.3f}s")

    print(f"\n{Colors.GREEN}🎯 TOTAL EXECUTION TIME: {total_duration:.3f}s{Colors.NC}")

    print(f"\n{Colors.YELLOW}💡 KEY INSIGHTS:{Colors.NC}")
    print("  • E2B supports custom Docker images via e2b.Dockerfile")
    print("  • Template building happens via E2B CLI: e2b template build")
    print("  • Snapshots need simulation - consider persistent storage")
    print("  • Custom templates enable pre-configured development environments")
    print("  • Permission management is crucial for workspace setup")

    print(f"\n{Colors.MAGENTA}🚀 NEXT STEPS:{Colors.NC}")
    print("  1. Create actual custom template: e2b template build --name outline-dev")
    print("  2. Use template ID in sandbox configuration")
    print("  3. Implement persistent storage for true snapshot functionality")
    print("  4. Consider pre-building templates with common dependencies")
    print("  5. Optimize permissions and workspace setup in custom Dockerfile")

    print(
        f"\n{Colors.WHITE}✨ Grainchain E2B Dockerfile test completed successfully!{Colors.NC}"
    )


if __name__ == "__main__":
    asyncio.run(main())
