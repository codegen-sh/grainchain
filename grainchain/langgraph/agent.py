"""
LangGraph agent implementation for Grainchain sandbox integration.
"""

import logging
from collections.abc import Sequence
from typing import Annotated, Any, Optional, Union

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict

from grainchain.core.interfaces import SandboxConfig
from grainchain.langgraph.tools import (
    SandboxFileUploadTool,
    SandboxSnapshotTool,
    SandboxTool,
)

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the sandbox agent."""

    messages: Annotated[Sequence[BaseMessage], add_messages]


class SandboxAgent:
    """
    A LangGraph agent that can execute code in Grainchain sandboxes.

    This agent provides a clear, idiomatic pattern for creating LangGraph agents
    that can use sandbox environments for code execution, file operations, and
    state management through snapshots.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        provider: Optional[Union[str, Any]] = None,
        config: Optional[SandboxConfig] = None,
        additional_tools: Optional[list[BaseTool]] = None,
        system_message: Optional[str] = None,
    ):
        """
        Initialize the SandboxAgent.

        Args:
            llm: Language model to use for the agent
            provider: Sandbox provider name or instance (e.g., 'local', 'e2b')
            config: Sandbox configuration
            additional_tools: Additional tools to include in the agent
            system_message: System message to prepend to conversations
        """
        self.llm = llm
        self.provider = provider
        self.config = config or SandboxConfig()
        self.system_message = system_message or self._default_system_message()

        # Create sandbox tools
        self.sandbox_tool = SandboxTool(provider=provider, config=config)
        self.file_upload_tool = SandboxFileUploadTool(sandbox_tool=self.sandbox_tool)
        self.snapshot_tool = SandboxSnapshotTool(sandbox_tool=self.sandbox_tool)

        # Combine all tools
        self.tools = [
            self.sandbox_tool,
            self.file_upload_tool,
            self.snapshot_tool,
        ]
        if additional_tools:
            self.tools.extend(additional_tools)

        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Create the graph
        self.graph = self._create_graph()

    def _default_system_message(self) -> str:
        """Default system message for the sandbox agent."""
        return (
            "You are a helpful assistant with access to a secure sandbox environment. "
            "You can execute commands, upload files, and manage sandbox state using snapshots. "
            "Use the sandbox tools to help users with their programming and system administration tasks. "
            "Always be careful with destructive operations and consider creating snapshots before major changes."
        )

    def _create_graph(self) -> StateGraph:
        """Create the LangGraph state graph."""
        # Create the graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", ToolNode(self.tools))

        # Set entry point
        workflow.set_entry_point("agent")

        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            },
        )

        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    def _call_model(self, state: AgentState) -> dict[str, Any]:
        """Call the language model with the current state."""
        messages = state["messages"]

        # Add system message if this is the first call
        if not messages or not isinstance(messages[0], HumanMessage):
            messages = [HumanMessage(content=self.system_message)] + list(messages)

        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def _should_continue(self, state: AgentState) -> str:
        """Determine whether to continue with tool calls or end."""
        messages = state["messages"]
        last_message = messages[-1]

        # If the LLM makes a tool call, continue to tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"

        # Otherwise, end
        return "end"

    async def arun(
        self,
        message: str,
        thread_id: Optional[str] = None,
        config: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Asynchronously run the agent with a message.

        Args:
            message: Input message from the user
            thread_id: Optional thread ID for conversation tracking
            config: Optional configuration for the run

        Returns:
            Agent's response as a string
        """
        try:
            # Prepare initial state
            initial_state = {"messages": [HumanMessage(content=message)]}

            # Run the graph
            final_state = await self.graph.ainvoke(initial_state, config=config or {})

            # Extract the final response
            messages = final_state["messages"]
            if messages:
                last_message = messages[-1]
                if isinstance(last_message, AIMessage):
                    return last_message.content

            return "No response generated."

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return f"Error: {str(e)}"

    def run(
        self,
        message: str,
        thread_id: Optional[str] = None,
        config: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Synchronously run the agent with a message.

        Args:
            message: Input message from the user
            thread_id: Optional thread ID for conversation tracking
            config: Optional configuration for the run

        Returns:
            Agent's response as a string
        """
        import asyncio

        try:
            # Check if we're already in an async context
            try:
                asyncio.get_running_loop()
                # If we're in an async context, we can't use run_until_complete
                # Instead, we need to schedule the coroutine
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        lambda: asyncio.run(self.arun(message, thread_id, config))
                    )
                    return future.result()
            except RuntimeError:
                # No running loop, we can create one
                return asyncio.run(self.arun(message, thread_id, config))
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return f"Error: {str(e)}"

    async def cleanup(self) -> None:
        """Clean up agent resources."""
        await self.sandbox_tool.cleanup()

    def __del__(self):
        """Cleanup when the agent is garbage collected."""
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


def create_sandbox_agent(
    llm: BaseChatModel,
    provider: Optional[Union[str, Any]] = None,
    config: Optional[SandboxConfig] = None,
    additional_tools: Optional[list[BaseTool]] = None,
    system_message: Optional[str] = None,
) -> SandboxAgent:
    """
    Factory function to create a SandboxAgent.

    This provides a convenient way to create a sandbox agent with sensible defaults.

    Args:
        llm: Language model to use for the agent
        provider: Sandbox provider name or instance (e.g., 'local', 'e2b')
        config: Sandbox configuration
        additional_tools: Additional tools to include in the agent
        system_message: System message to prepend to conversations

    Returns:
        Configured SandboxAgent instance
    """
    return SandboxAgent(
        llm=llm,
        provider=provider,
        config=config,
        additional_tools=additional_tools,
        system_message=system_message,
    )
