# Quick Start

Get up and running with GrainChain in just a few minutes! This guide will walk you through installation, basic setup, and your first sandbox execution.

## Installation

Install GrainChain using pip:

```bash
pip install grainchain
```

Or install from source for the latest features:

```bash
git clone https://github.com/codegen-sh/grainchain.git
cd grainchain
pip install -e .
```

## Basic Setup

### 1. Check Provider Availability

First, check which sandbox providers are available:

```bash
grainchain providers
```

This will show you which providers are installed and configured. You'll see output like:

```
🔧 Grainchain Sandbox Providers

✅ E2B          - Available (configured)
❌ Modal        - Not configured (missing MODAL_TOKEN)
❌ Daytona      - Not available (package not installed)

Use 'grainchain providers --setup' for configuration instructions.
```

### 2. Configure a Provider

Choose a provider and set up the required credentials:

#### E2B Setup
```bash
# Get your API key from https://e2b.dev
export E2B_API_KEY="your-e2b-api-key"
```

#### Modal Setup
```bash
# Get your token from https://modal.com
export MODAL_TOKEN="your-modal-token"
```

#### Daytona Setup
```bash
# Install the Daytona provider
pip install grainchain[daytona]

# Set up credentials
export DAYTONA_API_URL="your-daytona-url"
export DAYTONA_API_KEY="your-daytona-key"
```

### 3. Verify Setup

Test your configuration:

```bash
grainchain exec "echo 'Hello, GrainChain!'"
```

If everything is set up correctly, you should see:

```
Hello, GrainChain!
```

## Your First Python Script

Let's create and run a simple Python script:

### Using the Python API

```python
import asyncio
from grainchain import Sandbox

async def main():
    # Create a sandbox instance
    async with Sandbox() as sandbox:
        # Upload a Python script
        script_content = '''
import sys
import platform

print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Arguments: {sys.argv[1:]}")

# Simple calculation
numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
print(f"Sum of {numbers} = {total}")
'''
        
        await sandbox.upload_file("hello.py", script_content)
        
        # Execute the script
        result = await sandbox.execute("python hello.py arg1 arg2")
        
        print("Script output:")
        print(result.stdout)
        
        print(f"Exit code: {result.exit_code}")
        print(f"Execution time: {result.execution_time:.2f}s")

# Run the example
asyncio.run(main())
```

### Using the CLI

```bash
# Create a local script
cat > hello.py << 'EOF'
import sys
import platform

print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Arguments: {sys.argv[1:]}")

# Simple calculation
numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
print(f"Sum of {numbers} = {total}")
EOF

# Upload and run the script
grainchain run hello.py --args "arg1 arg2"
```

## Working with Files

### Upload and Download Files

```python
async def file_operations():
    async with Sandbox() as sandbox:
        # Upload a data file
        data = "name,age,city\nAlice,30,New York\nBob,25,San Francisco"
        await sandbox.upload_file("data.csv", data)
        
        # Create a processing script
        processor = '''
import csv

# Read the CSV file
with open("data.csv", "r") as f:
    reader = csv.DictReader(f)
    data = list(reader)

# Process the data
for row in data:
    row["age"] = int(row["age"])
    row["age_group"] = "young" if row["age"] < 30 else "adult"

# Write processed data
with open("processed.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age", "city", "age_group"])
    writer.writeheader()
    writer.writerows(data)

print("Data processed successfully!")
print(f"Processed {len(data)} records")
'''
        
        await sandbox.upload_file("process.py", processor)
        
        # Run the processor
        result = await sandbox.execute("python process.py")
        print(result.stdout)
        
        # Download the processed file
        processed_data = await sandbox.download_file("processed.csv")
        print("Processed data:")
        print(processed_data)

asyncio.run(file_operations())
```

## Error Handling

Always handle errors gracefully:

```python
from grainchain.exceptions import ExecutionError, TimeoutError, ProviderError

async def robust_execution():
    try:
        async with Sandbox() as sandbox:
            # This might fail
            result = await sandbox.execute("python nonexistent.py")
            
    except ExecutionError as e:
        print(f"Script execution failed:")
        print(f"Exit code: {e.exit_code}")
        print(f"Error output: {e.stderr}")
        
    except TimeoutError:
        print("Script execution timed out")
        
    except ProviderError as e:
        print(f"Provider error: {e}")
        print("Check your provider configuration")
        
    except Exception as e:
        print(f"Unexpected error: {e}")

asyncio.run(robust_execution())
```

## Configuration Options

### Environment Variables

```bash
# Default provider
export GRAINCHAIN_PROVIDER="e2b"

# Default timeout (seconds)
export GRAINCHAIN_TIMEOUT="30"

# Log level
export GRAINCHAIN_LOG_LEVEL="INFO"
```

### Configuration File

Create `~/.grainchain/config.yaml`:

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
```

### Programmatic Configuration

```python
from grainchain import configure

# Configure globally
configure({
    "default_provider": "e2b",
    "timeout": 60,
    "max_retries": 3
})

# Or configure per sandbox
sandbox = Sandbox(
    provider="modal",
    timeout=120,
    max_memory="2GB"
)
```

## Common Patterns

### Batch Processing

```python
async def batch_processing():
    commands = [
        "pip install requests",
        "python -c 'import requests; print(requests.__version__)'",
        "python -c 'print(\"Hello from batch!\")'",
    ]
    
    async with Sandbox() as sandbox:
        for i, command in enumerate(commands, 1):
            print(f"Running command {i}/{len(commands)}: {command}")
            result = await sandbox.execute(command)
            
            if result.exit_code == 0:
                print(f"✅ Success: {result.stdout.strip()}")
            else:
                print(f"❌ Failed: {result.stderr.strip()}")

asyncio.run(batch_processing())
```

### Resource Monitoring

```python
async def monitor_resources():
    async with Sandbox() as sandbox:
        # Run a resource-intensive task
        result = await sandbox.execute("""
python -c "
import time
import psutil
import os

print(f'PID: {os.getpid()}')
print(f'Memory usage: {psutil.Process().memory_info().rss / 1024 / 1024:.1f} MB')

# Simulate some work
for i in range(5):
    time.sleep(1)
    print(f'Step {i+1}/5 - Memory: {psutil.Process().memory_info().rss / 1024 / 1024:.1f} MB')
"
        """)
        
        print("Resource monitoring output:")
        print(result.stdout)
        print(f"Total execution time: {result.execution_time:.2f}s")

asyncio.run(monitor_resources())
```

## Next Steps

Now that you have GrainChain running, explore these topics:

- **[Configuration Guide](/guide/configuration)** - Advanced configuration options
- **[API Reference](/api/)** - Complete API documentation
- **[CLI Reference](/cli/)** - Command-line interface guide
- **[Examples](/examples/)** - More practical examples
- **[Troubleshooting](/guide/troubleshooting)** - Common issues and solutions

## Getting Help

If you run into issues:

1. Check the [troubleshooting guide](/guide/troubleshooting)
2. Verify your provider configuration with `grainchain providers --verbose`
3. Enable debug logging: `export GRAINCHAIN_LOG_LEVEL=DEBUG`
4. Join our [Discord community](https://discord.gg/codegen) for help
5. Report bugs on [GitHub Issues](https://github.com/codegen-sh/grainchain/issues)

