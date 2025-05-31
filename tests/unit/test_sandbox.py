"""
Unit tests for the main Sandbox class.

Tests the core sandbox functionality, provider integration, and error handling.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from grainchain import Sandbox, SandboxConfig
from grainchain.core.exceptions import SandboxError, ConfigurationError
from grainchain.core.interfaces import ExecutionResult, FileInfo, SandboxStatus, SandboxProvider


class MockSandboxProvider(SandboxProvider):
    """Mock implementation of SandboxProvider for testing."""
    
    def __init__(self, name="test_provider"):
        self._name = name
        self._create_sandbox_mock = AsyncMock()
        self._cleanup_mock = AsyncMock()
        self._get_sandbox_status_mock = AsyncMock()
        self._list_sandboxes_mock = AsyncMock()
    
    @property
    def name(self) -> str:
        return self._name
    
    async def create_sandbox(self, config):
        """Mock create_sandbox method."""
        return await self._create_sandbox_mock(config)
    
    async def cleanup(self):
        """Mock cleanup method."""
        return await self._cleanup_mock()
    
    async def get_sandbox_status(self, sandbox_id):
        """Mock get_sandbox_status method."""
        return await self._get_sandbox_status_mock(sandbox_id)
    
    async def list_sandboxes(self):
        """Mock list_sandboxes method."""
        return await self._list_sandboxes_mock()


class TestSandbox:
    """Test cases for the main Sandbox class."""
    
    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider for testing."""
        provider = MockSandboxProvider("test_provider")
        
        # Mock session
        mock_session = AsyncMock()
        mock_session.sandbox_id = "test_sandbox_123"
        mock_session.status = SandboxStatus.RUNNING
        
        provider._create_sandbox_mock.return_value = mock_session
        
        return provider
    
    @pytest.fixture
    def sandbox_config(self):
        """Create a test sandbox configuration."""
        return SandboxConfig(
            timeout=300,
            working_directory="/workspace",
            environment_vars={"TEST_VAR": "test_value"},
            auto_cleanup=True
        )
    
    def test_sandbox_creation(self, mock_provider, sandbox_config):
        """Test creating a sandbox instance."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        
        assert sandbox._provider == mock_provider
        assert sandbox._config == sandbox_config
        assert sandbox._session is None
        assert sandbox._closed is False
    
    def test_sandbox_creation_with_defaults(self):
        """Test creating a sandbox with default configuration."""
        with patch('grainchain.core.sandbox.get_config_manager') as mock_get_config:
            mock_config_manager = MagicMock()
            mock_config_manager.default_provider = "e2b"
            mock_config_manager.get_sandbox_defaults.return_value = SandboxConfig()
            mock_config_manager.get_provider_config.return_value = MagicMock()
            mock_get_config.return_value = mock_config_manager
            
            with patch('grainchain.core.sandbox.Sandbox._create_provider') as mock_create:
                mock_provider = AsyncMock()
                mock_create.return_value = mock_provider
                
                sandbox = Sandbox()
                
                assert sandbox._provider == mock_provider
                assert isinstance(sandbox._config, SandboxConfig)
    
    def test_sandbox_provider_resolution_string(self):
        """Test resolving provider from string name."""
        with patch('grainchain.core.sandbox.get_config_manager') as mock_get_config:
            mock_config_manager = MagicMock()
            mock_config_manager.get_provider_config.return_value = MagicMock()
            mock_get_config.return_value = mock_config_manager
            
            with patch('grainchain.providers.local.LocalProvider') as mock_local:
                mock_provider_instance = AsyncMock()
                mock_local.return_value = mock_provider_instance
                
                sandbox = Sandbox(provider="local")
                
                assert sandbox._provider == mock_provider_instance
                mock_local.assert_called_once()
    
    def test_sandbox_invalid_provider_type(self):
        """Test error handling for invalid provider type."""
        with pytest.raises(ConfigurationError, match="Invalid provider type"):
            Sandbox(provider=123)  # Invalid type
    
    def test_sandbox_unknown_provider_name(self):
        """Test error handling for unknown provider name."""
        with patch('grainchain.core.sandbox.get_config_manager') as mock_get_config:
            mock_config_manager = MagicMock()
            mock_config_manager.get_provider_config.return_value = MagicMock()
            mock_get_config.return_value = mock_config_manager
            
            with pytest.raises(ConfigurationError, match="Unknown provider"):
                Sandbox(provider="unknown_provider")
    
    async def test_sandbox_context_manager(self, mock_provider, sandbox_config):
        """Test using sandbox as async context manager."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        
        async with sandbox as ctx:
            assert ctx is sandbox
            assert sandbox._session is not None
            mock_provider._create_sandbox_mock.assert_called_once_with(sandbox_config)
        
        # Should be closed after context exit
        assert sandbox._closed is True
        sandbox._session.close.assert_called_once()
    
    async def test_sandbox_context_manager_creation_failure(self, mock_provider, sandbox_config):
        """Test context manager when sandbox creation fails."""
        mock_provider._create_sandbox_mock.side_effect = Exception("Creation failed")
        
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        
        with pytest.raises(SandboxError, match="Failed to create sandbox"):
            async with sandbox:
                pass
    
    async def test_sandbox_explicit_create(self, mock_provider, sandbox_config):
        """Test explicitly creating sandbox session."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        
        result = await sandbox.create()
        
        assert result is sandbox
        assert sandbox._session is not None
        mock_provider._create_sandbox_mock.assert_called_once_with(sandbox_config)
    
    async def test_sandbox_create_already_exists(self, mock_provider, sandbox_config):
        """Test error when trying to create session that already exists."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        await sandbox.create()
        
        with pytest.raises(SandboxError, match="Sandbox session already exists"):
            await sandbox.create()
    
    async def test_sandbox_reuse_closed(self, mock_provider, sandbox_config):
        """Test error when trying to reuse a closed sandbox."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        
        async with sandbox:
            pass  # This will close the sandbox
        
        with pytest.raises(SandboxError, match="Cannot reuse a closed sandbox"):
            async with sandbox:
                pass
    
    async def test_sandbox_execute(self, mock_provider, sandbox_config):
        """Test command execution in sandbox."""
        mock_result = ExecutionResult(
            command="echo 'test'",
            return_code=0,
            stdout="test\n",
            stderr="",
            execution_time=0.1
        )
        
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        
        async with sandbox:
            sandbox._session.execute.return_value = mock_result
            
            result = await sandbox.execute("echo 'test'")
            
            assert result == mock_result
            sandbox._session.execute.assert_called_once_with(
                command="echo 'test'",
                timeout=300,  # From config
                working_dir=None,
                environment=None
            )
    
    async def test_sandbox_execute_with_options(self, mock_provider, sandbox_config):
        """Test command execution with custom options."""
        mock_result = ExecutionResult(
            command="ls",
            return_code=0,
            stdout="file1.txt\n",
            stderr="",
            execution_time=0.05
        )
        
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        
        async with sandbox:
            sandbox._session.execute.return_value = mock_result
            
            result = await sandbox.execute(
                "ls",
                timeout=60,
                working_dir="/tmp",
                environment={"CUSTOM": "value"}
            )
            
            assert result == mock_result
            sandbox._session.execute.assert_called_once_with(
                command="ls",
                timeout=60,
                working_dir="/tmp",
                environment={"CUSTOM": "value"}
            )
    
    async def test_sandbox_execute_no_session(self, mock_provider, sandbox_config):
        """Test command execution without active session."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        
        with pytest.raises(SandboxError, match="Sandbox session not initialized"):
            await sandbox.execute("echo 'test'")
    
    async def test_sandbox_upload_file(self, mock_provider, sandbox_config):
        """Test file upload to sandbox."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        
        async with sandbox:
            await sandbox.upload_file("test.txt", "Hello, World!")
            
            sandbox._session.upload_file.assert_called_once_with(
                "test.txt", "Hello, World!", "w"
            )
    
    async def test_sandbox_upload_file_binary(self, mock_provider, sandbox_config):
        """Test binary file upload to sandbox."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        binary_content = b"\\x00\\x01\\x02\\x03"
        
        async with sandbox:
            await sandbox.upload_file("binary.dat", binary_content, "wb")
            
            sandbox._session.upload_file.assert_called_once_with(
                "binary.dat", binary_content, "wb"
            )
    
    async def test_sandbox_download_file(self, mock_provider, sandbox_config):
        """Test file download from sandbox."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        expected_content = b"File content"
        
        async with sandbox:
            sandbox._session.download_file.return_value = expected_content
            
            content = await sandbox.download_file("test.txt")
            
            assert content == expected_content
            sandbox._session.download_file.assert_called_once_with("test.txt")
    
    async def test_sandbox_list_files(self, mock_provider, sandbox_config):
        """Test listing files in sandbox."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        expected_files = [
            FileInfo(name="file1.txt", size=100, is_directory=False),
            FileInfo(name="dir1", size=0, is_directory=True)
        ]
        
        async with sandbox:
            sandbox._session.list_files.return_value = expected_files
            
            files = await sandbox.list_files("/workspace")
            
            assert files == expected_files
            sandbox._session.list_files.assert_called_once_with("/workspace")
    
    async def test_sandbox_list_files_default_path(self, mock_provider, sandbox_config):
        """Test listing files with default path."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        
        async with sandbox:
            sandbox._session.list_files.return_value = []
            
            await sandbox.list_files()
            
            sandbox._session.list_files.assert_called_once_with("/")
    
    async def test_sandbox_create_snapshot(self, mock_provider, sandbox_config):
        """Test creating sandbox snapshot."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        expected_snapshot_id = "snapshot_123"
        
        async with sandbox:
            sandbox._session.create_snapshot.return_value = expected_snapshot_id
            
            snapshot_id = await sandbox.create_snapshot()
            
            assert snapshot_id == expected_snapshot_id
            sandbox._session.create_snapshot.assert_called_once()
    
    async def test_sandbox_restore_snapshot(self, mock_provider, sandbox_config):
        """Test restoring sandbox snapshot."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        snapshot_id = "snapshot_123"
        
        async with sandbox:
            await sandbox.restore_snapshot(snapshot_id)
            
            sandbox._session.restore_snapshot.assert_called_once_with(snapshot_id)
    
    def test_sandbox_properties(self, mock_provider, sandbox_config):
        """Test sandbox properties."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        
        # Before session creation
        assert sandbox.status == SandboxStatus.UNKNOWN
        assert sandbox.sandbox_id is None
        assert sandbox.provider_name == "test_provider"
    
    async def test_sandbox_properties_with_session(self, mock_provider, sandbox_config):
        """Test sandbox properties with active session."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        
        async with sandbox:
            assert sandbox.status == SandboxStatus.RUNNING
            assert sandbox.sandbox_id == "test_sandbox_123"
            assert sandbox.provider_name == "test_provider"
    
    def test_sandbox_repr(self, mock_provider, sandbox_config):
        """Test sandbox string representation."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        
        repr_str = repr(sandbox)
        
        assert "Sandbox" in repr_str
        assert "test_provider" in repr_str
        assert "not_created" in repr_str
    
    async def test_sandbox_repr_with_session(self, mock_provider, sandbox_config):
        """Test sandbox string representation with active session."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        
        async with sandbox:
            repr_str = repr(sandbox)
            
            assert "Sandbox" in repr_str
            assert "test_provider" in repr_str
            assert "running" in repr_str
            assert "test_sandbox_123" in repr_str
    
    async def test_sandbox_operation_error_handling(self, mock_provider, sandbox_config):
        """Test error handling in sandbox operations."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        
        async with sandbox:
            # Test execute error
            sandbox._session.execute.side_effect = Exception("Execute failed")
            with pytest.raises(SandboxError, match="Command execution failed"):
                await sandbox.execute("test command")
            
            # Test upload error
            sandbox._session.upload_file.side_effect = Exception("Upload failed")
            with pytest.raises(SandboxError, match="File upload failed"):
                await sandbox.upload_file("test.txt", "content")
            
            # Test download error
            sandbox._session.download_file.side_effect = Exception("Download failed")
            with pytest.raises(SandboxError, match="File download failed"):
                await sandbox.download_file("test.txt")
            
            # Test list files error
            sandbox._session.list_files.side_effect = Exception("List failed")
            with pytest.raises(SandboxError, match="File listing failed"):
                await sandbox.list_files()
            
            # Test snapshot creation error
            sandbox._session.create_snapshot.side_effect = Exception("Snapshot failed")
            with pytest.raises(SandboxError, match="Snapshot creation failed"):
                await sandbox.create_snapshot()
            
            # Test snapshot restoration error
            sandbox._session.restore_snapshot.side_effect = Exception("Restore failed")
            with pytest.raises(SandboxError, match="Snapshot restoration failed"):
                await sandbox.restore_snapshot("snapshot_123")
    
    async def test_sandbox_close_error_handling(self, mock_provider, sandbox_config):
        """Test error handling during sandbox close."""
        sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
        
        async with sandbox:
            # Make close raise an exception
            sandbox._session.close.side_effect = Exception("Close failed")
            # Should not propagate the exception, just log it
        
        # Sandbox should still be marked as closed
        assert sandbox._closed is True
        assert sandbox._session is None
