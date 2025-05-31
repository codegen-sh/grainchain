# Grainchain

**Langchain for sandboxes** - A framework for managing sandbox environments with different providers.

## Overview

Grainchain provides a unified interface for creating and managing sandbox environments across different execution platforms. Currently supports Docker containers with plans for additional providers.

## Features

- **Docker Provider**: Full Docker container management
- **Async/Await Support**: Modern Python async programming
- **File Operations**: Upload/download files to/from sandboxes
- **Command Execution**: Execute commands with environment control
- **Resource Management**: CPU, memory, and network configuration
- **Session Management**: Create, manage, and cleanup sandbox sessions
- **Error Handling**: Comprehensive error handling and recovery

## Installation

```bash
pip install grainchain
```

For development:
```bash
git clone https://github.com/codegen-sh/grainchain.git
cd grainchain
pip install -e ".[dev]"
```

## Quick Start

### Basic Docker Usage

```python
import asyncio
from grainchain.providers.docker import DockerProvider

async def main():
    # Create provider
    provider = DockerProvider({
        'default_image': 'python:3.9-slim',
        'resource_limits': {'mem_limit': '512m'}
    })
    
    # Create and start session
    session = await provider.create_session()
    
    async with session:
        # Execute commands
        result = await session.execute_command("python --version")
        print(result['stdout'])
        
        # Upload and run a script
        await session.upload_file("local_script.py", "/tmp/script.py")
        result = await session.execute_command("python /tmp/script.py")
        print(result['stdout'])

asyncio.run(main())
```

### File Operations

```python
async def file_example():
    provider = DockerProvider()
    session = await provider.create_session(image="alpine:latest")
    
    async with session:
        # Upload file
        success = await session.upload_file("local_file.txt", "/remote/path.txt")
        
        # List files
        files = await session.list_files("/remote")
        for file_info in files:
            print(f"{file_info['name']} - {file_info['size']} bytes")
        
        # Download file
        success = await session.download_file("/remote/path.txt", "downloaded.txt")
```

## Configuration

### Docker Provider Configuration

```python
config = {
    'docker_url': 'tcp://localhost:2376',  # Optional: custom Docker daemon
    'default_image': 'ubuntu:20.04',       # Default container image
    'resource_limits': {
        'mem_limit': '1g',                  # Memory limit
        'cpu_count': 2                      # CPU count
    },
    'network_config': {
        'network_mode': 'bridge'            # Network mode
    },
    'volume_mounts': {
        '/host/path': {
            'bind': '/container/path',
            'mode': 'rw'
        }
    }
}

provider = DockerProvider(config)
```

### Session Configuration

```python
session = await provider.create_session(
    session_id="my-session",
    image="python:3.9-slim",
    working_dir="/workspace",
    environment={'DEBUG': 'true'},
    mem_limit="512m",
    cpu_count=1
)
```

## API Reference

### BaseSandboxProvider

Base class for all sandbox providers.

#### Methods

- `create_session(session_id=None, image=None, **kwargs)` - Create new session
- `destroy_session(session_id)` - Destroy existing session
- `get_session(session_id)` - Get session by ID
- `list_sessions()` - List all active sessions
- `cleanup_all_sessions()` - Clean up all sessions

### BaseSandboxSession

Base class for all sandbox sessions.

#### Methods

- `start()` - Start the sandbox session
- `stop()` - Stop the sandbox session
- `execute_command(command, working_dir=None, timeout=None, env=None)` - Execute command
- `upload_file(local_path, remote_path)` - Upload file to sandbox
- `download_file(remote_path, local_path)` - Download file from sandbox
- `list_files(path="/")` - List files in directory

#### Properties

- `is_active` - Check if session is active
- `session_id` - Session identifier

### DockerProvider

Docker-specific implementation of BaseSandboxProvider.

### DockerSession

Docker-specific implementation of BaseSandboxSession.

## Testing

Run unit tests (no Docker required):
```bash
pytest tests/unit/ -m unit
```

Run integration tests (requires Docker):
```bash
pytest tests/integration/ -m integration
```

Run all tests:
```bash
pytest
```

## Examples

See the `examples/` directory for comprehensive usage examples:

- `docker_usage.py` - Complete Docker provider examples
- Basic usage patterns
- File operations
- Multiple sessions
- Error handling
- Advanced configuration

## Development

### Setup Development Environment

```bash
git clone https://github.com/codegen-sh/grainchain.git
cd grainchain
pip install -e ".[dev]"
```

### Running Tests

```bash
# Unit tests only
pytest tests/unit/

# Integration tests (requires Docker)
pytest tests/integration/

# All tests
pytest

# With coverage
pytest --cov=grainchain
```

### Code Quality

```bash
# Format code
black grainchain/ tests/ examples/

# Lint code
flake8 grainchain/ tests/ examples/

# Type checking
mypy grainchain/
```

## Requirements

- Python 3.8+
- Docker (for Docker provider)
- docker-py library

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Roadmap

- [ ] Additional providers (Kubernetes, VM-based)
- [ ] Enhanced networking options
- [ ] Persistent storage support
- [ ] Monitoring and metrics
- [ ] Security enhancements
- [ ] Performance optimizations

