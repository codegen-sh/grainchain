# Getting Started with GrainChain

Welcome to GrainChain! This guide will help you get up and running with our sandbox-aware framework for building AI applications.

## What is GrainChain?

GrainChain is a unified Python interface for sandbox providers that extends Langchain with sandbox-aware capabilities. Just like Langchain abstracts LLM providers, GrainChain abstracts sandbox providers, enabling you to write code once and run it across multiple sandbox environments.

## Core Features

### 🏗️ Multi-Provider Support
GrainChain supports multiple sandbox providers out of the box:
- **E2B** - Cloud-based code execution sandboxes
- **Modal** - Serverless compute platform
- **Daytona** - Development environment platform
- **Custom Providers** - Extensible architecture for custom implementations

### ⚡ High Performance
- Optimized execution patterns
- Built-in performance monitoring
- Comprehensive benchmarking tools
- Resource usage tracking

### 🛡️ Secure Execution
- Isolated execution environments
- Resource limits and timeouts
- Safe code execution patterns
- Built-in security validations

### 🔧 Easy Integration
- Simple, consistent API across all providers
- Async/await support
- Context manager patterns
- Comprehensive error handling

## Quick Start

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

## Check Provider Availability

Before using GrainChain, check which sandbox providers are available:

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

## Architecture Overview

GrainChain follows a modular architecture that separates concerns and enables easy extensibility:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │    │   GrainChain    │    │   Providers     │
│   Layer         │◄──►│   Core          │◄──►│   (E2B, Modal) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Code     │    │   Execution     │    │   Sandbox       │
│   & Logic       │    │   Engine        │    │   Environments  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Components

- **Sandbox Interface** - Unified API for all providers
- **Provider Manager** - Handles provider selection and configuration
- **Execution Engine** - Manages code execution and result processing
- **Resource Monitor** - Tracks usage and performance metrics
- **Security Layer** - Validates and sanitizes code execution

## Next Steps

- [Installation](/guide/installation) - Install and set up GrainChain
- [Configuration](/guide/configuration) - Configure providers and settings
- [Quick Start](/guide/quick-start) - Get running in 5 minutes
- [Design Overview](/guide/design) - Understand the architecture
- [API Reference](/api/) - Explore the complete API

## Need Help?

- Check out our [Examples](/examples/) for common use cases
- Read the [CLI Reference](/cli/) for command-line usage
- Visit [Troubleshooting](/guide/troubleshooting) for common issues
- Join our [Discord community](https://discord.gg/codegen) for support

