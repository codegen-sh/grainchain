# Grainchain: Langchain for Sandboxes

## Overview

Grainchain is a unified Python library that provides a standardized interface for interacting with various sandbox providers. Inspired by Langchain's approach to LLM abstraction, Grainchain abstracts away the differences between sandbox providers, enabling developers to write code once and run it across multiple sandbox environments.

## Motivation

The sandbox ecosystem is rapidly expanding with providers like E2B, Modal, and others offering different APIs and capabilities. This fragmentation creates several challenges:

- **Vendor Lock-in**: Applications become tightly coupled to specific sandbox providers
- **Learning Curve**: Developers must learn multiple APIs for different providers
- **Migration Complexity**: Switching between providers requires significant code changes
- **Testing Challenges**: Testing across multiple providers is cumbersome

Grainchain solves these problems by providing a unified interface that abstracts provider-specific implementations.

## Core Principles

1. **Provider Agnostic**: Write once, run anywhere
2. **Clean API**: Simple, intuitive interface inspired by Langchain
3. **Extensible**: Easy to add new sandbox providers
4. **Type Safe**: Full TypeScript-style type hints for Python
5. **Async First**: Built for modern async/await patterns
6. **Production Ready**: Robust error handling and logging

## Architecture

### High-Level Architecture

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

### Core Components

1. **Sandbox Interface**: Abstract base class defining the standard API
2. **Provider Adapters**: Concrete implementations for each sandbox provider
3. **Configuration Manager**: Handles provider-specific configuration
4. **Session Manager**: Manages sandbox lifecycle and connections
5. **Error Handler**: Standardizes error handling across providers

## API Design

### Basic Usage

```python
from grainchain import Sandbox

# Create a sandbox (auto-detects provider from config)
async with Sandbox() as sandbox:
    # Execute code
    result = await sandbox.execute("print('Hello, World!')")
    print(result.stdout)  # "Hello, World!"

    # Upload files
    await sandbox.upload_file("script.py", content="print('uploaded')")

    # Execute uploaded file
    result = await sandbox.execute("python script.py")

    # Download files
    content = await sandbox.download_file("output.txt")
```

### Provider-Specific Usage

```python
from grainchain import Sandbox
from grainchain.providers import E2BProvider, ModalProvider

# Use specific provider
async with Sandbox(provider=E2BProvider()) as sandbox:
    result = await sandbox.execute("pip install numpy")

# Or configure via string
async with Sandbox(provider="modal") as sandbox:
    result = await sandbox.execute("echo 'Using Modal'")
```

### Advanced Configuration

```python
from grainchain import Sandbox, SandboxConfig
from grainchain.providers import E2BProvider

config = SandboxConfig(
    image="python:3.11",
    timeout=300,
    memory_limit="2GB",
    cpu_limit=2.0,
    environment_vars={"API_KEY": "secret"},
    working_directory="/workspace"
)

provider = E2BProvider(
    api_key="your-e2b-key",
    template="python-data-science"
)

async with Sandbox(provider=provider, config=config) as sandbox:
    result = await sandbox.execute("python analysis.py")
```

## Core Interface

### Sandbox Class

```python
class Sandbox:
    """Main sandbox interface"""

    async def __aenter__(self) -> 'Sandbox':
        """Async context manager entry"""

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""

    async def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        working_dir: Optional[str] = None
    ) -> ExecutionResult:
        """Execute a command in the sandbox"""

    async def upload_file(
        self,
        path: str,
        content: Union[str, bytes],
        mode: str = "w"
    ) -> None:
        """Upload a file to the sandbox"""

    async def download_file(self, path: str) -> bytes:
        """Download a file from the sandbox"""

    async def list_files(self, path: str = "/") -> List[FileInfo]:
        """List files in the sandbox"""

    async def create_snapshot(self) -> str:
        """Create a snapshot of the current sandbox state"""

    async def restore_snapshot(self, snapshot_id: str) -> None:
        """Restore sandbox to a previous snapshot"""

    @property
    def status(self) -> SandboxStatus:
        """Get current sandbox status"""
```

### ExecutionResult Class

```python
@dataclass
class ExecutionResult:
    """Result of command execution"""
    stdout: str
    stderr: str
    return_code: int
    execution_time: float
    success: bool

    @property
    def output(self) -> str:
        """Combined stdout and stderr"""
        return f"{self.stdout}\n{self.stderr}".strip()
```

## Provider Support

### Phase 1: Core Providers

1. **E2B Provider**
   - Code interpreter sandboxes
   - Custom image support
   - File operations
   - Snapshot support

2. **Modal Provider**
   - Serverless sandbox execution
   - GPU support
   - Custom environments
   - Volume mounting

### Phase 2: Extended Providers

3. **Local Provider** (for development/testing)
4. **Docker Provider** (coming soon - not currently supported)
5. **AWS Lambda Provider** (serverless execution)
6. **Google Cloud Run Provider**

## Configuration

### Environment Variables

```bash
# Default provider
GRAINCHAIN_DEFAULT_PROVIDER=e2b

# Provider-specific configuration
E2B_API_KEY=your-e2b-key
E2B_TEMPLATE=python-data-science

MODAL_TOKEN_ID=your-modal-token-id
MODAL_TOKEN_SECRET=your-modal-token-secret
```

### Configuration File

```yaml
# grainchain.yaml
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

## Error Handling

### Standard Exceptions

```python
class GrainchainError(Exception):
    """Base exception for all Grainchain errors"""

class SandboxError(GrainchainError):
    """Sandbox operation failed"""

class ProviderError(GrainchainError):
    """Provider-specific error"""

class ConfigurationError(GrainchainError):
    """Configuration error"""

class TimeoutError(GrainchainError):
    """Operation timed out"""

class AuthenticationError(GrainchainError):
    """Authentication failed"""
```

## Testing Strategy

### Unit Tests
- Mock provider implementations
- Test core interface functionality
- Configuration validation

### Integration Tests
- Real provider testing (with test accounts)
- End-to-end workflow testing
- Performance benchmarking

### Provider Tests
- Provider-specific functionality
- Error handling scenarios
- Resource cleanup verification

## Development Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Core interface design
- [ ] Base provider abstraction
- [ ] Configuration system
- [ ] Basic E2B provider implementation

### Phase 2: Core Features (Weeks 3-4)
- [ ] Modal provider implementation
- [ ] File operations
- [ ] Error handling
- [ ] Basic testing suite

### Phase 3: Advanced Features (Weeks 5-6)
- [ ] Snapshot support
- [ ] Async optimizations
- [ ] Comprehensive documentation
- [ ] Performance benchmarking

### Phase 4: Production Ready (Weeks 7-8)
- [ ] PyPI packaging
- [ ] CI/CD pipeline
- [ ] Integration examples
- [ ] Production deployment guide

## File Structure

```
grainchain/
├── grainchain/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── sandbox.py          # Main Sandbox class
│   │   ├── interfaces.py       # Abstract interfaces
│   │   ├── config.py          # Configuration management
│   │   └── exceptions.py      # Exception classes
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py           # Base provider class
│   │   ├── e2b.py            # E2B provider
│   │   ├── modal.py          # Modal provider
│   │   └── local.py          # Local provider (for testing)
│   └── utils/
│       ├── __init__.py
│       ├── logging.py        # Logging utilities
│       └── helpers.py        # Helper functions
├── tests/
│   ├── unit/
│   ├── integration/
│   └── providers/
├── examples/
│   ├── basic_usage.py
│   ├── data_analysis.py
│   └── multi_provider.py
├── docs/
│   ├── api_reference.md
│   ├── provider_guide.md
│   └── examples.md
├── pyproject.toml
├── README.md
├── DESIGN.md
└── CHANGELOG.md
```

## Success Metrics

1. **Developer Experience**: Time to first successful sandbox execution < 5 minutes
2. **Performance**: < 100ms overhead compared to direct provider APIs
3. **Reliability**: 99.9% success rate for basic operations
4. **Adoption**: 100+ GitHub stars within 3 months of PyPI release
5. **Community**: Active contributor base and issue resolution

## Future Considerations

1. **Plugin System**: Allow third-party provider implementations
2. **Monitoring**: Built-in metrics and observability
3. **Cost Optimization**: Intelligent provider selection based on cost
4. **Security**: Enhanced security features and audit logging
5. **Multi-language Support**: SDKs for other programming languages

---

This design document serves as the foundation for building Grainchain. It will be updated as the project evolves and new requirements emerge.
