#!/usr/bin/env python3
"""
E2B Snapshot Testing Script with Codegen Environment - Outline Setup

This script demonstrates:
1. Custom E2B template based on codegen.Dockerfile with modern tooling
2. Node.js 22, uv, comprehensive development environment
3. Repository cloning with streaming output
4. Dependency installation (yarn install)
5. Trivial edits and snapshot simulation
6. Sandbox lifecycle management with timing

Usage: python test_snapshot_simple.py
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

    # Execute command with extended timeout for complex operations
    result = await sandbox.execute(command, timeout=600)

    duration = time.time() - start_time

    if result.stdout:
        print(f"{Colors.WHITE}📤 STDOUT:{Colors.NC}")
        lines = result.stdout.split("\n")
        # Show first 15 and last 5 lines for better insight
        for line in lines[:15]:
            if line.strip():
                print(f"  {line}")
        if len(lines) > 20:
            print(f"  ... ({len(lines) - 20} more lines)")
            for line in lines[-5:]:
                if line.strip():
                    print(f"  {line}")

    if result.stderr:
        print(f"{Colors.RED}📥 STDERR:{Colors.NC}")
        for line in result.stderr.split("\n")[:10]:
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


def create_codegen_e2b_dockerfile() -> str:
    """Create E2B-compatible Dockerfile based on codegen.Dockerfile with modern tooling"""
    return """# E2B Codegen Development Environment
# Based on codegen.Dockerfile with Node.js 20, uv, and comprehensive dev tools
FROM e2bdev/code-interpreter:latest

# Set environment variables to prevent interactive prompts
ENV NVM_DIR=/home/user/.nvm \
    NODE_VERSION=20.18.0 \
    DEBIAN_FRONTEND=noninteractive \
    NODE_OPTIONS="--max-old-space-size=8192" \
    PYTHONUNBUFFERED=1 \
    COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
    IS_SANDBOX=true \
    NPM_CONFIG_YES=true \
    PIP_NO_INPUT=1 \
    YARN_ENABLE_IMMUTABLE_INSTALLS=false

# Install system dependencies and development tools
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    python3 \
    python3-pip \
    make \
    g++ \
    fd-find \
    ripgrep \
    lsof \
    tmux \
    nano \
    vim \
    htop \
    tree \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc

# Switch to user for remaining setup
USER user
WORKDIR /home/user

# Install NVM and Node.js 20
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash && \
    export NVM_DIR="$HOME/.nvm" && \
    [ -s "$NVM_DIR/nvm.sh" ] && \\. "$NVM_DIR/nvm.sh" && \
    nvm install $NODE_VERSION && \
    nvm use $NODE_VERSION && \
    nvm alias default $NODE_VERSION

# Install modern Node.js tooling
RUN export NVM_DIR="$HOME/.nvm" && \
    [ -s "$NVM_DIR/nvm.sh" ] && \\. "$NVM_DIR/nvm.sh" && \
    npm install -g \
        npm@latest \
        yarn@latest \
        pnpm@latest \
        typescript \
        ts-node \
        nodemon \
        prettier \
        eslint \
    && corepack enable \
    && corepack prepare yarn@stable --activate \
    && corepack prepare pnpm@latest --activate

# Set up environment for interactive shells
RUN echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.bashrc && \
    echo '[ -s "$NVM_DIR/nvm.sh" ] && \\. "$NVM_DIR/nvm.sh"' >> ~/.bashrc && \
    echo '[ -s "$NVM_DIR/bash_completion" ] && \\. "$NVM_DIR/bash_completion"' >> ~/.bashrc && \
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc && \
    echo 'export NODE_OPTIONS="--max-old-space-size=8192"' >> ~/.bashrc

# Create workspace directory
RUN mkdir -p /home/user/projects

# Set working directory
WORKDIR /home/user/projects

# Verify installation
RUN export NVM_DIR="$HOME/.nvm" && \
    [ -s "$NVM_DIR/nvm.sh" ] && \\. "$NVM_DIR/nvm.sh" && \
    echo "=== Codegen E2B Environment Ready ===" && \
    node --version && \
    npm --version && \
    yarn --version && \
    pnpm --version && \
    python3 --version && \
    echo "Environment setup complete!"
"""


async def create_custom_template() -> Optional[str]:
    """Create custom E2B template with Codegen Dockerfile"""
    print_step(1, "Creating Codegen-Based E2B Template", Colors.MAGENTA)

    # Create temporary directory for template
    with tempfile.TemporaryDirectory() as temp_dir:
        dockerfile_path = Path(temp_dir) / "e2b.Dockerfile"

        print_substep("Writing Codegen-inspired E2B Dockerfile")
        with open(dockerfile_path, "w") as f:
            f.write(create_codegen_e2b_dockerfile())

        print_substep("Dockerfile created with Node.js 20 + uv + modern dev tools")
        print(f"📁 Location: {dockerfile_path}")

        # For this demo, we'll use the base template
        # In practice, you'd run: e2b template build --name codegen-dev
        print_substep("Using base template (will set up environment dynamically)")
        print("💡 In practice, run: e2b template build --name codegen-dev")
        print("🎯 Features: Node.js 20, uv, yarn, pnpm, typescript, dev tools")

        return "base"  # Use base template for this demo


async def setup_modern_environment(sandbox) -> float:
    """Set up modern development environment with Node.js 20 and tooling"""
    print_step(2, "Setting Up Modern Development Environment", Colors.BLUE)

    # Install NVM and Node.js 22 in the current session
    setup_duration = await stream_command_output(
        sandbox,
        """
        export NVM_DIR="$HOME/.nvm" &&
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash &&
        source "$NVM_DIR/nvm.sh" &&
        nvm install 20.18.0 &&
        nvm use 20.18.0 &&
        nvm alias default 20.18.0 &&
        npm install -g yarn@latest pnpm@latest &&
        mkdir -p ~/projects &&
        echo "Modern environment ready!" &&
        node --version && npm --version && yarn --version
        """,
        "Modern tooling setup",
    )

    return setup_duration


async def setup_outline_environment(sandbox, template_id: str) -> dict[str, float]:
    """Set up Outline development environment with modern tooling"""
    timings = {}

    print_step(3, "Setting Up Outline Development Environment", Colors.BLUE)

    # Clone Outline repository
    print_substep("Cloning Outline repository from GitHub")
    clone_duration = await stream_command_output(
        sandbox,
        """
        cd ~/projects &&
        git clone https://github.com/outline/outline.git &&
        cd outline &&
        echo "Repository cloned successfully!" &&
        pwd && ls -la
        """,
        "Git clone operation",
    )
    timings["clone"] = clone_duration

    # Inspect repository and check Node.js requirements
    info_duration = await stream_command_output(
        sandbox,
        """
        cd ~/projects/outline &&
        echo "=== Repository Information ===" &&
        git log --oneline -5 &&
        echo "=== Package.json Node version requirements ===" &&
        grep -E '"node":|"engines"' package.json || echo "No engine requirements found" &&
        echo "=== Available scripts ===" &&
        cat package.json | grep -A 20 '"scripts"' | head -25
        """,
        "Repository inspection",
    )
    timings["inspect"] = info_duration

    return timings


async def install_dependencies_modern(sandbox) -> float:
    """Install Outline dependencies with modern Node.js and Yarn"""
    print_step(4, "Installing Dependencies with Modern Tooling", Colors.CYAN)

    # Install dependencies with proper Node.js environment
    install_duration = await stream_command_output(
        sandbox,
        """
        cd ~/projects/outline &&
        export NVM_DIR="$HOME/.nvm" &&
        source "$NVM_DIR/nvm.sh" &&
        echo "Using Node.js version:" && node --version &&
        echo "Using Yarn version:" && yarn --version &&
        echo "Starting dependency installation..." &&
        yarn install --frozen-lockfile
        """,
        "Yarn install with Node.js 20",
    )

    # Verify installation and show dependency stats
    verify_duration = await stream_command_output(
        sandbox,
        """
        cd ~/projects/outline &&
        export NVM_DIR="$HOME/.nvm" &&
        source "$NVM_DIR/nvm.sh" &&
        echo "=== Dependency verification ===" &&
        ls -la node_modules/ | head -10 &&
        echo "=== Package count ===" &&
        ls node_modules/ | wc -l &&
        echo "=== TypeScript and dev tools ===" &&
        yarn list --pattern="typescript|@types|eslint" --depth=0 | head -15
        """,
        "Dependency verification and stats",
    )

    return install_duration + verify_duration


async def make_development_edit(sandbox) -> float:
    """Make a development-focused edit with modern tools"""
    print_step(5, "Making Development Edit with Timestamp", Colors.YELLOW)

    # Create a development comment with environment info
    edit_duration = await stream_command_output(
        sandbox,
        """
        cd ~/projects/outline &&
        export NVM_DIR="$HOME/.nvm" &&
        source "$NVM_DIR/nvm.sh" &&
        echo "/* Grainchain E2B Snapshot Test - $(date) */" >> README.md &&
        echo "/* Node.js: $(node --version) | Yarn: $(yarn --version) */" >> README.md &&
        echo "/* Environment: E2B Codegen Template $(whoami)@$(hostname) */" >> README.md
        """,
        "Adding development timestamp",
    )

    # Verify the edit and show context
    verify_duration = await stream_command_output(
        sandbox,
        """
        cd ~/projects/outline &&
        echo "=== Last 5 lines of README.md ===" &&
        tail -5 README.md &&
        echo "=== File size and stats ===" &&
        wc -l README.md
        """,
        "Verifying development edit",
    )

    return edit_duration + verify_duration


async def create_comprehensive_snapshot(sandbox, snapshot_name: str) -> float:
    """Create comprehensive snapshot with development environment state"""
    print_step(6, f"Creating Comprehensive Snapshot: {snapshot_name}", Colors.MAGENTA)

    # Create snapshot with environment details
    snapshot_duration = await stream_command_output(
        sandbox,
        f"""
        cd ~/projects &&
        export NVM_DIR="$HOME/.nvm" &&
        source "$NVM_DIR/nvm.sh" &&
        echo "Creating comprehensive snapshot..." &&
        echo "=== Environment Snapshot {snapshot_name} ===" > {snapshot_name}_snapshot.log &&
        echo "Date: $(date)" >> {snapshot_name}_snapshot.log &&
        echo "Node.js: $(node --version)" >> {snapshot_name}_snapshot.log &&
        echo "Yarn: $(yarn --version)" >> {snapshot_name}_snapshot.log &&
        echo "NPM: $(npm --version)" >> {snapshot_name}_snapshot.log &&
        echo "Working Directory: $(pwd)" >> {snapshot_name}_snapshot.log &&
        echo "Files in outline/:" >> {snapshot_name}_snapshot.log &&
        ls -la outline/ | head -10 >> {snapshot_name}_snapshot.log &&
        tar -czf {snapshot_name}_snapshot.tar.gz outline/ &&
        echo "Snapshot creation completed!"
        """,
        "Creating environment snapshot",
    )

    # Verify snapshot with detailed information
    verify_duration = await stream_command_output(
        sandbox,
        f"""
        cd ~/projects &&
        echo "=== Snapshot Verification ===" &&
        ls -lh {snapshot_name}_snapshot.* &&
        echo "=== Snapshot Metadata ===" &&
        cat {snapshot_name}_snapshot.log &&
        echo "=== Archive Contents Preview ===" &&
        tar -tzf {snapshot_name}_snapshot.tar.gz | head -10
        """,
        "Verifying comprehensive snapshot",
    )

    return snapshot_duration + verify_duration


async def main():
    """Main execution flow for E2B Codegen snapshot testing"""
    start_time = time.time()

    print(f"{Colors.WHITE}{'=' * 80}")
    print("🚀 GRAINCHAIN E2B CODEGEN SNAPSHOT TESTING SUITE")
    print("📦 Testing: Codegen Environment + Outline + Modern Tooling + Snapshots")
    print(f"{'=' * 80}{Colors.NC}")

    # Check E2B API key
    if not os.getenv("E2B_API_KEY"):
        print(
            f"{Colors.RED}❌ Error: E2B_API_KEY environment variable not set{Colors.NC}"
        )
        print("💡 Get your API key from: https://e2b.dev/")
        return

    # Create custom template based on codegen.Dockerfile
    template_id = await create_custom_template()
    if not template_id:
        print(f"{Colors.RED}❌ Failed to create custom template{Colors.NC}")
        return

    timings = {}

    try:
        # Configure sandbox for modern development
        config = SandboxConfig(
            timeout=900,  # 15 minutes for comprehensive setup
            working_directory="/home/user",
            environment_vars={
                "NODE_ENV": "development",
                "NODE_OPTIONS": "--max-old-space-size=8192",
                "YARN_ENABLE_IMMUTABLE_INSTALLS": "false",
                "NPM_CONFIG_YES": "true",
                "COREPACK_ENABLE_DOWNLOAD_PROMPT": "0",
            },
        )

        # Step 1: Create first sandbox with modern environment
        print_step(7, "Creating E2B Sandbox with Codegen Environment", Colors.GREEN)
        creation_start = time.time()

        async with Sandbox(provider="e2b", config=config) as sandbox:
            creation_duration = time.time() - creation_start
            timings["sandbox_creation"] = creation_duration
            print_timing("Sandbox creation", creation_duration)

            # Set up modern development environment
            env_duration = await setup_modern_environment(sandbox)
            timings["env_setup"] = env_duration

            # Setup Outline environment
            setup_timings = await setup_outline_environment(sandbox, template_id)
            timings.update(setup_timings)

            # Install dependencies with modern tooling
            install_duration = await install_dependencies_modern(sandbox)
            timings["install"] = install_duration

            # Make development edit
            edit_duration = await make_development_edit(sandbox)
            timings["edit"] = edit_duration

            # Create comprehensive snapshot
            snapshot_duration = await create_comprehensive_snapshot(
                sandbox, "codegen_outline_configured"
            )
            timings["snapshot"] = snapshot_duration

            print_step(8, "Terminating First Sandbox", Colors.RED)
            print_substep("Sandbox with full environment will be destroyed")

        # Step 2: Create new sandbox to simulate snapshot restoration
        print_step(9, "Creating New Sandbox from 'Snapshot'", Colors.GREEN)

        restore_start = time.time()
        async with Sandbox(provider="e2b", config=config) as new_sandbox:
            restore_duration = time.time() - restore_start
            timings["sandbox_restore"] = restore_duration
            print_timing("New sandbox creation", restore_duration)

            # Simulate snapshot restoration with environment recreation
            print_substep("Simulating snapshot restoration")
            restore_sim_duration = await stream_command_output(
                new_sandbox,
                """
                echo "=== Snapshot Restoration Simulation ===" &&
                echo "In production, this would:" &&
                echo "1. Restore from persistent storage (S3, etc.)" &&
                echo "2. Or use pre-built custom template with environment" &&
                echo "3. Recreate the exact development state" &&
                mkdir -p ~/projects &&
                echo "Fresh sandbox ready for restoration!"
                """,
                "Snapshot restoration simulation",
            )
            timings["restore_simulation"] = restore_sim_duration

            # Verify new environment capabilities
            verify_duration = await stream_command_output(
                new_sandbox,
                """
                echo "=== New Sandbox Verification ===" &&
                whoami && pwd &&
                echo "Available tools:" &&
                which node || echo "Node.js not installed" &&
                which yarn || echo "Yarn not installed" &&
                ls -la ~/projects/
                """,
                "New sandbox verification",
            )
            timings["verification"] = verify_duration

    except Exception as e:
        print(f"{Colors.RED}❌ Error during execution: {e}{Colors.NC}")
        import traceback

        traceback.print_exc()
        return

    # Final comprehensive summary
    total_duration = time.time() - start_time

    print_step(10, "EXECUTION SUMMARY", Colors.WHITE)

    print(f"{Colors.CYAN}📊 DETAILED TIMINGS:{Colors.NC}")
    for operation, duration in timings.items():
        print(f"  {operation.replace('_', ' ').title()}: {duration:.3f}s")

    print(f"\n{Colors.GREEN}🎯 TOTAL EXECUTION TIME: {total_duration:.3f}s{Colors.NC}")

    print(f"\n{Colors.YELLOW}💡 KEY INSIGHTS:{Colors.NC}")
    print("  • E2B can run comprehensive development environments")
    print("  • Node.js 20 + modern tooling works well in sandboxes")
    print("  • Snapshot simulation enables development state preservation")
    print("  • Custom templates dramatically reduce setup time")
    print("  • Modern package managers (yarn, pnpm) perform well")

    print(f"\n{Colors.MAGENTA}🚀 PRODUCTION RECOMMENDATIONS:{Colors.NC}")
    print("  1. Build custom template: e2b template build --name codegen-dev")
    print("  2. Pre-install Node.js 20 and tooling in template")
    print("  3. Implement persistent storage for true snapshots")
    print("  4. Cache node_modules in custom templates")
    print("  5. Use template versioning for different environments")

    print(f"\n{Colors.BLUE}🛠️ NEXT STEPS:{Colors.NC}")
    print("  • Test with different Node.js projects")
    print("  • Implement real snapshot persistence")
    print("  • Optimize template build times")
    print("  • Add development container features")

    print(
        f"\n{Colors.WHITE}✨ Grainchain E2B Codegen snapshot test completed successfully!{Colors.NC}"
    )


if __name__ == "__main__":
    asyncio.run(main())
