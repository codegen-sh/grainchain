# Developer Guide

Welcome to the GrainChain developer guide! This section covers everything you need to know about contributing to GrainChain, understanding its architecture, and extending its functionality.

## Getting Started

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/codegen-sh/grainchain.git
   cd grainchain
   ```

2. **Set up the development environment**:
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install in development mode
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

4. **Run tests**:
   ```bash
   pytest
   ```

### Project Structure

```
grainchain/
├── grainchain/              # Main package
│   ├── __init__.py         # Package initialization
│   ├── core/               # Core functionality
│   │   ├── sandbox.py      # Main Sandbox class
│   │   ├── result.py       # SandboxResult class
│   │   └── exceptions.py   # Custom exceptions
│   ├── providers/          # Sandbox providers
│   │   ├── base.py         # Base provider interface
│   │   ├── e2b.py          # E2B provider
│   │   ├── modal.py        # Modal provider
│   │   └── daytona.py      # Daytona provider
│   ├── cli/                # Command-line interface
│   │   ├── main.py         # CLI entry point
│   │   └── commands/       # CLI commands
│   └── utils/              # Utility functions
├── tests/                  # Test suite
├── docs/                   # Documentation
├── examples/               # Example scripts
├── benchmarks/             # Performance benchmarks
└── scripts/                # Development scripts
```

## Architecture Overview

### Core Components

#### Sandbox Class
The main interface that users interact with:

```python
class Sandbox:
    def __init__(self, provider: str = None, **kwargs):
        self.provider = self._get_provider(provider, **kwargs)
    
    async def execute(self, command: str, **kwargs) -> SandboxResult:
        return await self.provider.execute(command, **kwargs)
    
    async def __aenter__(self):
        await self.provider.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.provider.stop()
```

#### Provider Interface
All providers implement the `BaseProvider` interface:

```python
from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @abstractmethod
    async def start(self) -> None:
        """Initialize the sandbox environment"""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Clean up the sandbox environment"""
        pass
    
    @abstractmethod
    async def execute(self, command: str, **kwargs) -> SandboxResult:
        """Execute a command in the sandbox"""
        pass
    
    @abstractmethod
    async def upload_file(self, path: str, content: str) -> None:
        """Upload a file to the sandbox"""
        pass
    
    @abstractmethod
    async def download_file(self, path: str) -> str:
        """Download a file from the sandbox"""
        pass
```

### Provider Implementation

#### Creating a New Provider

To create a new sandbox provider:

1. **Create the provider class**:
   ```python
   # grainchain/providers/my_provider.py
   from .base import BaseProvider
   from ..core.result import SandboxResult
   
   class MyProvider(BaseProvider):
       def __init__(self, **kwargs):
           self.config = kwargs
           self.session = None
       
       async def start(self):
           # Initialize connection to your sandbox service
           self.session = await create_session(self.config)
       
       async def stop(self):
           # Clean up resources
           if self.session:
               await self.session.close()
       
       async def execute(self, command: str, **kwargs):
           # Execute command using your provider's API
           result = await self.session.run(command)
           
           return SandboxResult(
               stdout=result.stdout,
               stderr=result.stderr,
               exit_code=result.exit_code,
               execution_time=result.duration
           )
       
       # Implement other required methods...
   ```

2. **Register the provider**:
   ```python
   # grainchain/providers/__init__.py
   from .my_provider import MyProvider
   
   PROVIDERS = {
       "e2b": E2BProvider,
       "modal": ModalProvider,
       "daytona": DaytonaProvider,
       "my_provider": MyProvider,  # Add your provider
   }
   ```

3. **Add configuration support**:
   ```python
   # grainchain/core/config.py
   PROVIDER_CONFIGS = {
       "my_provider": {
           "required_env": ["MY_PROVIDER_API_KEY"],
           "optional_env": ["MY_PROVIDER_ENDPOINT"],
           "default_config": {
               "timeout": 30,
               "max_memory": "1GB"
           }
       }
   }
   ```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=grainchain

# Run specific test file
pytest tests/test_sandbox.py

# Run tests for specific provider
pytest tests/providers/test_e2b.py -v
```

### Writing Tests

#### Unit Tests
```python
# tests/test_sandbox.py
import pytest
from grainchain import Sandbox
from grainchain.providers.base import BaseProvider

class MockProvider(BaseProvider):
    async def start(self):
        pass
    
    async def stop(self):
        pass
    
    async def execute(self, command):
        return SandboxResult(
            stdout="mock output",
            stderr="",
            exit_code=0,
            execution_time=0.1
        )

@pytest.mark.asyncio
async def test_sandbox_execute():
    sandbox = Sandbox(provider=MockProvider())
    async with sandbox:
        result = await sandbox.execute("echo test")
        assert result.stdout == "mock output"
        assert result.exit_code == 0
```

#### Integration Tests
```python
# tests/integration/test_e2b_integration.py
import pytest
from grainchain import Sandbox

@pytest.mark.integration
@pytest.mark.asyncio
async def test_e2b_real_execution():
    """Test actual E2B execution (requires API key)"""
    async with Sandbox(provider="e2b") as sandbox:
        result = await sandbox.execute("echo 'integration test'")
        assert "integration test" in result.stdout
        assert result.exit_code == 0
```

### Test Configuration

```python
# pytest.ini
[tool:pytest]
markers =
    integration: marks tests as integration tests (deselect with '-m "not integration"')
    slow: marks tests as slow (deselect with '-m "not slow"')
    e2b: marks tests that require E2B credentials
    modal: marks tests that require Modal credentials

asyncio_mode = auto
```

## Performance and Benchmarking

### Running Benchmarks

```bash
# Run all benchmarks
python -m benchmarks.run_all

# Run specific benchmark
python -m benchmarks.execution_speed

# Compare providers
python -m benchmarks.provider_comparison
```

### Creating Benchmarks

```python
# benchmarks/my_benchmark.py
import asyncio
import time
from grainchain import Sandbox

async def benchmark_execution_speed():
    """Benchmark command execution speed"""
    
    providers = ["e2b", "modal", "daytona"]
    commands = [
        "echo 'hello'",
        "python -c 'print(sum(range(1000)))'",
        "ls -la"
    ]
    
    results = {}
    
    for provider in providers:
        provider_results = []
        
        async with Sandbox(provider=provider) as sandbox:
            for command in commands:
                start_time = time.time()
                result = await sandbox.execute(command)
                end_time = time.time()
                
                provider_results.append({
                    "command": command,
                    "execution_time": result.execution_time,
                    "total_time": end_time - start_time,
                    "success": result.exit_code == 0
                })
        
        results[provider] = provider_results
    
    return results

if __name__ == "__main__":
    results = asyncio.run(benchmark_execution_speed())
    print(json.dumps(results, indent=2))
```

## Documentation

### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Start development server
cd docs
npm run dev

# Build for production
npm run build
```

### Writing Documentation

- Use clear, concise language
- Include code examples for all features
- Add type hints to all code samples
- Test all code examples before publishing

### Documentation Structure

```
docs/
├── guide/          # User guides and tutorials
├── api/            # API reference documentation
├── cli/            # CLI documentation
├── examples/       # Code examples
├── developer/      # Developer documentation
└── .vitepress/     # VitePress configuration
```

## Release Process

### Version Management

GrainChain uses semantic versioning (SemVer):

- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backward compatible
- **Patch** (0.0.X): Bug fixes, backward compatible

### Release Checklist

1. **Update version**:
   ```bash
   # Update version in pyproject.toml
   # Update CHANGELOG.md
   ```

2. **Run full test suite**:
   ```bash
   pytest
   python -m benchmarks.run_all
   ```

3. **Build and test package**:
   ```bash
   python -m build
   twine check dist/*
   ```

4. **Create release**:
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```

5. **Publish to PyPI**:
   ```bash
   twine upload dist/*
   ```

## Contributing Guidelines

### Code Style

- Follow PEP 8
- Use type hints for all public APIs
- Write docstrings for all public functions and classes
- Keep functions small and focused

### Commit Messages

Use conventional commit format:

```
type(scope): description

feat(providers): add support for new sandbox provider
fix(cli): resolve issue with command parsing
docs(api): update examples for async usage
test(integration): add tests for E2B provider
```

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## Getting Help

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share ideas
- **Discord**: Join our community for real-time help
- **Email**: Contact maintainers directly for security issues

## Next Steps

- [Contributing Guidelines](/developer/contributing) - Detailed contribution guide
- [Architecture Deep Dive](/developer/architecture) - Detailed architecture documentation
- [Testing Guide](/developer/testing) - Comprehensive testing documentation
- [API Reference](/api/) - Complete API documentation

