# Grainchain Troubleshooting Guide

This guide helps you resolve common issues when using Grainchain.

## Quick Diagnostics

Before diving into specific issues, run these commands to check your setup:

```bash
# Check Python version (requires 3.12+)
python --version

# Check if grainchain is installed
grainchain --version

# Test basic functionality
grainchain benchmark --provider local

# Check environment variables
echo "E2B_API_KEY: $E2B_API_KEY"
echo "MORPH_API_KEY: $MORPH_API_KEY"
echo "DAYTONA_API_KEY: $DAYTONA_API_KEY"
```

## Installation Issues

### Python Version Issues

**Problem**: `Python version not supported` or compatibility errors

**Solution**:
```bash
# Check current Python version
python --version

# Install Python 3.12+ using your system package manager
# Ubuntu/Debian:
sudo apt update && sudo apt install python3.12

# macOS with Homebrew:
brew install python@3.12

# Windows: Download from python.org
```

### Package Installation Issues

**Problem**: `ModuleNotFoundError: No module named 'grainchain'`

**Solutions**:
```bash
# Option 1: Install with pip
pip install grainchain

# Option 2: Install with uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv add grainchain

# Option 3: Development installation
git clone https://github.com/codegen-sh/grainchain.git
cd grainchain
uv sync  # or pip install -e .
```

**Problem**: `Permission denied` during installation

**Solutions**:
```bash
# Option 1: Use --user flag
pip install --user grainchain

# Option 2: Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install grainchain

# Option 3: Use uv (handles virtual environments automatically)
uv add grainchain
```

### Command Not Found

**Problem**: `grainchain: command not found`

**Solutions**:
```bash
# Check if grainchain is in PATH
which grainchain

# If using --user installation, add to PATH
export PATH="$HOME/.local/bin:$PATH"

# If using virtual environment, activate it
source venv/bin/activate

# If using uv, run with uv
uv run grainchain --version
```

## Provider Configuration Issues

### API Key Problems

**Problem**: `ProviderError: API key not found` or `Authentication failed`

**Solutions**:
```bash
# Set environment variables
export E2B_API_KEY="your-e2b-api-key"
export MORPH_API_KEY="your-morph-api-key"
export DAYTONA_API_KEY="your-daytona-api-key"

# Or create a .env file in your project directory
echo "E2B_API_KEY=your-e2b-api-key" > .env
echo "MORPH_API_KEY=your-morph-api-key" >> .env
echo "DAYTONA_API_KEY=your-daytona-api-key" >> .env

# Verify environment variables are set
env | grep API_KEY
```

**Problem**: Invalid or expired API keys

**Solutions**:
1. **E2B**: Get a new API key from [E2B Dashboard](https://e2b.dev/dashboard)
2. **Morph**: Get a new API key from [Morph Dashboard](https://morph.dev/dashboard)
3. **Daytona**: Get a new API key from [Daytona Dashboard](https://daytona.io/dashboard)

### Provider Connection Issues

**Problem**: `Connection timeout` or `Provider unavailable`

**Solutions**:
```bash
# Test with local provider first (no network required)
grainchain benchmark --provider local

# Check internet connectivity
ping google.com

# Try with increased timeout
python -c "
import asyncio
from grainchain import Sandbox, SandboxConfig

async def test():
    config = SandboxConfig(timeout=300)  # 5 minutes
    async with Sandbox(provider='e2b', config=config) as sandbox:
        result = await sandbox.execute('echo test')
        print(result.stdout)

asyncio.run(test())
"
```

## Runtime Issues

### File Operation Errors

**Problem**: `Directory not found: /workspace`

**Solution**:
```python
# Use relative paths for local provider
files = await sandbox.list_files(".")  # Instead of "/workspace"

# Check current working directory
result = await sandbox.execute("pwd")
print(f"Working directory: {result.stdout}")

# List files in current directory
result = await sandbox.execute("ls -la")
print(result.stdout)
```

**Problem**: `File not found` errors

**Solutions**:
```python
# Check if file exists before operations
result = await sandbox.execute("ls -la myfile.txt")
if result.return_code == 0:
    content = await sandbox.download_file("myfile.txt")
else:
    print("File does not exist")

# Use absolute paths when needed
await sandbox.upload_file("/tmp/myfile.txt", "content")
```

**Problem**: `Permission denied` errors

**Solutions**:
```python
# Make files executable
await sandbox.execute("chmod +x script.sh")

# Change file ownership if needed
await sandbox.execute("chown user:group file.txt")

# Check file permissions
result = await sandbox.execute("ls -la file.txt")
print(result.stdout)
```

### Execution Errors

**Problem**: Commands fail with non-zero exit codes

**Solutions**:
```python
# Always check execution results
result = await sandbox.execute("your_command")
if not result.success:
    print(f"Command failed with code {result.return_code}")
    print(f"Error: {result.stderr}")
    print(f"Output: {result.stdout}")

# Handle specific error codes
if result.return_code == 127:
    print("Command not found")
elif result.return_code == 1:
    print("General error")
```

**Problem**: `ModuleNotFoundError` in sandbox

**Solutions**:
```python
# Install packages in sandbox
await sandbox.execute("pip install pandas numpy")

# Check Python path
result = await sandbox.execute("python -c 'import sys; print(sys.path)'")
print(result.stdout)

# Use specific Python version
await sandbox.execute("python3 -m pip install package_name")
```

### Timeout Issues

**Problem**: Operations timeout

**Solutions**:
```python
# Increase timeout in configuration
config = SandboxConfig(timeout=600)  # 10 minutes
async with Sandbox(provider="local", config=config) as sandbox:
    # Long-running operations

# Break down large operations
# Instead of installing many packages at once:
packages = ["pandas", "numpy", "matplotlib"]
for package in packages:
    result = await sandbox.execute(f"pip install {package}")
    if not result.success:
        print(f"Failed to install {package}: {result.stderr}")
```

### Memory and Performance Issues

**Problem**: Sandbox runs out of memory

**Solutions**:
```python
# Use provider-specific configuration for more resources
config = SandboxConfig(
    provider_config={
        "memory": 4096,  # 4GB RAM
        "vcpus": 2,      # 2 CPU cores
    }
)

# Process data in chunks
# Instead of loading large datasets at once
chunk_size = 1000
for i in range(0, len(data), chunk_size):
    chunk = data[i:i+chunk_size]
    # Process chunk
```

## Debugging Tips

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your grainchain code here
```

### Inspect Sandbox State

```python
async with Sandbox() as sandbox:
    # Check environment
    result = await sandbox.execute("env")
    print("Environment variables:", result.stdout)

    # Check available commands
    result = await sandbox.execute("which python")
    print("Python location:", result.stdout)

    # Check disk space
    result = await sandbox.execute("df -h")
    print("Disk usage:", result.stdout)

    # Check memory
    result = await sandbox.execute("free -h")
    print("Memory usage:", result.stdout)
```

### Test Individual Components

```python
# Test basic execution
async def test_basic():
    async with Sandbox() as sandbox:
        result = await sandbox.execute("echo 'Hello World'")
        assert result.success
        assert "Hello World" in result.stdout

# Test file operations
async def test_files():
    async with Sandbox() as sandbox:
        await sandbox.upload_file("test.txt", "test content")
        content = await sandbox.download_file("test.txt")
        assert content.decode() == "test content"

# Run tests
import asyncio
asyncio.run(test_basic())
asyncio.run(test_files())
```

## Common Error Messages

### `SandboxError: Failed to create sandbox`

**Causes**:
- Invalid provider configuration
- Network connectivity issues
- API key problems

**Solutions**:
1. Test with local provider first
2. Check API keys and network connectivity
3. Verify provider-specific configuration

### `ProviderError: Operation not supported`

**Causes**:
- Using features not available in current provider
- Provider-specific limitations

**Solutions**:
1. Check provider documentation for supported features
2. Use alternative approaches for unsupported operations
3. Switch to a provider that supports the needed features

### `TimeoutError: Operation timed out`

**Causes**:
- Network latency
- Large file transfers
- Complex computations

**Solutions**:
1. Increase timeout in SandboxConfig
2. Break operations into smaller chunks
3. Use local provider for development/testing

## Getting Additional Help

### Self-Help Resources

1. **Run diagnostics**: `grainchain benchmark --provider local`
2. **Check examples**: Look at working code in `examples/` directory
3. **Read documentation**: Review README.md and other docs
4. **Check GitHub issues**: Search for similar problems

### Community Support

1. **GitHub Issues**: [Report bugs or ask questions](https://github.com/codegen-sh/grainchain/issues)
2. **Discord Community**: [Join our Discord](https://discord.gg/codegen)
3. **Documentation**: [Full documentation](https://github.com/codegen-sh/grainchain)

### Reporting Issues

When reporting issues, please include:

1. **Environment information**:
   ```bash
   python --version
   grainchain --version
   uname -a  # On Unix systems
   ```

2. **Error messages**: Full error output and stack traces

3. **Minimal reproduction**: Smallest code example that reproduces the issue

4. **Expected vs actual behavior**: What you expected vs what happened

5. **Configuration**: Provider settings, environment variables (without API keys)

Example issue report:
```
**Environment:**
- Python 3.12.0
- Grainchain 0.1.0
- Ubuntu 22.04

**Issue:**
Getting "Directory not found: /workspace" error when running basic example

**Code:**
```python
# Minimal reproduction code here
```

**Error:**
```
Full error message and stack trace here
```

**Expected:** Should list files in workspace
**Actual:** Throws ProviderError about missing directory
```
