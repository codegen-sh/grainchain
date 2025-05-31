# Grainchain 🌾

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

## ⚡ Performance Benchmarks

Compare sandbox providers with comprehensive performance testing:

### Quick Performance Test

```bash
# Test individual providers
grainchain benchmark --provider local
grainchain benchmark --provider e2b
grainchain benchmark --provider daytona

# Generate timestamped results
grainchain benchmark --provider local --output benchmarks/results/

# Check latest benchmark status (without running new tests)
./scripts/benchmark_status.sh
```

### Full Benchmark Suite

Run comprehensive benchmarks across all providers:

```bash
# Quick: Run all providers and save results
for provider in local e2b daytona; do
    echo "🚀 Testing $provider..."
    grainchain benchmark --provider $provider --output benchmarks/results/
done

# Comprehensive: Generate a full report that can be committed
./scripts/benchmark_all.sh

# Advanced: Use the detailed benchmark script
./benchmarks/scripts/run_grainchain_benchmark.sh "local e2b daytona" 3
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

> **Performance Notes**:
>
> - Local: Best for development/testing (17x faster than E2B, 28x faster than Daytona)
> - E2B: Production-ready with good speed and reliability
> - Daytona: Full workspace environments with comprehensive tooling

Results are automatically saved to `benchmarks/results/` and can be committed to track performance over time.

## 🎯 Why Grainchain?

The sandbox ecosystem is rapidly expanding with providers like [E2B](https://e2b.dev/), [Daytona](https://daytona.io/), and others. Each has different APIs and capabilities, creating:

- **Vendor Lock-in**: Applications become tightly coupled to specific providers
- **Learning Curve**: Developers must learn multiple APIs
- **Migration Complexity**: Switching providers requires significant code changes
- **Testing Challenges**: Testing across multiple providers is cumbersome

Grainchain solves these problems with a unified interface that abstracts provider-specific implementations.

## 🏗️ Architecture

```
┌─────────────────┐
│   Application   │
└─────────────────┘
         │
┌─────────────────┐
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

### Testing

Grainchain includes a comprehensive test suite with >90% code coverage to ensure reliability across all providers.

### Running Tests

```bash
# Run all tests
uv run pytest

# Run only unit tests
uv run pytest tests/unit/ -v

# Run only integration tests
uv run pytest tests/integration/ -v

# Run tests with coverage
uv run pytest --cov=grainchain --cov-report=html

# Run tests for specific provider
uv run pytest tests/integration/test_local_provider.py -v

# Run performance tests
uv run pytest -m slow

# Run tests excluding slow tests
uv run pytest -m "not slow"
```

### Test Categories

- **Unit Tests** (`tests/unit/`): Fast, isolated tests for core functionality
  - `test_sandbox.py`: Core Sandbox class tests
  - `test_providers.py`: Provider implementation tests
  - `test_config.py`: Configuration management tests
  - `test_exceptions.py`: Exception handling tests
  - `test_interfaces.py`: Interface and data structure tests

- **Integration Tests** (`tests/integration/`): Real provider interactions
  - `test_e2b_provider.py`: E2B provider integration tests
  - `test_modal_provider.py`: Modal provider integration tests
  - `test_daytona_provider.py`: Daytona provider integration tests
  - `test_local_provider.py`: Local provider integration tests

### Test Configuration

Tests are configured via `pytest.ini` with the following markers:

- `unit`: Unit tests (fast, no external dependencies)
- `integration`: Integration tests (require provider credentials)
- `slow`: Slow tests that may take longer to run
- `e2b`: Tests requiring E2B provider
- `modal`: Tests requiring Modal provider
- `daytona`: Tests requiring Daytona provider
- `local`: Tests requiring Local provider
- `snapshot`: Tests for snapshot functionality

### Provider Credentials for Integration Tests

To run integration tests with real providers, set these environment variables:

```bash
# E2B
export E2B_API_KEY=your-e2b-api-key

# Modal
export MODAL_TOKEN_ID=your-modal-token-id
export MODAL_TOKEN_SECRET=your-modal-token-secret

# Daytona
export DAYTONA_API_KEY=your-daytona-api-key
```

### Continuous Integration

Tests run automatically on GitHub Actions for:

- **All Python versions** (3.9, 3.10, 3.11, 3.12) on pull requests
- **Integration tests** with real providers on main branch pushes
- **Performance tests** and benchmarks on releases
- **Security scans** with bandit on all commits

### Coverage Requirements

- Minimum coverage: **90%**
- All new code must include tests
- Integration tests must cover happy path and error scenarios
- Performance tests ensure operations complete within expected timeframes

### CLI Commands

Grainchain includes a comprehensive CLI for development:

```bash
grainchain --help              # Show all commands
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
- Built for the [E2B](https://e2b.dev/) and [Daytona](https://daytona.io/) communities
- Thanks to all contributors and early adopters

---

**Built with ❤️ by the [Codegen](https://codegen.com) team**
