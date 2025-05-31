"""
Tests for local sandbox integration.
"""

from unittest.mock import MagicMock, patch

import pytest
from langchain_core.tools import tool

from grainchain.core.interfaces import SandboxConfig
from grainchain.langgraph.local_integration import (
    LocalSandboxAgent,
    SandboxAgentManager,
    create_local_sandbox_agent,
)


class MockChatModel:
    """Mock chat model for testing."""

    def __init__(self):
        self.tools = []

    def bind_tools(self, tools):
        """Mock bind_tools method."""
        self.tools = tools
        return self


class TestLocalSandboxAgent:
    """Test the LocalSandboxAgent class."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM."""
        return MockChatModel()

    def test_init_default(self, mock_llm):
        """Test default initialization."""
        agent = LocalSandboxAgent(llm=mock_llm)

        assert agent.llm == mock_llm
        assert agent.provider == "local"
        assert isinstance(agent.config, SandboxConfig)
        assert agent.config.working_directory == "~/sandbox_workspace"
        assert agent.config.timeout == 60
        assert agent.config.auto_cleanup is True
        assert agent.config.keep_alive is False

    def test_init_custom_params(self, mock_llm):
        """Test initialization with custom parameters."""
        agent = LocalSandboxAgent(
            llm=mock_llm, working_directory="/custom/path", timeout=120
        )

        assert agent.config.working_directory == "/custom/path"
        assert agent.config.timeout == 120

    def test_init_with_additional_tools(self, mock_llm):
        """Test initialization with additional tools."""

        @tool
        def custom_tool(input: str) -> str:
            """A custom tool."""
            return f"Custom: {input}"

        agent = LocalSandboxAgent(llm=mock_llm, additional_tools=[custom_tool])

        assert len(agent.tools) == 4  # 3 default + 1 custom

    def test_local_system_message(self, mock_llm):
        """Test that local system message is used."""
        agent = LocalSandboxAgent(llm=mock_llm)

        assert "local sandbox environment" in agent.system_message
        assert "development" in agent.system_message
        assert "testing" in agent.system_message


class TestCreateLocalSandboxAgent:
    """Test the create_local_sandbox_agent factory function."""

    def test_create_local_sandbox_agent(self):
        """Test factory function."""
        mock_llm = MockChatModel()

        agent = create_local_sandbox_agent(
            llm=mock_llm, working_directory="/test/path", timeout=90
        )

        assert isinstance(agent, LocalSandboxAgent)
        assert agent.llm == mock_llm
        assert agent.config.working_directory == "/test/path"
        assert agent.config.timeout == 90


class TestSandboxAgentManager:
    """Test the SandboxAgentManager class."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM."""
        return MockChatModel()

    @pytest.fixture
    def manager(self):
        """Create a SandboxAgentManager instance."""
        return SandboxAgentManager()

    def test_init(self, manager):
        """Test manager initialization."""
        assert len(manager.agents) == 0
        assert manager._active_agent is None

    def test_add_agent(self, manager, mock_llm):
        """Test adding an agent."""
        with patch(
            "grainchain.langgraph.local_integration.SandboxAgent"
        ) as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent

            agent = manager.add_agent("test_agent", mock_llm, provider="local")

            assert "test_agent" in manager.agents
            assert manager.agents["test_agent"] == mock_agent
            assert manager._active_agent == "test_agent"
            assert agent == mock_agent

    def test_add_agent_duplicate_name(self, manager, mock_llm):
        """Test adding agent with duplicate name."""
        with patch("grainchain.langgraph.local_integration.SandboxAgent"):
            manager.add_agent("test_agent", mock_llm)

            with pytest.raises(ValueError, match="Agent 'test_agent' already exists"):
                manager.add_agent("test_agent", mock_llm)

    def test_add_local_agent(self, manager, mock_llm):
        """Test adding a local agent."""
        with patch(
            "grainchain.langgraph.local_integration.LocalSandboxAgent"
        ) as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent

            agent = manager.add_local_agent("local_agent", mock_llm)

            assert "local_agent" in manager.agents
            assert manager.agents["local_agent"] == mock_agent
            assert manager._active_agent == "local_agent"
            assert agent == mock_agent

    def test_get_agent(self, manager, mock_llm):
        """Test getting an agent."""
        with patch(
            "grainchain.langgraph.local_integration.SandboxAgent"
        ) as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent

            manager.add_agent("test_agent", mock_llm)

            retrieved_agent = manager.get_agent("test_agent")
            assert retrieved_agent == mock_agent

            non_existent = manager.get_agent("non_existent")
            assert non_existent is None

    def test_set_active_agent(self, manager, mock_llm):
        """Test setting active agent."""
        with patch("grainchain.langgraph.local_integration.SandboxAgent"):
            manager.add_agent("agent1", mock_llm)
            manager.add_agent("agent2", mock_llm)

            manager.set_active_agent("agent2")
            assert manager._active_agent == "agent2"

            with pytest.raises(ValueError, match="Agent 'non_existent' not found"):
                manager.set_active_agent("non_existent")

    def test_get_active_agent(self, manager, mock_llm):
        """Test getting active agent."""
        assert manager.get_active_agent() is None

        with patch(
            "grainchain.langgraph.local_integration.SandboxAgent"
        ) as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent

            manager.add_agent("test_agent", mock_llm)

            active_agent = manager.get_active_agent()
            assert active_agent == mock_agent

    def test_run_with_active_agent(self, manager, mock_llm):
        """Test running with active agent."""
        with patch(
            "grainchain.langgraph.local_integration.SandboxAgent"
        ) as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.run.return_value = "Test response"
            mock_agent_class.return_value = mock_agent

            manager.add_agent("test_agent", mock_llm)

            result = manager.run("Test message")

            assert result == "Test response"
            mock_agent.run.assert_called_once_with("Test message")

    def test_run_with_specific_agent(self, manager, mock_llm):
        """Test running with specific agent."""
        with patch(
            "grainchain.langgraph.local_integration.SandboxAgent"
        ) as mock_agent_class:
            mock_agent1 = MagicMock()
            mock_agent1.run.return_value = "Agent 1 response"
            mock_agent2 = MagicMock()
            mock_agent2.run.return_value = "Agent 2 response"
            mock_agent_class.side_effect = [mock_agent1, mock_agent2]

            manager.add_agent("agent1", mock_llm)
            manager.add_agent("agent2", mock_llm)

            result = manager.run("Test message", agent_name="agent1")

            assert result == "Agent 1 response"
            mock_agent1.run.assert_called_once_with("Test message")

    def test_run_no_active_agent(self, manager):
        """Test running with no active agent."""
        result = manager.run("Test message")
        assert "Error: No active agent available" in result

    def test_run_non_existent_agent(self, manager, mock_llm):
        """Test running with non-existent agent."""
        with patch("grainchain.langgraph.local_integration.SandboxAgent"):
            manager.add_agent("test_agent", mock_llm)

            result = manager.run("Test message", agent_name="non_existent")
            assert "Error: Agent 'non_existent' not found" in result

    @pytest.mark.asyncio
    async def test_arun(self, manager, mock_llm):
        """Test async run."""
        with patch(
            "grainchain.langgraph.local_integration.SandboxAgent"
        ) as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.arun.return_value = "Async response"
            mock_agent_class.return_value = mock_agent

            manager.add_agent("test_agent", mock_llm)

            result = await manager.arun("Test message")

            assert result == "Async response"
            mock_agent.arun.assert_called_once_with("Test message")

    def test_list_agents(self, manager, mock_llm):
        """Test listing agents."""
        assert manager.list_agents() == []

        with patch("grainchain.langgraph.local_integration.SandboxAgent"):
            manager.add_agent("agent1", mock_llm)
            manager.add_agent("agent2", mock_llm)

            agents = manager.list_agents()
            assert set(agents) == {"agent1", "agent2"}

    def test_remove_agent(self, manager, mock_llm):
        """Test removing an agent."""
        with patch(
            "grainchain.langgraph.local_integration.SandboxAgent"
        ) as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent

            manager.add_agent("test_agent", mock_llm)
            assert "test_agent" in manager.agents
            assert manager._active_agent == "test_agent"

            manager.remove_agent("test_agent")

            assert "test_agent" not in manager.agents
            assert manager._active_agent is None

    def test_remove_agent_updates_active(self, manager, mock_llm):
        """Test removing active agent updates active agent."""
        with patch("grainchain.langgraph.local_integration.SandboxAgent"):
            manager.add_agent("agent1", mock_llm)
            manager.add_agent("agent2", mock_llm)

            # agent1 should be active (first added)
            assert manager._active_agent == "agent1"

            manager.remove_agent("agent1")

            # agent2 should now be active
            assert manager._active_agent == "agent2"

    @pytest.mark.asyncio
    async def test_cleanup(self, manager, mock_llm):
        """Test cleanup functionality."""
        with patch(
            "grainchain.langgraph.local_integration.SandboxAgent"
        ) as mock_agent_class:
            mock_agent1 = MagicMock()
            mock_agent2 = MagicMock()
            mock_agent_class.side_effect = [mock_agent1, mock_agent2]

            manager.add_agent("agent1", mock_llm)
            manager.add_agent("agent2", mock_llm)

            await manager.cleanup()

            mock_agent1.cleanup.assert_called_once()
            mock_agent2.cleanup.assert_called_once()
