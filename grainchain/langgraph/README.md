# Grainchain LangGraph Integration

This module provides seamless integration between Grainchain sandbox providers and LangGraph, enabling you to build AI agents that can execute code safely in isolated environments.

## Overview

The LangGraph integration offers:

- **🛠️ LangChain Tools**: Ready-to-use tools for sandbox operations
- **🤖 Pre-built Agents**: Complete agent implementations with sensible defaults
- **🔧 Local Integration**: Optimized patterns for local development
- **📦 Agent Management**: Tools for managing multiple agents

## Quick Start

### Basic Usage

```python
from langchain_openai import ChatOpenAI
from grainchain.langgraph import create_local_sandbox_agent

# Create LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# Create agent
agent = create_local_sandbox_agent(llm)

# Use the agent
response = await agent.arun("Create a Python script that prints 'Hello, World!'")
print(response)
```

### Using Individual Tools

```python
from langchain_openai import ChatOpenAI
from grainchain.langgraph.tools import SandboxTool
from langgraph.prebuilt import create_react_agent

# Create tools
sandbox_tool = SandboxTool(provider="local")

# Create agent with tools
llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(llm, [sandbox_tool])

# Use the agent
response = agent.invoke({"messages": [("user", "Run 'echo Hello World'")]})
```

## Components

### 1. Tools (`grainchain.langgraph.tools`)

#### SandboxTool
Execute commands in a sandbox environment.

```python
from grainchain.langgraph.tools import SandboxTool

tool = SandboxTool(provider="local")
result = await tool._arun("python --version")
```

#### SandboxFileUploadTool
Upload files to the sandbox.

```python
from grainchain.langgraph.tools import SandboxFileUploadTool

upload_tool = SandboxFileUploadTool(sandbox_tool=sandbox_tool)
result = await upload_tool._arun("script.py", "print('Hello!')")
```

#### SandboxSnapshotTool
Create and restore sandbox snapshots.

```python
from grainchain.langgraph.tools import SandboxSnapshotTool

snapshot_tool = SandboxSnapshotTool(sandbox_tool=sandbox_tool)
snapshot_id = await snapshot_tool._arun("create")
await snapshot_tool._arun("restore", snapshot_id=snapshot_id)
```

### 2. Agents (`grainchain.langgraph.agent`)

#### SandboxAgent
A complete LangGraph agent with sandbox capabilities.

```python
from grainchain.langgraph.agent import SandboxAgent
from grainchain.core.interfaces import SandboxConfig

config = SandboxConfig(timeout=120, working_directory="/workspace")
agent = SandboxAgent(
    llm=llm,
    provider="e2b",
    config=config,
    system_message="You are a Python coding assistant."
)

response = await agent.arun("Write a function to calculate fibonacci numbers")
```

#### Factory Function
Convenient agent creation:

```python
from grainchain.langgraph import create_sandbox_agent

agent = create_sandbox_agent(
    llm=llm,
    provider="local",
    additional_tools=[custom_tool]
)
```

### 3. Local Integration (`grainchain.langgraph.local_integration`)

#### LocalSandboxAgent
Optimized for local development:

```python
from grainchain.langgraph.local_integration import LocalSandboxAgent

agent = LocalSandboxAgent(
    llm=llm,
    working_directory="./workspace",
    timeout=60
)
```

#### SandboxAgentManager
Manage multiple agents:

```python
from grainchain.langgraph.local_integration import SandboxAgentManager

manager = SandboxAgentManager()
manager.add_local_agent("dev", llm)
manager.add_agent("prod", llm, provider="e2b")

# Use different agents
dev_response = manager.run("Test locally", agent_name="dev")
prod_response = manager.run("Deploy code", agent_name="prod")
```

## Advanced Usage

### Custom Tools Integration

```python
from langchain_core.tools import tool
from grainchain.langgraph import create_sandbox_agent

@tool
def custom_analysis_tool(data: str) -> str:
    """Analyze data using custom logic."""
    return f"Analysis result: {len(data)} characters"

agent = create_sandbox_agent(
    llm=llm,
    provider="local",
    additional_tools=[custom_analysis_tool]
)
```

### Provider-Specific Configuration

```python
from grainchain.core.interfaces import SandboxConfig
from grainchain.langgraph import SandboxAgent

# E2B configuration
e2b_config = SandboxConfig(
    image="python:3.11",
    timeout=300,
    environment_vars={"API_KEY": "secret"}
)

e2b_agent = SandboxAgent(
    llm=llm,
    provider="e2b",
    config=e2b_config
)

# Local configuration
local_config = SandboxConfig(
    working_directory="/tmp/sandbox",
    timeout=60,
    auto_cleanup=True
)

local_agent = SandboxAgent(
    llm=llm,
    provider="local",
    config=local_config
)
```

### Async/Sync Usage

```python
# Async usage (recommended)
async def async_example():
    agent = create_local_sandbox_agent(llm)
    response = await agent.arun("Create a web scraper")
    await agent.cleanup()

# Sync usage
def sync_example():
    agent = create_local_sandbox_agent(llm)
    response = agent.run("Create a web scraper")
    # Cleanup happens automatically
```

## Error Handling

```python
try:
    agent = create_local_sandbox_agent(llm)
    response = await agent.arun("Invalid command")
except Exception as e:
    print(f"Agent error: {e}")
finally:
    await agent.cleanup()
```

## Best Practices

### 1. Resource Management
Always clean up agents when done:

```python
async with agent:
    response = await agent.arun("Some task")
# Cleanup happens automatically
```

### 2. Provider Selection
- **Local**: Fast, good for development and testing
- **E2B**: Reliable, good for production workloads
- **Daytona**: Full development environments

### 3. Configuration
Use appropriate timeouts and resource limits:

```python
config = SandboxConfig(
    timeout=300,  # 5 minutes for complex tasks
    memory_limit="2GB",
    auto_cleanup=True
)
```

### 4. System Messages
Provide clear instructions to the agent:

```python
system_message = (
    "You are a Python expert with access to a sandbox. "
    "Always test your code before providing it to the user. "
    "Use snapshots before making major changes."
)
```

## Testing

The integration includes comprehensive tests with mocked LLMs:

```python
# Run tests
pytest tests/langgraph/

# Run specific test file
pytest tests/langgraph/test_tools.py -v
```

## Examples

See the `examples/langgraph/` directory for complete examples:

- `basic_agent.py`: Mock LLM demonstration
- `real_llm_example.py`: Interactive OpenAI example
- `README.md`: Detailed usage examples

## Requirements

### Core Requirements
```
grainchain[langgraph]
```

### Optional Requirements
```
langchain-openai  # For OpenAI models
langchain-anthropic  # For Anthropic models
```

## Installation

```bash
# Basic installation
pip install grainchain[langgraph]

# With OpenAI support
pip install grainchain[langgraph] langchain-openai

# Development installation
git clone https://github.com/codegen-sh/grainchain.git
cd grainchain
pip install -e .[langgraph,dev]
```

## API Reference

### Classes

- `SandboxAgent`: Main agent class with full LangGraph integration
- `LocalSandboxAgent`: Specialized agent for local development
- `SandboxAgentManager`: Multi-agent management
- `SandboxTool`: LangChain tool for command execution
- `SandboxFileUploadTool`: LangChain tool for file operations
- `SandboxSnapshotTool`: LangChain tool for state management

### Functions

- `create_sandbox_agent()`: Factory for general sandbox agents
- `create_local_sandbox_agent()`: Factory for local sandbox agents

### Configuration

- `SandboxConfig`: Configuration for sandbox behavior
- Provider-specific settings through config dictionaries

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see the main Grainchain repository for details.
