# CLI Reference

GrainChain provides a powerful command-line interface for managing sandbox providers, running code, and performing various operations without writing Python code.

## Installation

The CLI is included when you install GrainChain:

```bash
pip install grainchain
```

Verify installation:

```bash
grainchain --version
```

## Basic Usage

```bash
# Check available providers
grainchain providers

# Execute code in a sandbox
grainchain exec "echo 'Hello World'"

# Run a Python script
grainchain run script.py

# Check provider status
grainchain status
```

## Global Options

All commands support these global options:

```bash
grainchain [COMMAND] [OPTIONS]

Global Options:
  --provider TEXT     Specify sandbox provider (e2b, modal, daytona)
  --config PATH       Path to configuration file
  --verbose          Enable verbose output
  --quiet            Suppress non-essential output
  --help             Show help message
```

## Core Commands

### `providers`
Manage and check sandbox providers.

```bash
# List all providers
grainchain providers

# Check specific provider
grainchain providers --check e2b

# Show setup instructions
grainchain providers --setup

# Show only available providers
grainchain providers --available-only
```

### `exec`
Execute commands in a sandbox.

```bash
# Basic execution
grainchain exec "python --version"

# With specific provider
grainchain exec --provider modal "pip list"

# With timeout
grainchain exec --timeout 30 "long_running_command"

# With environment variables
grainchain exec --env API_KEY=secret "python app.py"
```

### `run`
Execute files in a sandbox.

```bash
# Run Python script
grainchain run script.py

# Run with arguments
grainchain run script.py --args "arg1 arg2"

# Upload and run
grainchain run local_script.py --upload

# Run with specific working directory
grainchain run script.py --cwd /workspace
```

### `upload`
Upload files to sandbox.

```bash
# Upload single file
grainchain upload local_file.txt /remote/path/

# Upload directory
grainchain upload ./local_dir/ /remote/dir/ --recursive

# Upload with specific provider
grainchain upload --provider e2b file.txt /workspace/
```

### `download`
Download files from sandbox.

```bash
# Download single file
grainchain download /remote/file.txt ./local_file.txt

# Download directory
grainchain download /remote/dir/ ./local_dir/ --recursive

# Download to stdout
grainchain download /remote/log.txt -
```

## Configuration

### Configuration File

Create a configuration file at `~/.grainchain/config.yaml`:

```yaml
default_provider: e2b
timeout: 30
max_retries: 3

providers:
  e2b:
    api_key: ${E2B_API_KEY}
    template: python-3.11
  
  modal:
    token: ${MODAL_TOKEN}
    image: python:3.11-slim
  
  daytona:
    api_url: ${DAYTONA_API_URL}
    api_key: ${DAYTONA_API_KEY}
```

### Environment Variables

```bash
# Provider credentials
export E2B_API_KEY="your-e2b-key"
export MODAL_TOKEN="your-modal-token"
export DAYTONA_API_KEY="your-daytona-key"

# Global settings
export GRAINCHAIN_PROVIDER="e2b"
export GRAINCHAIN_TIMEOUT="60"
export GRAINCHAIN_LOG_LEVEL="INFO"
```

## Advanced Usage

### Batch Operations

```bash
# Run multiple commands
grainchain batch commands.txt

# Where commands.txt contains:
# exec "pip install requests"
# run setup.py
# exec "python test.py"
```

### Monitoring and Debugging

```bash
# Enable debug logging
grainchain --verbose exec "python script.py"

# Monitor resource usage
grainchain exec --monitor "python heavy_script.py"

# Save execution logs
grainchain exec --log-file execution.log "python script.py"
```

### Provider Management

```bash
# Test provider connectivity
grainchain test --provider e2b

# Show provider capabilities
grainchain info --provider modal

# Reset provider configuration
grainchain reset --provider daytona
```

## Examples

### Development Workflow

```bash
# Check if providers are set up
grainchain providers --available-only

# Upload your project
grainchain upload ./my_project/ /workspace/ --recursive

# Install dependencies
grainchain exec "cd /workspace && pip install -r requirements.txt"

# Run tests
grainchain exec "cd /workspace && python -m pytest"

# Download results
grainchain download /workspace/test_results.xml ./
```

### CI/CD Integration

```bash
#!/bin/bash
# ci-script.sh

# Validate code in sandbox
grainchain run validate.py --provider e2b

# Run security checks
grainchain exec --provider modal "bandit -r /workspace"

# Performance testing
grainchain exec --timeout 300 "python benchmark.py"
```

## Troubleshooting

### Common Issues

```bash
# Check provider status
grainchain status

# Test connectivity
grainchain test --all-providers

# Reset configuration
grainchain config --reset

# Show debug information
grainchain debug
```

### Getting Help

```bash
# General help
grainchain --help

# Command-specific help
grainchain exec --help
grainchain providers --help

# Show version and system info
grainchain version --verbose
```

## Next Steps

- [Commands Reference](/cli/commands) - Detailed command documentation
- [Configuration Guide](/cli/configuration) - Advanced configuration options
- [CLI Examples](/cli/examples) - Practical CLI usage examples
- [API Reference](/api/) - Python API documentation

