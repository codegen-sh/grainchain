---
layout: home

hero:
  name: "GrainChain"
  text: "Langchain for Sandboxes"
  tagline: A powerful framework for building sandbox-aware AI applications
  image:
    src: /logo.svg
    alt: GrainChain
  actions:
    - theme: brand
      text: Get Started
      link: /guide/
    - theme: alt
      text: View on GitHub
      link: https://github.com/codegen-sh/grainchain

features:
  - icon: 🏗️
    title: Sandbox Integration
    details: Seamlessly integrate with various sandbox providers including E2B, Modal, and Daytona for secure code execution.
  
  - icon: ⚡
    title: High Performance
    details: Optimized for speed with comprehensive benchmarking tools to measure and improve performance across different scenarios.
  
  - icon: 🔧
    title: Flexible Architecture
    details: Modular design that supports multiple providers and execution environments with easy configuration and customization.
  
  - icon: 🛡️
    title: Secure Execution
    details: Built-in security features and isolation mechanisms to ensure safe execution of untrusted code in controlled environments.
  
  - icon: 📊
    title: Comprehensive Monitoring
    details: Built-in analytics and monitoring capabilities to track performance, usage patterns, and system health.
  
  - icon: 🚀
    title: Production Ready
    details: Battle-tested framework with extensive documentation, examples, and best practices for production deployments.
---

## Quick Start

Get up and running with GrainChain in minutes:

```bash
# Install GrainChain
pip install grainchain

# Set up your environment
cp .env.example .env
# Edit .env with your provider credentials

# Run a simple example
python -c "
from grainchain import GrainChain
gc = GrainChain()
result = gc.execute('print(\"Hello, GrainChain!\")')
print(result)
"
```

## What is GrainChain?

GrainChain is a powerful framework that extends Langchain with sandbox-aware capabilities, enabling you to build AI applications that can safely execute code in isolated environments. It provides seamless integration with multiple sandbox providers and offers comprehensive tools for monitoring, benchmarking, and optimizing your applications.

### Key Capabilities

- **Multi-Provider Support**: Works with E2B, Modal, Daytona, and other sandbox providers
- **Secure Code Execution**: Safe execution of untrusted code in isolated environments
- **Performance Optimization**: Built-in benchmarking and performance monitoring tools
- **Flexible Configuration**: Easy setup and customization for different use cases
- **Production Ready**: Comprehensive error handling, logging, and monitoring
- **Extensible Architecture**: Plugin system for custom providers and extensions

### Use Cases

- **AI Code Generation**: Safely execute and test generated code
- **Educational Platforms**: Provide secure coding environments for students
- **Code Analysis**: Analyze and execute code in controlled environments
- **Automated Testing**: Run tests in isolated sandbox environments
- **Research & Development**: Experiment with code execution patterns safely

## Architecture Overview

```mermaid
graph TB
    A[GrainChain Core] --> B[Provider Manager]
    B --> C[E2B Provider]
    B --> D[Modal Provider]
    B --> E[Daytona Provider]
    B --> F[Custom Provider]
    
    A --> G[Execution Engine]
    G --> H[Code Validator]
    G --> I[Resource Monitor]
    G --> J[Result Processor]
    
    A --> K[Analytics Engine]
    K --> L[Performance Metrics]
    K --> M[Usage Analytics]
    K --> N[Health Monitoring]
```

## Getting Help

- 📖 [Read the Guide](/guide/) - Comprehensive documentation
- 🔧 [API Reference](/api/) - Detailed API documentation
- 💻 [CLI Reference](/cli/) - Command-line interface guide
- 📝 [Examples](/examples/) - Practical examples and tutorials
- 🐛 [Report Issues](https://github.com/codegen-sh/grainchain/issues) - Bug reports and feature requests
- 💬 [Join our Discord](https://discord.gg/codegen) - Community support

## Quick Links

- [Installation Guide](/guide/installation) - Get GrainChain installed
- [Configuration](/guide/configuration) - Set up your environment
- [API Features](/api/features) - Explore core functionality
- [Benchmarking](/guide/benchmarking) - Performance testing tools
- [Troubleshooting](/guide/troubleshooting) - Common issues and solutions

