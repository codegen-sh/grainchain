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

## 🎯 Why Grainchain?

The sandbox ecosystem is rapidly expanding with providers like [E2B](https://e2b.dev/), [Modal](https://modal.com/), and others. Each has different APIs and capabilities, creating:

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
│  (E2B, Modal)   │
└─────────────────┘
```

## 📦 Installation

```bash
# Basic installation
pip install grainchain

# With E2B support
pip install grainchain[e2b]

# With Modal support
pip install grainchain[modal]

# With all providers
pip install grainchain[all]
```

## 🔧 Supported Providers

| Provider    | Status       | Features                                               |
| ----------- | ------------ | ------------------------------------------------------ |
| **E2B**     | ✅ Supported | Code interpreter, custom images, file operations       |
| **Modal**   | ✅ Supported | Serverless execution, GPU support, custom environments |
| **Blaxel**  | ✅ Supported | Cloud sandbox environments, scalable execution         |
| **Daytona** | ✅ Supported | Development environments, collaborative coding         |
| **Local**   | ✅ Supported | Local development and testing                          |
| **Docker**  | 🚧 Planned   | Local Docker containers                                |

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

async with Sandbox(provider="modal") as sandbox:
    result = await sandbox.execute("echo 'Using Modal'")
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

# Modal configuration
export MODAL_TOKEN_ID=your-modal-token-id
export MODAL_TOKEN_SECRET=your-modal-token-secret
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

  modal:
    token_id: ${MODAL_TOKEN_ID}
    token_secret: ${MODAL_TOKEN_SECRET}
    image: python:3.11
    cpu: 2.0
    memory: 4GB

sandbox_defaults:
  timeout: 180
  working_directory: /workspace
  auto_cleanup: true
```

## 📊 Benchmarking Infrastructure

This repository includes a comprehensive benchmarking infrastructure for the [Outline](https://github.com/outline/outline) application. The system automatically measures performance impacts using the codex-universal base image.

### Quick Start

```bash
# Install dependencies
make install

# Run benchmarks
make benchmark

# Run and publish results
make publish
```

### Features

- 🐳 **Docker-based**: Uses codex-universal base image for consistent environments
- 📈 **Comprehensive Metrics**: Measures build time, memory usage, file system stats
- 🤖 **Automated**: GitHub Actions for scheduled execution and result publishing
- 📊 **Multiple Formats**: Generates HTML, JSON, and Markdown reports
- 🔄 **Change Impact**: Tests performance impact of trivial code changes

See [`benchmarks/README.md`](benchmarks/README.md) for detailed documentation.

## 🧪 Examples

Check out the [examples](./examples/) directory for comprehensive usage examples:

- [`basic_usage.py`](./examples/basic_usage.py) - Core functionality and provider usage
- [`data_analysis.py`](./examples/data_analysis.py) - Data science workflow example

## 🛠️ Development

### Setup

```bash
git clone https://github.com/codegen-sh/grainchain.git
cd grainchain
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
black grainchain/
isort grainchain/
mypy grainchain/
ruff grainchain/
```

## 🗺️ Roadmap

### Phase 1: Foundation ✅

- [x] Core interface design
- [x] Base provider abstraction
- [x] Configuration system
- [x] E2B provider implementation
- [x] Modal provider implementation
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
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Inspired by [Langchain](https://github.com/langchain-ai/langchain) for LLM abstraction
- Built for the [E2B](https://e2b.dev/) and [Modal](https://modal.com/) communities
- Thanks to all contributors and early adopters

---

**Built with ❤️ by the [Codegen](https://codegen.com) team**
