# Grainchain API Features Documentation

> **Comprehensive guide to Grainchain's unified sandbox interface, snapshotting capabilities, and Docker support**

## Table of Contents

1. [Overview](#overview)
2. [Core API Interface](#core-api-interface)
3. [Snapshotting Capabilities](#snapshotting-capabilities)
4. [Custom Docker Support](#custom-docker-support)
5. [Provider Comparison Matrix](#provider-comparison-matrix)
6. [Usage Examples](#usage-examples)
7. [Provider Selection Guide](#provider-selection-guide)

## Overview

Grainchain provides a unified Python interface for interacting with various sandbox providers, abstracting away provider-specific implementations while maintaining access to advanced features like snapshotting and custom Docker environments.

### Design Philosophy

- **Provider Agnostic**: Write once, run anywhere across different sandbox providers
- **Clean API**: Simple, intuitive interface inspired by Langchain
- **Extensible**: Easy to add new sandbox providers
- **Type Safe**: Full type hints for Python development
- **Async First**: Built for modern async/await patterns

### Supported Providers

| Provider | Status | Specialization |
|----------|--------|----------------|
| **E2B** | ✅ Production Ready | Custom Docker images, development environments |
| **Morph** | ✅ Production Ready | Memory snapshots, instant state management |
| **Daytona** | ✅ Production Ready | Cloud development workspaces |
| **Modal** | ✅ Production Ready | Serverless compute with custom images |
| **Local** | ✅ Production Ready | Direct execution without containerization |
| **Docker** | 🚧 Coming Soon | Local Docker containers |

## Core API Interface

### Main Sandbox Class

The `Sandbox` class provides the primary interface for all sandbox operations:

```python
from grainchain import Sandbox, SandboxConfig

# Basic usage with default provider
async with Sandbox() as sandbox:
    result = await sandbox.execute("echo 'Hello World'")
    print(result.stdout)

# Advanced configuration
config = SandboxConfig(
    timeout=600,
    memory_limit="4GB",
    cpu_limit=2.0,
    image="python:3.11",
    environment_vars={"DEBUG": "1"}
)

async with Sandbox(provider="e2b", config=config) as sandbox:
    # Your code here
    pass
```

### Core Methods

#### Command Execution

```python
async def execute(
    command: str,
    timeout: Optional[int] = None,
    working_dir: Optional[str] = None,
    environment: Optional[dict[str, str]] = None,
) -> ExecutionResult
```

**Features:**
- Execute shell commands in the sandbox
- Configurable timeout and working directory
- Environment variable injection
- Comprehensive result metadata

**Example:**
```python
result = await sandbox.execute(
    "python script.py --verbose",
    timeout=300,
    working_dir="/workspace",
    environment={"LOG_LEVEL": "DEBUG"}
)

print(f"Exit code: {result.return_code}")
print(f"Output: {result.stdout}")
print(f"Errors: {result.stderr}")
print(f"Duration: {result.execution_time}s")
```

#### File Operations

```python
# Upload files
async def upload_file(
    path: str,
    content: Union[str, bytes],
    mode: str = "w"
) -> None

# Download files
async def download_file(path: str) -> bytes

# List directory contents
async def list_files(path: str = "/") -> list[FileInfo]
```

**Example:**
```python
# Upload a Python script
await sandbox.upload_file(
    "script.py",
    "print('Hello from uploaded script!')"
)

# Upload binary data
with open("data.zip", "rb") as f:
    await sandbox.upload_file("data.zip", f.read(), mode="wb")

# List files
files = await sandbox.list_files("/workspace")
for file in files:
    print(f"{file.name}: {file.size} bytes")

# Download results
result_data = await sandbox.download_file("output.json")
```

#### State Management

```python
# Create snapshots
async def create_snapshot() -> str

# Restore from snapshots
async def restore_snapshot(snapshot_id: str) -> None

# Advanced lifecycle management
async def terminate() -> None
async def wake_up(snapshot_id: Optional[str] = None) -> None
```

## Snapshotting Capabilities

Grainchain supports different types of snapshotting depending on the provider:

### Memory Snapshotting vs. Filesystem Snapshotting

#### Memory Snapshotting (Morph Provider)

**What it is:** Captures the complete memory state of the running sandbox, including:
- Process memory
- Kernel state
- Network connections
- Open file descriptors

**Advantages:**
- **Instant snapshots** (<250ms)
- **Complete state preservation** including running processes
- **Fast restoration** with minimal overhead
- **True pause/resume** functionality

**Use Cases:**
- Long-running computations that need to be paused
- Interactive development sessions
- Debugging complex state scenarios

**Example:**
```python
async with Sandbox(provider="morph") as sandbox:
    # Start a long-running process
    await sandbox.execute("python long_computation.py &")

    # Create instant memory snapshot
    snapshot_id = await sandbox.create_snapshot()
    print(f"Memory snapshot created: {snapshot_id}")

    # Terminate sandbox (preserves snapshots)
    await sandbox.terminate()

    # Later: wake up from exact state
    await sandbox.wake_up(snapshot_id)
    # Process continues exactly where it left off
```

#### Filesystem Snapshotting (E2B, Local, Daytona, Modal)

**What it is:** Captures the filesystem state of the sandbox:
- File contents
- Directory structure
- File permissions
- Installed packages

**Advantages:**
- **Portable** across different instances
- **Persistent** storage of work
- **Reproducible** environments
- **Version control** for development states

**Limitations:**
- Running processes are not preserved
- Network connections are lost
- Memory state is not captured

**Use Cases:**
- Saving development environment setups
- Creating reproducible build environments
- Sharing configured workspaces
- Backup and restore workflows

**Example:**
```python
async with Sandbox(provider="e2b") as sandbox:
    # Set up environment
    await sandbox.execute("pip install numpy pandas")
    await sandbox.upload_file("config.json", json.dumps(config))

    # Create filesystem snapshot
    snapshot_id = await sandbox.create_snapshot()
    print(f"Filesystem snapshot created: {snapshot_id}")

    # Later: restore environment
    async with Sandbox(provider="e2b") as new_sandbox:
        await new_sandbox.restore_snapshot(snapshot_id)
        # Environment is restored with packages and files
```

### Provider-Specific Snapshot Support

| Provider | Snapshot Type | Creation Speed | Restoration Speed | Preserves Processes | Notes |
|----------|---------------|----------------|-------------------|-------------------|-------|
| **Morph** | Memory | <250ms | <500ms | ✅ Yes | True pause/resume functionality |
| **E2B** | Filesystem | 2-10s | 5-15s | ❌ No | Template-based restoration |
| **Local** | Filesystem | 1-5s | 1-3s | ❌ No | Directory-based snapshots |
| **Daytona** | Filesystem | 3-8s | 5-12s | ❌ No | Workspace state preservation |
| **Modal** | Filesystem | 2-6s | 4-10s | ❌ No | Container image snapshots |

### Advanced Snapshot Workflows

#### Snapshot Chains (All Providers)

```python
async with Sandbox() as sandbox:
    # Base setup
    await sandbox.execute("apt-get update && apt-get install -y git")
    base_snapshot = await sandbox.create_snapshot()

    # Development branch 1
    await sandbox.execute("git clone repo1.git")
    dev1_snapshot = await sandbox.create_snapshot()

    # Reset to base and try different approach
    await sandbox.restore_snapshot(base_snapshot)
    await sandbox.execute("git clone repo2.git")
    dev2_snapshot = await sandbox.create_snapshot()
```

#### Terminate/Wake-up Cycle (Morph Only)

```python
async with Sandbox(provider="morph") as sandbox:
    # Start work
    await sandbox.execute("python training_script.py &")

    # Save state and terminate to save costs
    snapshot_id = await sandbox.create_snapshot()
    await sandbox.terminate()

    # Resume later exactly where we left off
    await sandbox.wake_up(snapshot_id)
    # Training continues from exact point
```

## Custom Docker Support

### Current Docker Support by Provider

#### E2B Provider - Full Custom Docker Support ✅

**Capabilities:**
- Custom Dockerfile support via `e2b.Dockerfile`
- Template-based image management
- Pre-built environment templates
- Development-optimized base images

**Configuration:**
```python
config = SandboxConfig(
    provider_config={
        "template": "custom-nodejs-template",  # Your custom template
        "api_key": "your-e2b-api-key"
    }
)

async with Sandbox(provider="e2b", config=config) as sandbox:
    # Runs in your custom Docker environment
    result = await sandbox.execute("node --version")
```

**Custom Dockerfile Example:**
```dockerfile
# e2b.Dockerfile
FROM e2b/code-interpreter:latest

# Install Node.js 18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

# Install Yarn
RUN npm install -g yarn

# Set up workspace
WORKDIR /workspace
RUN chown -R user:user /workspace

# Install development tools
RUN apt-get update && apt-get install -y \
    git \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*
```

**Template Creation:**
```bash
# Create template from Dockerfile
e2b template build --name my-custom-template

# Use in Grainchain
export E2B_TEMPLATE=my-custom-template
```

#### Morph Provider - Custom Base Images ✅

**Capabilities:**
- Pre-configured base images
- Custom image selection via `image_id`
- Optimized for specific use cases

**Configuration:**
```python
config = SandboxConfig(
    provider_config={
        "image_id": "morphvm-python",  # or "morphvm-minimal", "morphvm-nodejs"
        "vcpus": 2,
        "memory": 2048,  # MB
        "disk_size": 10240  # MB
    }
)

async with Sandbox(provider="morph", config=config) as sandbox:
    # Runs on your selected base image
    pass
```

**Available Base Images:**
- `morphvm-minimal`: Lightweight Ubuntu base
- `morphvm-python`: Python development environment
- `morphvm-nodejs`: Node.js development environment
- Custom images: Contact Morph for custom base image creation

#### Modal Provider - Custom Image Support ✅

**Capabilities:**
- Custom Docker images via Modal's image system
- Programmatic image building
- Package and dependency management

**Configuration:**
```python
import modal

# Define custom image
custom_image = modal.Image.from_registry("python:3.11").pip_install([
    "numpy",
    "pandas",
    "scikit-learn"
])

config = SandboxConfig(
    provider_config={
        "image": custom_image,
        "token_id": "your-modal-token-id",
        "token_secret": "your-modal-token-secret"
    }
)
```

#### Local Provider - No Docker Support ❌

**Current State:**
- Runs directly on host machine
- No containerization
- Fastest for development/testing
- No isolation between sandboxes

**Use Cases:**
- Local development
- Testing Grainchain code
- Environments where Docker isn't available

#### Docker Provider - Coming Soon 🚧

**Planned Features:**
- Local Docker container management
- Custom Dockerfile support
- Volume mounting
- Network configuration
- Resource limits

**Expected API:**
```python
# Future Docker provider API
config = SandboxConfig(
    image="python:3.11",
    provider_config={
        "dockerfile": "./custom.Dockerfile",
        "volumes": {"/host/path": "/container/path"},
        "ports": {"8080": "8080"},
        "network": "bridge"
    }
)

async with Sandbox(provider="docker", config=config) as sandbox:
    # Will run in local Docker container
    pass
```

### Docker Support Comparison

| Provider | Docker Support | Custom Images | Dockerfile | Base Images | Status |
|----------|----------------|---------------|------------|-------------|--------|
| **E2B** | ✅ Full | ✅ Yes | ✅ e2b.Dockerfile | ✅ Multiple | Production |
| **Morph** | ✅ Partial | ❌ No | ❌ No | ✅ Curated | Production |
| **Modal** | ✅ Full | ✅ Yes | ✅ Programmatic | ✅ Registry | Production |
| **Daytona** | ✅ Partial | ✅ Limited | ❌ No | ✅ Templates | Production |
| **Local** | ❌ None | ❌ No | ❌ No | ❌ No | Development Only |
| **Docker** | 🚧 Planned | 🚧 Planned | 🚧 Planned | 🚧 Planned | Coming Soon |

## Provider Comparison Matrix

### Feature Support Matrix

| Feature | E2B | Morph | Daytona | Modal | Local | Docker* |
|---------|-----|-------|---------|-------|-------|---------|
| **Core Execution** | ✅ | ✅ | ✅ | ✅ | ✅ | 🚧 |
| **File Operations** | ✅ | ✅ | ✅ | ✅ | ✅ | 🚧 |
| **Filesystem Snapshots** | ✅ | ❌ | ✅ | ✅ | ✅ | 🚧 |
| **Memory Snapshots** | ❌ | ✅ | ❌ | ❌ | ❌ | 🚧 |
| **Terminate/Wake-up** | ❌ | ✅ | ❌ | ❌ | ❌ | 🚧 |
| **Custom Docker** | ✅ | ❌ | ❌ | ✅ | ❌ | 🚧 |
| **Base Images** | ✅ | ✅ | ✅ | ✅ | ❌ | 🚧 |
| **Resource Limits** | ✅ | ✅ | ✅ | ✅ | ❌ | 🚧 |
| **Persistent Storage** | ✅ | ✅ | ✅ | ✅ | ✅ | 🚧 |
| **Network Access** | ✅ | ✅ | ✅ | ✅ | ✅ | 🚧 |

*Docker provider features are planned

### Performance Characteristics

| Provider | Startup Time | Execution Overhead | Snapshot Creation | Snapshot Restoration |
|----------|--------------|-------------------|-------------------|---------------------|
| **E2B** | 5-15s | Low | 2-10s | 5-15s |
| **Morph** | <250ms | Minimal | <250ms | <500ms |
| **Daytona** | 10-30s | Low | 3-8s | 5-12s |
| **Modal** | 2-8s | Low | 2-6s | 4-10s |
| **Local** | <100ms | None | 1-5s | 1-3s |

### Cost Considerations

| Provider | Pricing Model | Cost Efficiency | Free Tier |
|----------|---------------|-----------------|-----------|
| **E2B** | Per-minute usage | High for development | ✅ Available |
| **Morph** | Per-instance + snapshots | High for long-running | ❌ Paid only |
| **Daytona** | Workspace-based | Medium | ✅ Available |
| **Modal** | Compute + storage | High for batch jobs | ✅ Available |
| **Local** | Free | Highest | ✅ Always free |

## Usage Examples

### Basic Execution Workflow

```python
import asyncio
from grainchain import Sandbox

async def basic_workflow():
    async with Sandbox() as sandbox:
        # Install dependencies
        await sandbox.execute("pip install requests beautifulsoup4")

        # Upload script
        script = """
import requests
from bs4 import BeautifulSoup

response = requests.get('https://httpbin.org/json')
print(f"Status: {response.status_code}")
print(f"Data: {response.json()}")
"""
        await sandbox.upload_file("scraper.py", script)

        # Execute script
        result = await sandbox.execute("python scraper.py")
        print(result.stdout)

asyncio.run(basic_workflow())
```

### Advanced Snapshotting Workflow

```python
async def snapshot_workflow():
    async with Sandbox(provider="e2b") as sandbox:
        # Set up base environment
        await sandbox.execute("apt-get update")
        await sandbox.execute("apt-get install -y nodejs npm")
        base_snapshot = await sandbox.create_snapshot()

        # Try different approaches
        approaches = [
            "npm install express",
            "npm install fastify",
            "npm install koa"
        ]

        results = {}
        for approach in approaches:
            # Reset to base state
            await sandbox.restore_snapshot(base_snapshot)

            # Try approach
            result = await sandbox.execute(approach)
            await sandbox.execute("npm list --depth=0")

            # Save result state
            snapshot_id = await sandbox.create_snapshot()
            results[approach] = {
                "success": result.success,
                "snapshot": snapshot_id
            }

        # Use best approach
        best_approach = max(results.items(), key=lambda x: x[1]["success"])
        await sandbox.restore_snapshot(best_approach[1]["snapshot"])

        print(f"Using best approach: {best_approach[0]}")
```

### Multi-Provider Comparison

```python
async def compare_providers():
    providers = ["local", "e2b", "morph"]
    results = {}

    for provider in providers:
        try:
            async with Sandbox(provider=provider) as sandbox:
                start_time = time.time()
                result = await sandbox.execute("python -c 'print(\"Hello from\", \"" + provider + "\")'")
                duration = time.time() - start_time

                results[provider] = {
                    "success": result.success,
                    "duration": duration,
                    "output": result.stdout.strip()
                }
        except Exception as e:
            results[provider] = {"error": str(e)}

    for provider, result in results.items():
        print(f"{provider}: {result}")
```

### Custom Docker Environment

```python
async def custom_docker_workflow():
    # E2B with custom template
    e2b_config = SandboxConfig(
        provider_config={
            "template": "my-nodejs-template"
        }
    )

    async with Sandbox(provider="e2b", config=e2b_config) as sandbox:
        # Your custom environment is ready
        result = await sandbox.execute("node --version && npm --version")
        print(f"E2B Custom Environment: {result.stdout}")

    # Morph with custom base image
    morph_config = SandboxConfig(
        provider_config={
            "image_id": "morphvm-python",
            "memory": 2048
        }
    )

    async with Sandbox(provider="morph", config=morph_config) as sandbox:
        result = await sandbox.execute("python --version && pip --version")
        print(f"Morph Custom Image: {result.stdout}")
```

## Provider Selection Guide

### Decision Tree

```
Choose your provider based on your needs:

📊 **Performance Priority**
├── Fastest startup → Local (development only)
├── Fastest snapshots → Morph (<250ms)
└── Balanced performance → E2B or Modal

🔧 **Feature Requirements**
├── Memory snapshots → Morph (only option)
├── Custom Docker → E2B or Modal
├── Long-running processes → Morph (terminate/wake-up)
└── Simple file operations → Any provider

💰 **Cost Considerations**
├── Free development → Local, E2B (free tier), Modal (free tier)
├── Production efficiency → Morph (pay for what you use)
└── Batch processing → Modal (serverless pricing)

🏗️ **Use Case Specific**
├── CI/CD pipelines → E2B (Docker support)
├── Interactive development → Morph (memory snapshots)
├── Data processing → Modal (scalable compute)
├── Local testing → Local (no overhead)
└── Team workspaces → Daytona (collaboration features)
```

### Recommended Configurations

#### Development Environment

```python
# For local development and testing
config = SandboxConfig(
    timeout=300,
    auto_cleanup=True
)
sandbox = Sandbox(provider="local", config=config)
```

#### Production CI/CD

```python
# For production builds and deployments
config = SandboxConfig(
    timeout=1800,  # 30 minutes
    memory_limit="4GB",
    cpu_limit=2.0,
    image="ubuntu:22.04",
    provider_config={
        "template": "ci-cd-template"
    }
)
sandbox = Sandbox(provider="e2b", config=config)
```

#### Long-Running Computations

```python
# For ML training, data processing
config = SandboxConfig(
    timeout=None,  # No timeout
    provider_config={
        "image_id": "morphvm-python",
        "memory": 8192,  # 8GB
        "vcpus": 4
    }
)
sandbox = Sandbox(provider="morph", config=config)
```

#### Interactive Development

```python
# For development with frequent state changes
config = SandboxConfig(
    keep_alive=True,
    provider_config={
        "image_id": "morphvm-minimal"
    }
)
sandbox = Sandbox(provider="morph", config=config)
```

---

## Summary

Grainchain provides a powerful, unified interface for sandbox management with:

✅ **Unified API** across 5+ providers
✅ **Advanced snapshotting** (memory + filesystem)
✅ **Custom Docker support** (E2B, Modal, Morph)
✅ **Production-ready** providers with different specializations
✅ **Type-safe** Python interface with async support

**Key Takeaways:**
- Use **Morph** for memory snapshots and instant state management
- Use **E2B** for custom Docker environments and development
- Use **Modal** for scalable compute with custom images
- Use **Local** for development and testing without overhead
- **Docker provider** coming soon for local container management

The choice of provider depends on your specific needs for performance, features, cost, and use case requirements.
