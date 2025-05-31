"""Unit tests for the core Sandbox class."""

from unittest.mock import patch

import pytest

from grainchain import Sandbox
from grainchain.core.exceptions import (
    ConfigurationError,
    SandboxError,
)
from grainchain.core.interfaces import ExecutionResult, SandboxStatus


class TestSandbox:
    """Test cases for the Sandbox class."""

    @pytest.mark.unit
    def test_sandbox_init_with_provider_string(self, config_manager):
        """Test sandbox initialization with provider string."""
        with patch(
            "grainchain.core.sandbox.get_config_manager", return_value=config_manager
        ):
            sandbox = Sandbox(provider="local")
            assert sandbox.provider_name == "local"

    @pytest.mark.unit
    def test_sandbox_init_with_provider_instance(self, mock_provider):
        """Test sandbox initialization with provider instance."""
        sandbox = Sandbox(provider=mock_provider)
        assert sandbox.provider_name == "mock"

    @pytest.mark.unit
    def test_sandbox_init_with_config(self, mock_provider, test_config):
        """Test sandbox initialization with custom config."""
        sandbox = Sandbox(provider=mock_provider, config=test_config)
        assert sandbox._config == test_config

    @pytest.mark.unit
    def test_sandbox_init_invalid_provider_type(self):
        """Test sandbox initialization with invalid provider type."""
        with pytest.raises(ConfigurationError, match="Invalid provider type"):
            Sandbox(provider=123)

    @pytest.mark.unit
    async def test_sandbox_context_manager(self, mock_provider, test_config):
        """Test sandbox as async context manager."""
        sandbox = Sandbox(provider=mock_provider, config=test_config)

        async with sandbox as ctx:
            assert ctx is sandbox
            assert sandbox.sandbox_id is not None
            assert sandbox.status == SandboxStatus.RUNNING

    @pytest.mark.unit
    async def test_sandbox_explicit_create_close(self, mock_provider, test_config):
        """Test explicit sandbox creation and closing."""
        sandbox = Sandbox(provider=mock_provider, config=test_config)

        # Create sandbox
        await sandbox.create()
        assert sandbox.sandbox_id is not None
        assert sandbox.status == SandboxStatus.RUNNING

        # Close sandbox
        await sandbox.close()
        assert sandbox._closed

    @pytest.mark.unit
    async def test_sandbox_double_create_error(self, mock_provider, test_config):
        """Test that creating sandbox twice raises error."""
        sandbox = Sandbox(provider=mock_provider, config=test_config)

        await sandbox.create()
        with pytest.raises(SandboxError, match="Sandbox session already exists"):
            await sandbox.create()

    @pytest.mark.unit
    async def test_sandbox_reuse_closed_error(self, mock_provider, test_config):
        """Test that reusing closed sandbox raises error."""
        sandbox = Sandbox(provider=mock_provider, config=test_config)

        async with sandbox:
            pass  # Sandbox is closed after context

        with pytest.raises(SandboxError, match="Cannot reuse a closed sandbox"):
            async with sandbox:
                pass

    @pytest.mark.unit
    async def test_execute_command(self, mock_sandbox):
        """Test command execution."""
        result = await mock_sandbox.execute("echo 'Hello, World!'")

        assert isinstance(result, ExecutionResult)
        assert result.command == "echo 'Hello, World!'"
        assert result.return_code == 0
        assert "Hello, World!" in result.stdout

    @pytest.mark.unit
    async def test_execute_command_with_options(self, mock_sandbox):
        """Test command execution with additional options."""
        result = await mock_sandbox.execute(
            "python -c 'print(\"test\")'",
            timeout=60,
            working_dir="/tmp",
            environment={"TEST_VAR": "test_value"},
        )

        assert result.return_code == 0
        assert "Python output" in result.stdout

    @pytest.mark.unit
    async def test_execute_command_failure(self, mock_sandbox):
        """Test command execution failure."""
        result = await mock_sandbox.execute("exit 1")

        assert result.return_code == 1
        assert "Command failed" in result.stderr

    @pytest.mark.unit
    async def test_execute_without_session(self, mock_provider, test_config):
        """Test command execution without active session."""
        sandbox = Sandbox(provider=mock_provider, config=test_config)

        with pytest.raises(SandboxError, match="Sandbox session not initialized"):
            await sandbox.execute("echo test")

    @pytest.mark.unit
    async def test_upload_file_string(self, mock_sandbox):
        """Test file upload with string content."""
        content = "Hello, World!"
        await mock_sandbox.upload_file("/test/hello.txt", content)

        # Verify file was uploaded (check mock session)
        session = mock_sandbox._session
        assert "/test/hello.txt" in session.uploaded_files
        assert session.uploaded_files["/test/hello.txt"]["content"] == content.encode()

    @pytest.mark.unit
    async def test_upload_file_bytes(self, mock_sandbox):
        """Test file upload with bytes content."""
        content = b"Binary content"
        await mock_sandbox.upload_file("/test/binary.bin", content, mode="wb")

        session = mock_sandbox._session
        assert "/test/binary.bin" in session.uploaded_files
        assert session.uploaded_files["/test/binary.bin"]["content"] == content

    @pytest.mark.unit
    async def test_download_file(self, mock_sandbox):
        """Test file download."""
        # First upload a file
        content = "Test file content"
        await mock_sandbox.upload_file("/test/download.txt", content)

        # Then download it
        downloaded = await mock_sandbox.download_file("/test/download.txt")
        assert downloaded == content.encode()

    @pytest.mark.unit
    async def test_download_nonexistent_file(self, mock_sandbox):
        """Test downloading non-existent file."""
        with pytest.raises(SandboxError, match="File download failed"):
            await mock_sandbox.download_file("/nonexistent/file.txt")

    @pytest.mark.unit
    async def test_list_files(self, mock_sandbox):
        """Test file listing."""
        # Upload some files
        await mock_sandbox.upload_file("/test/file1.txt", "content1")
        await mock_sandbox.upload_file("/test/file2.txt", "content2")

        files = await mock_sandbox.list_files("/test")

        assert len(files) >= 2  # At least our uploaded files
        file_names = [f.name for f in files]
        assert "file1.txt" in file_names
        assert "file2.txt" in file_names

    @pytest.mark.unit
    async def test_create_snapshot(self, mock_sandbox):
        """Test snapshot creation."""
        # Upload a file first
        await mock_sandbox.upload_file("/test/snapshot_test.txt", "snapshot content")

        snapshot_id = await mock_sandbox.create_snapshot()

        assert isinstance(snapshot_id, str)
        assert snapshot_id.startswith("snapshot_")

    @pytest.mark.unit
    async def test_restore_snapshot(self, mock_sandbox):
        """Test snapshot restoration."""
        # Upload initial file
        await mock_sandbox.upload_file("/test/initial.txt", "initial content")

        # Create snapshot
        snapshot_id = await mock_sandbox.create_snapshot()

        # Upload another file
        await mock_sandbox.upload_file("/test/after_snapshot.txt", "after snapshot")

        # Restore snapshot
        await mock_sandbox.restore_snapshot(snapshot_id)

        # Verify restoration (the second file should be gone)
        session = mock_sandbox._session
        assert "/test/initial.txt" in session.uploaded_files
        assert "/test/after_snapshot.txt" not in session.uploaded_files

    @pytest.mark.unit
    async def test_restore_invalid_snapshot(self, mock_sandbox):
        """Test restoring invalid snapshot."""
        with pytest.raises(SandboxError, match="Snapshot restoration failed"):
            await mock_sandbox.restore_snapshot("invalid_snapshot_id")

    @pytest.mark.unit
    def test_sandbox_properties(self, mock_sandbox):
        """Test sandbox properties."""
        assert mock_sandbox.provider_name == "mock"
        assert mock_sandbox.status == SandboxStatus.RUNNING
        assert mock_sandbox.sandbox_id is not None

    @pytest.mark.unit
    def test_sandbox_repr(self, mock_sandbox):
        """Test sandbox string representation."""
        repr_str = repr(mock_sandbox)
        assert "Sandbox" in repr_str
        assert "provider=mock" in repr_str
        assert "status=running" in repr_str

    @pytest.mark.unit
    async def test_provider_creation_error(self, config_manager):
        """Test error handling during provider creation."""
        with patch(
            "grainchain.core.sandbox.get_config_manager", return_value=config_manager
        ):
            with pytest.raises(ConfigurationError, match="Unknown provider"):
                Sandbox(provider="unknown_provider")

    @pytest.mark.unit
    async def test_session_creation_error(self, failing_provider, test_config):
        """Test error handling during session creation."""
        sandbox = Sandbox(provider=failing_provider, config=test_config)

        with pytest.raises(SandboxError, match="Failed to create sandbox"):
            async with sandbox:
                pass

    @pytest.mark.unit
    async def test_operation_without_session_error(self, mock_provider, test_config):
        """Test operations without active session raise appropriate errors."""
        sandbox = Sandbox(provider=mock_provider, config=test_config)

        operations = [
            lambda: sandbox.execute("echo test"),
            lambda: sandbox.upload_file("/test.txt", "content"),
            lambda: sandbox.download_file("/test.txt"),
            lambda: sandbox.list_files("/"),
            lambda: sandbox.create_snapshot(),
            lambda: sandbox.restore_snapshot("test"),
        ]

        for operation in operations:
            with pytest.raises(SandboxError, match="Sandbox session not initialized"):
                await operation()

    @pytest.mark.unit
    async def test_timeout_handling(self, mock_sandbox):
        """Test timeout handling in command execution."""
        with pytest.raises(SandboxError, match="Command execution failed"):
            await mock_sandbox.execute("timeout_command")

    @pytest.mark.unit
    async def test_config_override_timeout(self, mock_sandbox):
        """Test that timeout parameter overrides config default."""
        # The mock session records the timeout parameter
        await mock_sandbox.execute("echo test", timeout=120)

        session = mock_sandbox._session
        last_command = session.executed_commands[-1]
        assert last_command["timeout"] == 120

    @pytest.mark.unit
    async def test_environment_variables(self, mock_sandbox):
        """Test environment variable passing."""
        env_vars = {"CUSTOM_VAR": "custom_value", "ANOTHER_VAR": "another_value"}
        await mock_sandbox.execute("echo $CUSTOM_VAR", environment=env_vars)

        session = mock_sandbox._session
        last_command = session.executed_commands[-1]
        assert last_command["environment"] == env_vars

    @pytest.mark.unit
    async def test_working_directory(self, mock_sandbox):
        """Test working directory specification."""
        await mock_sandbox.execute("pwd", working_dir="/custom/dir")

        session = mock_sandbox._session
        last_command = session.executed_commands[-1]
        assert last_command["working_dir"] == "/custom/dir"


class TestSandboxIntegration:
    """Integration tests for Sandbox with different providers."""

    @pytest.mark.unit
    async def test_multiple_sandboxes_same_provider(self, mock_provider, test_config):
        """Test creating multiple sandboxes with the same provider."""
        sandbox1 = Sandbox(provider=mock_provider, config=test_config)
        sandbox2 = Sandbox(provider=mock_provider, config=test_config)

        async with sandbox1:
            async with sandbox2:
                assert sandbox1.sandbox_id != sandbox2.sandbox_id
                assert len(mock_provider.created_sessions) == 2

    @pytest.mark.unit
    async def test_sandbox_cleanup_on_exception(self, mock_provider, test_config):
        """Test that sandbox is properly cleaned up on exception."""
        sandbox = Sandbox(provider=mock_provider, config=test_config)

        try:
            async with sandbox:
                raise ValueError("Test exception")
        except ValueError:
            pass

        assert sandbox._closed

    @pytest.mark.unit
    async def test_provider_cleanup(self, mock_provider, test_config):
        """Test provider cleanup functionality."""
        sandbox1 = Sandbox(provider=mock_provider, config=test_config)
        sandbox2 = Sandbox(provider=mock_provider, config=test_config)

        async with sandbox1:
            async with sandbox2:
                pass

        # Clean up provider
        await mock_provider.cleanup()
        assert mock_provider._closed
        assert len(mock_provider._sessions) == 0
