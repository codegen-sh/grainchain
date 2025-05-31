# LangGraph Integration Examples

This directory contains examples demonstrating how to use Grainchain with LangGraph for building AI agents that can execute code in sandbox environments.

## Examples

### 1. Basic Agent (`basic_agent.py`)

A simple example using a mock LLM to demonstrate the basic concepts:

```bash
python examples/langgraph/basic_agent.py
```

This example shows:
- How to create a sandbox agent
- Basic tool usage (file upload, command execution)
- Mock LLM responses for demonstration

### 2. Real LLM Example (`real_llm_example.py`)

An interactive example using OpenAI's GPT models:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Install required dependencies
pip install grainchain[langgraph] langchain-openai

# Run the example
python examples/langgraph/real_llm_example.py
```

This example provides:
- Interactive chat interface
- Real LLM integration with OpenAI
- Practical coding assistance scenarios

## Key Features Demonstrated

### 🛠️ Sandbox Tools
- **Command Execution**: Run shell commands, Python scripts, etc.
- **File Operations**: Upload, create, and manage files
- **Snapshots**: Save and restore sandbox states

### 🤖 Agent Patterns
- **Local Sandbox Agent**: Optimized for development and testing
- **Custom System Messages**: Tailored agent behavior
- **Tool Integration**: Seamless LangGraph tool usage

### 🔧 Integration Patterns
- **Factory Functions**: Easy agent creation
- **Agent Manager**: Handle multiple agents
- **Async/Sync Support**: Flexible execution models

## Usage Patterns

### Quick Start

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

### Advanced Usage

```python
from grainchain.langgraph import SandboxAgent, SandboxAgentManager
from grainchain.core.interfaces import SandboxConfig

# Custom configuration
config = SandboxConfig(
    timeout=120,
    working_directory="/custom/workspace",
    environment_vars={"DEBUG": "1"}
)

# Create agent with custom config
agent = SandboxAgent(
    llm=llm,
    provider="local",
    config=config,
    system_message="You are a specialized data science assistant."
)

# Or use agent manager for multiple agents
manager = SandboxAgentManager()
manager.add_local_agent("dev", llm)
manager.add_agent("prod", llm, provider="e2b")

# Switch between agents
response = manager.run("Test command", agent_name="dev")
```

## Example Requests

Try these requests with the interactive example:

### Python Development
- "Create a Python script that calculates fibonacci numbers"
- "Write a function to sort a list and create unit tests for it"
- "Create a simple class for managing a todo list"

### Data Analysis
- "Create a data analysis script that reads a CSV and generates plots"
- "Write a script to analyze web server logs"
- "Create a simple machine learning model with scikit-learn"

### Web Development
- "Create a simple Flask web application"
- "Write a web scraper using requests and BeautifulSoup"
- "Create a REST API with FastAPI"

### System Administration
- "Check system resources and create a monitoring script"
- "Create a backup script for important files"
- "Write a log analysis tool"

## Requirements

### Basic Example
- Python 3.9+
- grainchain[langgraph]

### Real LLM Example
- Python 3.9+
- grainchain[langgraph]
- langchain-openai
- OpenAI API key

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

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you have installed the langgraph extras:
   ```bash
   pip install grainchain[langgraph]
   ```

2. **OpenAI API Errors**: Ensure your API key is set:
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

3. **Sandbox Errors**: Check that you have permissions to create files in the working directory.

### Getting Help

- Check the main Grainchain documentation
- Review the test files for more usage examples
- Open an issue on GitHub for bugs or feature requests
