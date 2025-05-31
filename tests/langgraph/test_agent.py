"""
Tests for LangGraph agent integration.
"""

from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

from grainchain.core.interfaces import SandboxConfig
from grainchain.langgraph.agent import SandboxAgent, create_sandbox_agent


class MockChatModel:
    """Mock chat model for testing."""

    def __init__(self):
        self.tools = []
        self.responses = []
        self.call_count = 0

    def bind_tools(self, tools):
        """Mock bind_tools method."""
        self.tools = tools
        return self

    def invoke(self, messages):
        """Mock invoke method."""
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
        else:
            response = AIMessage(content="Default response")

        self.call_count += 1
        return response

    def set_responses(self, responses):
        """Set predefined responses."""
        self.responses = responses
        self.call_count = 0


class TestSandboxAgent:
    """Test the SandboxAgent class."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM."""
        return MockChatModel()

    @pytest.fixture
    def sandbox_agent(self, mock_llm):
        """Create a SandboxAgent instance."""
        return SandboxAgent(llm=mock_llm, provider="local")

    def test_init(self, mock_llm):
        """Test agent initialization."""
        agent = SandboxAgent(llm=mock_llm, provider="local")

        assert agent.llm == mock_llm
        assert agent.provider == "local"
        assert isinstance(agent.config, SandboxConfig)
        assert len(agent.tools) == 3  # sandbox_tool, file_upload_tool, snapshot_tool
        assert agent.llm_with_tools is not None
        assert agent.graph is not None

    def test_init_with_additional_tools(self, mock_llm):
        """Test agent initialization with additional tools."""

        @tool
        def custom_tool(input: str) -> str:
            """A custom tool."""
            return f"Custom: {input}"

        agent = SandboxAgent(
            llm=mock_llm, provider="local", additional_tools=[custom_tool]
        )

        assert len(agent.tools) == 4  # 3 default + 1 custom

    def test_init_with_custom_system_message(self, mock_llm):
        """Test agent initialization with custom system message."""
        custom_message = "You are a specialized coding assistant."
        agent = SandboxAgent(
            llm=mock_llm, provider="local", system_message=custom_message
        )

        assert agent.system_message == custom_message

    def test_should_continue_with_tool_calls(self, sandbox_agent):
        """Test should_continue when LLM makes tool calls."""
        # Mock message with tool calls
        mock_message = MagicMock()
        mock_message.tool_calls = [{"name": "sandbox_execute", "args": {}}]

        state = {"messages": [mock_message]}
        result = sandbox_agent._should_continue(state)

        assert result == "continue"

    def test_should_continue_without_tool_calls(self, sandbox_agent):
        """Test should_continue when LLM doesn't make tool calls."""
        mock_message = AIMessage(content="Just a regular response")

        state = {"messages": [mock_message]}
        result = sandbox_agent._should_continue(state)

        assert result == "end"

    def test_call_model(self, sandbox_agent, mock_llm):
        """Test _call_model method."""
        mock_llm.set_responses([AIMessage(content="Test response")])

        state = {"messages": [HumanMessage(content="Test message")]}
        result = sandbox_agent._call_model(state)

        assert "messages" in result
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert result["messages"][0].content == "Test response"

    @pytest.mark.asyncio
    async def test_arun_simple(self, sandbox_agent, mock_llm):
        """Test async run with simple response."""
        mock_llm.set_responses([AIMessage(content="Hello, I can help you!")])

        with patch.object(sandbox_agent.graph, "ainvoke") as mock_ainvoke:
            mock_ainvoke.return_value = {
                "messages": [
                    HumanMessage(content="Hello"),
                    AIMessage(content="Hello, I can help you!"),
                ]
            }

            result = await sandbox_agent.arun("Hello")

            assert result == "Hello, I can help you!"
            mock_ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_arun_no_response(self, sandbox_agent):
        """Test async run with no response."""
        with patch.object(sandbox_agent.graph, "ainvoke") as mock_ainvoke:
            mock_ainvoke.return_value = {"messages": []}

            result = await sandbox_agent.arun("Hello")

            assert result == "No response generated."

    @pytest.mark.asyncio
    async def test_arun_exception(self, sandbox_agent):
        """Test async run with exception."""
        with patch.object(sandbox_agent.graph, "ainvoke") as mock_ainvoke:
            mock_ainvoke.side_effect = Exception("Graph execution failed")

            result = await sandbox_agent.arun("Hello")

            assert "Error:" in result
            assert "Graph execution failed" in result

    def test_run_sync(self, sandbox_agent, mock_llm):
        """Test synchronous run wrapper."""
        mock_llm.set_responses([AIMessage(content="Sync response")])

        with patch.object(sandbox_agent, "arun") as mock_arun:
            mock_arun.return_value = "Sync response"

            # Mock asyncio.run_until_complete
            with patch("asyncio.get_event_loop") as mock_get_loop:
                mock_loop = MagicMock()
                mock_loop.run_until_complete.return_value = "Sync response"
                mock_get_loop.return_value = mock_loop

                result = sandbox_agent.run("Hello")

                assert result == "Sync response"

    @pytest.mark.asyncio
    async def test_cleanup(self, sandbox_agent):
        """Test cleanup functionality."""
        with patch.object(sandbox_agent.sandbox_tool, "cleanup") as mock_cleanup:
            await sandbox_agent.cleanup()
            mock_cleanup.assert_called_once()


class TestCreateSandboxAgent:
    """Test the create_sandbox_agent factory function."""

    def test_create_sandbox_agent(self):
        """Test factory function."""
        mock_llm = MockChatModel()

        agent = create_sandbox_agent(
            llm=mock_llm, provider="local", system_message="Custom message"
        )

        assert isinstance(agent, SandboxAgent)
        assert agent.llm == mock_llm
        assert agent.provider == "local"
        assert agent.system_message == "Custom message"
