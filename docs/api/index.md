# API Reference

GrainChain provides a comprehensive Python API for interacting with sandbox providers. This section covers all the core classes, methods, and interfaces you need to build sandbox-aware applications.

## Core Classes

### Sandbox
The main interface for interacting with sandbox environments.

```python
from grainchain import Sandbox

# Create a sandbox instance
sandbox = Sandbox(provider="e2b")

# Use as context manager (recommended)
async with Sandbox() as sandbox:
    result = await sandbox.execute("echo 'Hello World'")
    print(result.stdout)
```

### SandboxResult
Represents the result of code execution in a sandbox.

```python
class SandboxResult:
    stdout: str          # Standard output
    stderr: str          # Standard error  
    exit_code: int       # Exit code
    execution_time: float # Execution time in seconds
    resource_usage: dict  # Resource usage metrics
```

### Provider Interface
Base interface that all sandbox providers implement.

```python
from grainchain.providers import BaseProvider

class CustomProvider(BaseProvider):
    async def execute(self, command: str) -> SandboxResult:
        # Custom implementation
        pass
```

## Quick Reference

### Basic Operations

```python
# Execute a command
result = await sandbox.execute("python script.py")

# Upload a file
await sandbox.upload_file("data.txt", content="Hello World")

# Download a file
content = await sandbox.download_file("output.txt")

# List files
files = await sandbox.list_files("/workspace")

# Check if file exists
exists = await sandbox.file_exists("config.json")
```

### Advanced Features

```python
# Execute with timeout
result = await sandbox.execute("long_running_script.py", timeout=30)

# Execute with environment variables
result = await sandbox.execute(
    "python app.py", 
    env={"API_KEY": "secret", "DEBUG": "true"}
)

# Execute with working directory
result = await sandbox.execute("make build", cwd="/project")

# Stream output in real-time
async for line in sandbox.stream_execute("tail -f log.txt"):
    print(line)
```

## Provider-Specific Features

Different providers offer unique capabilities:

### E2B Provider
```python
from grainchain.providers import E2BProvider

# Create with specific template
provider = E2BProvider(template="python-3.11")

# Access E2B-specific features
await provider.install_package("numpy")
await provider.create_snapshot("my-snapshot")
```

### Modal Provider
```python
from grainchain.providers import ModalProvider

# Create with custom image
provider = ModalProvider(image="python:3.11-slim")

# Use Modal-specific features
await provider.mount_volume("/data", volume_name="my-data")
```

## Error Handling

GrainChain provides comprehensive error handling:

```python
from grainchain.exceptions import (
    SandboxError,
    ExecutionError,
    TimeoutError,
    ProviderError
)

try:
    result = await sandbox.execute("risky_command")
except TimeoutError:
    print("Command timed out")
except ExecutionError as e:
    print(f"Execution failed: {e.stderr}")
except ProviderError as e:
    print(f"Provider error: {e}")
```

## Configuration

Configure GrainChain through environment variables or configuration files:

```python
from grainchain import configure

# Configure globally
configure({
    "default_provider": "e2b",
    "timeout": 30,
    "max_retries": 3,
    "log_level": "INFO"
})

# Or configure per sandbox
sandbox = Sandbox(
    provider="modal",
    timeout=60,
    max_memory="2GB"
)
```

## Next Steps

- [Core Features](/api/features) - Detailed feature documentation
- [Provider Guide](/api/providers) - Provider-specific documentation
- [Sandbox Management](/api/sandbox) - Advanced sandbox operations
- [Examples](/examples/) - Practical usage examples

