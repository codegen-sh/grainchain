"""
Unit tests for sandbox providers.

Tests all provider implementations including E2B, Modal, and Local providers.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

import pytest

from grainchain import SandboxConfig
from grainchain.core.exceptions import AuthenticationError, ProviderError
from grainchain.core.interfaces import ExecutionResult, FileInfo
from grainchain.providers.base import BaseSandboxProvider, BaseSandboxSession
from grainchain.providers.local import LocalProvider, LocalSandboxSession
from grainchain.providers.e2b import E2BProvider, E2BSandboxSession
from grainchain.providers.modal import ModalProvider, ModalSandboxSession


class TestBaseSandboxProvider:
    """Test cases for the base sandbox provider."""
    
    def test_base_provider_is_abstract(self):
        """Test that base provider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseSandboxProvider()
    
    def test_base_provider_interface(self):
        """Test that base provider defines the correct interface."""
        # Check that required methods are defined
        assert hasattr(BaseSandboxProvider, 'provider_name')
        assert hasattr(BaseSandboxProvider, 'create_session')
        assert hasattr(BaseSandboxProvider, 'cleanup')


class TestBaseSandboxSession:
    """Test cases for the base sandbox session."""
    
    def test_base_session_is_abstract(self):
        """Test that base session cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseSandboxSession()
    
    def test_base_session_interface(self):
        """Test that base session defines the correct interface."""
        # Check that required methods are defined
        assert hasattr(BaseSandboxSession, 'execute')
        assert hasattr(BaseSandboxSession, 'upload_file')
        assert hasattr(BaseSandboxSession, 'download_file')
        assert hasattr(BaseSandboxSession, 'list_files')
        assert hasattr(BaseSandboxSession, 'create_snapshot')
        assert hasattr(BaseSandboxSession, 'restore_snapshot')
        assert hasattr(BaseSandboxSession, 'cleanup')


class TestLocalProvider:
    """Test cases for the Local provider."""
    
    def test_local_provider_creation(self):
        """Test creating a local provider."""
        provider = LocalProvider()
        assert provider.provider_name == "local"
    
    async def test_local_provider_create_session(self, temp_dir):
        """Test creating a local session."""
        provider = LocalProvider()
        config = SandboxConfig(working_directory=str(temp_dir))
        
        session = await provider.create_session(config)
        
        assert isinstance(session, LocalSandboxSession)
        assert session.working_directory == temp_dir
        
        await session.cleanup()
    
    async def test_local_provider_cleanup(self, temp_dir):
        """Test local provider cleanup."""
        provider = LocalProvider()
        config = SandboxConfig(working_directory=str(temp_dir))
        
        # Create multiple sessions
        session1 = await provider.create_session(config)
        session2 = await provider.create_session(config)
        
        # Cleanup provider
        await provider.cleanup()
        
        # Sessions should be cleaned up
        assert not session1.working_directory.exists()
        assert not session2.working_directory.exists()


class TestLocalSandboxSession:
    """Test cases for the Local sandbox session."""
    
    async def test_local_session_execute_command(self, temp_dir):
        """Test executing commands in local session."""
        session = LocalSandboxSession(str(temp_dir), SandboxConfig())
        
        # Test simple echo command
        result = await session.execute("echo 'Hello, Local!'")
        
        assert isinstance(result, ExecutionResult)
        assert result.success
        assert result.return_code == 0
        assert "Hello, Local!" in result.stdout
        
        await session.cleanup()
    
    async def test_local_session_execute_with_timeout(self, temp_dir):
        """Test command execution with timeout."""
        session = LocalSandboxSession(str(temp_dir), SandboxConfig())
        
        # Test command that should complete quickly
        result = await session.execute("echo 'quick'", timeout=5)
        
        assert result.success
        assert "quick" in result.stdout
        
        await session.cleanup()
    
    async def test_local_session_execute_failure(self, temp_dir):
        """Test handling command execution failure."""
        session = LocalSandboxSession(str(temp_dir), SandboxConfig())
        
        # Execute a command that should fail
        result = await session.execute("nonexistent_command_12345")
        
        assert not result.success
        assert result.return_code != 0
        assert len(result.stderr) > 0
        
        await session.cleanup()
    
    async def test_local_session_upload_file(self, temp_dir):
        """Test uploading files to local session."""
        session = LocalSandboxSession(str(temp_dir), SandboxConfig())
        
        content = b"Test file content"
        await session.upload_file("test.txt", content)
        
        # Verify file was created
        file_path = temp_dir / "test.txt"
        assert file_path.exists()
        assert file_path.read_bytes() == content
        
        await session.cleanup()
    
    async def test_local_session_upload_file_nested_path(self, temp_dir):
        """Test uploading files to nested paths."""
        session = LocalSandboxSession(str(temp_dir), SandboxConfig())
        
        content = b"Nested file content"
        await session.upload_file("subdir/nested.txt", content)
        
        # Verify file was created with directory structure
        file_path = temp_dir / "subdir" / "nested.txt"
        assert file_path.exists()
        assert file_path.read_bytes() == content
        
        await session.cleanup()
    
    async def test_local_session_download_file(self, temp_dir):
        """Test downloading files from local session."""
        session = LocalSandboxSession(str(temp_dir), SandboxConfig())
        
        # Create a file first
        content = b"Download test content"
        file_path = temp_dir / "download.txt"
        file_path.write_bytes(content)
        
        # Download the file
        downloaded_content = await session.download_file("download.txt")
        
        assert downloaded_content == content
        
        await session.cleanup()
    
    async def test_local_session_download_nonexistent_file(self, temp_dir):
        """Test downloading a non-existent file."""
        session = LocalSandboxSession(str(temp_dir), SandboxConfig())
        
        with pytest.raises(FileNotFoundError):
            await session.download_file("nonexistent.txt")
        
        await session.cleanup()
    
    async def test_local_session_list_files(self, temp_dir):
        """Test listing files in local session."""
        session = LocalSandboxSession(str(temp_dir), SandboxConfig())
        
        # Create some files
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.py").write_text("print('hello')")
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir" / "file3.txt").write_text("content3")
        
        # List files in root
        files = await session.list_files("/")
        
        assert len(files) >= 3  # At least the files we created
        file_names = [f.name for f in files]
        assert "file1.txt" in file_names
        assert "file2.py" in file_names
        assert "subdir" in file_names
        
        # Check file info
        for file_info in files:
            assert isinstance(file_info, FileInfo)
            assert file_info.path is not None
            assert file_info.size >= 0
        
        await session.cleanup()
    
    async def test_local_session_create_snapshot(self, temp_dir):
        """Test creating snapshots in local session."""
        session = LocalSandboxSession(str(temp_dir), SandboxConfig())
        
        # Create some files
        await session.upload_file("file1.txt", b"content1")
        await session.upload_file("file2.txt", b"content2")
        
        # Create snapshot
        snapshot_id = await session.create_snapshot()
        
        assert snapshot_id is not None
        assert isinstance(snapshot_id, str)
        
        # Verify snapshot directory exists
        snapshot_path = session.working_directory / f"snapshot_{snapshot_id}"
        assert snapshot_path.exists()
        assert (snapshot_path / "file1.txt").exists()
        assert (snapshot_path / "file2.txt").exists()
        
        await session.cleanup()
    
    async def test_local_session_restore_snapshot(self, temp_dir):
        """Test restoring snapshots in local session."""
        session = LocalSandboxSession(str(temp_dir), SandboxConfig())
        
        # Create initial files
        await session.upload_file("file1.txt", b"original1")
        await session.upload_file("file2.txt", b"original2")
        
        # Create snapshot
        snapshot_id = await session.create_snapshot()
        
        # Modify files
        await session.upload_file("file1.txt", b"modified1")
        await session.upload_file("file3.txt", b"new_file")
        
        # Restore snapshot
        await session.restore_snapshot(snapshot_id)
        
        # Verify restoration
        content1 = await session.download_file("file1.txt")
        content2 = await session.download_file("file2.txt")
        
        assert content1 == b"original1"
        assert content2 == b"original2"
        
        # New file should be gone
        with pytest.raises(FileNotFoundError):
            await session.download_file("file3.txt")
        
        await session.cleanup()
    
    async def test_local_session_restore_invalid_snapshot(self, temp_dir):
        """Test restoring an invalid snapshot."""
        session = LocalSandboxSession(str(temp_dir), SandboxConfig())
        
        with pytest.raises(ValueError, match="Snapshot not found"):
            await session.restore_snapshot("invalid_snapshot_id")
        
        await session.cleanup()
    
    async def test_local_session_cleanup(self, temp_dir):
        """Test local session cleanup."""
        session = LocalSandboxSession(str(temp_dir), SandboxConfig())
        
        # Create some files and snapshots
        await session.upload_file("file.txt", b"content")
        snapshot_id = await session.create_snapshot()
        
        # Cleanup
        await session.cleanup()
        
        # Working directory should be removed
        assert not session.working_directory.exists()


class TestE2BProvider:
    """Test cases for the E2B provider."""
    
    def test_e2b_provider_creation_with_api_key(self):
        """Test creating E2B provider with API key."""
        provider = E2BProvider(api_key="test_key")
        assert provider.provider_name == "e2b"
        assert provider.api_key == "test_key"
    
    def test_e2b_provider_creation_without_api_key(self):
        """Test creating E2B provider without API key."""
        with patch.dict(os.environ, {"E2B_API_KEY": "env_key"}):
            provider = E2BProvider()
            assert provider.api_key == "env_key"
    
    def test_e2b_provider_creation_no_api_key_available(self):
        """Test creating E2B provider when no API key is available."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AuthenticationError, match="E2B API key not provided"):
                E2BProvider()
    
    @patch('grainchain.providers.e2b.Sandbox')
    async def test_e2b_provider_create_session(self, mock_e2b_sandbox):
        """Test creating E2B session."""
        # Mock E2B Sandbox
        mock_sandbox_instance = AsyncMock()
        mock_sandbox_instance.id = "test_sandbox_id"
        mock_e2b_sandbox.create.return_value = mock_sandbox_instance
        
        provider = E2BProvider(api_key="test_key")
        config = SandboxConfig()
        
        session = await provider.create_session(config)
        
        assert isinstance(session, E2BSandboxSession)
        assert session.sandbox_id == "test_sandbox_id"
        
        # Verify E2B Sandbox was created with correct parameters
        mock_e2b_sandbox.create.assert_called_once()
    
    @patch('grainchain.providers.e2b.Sandbox')
    async def test_e2b_provider_create_session_with_template(self, mock_e2b_sandbox):
        """Test creating E2B session with custom template."""
        mock_sandbox_instance = AsyncMock()
        mock_sandbox_instance.id = "test_sandbox_id"
        mock_e2b_sandbox.create.return_value = mock_sandbox_instance
        
        provider = E2BProvider(api_key="test_key", template="python-data-science")
        config = SandboxConfig()
        
        session = await provider.create_session(config)
        
        # Verify template was passed
        call_args = mock_e2b_sandbox.create.call_args
        assert "template" in call_args.kwargs
        assert call_args.kwargs["template"] == "python-data-science"
    
    async def test_e2b_provider_cleanup(self):
        """Test E2B provider cleanup."""
        provider = E2BProvider(api_key="test_key")
        
        # Create mock sessions
        session1 = AsyncMock()
        session2 = AsyncMock()
        provider.sessions = {"id1": session1, "id2": session2}
        
        await provider.cleanup()
        
        # Verify sessions were cleaned up
        session1.cleanup.assert_called_once()
        session2.cleanup.assert_called_once()
        assert len(provider.sessions) == 0


class TestE2BSandboxSession:
    """Test cases for the E2B sandbox session."""
    
    def test_e2b_session_creation(self):
        """Test creating E2B session."""
        mock_sandbox = AsyncMock()
        mock_sandbox.id = "test_id"
        config = SandboxConfig()
        
        session = E2BSandboxSession(mock_sandbox, config)
        
        assert session.sandbox_id == "test_id"
        assert session.config == config
        assert session.e2b_sandbox == mock_sandbox
    
    async def test_e2b_session_execute(self):
        """Test executing commands in E2B session."""
        mock_sandbox = AsyncMock()
        mock_sandbox.id = "test_id"
        
        # Mock execution result
        mock_result = MagicMock()
        mock_result.stdout = "Hello, E2B!"
        mock_result.stderr = ""
        mock_result.exit_code = 0
        mock_sandbox.commands.run.return_value = mock_result
        
        session = E2BSandboxSession(mock_sandbox, SandboxConfig())
        
        result = await session.execute("echo 'Hello, E2B!'")
        
        assert isinstance(result, ExecutionResult)
        assert result.success
        assert result.return_code == 0
        assert result.stdout == "Hello, E2B!"
        
        # Verify E2B command was called
        mock_sandbox.commands.run.assert_called_once_with("echo 'Hello, E2B!'")
    
    async def test_e2b_session_execute_with_timeout(self):
        """Test executing commands with timeout in E2B session."""
        mock_sandbox = AsyncMock()
        mock_sandbox.id = "test_id"
        
        mock_result = MagicMock()
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_result.exit_code = 0
        mock_sandbox.commands.run.return_value = mock_result
        
        session = E2BSandboxSession(mock_sandbox, SandboxConfig())
        
        await session.execute("echo 'test'", timeout=30)
        
        # Verify timeout was passed to E2B
        call_args = mock_sandbox.commands.run.call_args
        assert "timeout" in call_args.kwargs
        assert call_args.kwargs["timeout"] == 30
    
    async def test_e2b_session_upload_file(self):
        """Test uploading files in E2B session."""
        mock_sandbox = AsyncMock()
        mock_sandbox.id = "test_id"
        
        session = E2BSandboxSession(mock_sandbox, SandboxConfig())
        
        content = b"Test content"
        await session.upload_file("test.txt", content)
        
        # Verify E2B file upload was called
        mock_sandbox.files.write.assert_called_once_with("test.txt", content)
    
    async def test_e2b_session_download_file(self):
        """Test downloading files in E2B session."""
        mock_sandbox = AsyncMock()
        mock_sandbox.id = "test_id"
        mock_sandbox.files.read.return_value = b"Downloaded content"
        
        session = E2BSandboxSession(mock_sandbox, SandboxConfig())
        
        content = await session.download_file("test.txt")
        
        assert content == b"Downloaded content"
        mock_sandbox.files.read.assert_called_once_with("test.txt")
    
    async def test_e2b_session_list_files(self):
        """Test listing files in E2B session."""
        mock_sandbox = AsyncMock()
        mock_sandbox.id = "test_id"
        
        # Mock file list response
        mock_files = [
            MagicMock(name="file1.txt", path="/workspace/file1.txt", size=100, is_dir=False),
            MagicMock(name="file2.py", path="/workspace/file2.py", size=200, is_dir=False),
            MagicMock(name="subdir", path="/workspace/subdir", size=0, is_dir=True),
        ]
        mock_sandbox.files.list.return_value = mock_files
        
        session = E2BSandboxSession(mock_sandbox, SandboxConfig())
        
        files = await session.list_files("/workspace")
        
        assert len(files) == 3
        assert all(isinstance(f, FileInfo) for f in files)
        
        # Check file details
        file_names = [f.name for f in files]
        assert "file1.txt" in file_names
        assert "file2.py" in file_names
        assert "subdir" in file_names
        
        mock_sandbox.files.list.assert_called_once_with("/workspace")
    
    async def test_e2b_session_cleanup(self):
        """Test E2B session cleanup."""
        mock_sandbox = AsyncMock()
        mock_sandbox.id = "test_id"
        
        session = E2BSandboxSession(mock_sandbox, SandboxConfig())
        
        await session.cleanup()
        
        # Verify E2B sandbox was closed
        mock_sandbox.close.assert_called_once()


class TestModalProvider:
    """Test cases for the Modal provider."""
    
    def test_modal_provider_creation_with_credentials(self):
        """Test creating Modal provider with credentials."""
        provider = ModalProvider(token_id="test_id", token_secret="test_secret")
        assert provider.provider_name == "modal"
        assert provider.token_id == "test_id"
        assert provider.token_secret == "test_secret"
    
    def test_modal_provider_creation_from_env(self):
        """Test creating Modal provider from environment variables."""
        with patch.dict(os.environ, {
            "MODAL_TOKEN_ID": "env_id",
            "MODAL_TOKEN_SECRET": "env_secret"
        }):
            provider = ModalProvider()
            assert provider.token_id == "env_id"
            assert provider.token_secret == "env_secret"
    
    def test_modal_provider_creation_missing_credentials(self):
        """Test creating Modal provider with missing credentials."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AuthenticationError, match="Modal credentials not provided"):
                ModalProvider()
    
    @patch('grainchain.providers.modal.modal')
    async def test_modal_provider_create_session(self, mock_modal):
        """Test creating Modal session."""
        # Mock Modal client
        mock_client = AsyncMock()
        mock_modal.Client.return_value = mock_client
        
        provider = ModalProvider(token_id="test_id", token_secret="test_secret")
        config = SandboxConfig()
        
        session = await provider.create_session(config)
        
        assert isinstance(session, ModalSandboxSession)
        assert session.client == mock_client
        
        # Verify Modal client was created
        mock_modal.Client.assert_called_once()
    
    async def test_modal_provider_cleanup(self):
        """Test Modal provider cleanup."""
        provider = ModalProvider(token_id="test_id", token_secret="test_secret")
        
        # Create mock sessions
        session1 = AsyncMock()
        session2 = AsyncMock()
        provider.sessions = {"id1": session1, "id2": session2}
        
        await provider.cleanup()
        
        # Verify sessions were cleaned up
        session1.cleanup.assert_called_once()
        session2.cleanup.assert_called_once()
        assert len(provider.sessions) == 0


class TestModalSandboxSession:
    """Test cases for the Modal sandbox session."""
    
    def test_modal_session_creation(self):
        """Test creating Modal session."""
        mock_client = AsyncMock()
        config = SandboxConfig()
        
        session = ModalSandboxSession(mock_client, config)
        
        assert session.client == mock_client
        assert session.config == config
        assert session.session_id is not None
    
    async def test_modal_session_execute(self):
        """Test executing commands in Modal session."""
        mock_client = AsyncMock()
        
        # Mock Modal function execution
        mock_function = AsyncMock()
        mock_function.remote.return_value = {
            "stdout": "Hello, Modal!",
            "stderr": "",
            "return_code": 0,
            "execution_time": 0.1
        }
        mock_client.get_function.return_value = mock_function
        
        session = ModalSandboxSession(mock_client, SandboxConfig())
        
        result = await session.execute("echo 'Hello, Modal!'")
        
        assert isinstance(result, ExecutionResult)
        assert result.success
        assert result.return_code == 0
        assert result.stdout == "Hello, Modal!"
    
    async def test_modal_session_upload_file(self):
        """Test uploading files in Modal session."""
        mock_client = AsyncMock()
        
        session = ModalSandboxSession(mock_client, SandboxConfig())
        
        content = b"Test content"
        await session.upload_file("test.txt", content)
        
        # Verify file was stored in session
        assert "test.txt" in session.files
        assert session.files["test.txt"] == content
    
    async def test_modal_session_download_file(self):
        """Test downloading files in Modal session."""
        mock_client = AsyncMock()
        
        session = ModalSandboxSession(mock_client, SandboxConfig())
        
        # Upload file first
        content = b"Download test"
        session.files["test.txt"] = content
        
        downloaded_content = await session.download_file("test.txt")
        
        assert downloaded_content == content
    
    async def test_modal_session_download_nonexistent_file(self):
        """Test downloading non-existent file in Modal session."""
        mock_client = AsyncMock()
        
        session = ModalSandboxSession(mock_client, SandboxConfig())
        
        with pytest.raises(FileNotFoundError):
            await session.download_file("nonexistent.txt")
    
    async def test_modal_session_list_files(self):
        """Test listing files in Modal session."""
        mock_client = AsyncMock()
        
        session = ModalSandboxSession(mock_client, SandboxConfig())
        
        # Add some files
        session.files["file1.txt"] = b"content1"
        session.files["file2.py"] = b"print('hello')"
        
        files = await session.list_files("/")
        
        assert len(files) == 2
        file_names = [f.name for f in files]
        assert "file1.txt" in file_names
        assert "file2.py" in file_names
    
    async def test_modal_session_cleanup(self):
        """Test Modal session cleanup."""
        mock_client = AsyncMock()
        
        session = ModalSandboxSession(mock_client, SandboxConfig())
        
        # Add some files
        session.files["test.txt"] = b"content"
        
        await session.cleanup()
        
        # Files should be cleared
        assert len(session.files) == 0

