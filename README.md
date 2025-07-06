# Grainchain ⏳

> **Langchain for Sandboxes** - A unified Python interface for sandbox providers

Grainchain provides a clean, consistent API for interacting with various sandbox providers, enabling developers to write code once and run it across multiple sandbox environments. Just like Langchain abstracts LLM providers, Grainchain abstracts sandbox providers.

## 🚀 Quick Start

```python
import asyncio
from grainchain import Sandbox

async def main():
    # Create a sandbox with the default provider
    async with Sandbox() as sandbox:
        # Execute code
        result = await sandbox.execute("echo 'Hello, Grainchain!'")
        print(result.stdout)  # "Hello, Grainchain!"

        # Upload and run a Python script
        await sandbox.upload_file("script.py", "print('Hello from Python!')")
        result = await sandbox.execute("python script.py")
        print(result.stdout)  # "Hello from Python!"

asyncio.run(main())
```

## 🔍 Check Provider Availability

Before using Grainchain, check which sandbox providers are available and properly configured:

### CLI Command

```bash
# Check all providers
grainchain providers

# Show detailed setup instructions
grainchain providers --verbose

# Check specific provider
grainchain providers --check e2b

# Show only available providers
grainchain providers --available-only
```

**Example output:**
```
🔧 Grainchain Sandbox Providers

📌 Default provider: local ✅

✅ LOCAL
   Dependencies: ✅
   Configuration: ✅

❌ E2B
   Dependencies: ❌
   Install: pip install grainchain[e2b]
   Configuration: ❌
   Missing: E2B_API_KEY
   Setup:
     Set the following environment variables:
       export E2B_API_KEY='your-e2b-api-key-here'

📊 Summary: 1/5 providers available
```

### Python API

```python
from grainchain import get_providers_info, get_available_providers, check_provider

# Get all provider information
providers = get_providers_info()
for name, info in providers.items():
    print(f"{name}: {'���' if info.available else '❌'}")

# Get only available providers
available = get_available_providers()
print(f"Ready to use: {', '.join(available)}")

# Check specific provider
e2b_info = check_provider("e2b")
if not e2b_info.available:
    print(f"E2B setup needed: {e2b_info.missing_config}")
```

### Provider Requirements

| Provider | Dependencies | Environment Variables | Install Command |
|----------|-------------|----------------------|-----------------|
| **Local** | None | None | Built-in ✅ |
| **E2B** | `e2b` | `E2B_API_KEY` | `pip install grainchain[e2b]` |
| **Modal** | `modal` | `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET` | `pip install grainchain[modal]` |
| **Daytona** | `daytona` | `DAYTONA_API_KEY` | `pip install daytona-sdk` |
| **Morph** | `morphcloud` | `MORPH_API_KEY` | `pip install morphcloud` |

## ⚡ Performance Benchmarks

Compare sandbox providers with comprehensive performance testing:

### Quick Performance Test

```bash
# Test individual providers
grainchain benchmark --provider local
grainchain benchmark --provider e2b
grainchain benchmark --provider daytona
grainchain benchmark --provider morph

# Generate timestamped results
grainchain benchmark --provider local --output benchmarks/results/

# Check latest benchmark status (without running new tests)
./scripts/benchmark_status.sh
```

### Full Benchmark Suite

Run comprehensive benchmarks across all providers:

```bash
# Quick: Run all providers and save results
for provider in local e2b daytona morph; do
    echo "🚀 Testing $provider..."
    grainchain benchmark --provider $provider --output benchmarks/results/
done

# Comprehensive: Generate a full report that can be committed
./scripts/benchmark_all.sh

# Advanced: Use the detailed benchmark script
./benchmarks/scripts/run_grainchain_benchmark.sh "local e2b daytona morph" 3
```

The `benchmark_all.sh` script generates timestamped reports in `benchmarks/results/` that include:

- Performance comparison tables
- Environment details (OS, commit hash)
- Analysis and recommendations
- Raw benchmark data for tracking trends

### Current Performance Baseline

Latest benchmark results (updated 2024-05-31):

| Provider    | Total Time | Basic Echo | Python Test | File Ops | Performance      |
| ----------- | ---------- | ---------- | ----------- | -------- | ---------------- |
| **Local**   | 0.036s     | 0.007s     | 0.021s      | 0.008s   | ⚡ Fastest       |
| **E2B**     | 0.599s     | 0.331s     | 0.111s      | 0.156s   | 🚀 Balanced      |
| **Daytona** | 1.012s     | 0.305s     | 0.156s      | 0.551s   | 🛡️ Comprehensive |
| **Morph**   | 0.250s     | 0.005s     | 0.010s      | 0.005s   | 🚀 Instant Snapshots |

> **Performance Notes**:
>
> - Local: Best for development/testing (17x faster than E2B, 28x faster than Daytona)
> - E2B: Production-ready with good speed and reliability
> - Daytona: Full workspace environments with comprehensive tooling
> - Morph: Custom base images, instant snapshots, <250ms startup

Results are automatically saved to `benchmarks/results/` and can be committed to track performance over time.

## 🎯 Why Grainchain?

The sandbox ecosystem is rapidly expanding with providers like [E2B](https://e2b.dev/), [Daytona](https://daytona.io/), [Morph](https://morph.dev/), and others. Each has different APIs and capabilities, creating:

- **Vendor Lock-in**: Applications become tightly coupled to specific providers
- **Learning Curve**: Developers must learn multiple APIs
- **Migration Complexity**: Switching providers requires significant code changes
- **Testing Challenges**: Testing across multiple providers is cumbersome

Grainchain solves these problems with a unified interface that abstracts provider-specific implementations.

## 🏗️ Architecture

```
┌─────────────────┐
│   Application   │
�������─────────────────┘
         │
┌──────────���──────┐
│   Grainchain    │
│   Core API      │
└─────────────────┘
         │
┌─────────────────┐
│   Provider      │
│   Adapters      │
└─────────────────┘
         │
┌─────────────────┐
│   Sandbox       │
│   Providers     │
│  (E2B, Daytona) │
└─────────────────┘
```

## 📦 Installation

### For Users

```bash
# Basic installation
pip install grainchain

# With E2B support
pip install grainchain[e2b]

# With Daytona support
pip install grainchain[daytona]

# With Morph support
pip install grainchain[morph]

# With Local provider support
pip install grainchain[local]

# With Docker provider support
pip install grainchain[docker]

# With all sandbox providers
pip install grainchain[all]

# For benchmarking (docker, psutil)
pip install grainchain[benchmark]

# For data science examples (numpy, pandas, matplotlib)
pip install grainchain[examples]
```

### For Development

```bash
# Clone the repository
git clone https://github.com/codegen-sh/grainchain.git
cd grainchain

# Set up development environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install core development dependencies
uv sync --extra dev

# Optional: Install benchmarking tools (if you need docker benchmarks)
uv sync --extra benchmark

# Optional: Install data science dependencies (if you need examples)
uv sync --extra examples

# Or install everything
uv sync --all-extras

# Install pre-commit hooks
grainchain install-hooks
```

## 🔧 Supported Providers

| Provider    | Status       | Features                                         |
| ----------- | ------------ | ------------------------------------------------ |
| **E2B**     | ✅ Supported | Code interpreter, custom images, file operations |
| **Daytona** | ✅ Supported | Development environments, workspace management   |
| **Morph**   | ✅ Supported | Custom base images, instant snapshots, <250ms startup |
| **Local**   | ✅ Supported | Local development and testing                    |
| **Docker**  | 🚧 Planned   | Local Docker containers                          |

### Daytona Troubleshooting

If you encounter SSL certificate errors with Daytona:

```
SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate
```

This typically indicates:

1. **Development Environment**: The API endpoint may be using self-signed certificates
2. **API Key Environment**: Ensure your API key matches the intended environment (production vs staging)
3. **Network Issues**: Check if you're behind a corporate firewall

**Solution**: Verify your Daytona API key is for the correct environment and contact Daytona support if the issue persists.

### Morph Configuration

Morph.so provides instant snapshots and custom base images with <250ms startup times. Key configuration options:

```python
from grainchain import Sandbox, SandboxConfig

# Basic Morph configuration
config = SandboxConfig(
    provider_config={
        "image_id": "morphvm-minimal",  # or your custom base image
        "vcpus": 2,                     # CPU cores
        "memory": 2048,                 # Memory in MB
        "disk_size": 8192,              # Disk size in MB
    }
)

async with Sandbox(provider="morph", config=config) as sandbox:
    # Your code here
    pass
```

**Key Features:**
- **Custom Base Images**: Use `image_id` to specify your custom-configured base image
- **Instant Snapshots**: Create and restore snapshots in milliseconds
- **Fast Startup**: <250ms startup times for rapid development cycles
- **Resource Control**: Fine-tune CPU, memory, and disk allocation

**Environment Variables:**
```bash
export MORPH_API_KEY=your-morph-api-key
```

## 📖 Usage Examples

### Basic Usage

```python
from grainchain import Sandbox

# Use default provider (configured via environment or config file)
async with Sandbox() as sandbox:
    result = await sandbox.execute("pip install requests")
    result = await sandbox.execute("python -c 'import requests; print(requests.__version__)'")
```

### Provider-Specific Usage

```python
from grainchain import Sandbox

# Use specific provider
async with Sandbox(provider="e2b") as sandbox:
    result = await sandbox.execute("echo 'Using E2B'")

async with Sandbox(provider="daytona") as sandbox:
    result = await sandbox.execute("echo 'Using Daytona'")

async with Sandbox(provider="local") as sandbox:
    result = await sandbox.execute("echo 'Using Local'")

async with Sandbox(provider="morph") as sandbox:
    result = await sandbox.execute("echo 'Using Morph'")
```

### Advanced Configuration

```python
from grainchain import Sandbox, SandboxConfig

config = SandboxConfig(
    timeout=300,
    memory_limit="2GB",
    cpu_limit=2.0,
    environment_vars={"API_KEY": "secret"},
    working_directory="/workspace"
)

async with Sandbox(provider="e2b", config=config) as sandbox:
    result = await sandbox.execute("echo $API_KEY")
```

### File Operations

```python
async with Sandbox() as sandbox:
    # Upload files
    await sandbox.upload_file("data.csv", csv_content)
    await sandbox.upload_file("script.py", python_code)

    # Execute uploaded script
    result = await sandbox.execute("python script.py")

    # Download results
    output = await sandbox.download_file("results.json")

    # List files
    files = await sandbox.list_files("/workspace")
    for file in files:
        print(f"{file.name}: {file.size} bytes")
```

### Snapshots (Local Provider)

```python
async with Sandbox(provider="local") as sandbox:
    # Set up environment
    await sandbox.execute("pip install numpy")
    await sandbox.upload_file("data.py", "import numpy as np")

    # Create snapshot
    snapshot_id = await sandbox.create_snapshot()

    # Make changes
    await sandbox.execute("pip install pandas")

    # Restore to snapshot
    await sandbox.restore_snapshot(snapshot_id)
```

## ⚙️ Configuration

### Environment Variables

```bash
# Default provider
export GRAINCHAIN_DEFAULT_PROVIDER=e2b

# E2B configuration
export E2B_API_KEY=your-e2b-key
export E2B_TEMPLATE=python-data-science

# Daytona configuration
export DAYTONA_API_KEY=your-daytona-key
export DAYTONA_WORKSPACE_TEMPLATE=python-dev

# Morph configuration
export MORPH_API_KEY=your-morph-key
export MORPH_TEMPLATE=custom-base-image
```

### Configuration File

Create `grainchain.yaml` in your project root:

```yaml
default_provider: e2b

providers:
  e2b:
    api_key: ${E2B_API_KEY}
    template: python-data-science
    timeout: 300

  daytona:
    api_key: ${DAYTONA_API_KEY}
    timeout: 300

  morph:
    api_key: ${MORPH_API_KEY}
    template: custom-base-image
    timeout: 300

sandbox_defaults:
  timeout: 180
  working_directory: /workspace
  auto_cleanup: true
```

## 🧪 Examples

Check out the [examples](./examples/) directory for comprehensive usage examples:

- [`basic_usage.py`](./examples/basic_usage.py) - Core functionality and provider usage
- [`data_analysis.py`](./examples/data_analysis.py) - Data science workflow example

## 🛠️ Development

### Development Workflow

```bash
# Set up development environment
uv venv
source .venv/bin/activate
uv sync --all-extras

# Install pre-commit hooks
grainchain install-hooks

# Run tests
grainchain test

# Run tests with coverage
grainchain test --cov

# Format and fix code
grainchain format

# Lint code
grainchain lint --fix

# Type check (currently disabled)
grainchain typecheck

# Run all quality checks
grainchain check

# Run benchmarks
grainchain benchmark --provider local

# Generate comprehensive performance report (committable)
./scripts/benchmark_all.sh

# Check latest performance status
./scripts/benchmark_status.sh
```

### CLI Commands

Grainchain includes a comprehensive CLI for development:

```bash
grainchain --help              # Show all commands
grainchain providers           # Check provider availability
grainchain providers --verbose # Show detailed setup instructions
grainchain test               # Run pytest
grainchain test --cov         # Run tests with coverage
grainchain lint               # Run ruff linting
grainchain format             # Format with ruff
grainchain typecheck          # Type checking (temporarily disabled)
grainchain benchmark          # Run performance benchmarks
grainchain install-hooks      # Install pre-commit hooks
grainchain check             # Run all quality checks
```

### Code Quality

All code is automatically checked with:

- **Ruff** - Fast Python linting, formatting, and import sorting
- **mypy** - Static type checking (temporarily disabled)
- **Pre-commit hooks** - Automated quality checks

## 🗺️ Roadmap

### Phase 1: Foundation ✅

- [x] Core interface design
- [x] Base provider abstraction
- [x] Configuration system
- [x] E2B provider implementation
- [x] Daytona provider implementation
- [x] Morph provider implementation
- [x] Local provider for testing

### Phase 2: Enhanced Features 🚧

- [ ] Comprehensive test suite
- [ ] Error handling improvements
- [ ] Performance optimizations
- [ ] Documentation website

### Phase 3: Ecosystem 🔮

- [ ] Docker provider
- [ ] Plugin system for custom providers
- [ ] Monitoring and observability
- [ ] Cost optimization features

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Set up development environment: `uv sync --all-extras`
4. Make your changes
5. Run quality checks: `grainchain check`
6. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Inspired by [Langchain](https://github.com/langchain-ai/langchain) for LLM abstraction
- Built for the [E2B](https://e2b.dev/), [Daytona](https://daytona.io/), and [Morph](https://morph.dev/) communities
- Thanks to all contributors and early adopters

---

**Built with ❤️ by the [Codegen](https://codegen.com) team**
