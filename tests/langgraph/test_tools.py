"""
Tests for LangGraph tools integration.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from grainchain.core.interfaces import ExecutionResult, SandboxConfig
from grainchain.langgraph.tools import (
    SandboxFileUploadTool,
    SandboxSnapshotTool,
    SandboxTool,
)


class TestSandboxTool:
    """Test the SandboxTool class."""

    @pytest.fixture
    def mock_sandbox(self):
        """Create a mock sandbox."""
        sandbox = AsyncMock()
        sandbox.execute.return_value = ExecutionResult(
            stdout="Hello, World!",
            stderr="",
            return_code=0,
            execution_time=0.1,
            success=True,
            command="echo 'Hello, World!'",
        )
        return sandbox

    @pytest.fixture
    def sandbox_tool(self):
        """Create a SandboxTool instance."""
        return SandboxTool(provider="local")

    @pytest.mark.asyncio
    async def test_arun_success(self, sandbox_tool, mock_sandbox):
        """Test successful async execution."""
        with patch("grainchain.langgraph.tools.Sandbox") as mock_sandbox_class:
            mock_sandbox_class.return_value = mock_sandbox

            result = await sandbox_tool._arun("echo 'Hello, World!'")

            assert "STDOUT:" in result
            assert "Hello, World!" in result
            assert "Return code: 0" in result
            assert "Execution time: 0.10s" in result

    @pytest.mark.asyncio
    async def test_arun_with_stderr(self, sandbox_tool, mock_sandbox):
        """Test execution with stderr output."""
        mock_sandbox.execute.return_value = ExecutionResult(
            stdout="",
            stderr="Warning: something happened",
            return_code=0,
            execution_time=0.2,
            success=True,
            command="some_command",
        )

        with patch("grainchain.langgraph.tools.Sandbox") as mock_sandbox_class:
            mock_sandbox_class.return_value = mock_sandbox

            result = await sandbox_tool._arun("some_command")

            assert "STDERR:" in result
            assert "Warning: something happened" in result
            assert "Return code: 0" in result

    @pytest.mark.asyncio
    async def test_arun_failure(self, sandbox_tool, mock_sandbox):
        """Test execution failure."""
        mock_sandbox.execute.side_effect = Exception("Execution failed")

        with patch("grainchain.langgraph.tools.Sandbox") as mock_sandbox_class:
            mock_sandbox_class.return_value = mock_sandbox

            result = await sandbox_tool._arun("failing_command")

            assert "Error executing command:" in result
            assert "Execution failed" in result

    def test_run_sync(self, sandbox_tool, mock_sandbox):
        """Test synchronous execution wrapper."""
        mock_sandbox.execute.return_value = ExecutionResult(
            stdout="Sync test",
            stderr="",
            return_code=0,
            execution_time=0.1,
            success=True,
            command="sync_command",
        )

        with patch("grainchain.langgraph.tools.Sandbox") as mock_sandbox_class:
            mock_sandbox_class.return_value = mock_sandbox

            result = sandbox_tool._run("sync_command")

            assert "STDOUT:" in result
            assert "Sync test" in result

    @pytest.mark.asyncio
    async def test_cleanup(self, sandbox_tool, mock_sandbox):
        """Test cleanup functionality."""
        sandbox_tool._sandbox = mock_sandbox

        await sandbox_tool.cleanup()

        mock_sandbox.close.assert_called_once()
        assert sandbox_tool._sandbox is None


class TestSandboxFileUploadTool:
    """Test the SandboxFileUploadTool class."""

    @pytest.fixture
    def mock_sandbox_tool(self):
        """Create a mock SandboxTool."""
        tool = MagicMock()
        tool._sandbox = AsyncMock()
        tool._provider = "local"
        tool._config = SandboxConfig()
        return tool

    @pytest.fixture
    def file_upload_tool(self, mock_sandbox_tool):
        """Create a SandboxFileUploadTool instance."""
        return SandboxFileUploadTool(sandbox_tool=mock_sandbox_tool)

    @pytest.mark.asyncio
    async def test_arun_success(self, file_upload_tool, mock_sandbox_tool):
        """Test successful file upload."""
        result = await file_upload_tool._arun("test.py", "print('hello')")

        mock_sandbox_tool._sandbox.upload_file.assert_called_once_with(
            "test.py", "print('hello')", "w"
        )
        assert "Successfully uploaded file to test.py" in result

    @pytest.mark.asyncio
    async def test_arun_no_sandbox(self, file_upload_tool, mock_sandbox_tool):
        """Test file upload when sandbox doesn't exist."""
        mock_sandbox_tool._sandbox = None

        with patch("grainchain.langgraph.tools.Sandbox") as mock_sandbox_class:
            mock_sandbox = AsyncMock()
            mock_sandbox_class.return_value = mock_sandbox

            await file_upload_tool._arun("test.py", "content")

            mock_sandbox_class.assert_called_once()
            mock_sandbox.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_arun_failure(self, file_upload_tool, mock_sandbox_tool):
        """Test file upload failure."""
        mock_sandbox_tool._sandbox.upload_file.side_effect = Exception("Upload failed")

        result = await file_upload_tool._arun("test.py", "content")

        assert "Error uploading file:" in result
        assert "Upload failed" in result


class TestSandboxSnapshotTool:
    """Test the SandboxSnapshotTool class."""

    @pytest.fixture
    def mock_sandbox_tool(self):
        """Create a mock SandboxTool."""
        tool = MagicMock()
        tool._sandbox = AsyncMock()
        tool._provider = "local"
        tool._config = SandboxConfig()
        return tool

    @pytest.fixture
    def snapshot_tool(self, mock_sandbox_tool):
        """Create a SandboxSnapshotTool instance."""
        return SandboxSnapshotTool(sandbox_tool=mock_sandbox_tool)

    @pytest.mark.asyncio
    async def test_create_snapshot(self, snapshot_tool, mock_sandbox_tool):
        """Test snapshot creation."""
        mock_sandbox_tool._sandbox.create_snapshot.return_value = "snapshot_123"

        result = await snapshot_tool._arun("create")

        mock_sandbox_tool._sandbox.create_snapshot.assert_called_once()
        assert "Created snapshot with ID: snapshot_123" in result

    @pytest.mark.asyncio
    async def test_restore_snapshot(self, snapshot_tool, mock_sandbox_tool):
        """Test snapshot restoration."""
        result = await snapshot_tool._arun("restore", "snapshot_123")

        mock_sandbox_tool._sandbox.restore_snapshot.assert_called_once_with(
            "snapshot_123"
        )
        assert "Restored snapshot: snapshot_123" in result

    @pytest.mark.asyncio
    async def test_restore_without_id(self, snapshot_tool, mock_sandbox_tool):
        """Test restore without snapshot ID."""
        result = await snapshot_tool._arun("restore")

        assert "Error: snapshot_id is required for restore action" in result

    @pytest.mark.asyncio
    async def test_invalid_action(self, snapshot_tool, mock_sandbox_tool):
        """Test invalid action."""
        result = await snapshot_tool._arun("invalid_action")

        assert "Error: Unknown action 'invalid_action'" in result

    @pytest.mark.asyncio
    async def test_snapshot_failure(self, snapshot_tool, mock_sandbox_tool):
        """Test snapshot operation failure."""
        mock_sandbox_tool._sandbox.create_snapshot.side_effect = Exception(
            "Snapshot failed"
        )

        result = await snapshot_tool._arun("create")

        assert "Error performing snapshot operation:" in result
        assert "Snapshot failed" in result
