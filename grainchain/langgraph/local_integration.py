"""
Integration helpers for using SandboxAgent with LocalSandbox.
"""

import logging
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from grainchain.core.interfaces import SandboxConfig
from grainchain.langgraph.agent import SandboxAgent

logger = logging.getLogger(__name__)


class LocalSandboxAgent(SandboxAgent):
    """
    A specialized SandboxAgent configured for local sandbox usage.

    This provides a convenient way to create an agent that uses the local
    sandbox provider with optimized settings for development and testing.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        working_directory: str = "~/sandbox_workspace",
        timeout: int = 60,
        additional_tools: list[BaseTool] | None = None,
        system_message: str | None = None,
    ):
        """
        Initialize the LocalSandboxAgent.

        Args:
            llm: Language model to use for the agent
            working_directory: Working directory for sandbox operations
            timeout: Default timeout for operations in seconds
            additional_tools: Additional tools to include in the agent
            system_message: System message to prepend to conversations
        """
        # Create local sandbox configuration
        config = SandboxConfig(
            working_directory=working_directory,
            timeout=timeout,
            auto_cleanup=True,
            keep_alive=False,
        )

        # Use local provider
        super().__init__(
            llm=llm,
            provider="local",
            config=config,
            additional_tools=additional_tools,
            system_message=system_message or self._local_system_message(),
        )

    def _local_system_message(self) -> str:
        """System message optimized for local sandbox usage."""
        return (
            "You are a helpful assistant with access to a local sandbox environment. "
            "This sandbox runs on the local machine and is perfect for development, "
            "testing, and quick prototyping. You can execute commands, create files, "
            "install packages, and perform various system operations safely. "
            "The sandbox provides isolation while being fast and responsive. "
            "Use snapshots to save important states before making significant changes."
        )


def create_local_sandbox_agent(
    llm: BaseChatModel,
    working_directory: str = "~/sandbox_workspace",
    timeout: int = 60,
    additional_tools: list[BaseTool] | None = None,
    system_message: str | None = None,
) -> LocalSandboxAgent:
    """
    Factory function to create a LocalSandboxAgent.

    This provides the most convenient way to create a sandbox agent for local
    development and testing scenarios.

    Args:
        llm: Language model to use for the agent
        working_directory: Working directory for sandbox operations
        timeout: Default timeout for operations in seconds
        additional_tools: Additional tools to include in the agent
        system_message: System message to prepend to conversations

    Returns:
        Configured LocalSandboxAgent instance

    Example:
        ```python
        from langchain_openai import ChatOpenAI
        from grainchain.langgraph import create_local_sandbox_agent

        # Create LLM
        llm = ChatOpenAI(model="gpt-4")

        # Create agent
        agent = create_local_sandbox_agent(llm)

        # Use the agent
        response = agent.run("Create a Python script that prints 'Hello, World!'")
        print(response)
        ```
    """
    return LocalSandboxAgent(
        llm=llm,
        working_directory=working_directory,
        timeout=timeout,
        additional_tools=additional_tools,
        system_message=system_message,
    )


class SandboxAgentManager:
    """
    Manager class for handling multiple sandbox agents and their lifecycle.

    This class helps manage multiple agents, handle cleanup, and provides
    utilities for switching between different sandbox providers.
    """

    def __init__(self):
        """Initialize the agent manager."""
        self.agents: dict[str, SandboxAgent] = {}
        self._active_agent: str | None = None

    def add_agent(
        self,
        name: str,
        llm: BaseChatModel,
        provider: str | Any | None = None,
        config: SandboxConfig | None = None,
        additional_tools: list[BaseTool] | None = None,
        system_message: str | None = None,
    ) -> SandboxAgent:
        """
        Add a new agent to the manager.

        Args:
            name: Unique name for the agent
            llm: Language model to use for the agent
            provider: Sandbox provider name or instance
            config: Sandbox configuration
            additional_tools: Additional tools to include in the agent
            system_message: System message to prepend to conversations

        Returns:
            The created SandboxAgent instance
        """
        if name in self.agents:
            raise ValueError(f"Agent '{name}' already exists")

        agent = SandboxAgent(
            llm=llm,
            provider=provider,
            config=config,
            additional_tools=additional_tools,
            system_message=system_message,
        )

        self.agents[name] = agent

        # Set as active if it's the first agent
        if self._active_agent is None:
            self._active_agent = name

        return agent

    def add_local_agent(
        self,
        name: str,
        llm: BaseChatModel,
        working_directory: str = "~/sandbox_workspace",
        timeout: int = 60,
        additional_tools: list[BaseTool] | None = None,
        system_message: str | None = None,
    ) -> LocalSandboxAgent:
        """
        Add a local sandbox agent to the manager.

        Args:
            name: Unique name for the agent
            llm: Language model to use for the agent
            working_directory: Working directory for sandbox operations
            timeout: Default timeout for operations in seconds
            additional_tools: Additional tools to include in the agent
            system_message: System message to prepend to conversations

        Returns:
            The created LocalSandboxAgent instance
        """
        if name in self.agents:
            raise ValueError(f"Agent '{name}' already exists")

        agent = LocalSandboxAgent(
            llm=llm,
            working_directory=working_directory,
            timeout=timeout,
            additional_tools=additional_tools,
            system_message=system_message,
        )

        self.agents[name] = agent

        # Set as active if it's the first agent
        if self._active_agent is None:
            self._active_agent = name

        return agent

    def get_agent(self, name: str) -> SandboxAgent | None:
        """Get an agent by name."""
        return self.agents.get(name)

    def set_active_agent(self, name: str) -> None:
        """Set the active agent."""
        if name not in self.agents:
            raise ValueError(f"Agent '{name}' not found")
        self._active_agent = name

    def get_active_agent(self) -> SandboxAgent | None:
        """Get the currently active agent."""
        if self._active_agent:
            return self.agents.get(self._active_agent)
        return None

    def run(self, message: str, agent_name: str | None = None) -> str:
        """
        Run a message with the specified agent or the active agent.

        Args:
            message: Input message
            agent_name: Name of agent to use (uses active agent if None)

        Returns:
            Agent's response
        """
        if agent_name:
            agent = self.get_agent(agent_name)
            if not agent:
                return f"Error: Agent '{agent_name}' not found"
        else:
            agent = self.get_active_agent()
            if not agent:
                return "Error: No active agent available"

        return agent.run(message)

    async def arun(self, message: str, agent_name: str | None = None) -> str:
        """
        Asynchronously run a message with the specified agent or the active agent.

        Args:
            message: Input message
            agent_name: Name of agent to use (uses active agent if None)

        Returns:
            Agent's response
        """
        if agent_name:
            agent = self.get_agent(agent_name)
            if not agent:
                return f"Error: Agent '{agent_name}' not found"
        else:
            agent = self.get_active_agent()
            if not agent:
                return "Error: No active agent available"

        return await agent.arun(message)

    async def cleanup(self) -> None:
        """Clean up all agents."""
        for agent in self.agents.values():
            await agent.cleanup()

    def list_agents(self) -> list[str]:
        """List all agent names."""
        return list(self.agents.keys())

    def remove_agent(self, name: str) -> None:
        """Remove an agent from the manager."""
        if name in self.agents:
            # Clean up the agent
            try:
                import asyncio

                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.agents[name].cleanup())
                else:
                    loop.run_until_complete(self.agents[name].cleanup())
            except Exception:
                pass

            # Remove from manager
            del self.agents[name]

            # Update active agent if necessary
            if self._active_agent == name:
                self._active_agent = (
                    next(iter(self.agents.keys())) if self.agents else None
                )

    def __del__(self):
        """Cleanup when the manager is garbage collected."""
        try:
            import asyncio

            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.cleanup())
            else:
                loop.run_until_complete(self.cleanup())
        except Exception:
            # Ignore cleanup errors during garbage collection
            pass
