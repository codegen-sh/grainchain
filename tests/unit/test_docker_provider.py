"""
Unit tests for Docker provider.
"""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from pathlib import Path
import tempfile
import os

from grainchain.providers.docker import DockerProvider, DockerSession


class TestDockerSession:
    """Test cases for DockerSession."""
    
    @pytest.fixture
    def mock_docker_client(self):
        """Mock Docker client."""
        client = Mock()
        client.containers = Mock()
        client.images = Mock()
        return client
    
    @pytest.fixture
    def mock_provider(self, mock_docker_client):
        """Mock Docker provider."""
        provider = Mock(spec=DockerProvider)
        provider.docker_client = mock_docker_client
        return provider
    
    @pytest.fixture
    def docker_session(self, mock_provider):
        """Create a Docker session for testing."""
        return DockerSession(
            session_id="test-session",
            provider=mock_provider,
            image="ubuntu:20.04"
        )
    
    def test_init(self, docker_session):
        """Test session initialization."""
        assert docker_session.session_id == "test-session"
        assert docker_session.image == "ubuntu:20.04"
        assert not docker_session.is_active
        assert docker_session.container is None
    
    @pytest.mark.asyncio
    async def test_start_success(self, docker_session, mock_docker_client):
        """Test successful session start."""
        # Mock container
        mock_container = Mock()
        mock_container.id = "container-123"
        mock_docker_client.containers.run.return_value = mock_container
        mock_docker_client.images.get.return_value = Mock()  # Image exists
        
        await docker_session.start()
        
        assert docker_session.is_active
        assert docker_session.container == mock_container
        mock_docker_client.containers.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_image_not_found(self, docker_session, mock_docker_client):
        """Test session start when image needs to be pulled."""
        from docker.errors import ImageNotFound
        
        # Mock container
        mock_container = Mock()
        mock_container.id = "container-123"
        mock_docker_client.containers.run.return_value = mock_container
        
        # First call raises ImageNotFound, second succeeds
        mock_docker_client.images.get.side_effect = [ImageNotFound("Image not found"), Mock()]
        mock_docker_client.images.pull.return_value = Mock()
        
        await docker_session.start()
        
        assert docker_session.is_active
        mock_docker_client.images.pull.assert_called_once_with("ubuntu:20.04")
    
    @pytest.mark.asyncio
    async def test_start_already_active(self, docker_session):
        """Test starting an already active session."""
        docker_session._is_active = True
        
        await docker_session.start()
        
        # Should not call docker client
        docker_session.docker_client.containers.run.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_stop_success(self, docker_session):
        """Test successful session stop."""
        mock_container = Mock()
        docker_session.container = mock_container
        docker_session._is_active = True
        
        await docker_session.stop()
        
        assert not docker_session.is_active
        mock_container.stop.assert_called_once_with(timeout=10)
        mock_container.remove.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stop_not_active(self, docker_session):
        """Test stopping an inactive session."""
        await docker_session.stop()
        
        # Should not raise error
        assert not docker_session.is_active
    
    @pytest.mark.asyncio
    async def test_execute_command_success(self, docker_session):
        """Test successful command execution."""
        mock_container = Mock()
        mock_exec_result = Mock()
        mock_exec_result.output = (b"Hello World\n", b"")
        mock_exec_result.exit_code = 0
        mock_container.exec_run.return_value = mock_exec_result
        
        docker_session.container = mock_container
        docker_session._is_active = True
        
        result = await docker_session.execute_command("echo 'Hello World'")
        
        assert result['stdout'] == "Hello World\n"
        assert result['stderr'] == ""
        assert result['exit_code'] == 0
        assert 'execution_time' in result
        mock_container.exec_run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_command_with_error(self, docker_session):
        """Test command execution with error."""
        mock_container = Mock()
        mock_exec_result = Mock()
        mock_exec_result.output = (b"", b"Command not found\n")
        mock_exec_result.exit_code = 127
        mock_container.exec_run.return_value = mock_exec_result
        
        docker_session.container = mock_container
        docker_session._is_active = True
        
        result = await docker_session.execute_command("nonexistent-command")
        
        assert result['stdout'] == ""
        assert result['stderr'] == "Command not found\n"
        assert result['exit_code'] == 127
    
    @pytest.mark.asyncio
    async def test_execute_command_not_active(self, docker_session):
        """Test command execution when session is not active."""
        with pytest.raises(RuntimeError, match="Session is not active"):
            await docker_session.execute_command("echo test")
    
    @pytest.mark.asyncio
    async def test_upload_file_success(self, docker_session):
        """Test successful file upload."""
        mock_container = Mock()
        docker_session.container = mock_container
        docker_session._is_active = True
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            result = await docker_session.upload_file(temp_file, "/remote/path/file.txt")
            
            assert result is True
            mock_container.put_archive.assert_called_once()
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_upload_file_not_exists(self, docker_session):
        """Test file upload when local file doesn't exist."""
        docker_session._is_active = True
        docker_session.container = Mock()
        
        result = await docker_session.upload_file("/nonexistent/file.txt", "/remote/path")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_download_file_success(self, docker_session):
        """Test successful file download."""
        import tarfile
        import io
        
        mock_container = Mock()
        docker_session.container = mock_container
        docker_session._is_active = True
        
        # Create mock tar data
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            info = tarfile.TarInfo(name="file.txt")
            info.size = 12
            tar.addfile(info, io.BytesIO(b"test content"))
        
        tar_stream.seek(0)
        mock_container.get_archive.return_value = ([tar_stream.getvalue()], {})
        
        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = os.path.join(temp_dir, "downloaded.txt")
            result = await docker_session.download_file("/remote/file.txt", local_path)
            
            assert result is True
            mock_container.get_archive.assert_called_once_with("/remote/file.txt")
    
    @pytest.mark.asyncio
    async def test_list_files_success(self, docker_session):
        """Test successful file listing."""
        mock_container = Mock()
        docker_session.container = mock_container
        docker_session._is_active = True
        
        # Mock execute_command for ls
        with patch.object(docker_session, 'execute_command') as mock_exec:
            mock_exec.return_value = {
                'stdout': 'total 8\ndrwxr-xr-x 2 root root 4096 Jan 1 12:00 .\ndrwxr-xr-x 3 root root 4096 Jan 1 12:00 ..\n-rw-r--r-- 1 root root   12 Jan 1 12:00 file.txt\n',
                'stderr': '',
                'exit_code': 0
            }
            
            files = await docker_session.list_files("/test")
            
            assert len(files) == 3
            assert files[0]['name'] == '.'
            assert files[0]['is_directory'] is True
            assert files[2]['name'] == 'file.txt'
            assert files[2]['is_directory'] is False


class TestDockerProvider:
    """Test cases for DockerProvider."""
    
    @pytest.fixture
    def mock_docker_client(self):
        """Mock Docker client."""
        with patch('grainchain.providers.docker.docker') as mock_docker:
            client = Mock()
            client.ping.return_value = True
            mock_docker.from_env.return_value = client
            mock_docker.DockerClient.return_value = client
            yield client
    
    @pytest.fixture
    def docker_provider(self, mock_docker_client):
        """Create a Docker provider for testing."""
        return DockerProvider()
    
    def test_init_default_config(self, docker_provider):
        """Test provider initialization with default config."""
        assert docker_provider.default_image == 'ubuntu:20.04'
        assert docker_provider.resource_limits['mem_limit'] == '1g'
        assert docker_provider.network_config['network_mode'] == 'bridge'
    
    def test_init_custom_config(self, mock_docker_client):
        """Test provider initialization with custom config."""
        config = {
            'default_image': 'alpine:latest',
            'resource_limits': {'mem_limit': '2g', 'cpu_count': 2},
            'docker_url': 'tcp://localhost:2376'
        }
        
        with patch('grainchain.providers.docker.docker') as mock_docker:
            client = Mock()
            client.ping.return_value = True
            mock_docker.DockerClient.return_value = client
            
            provider = DockerProvider(config)
            
            assert provider.default_image == 'alpine:latest'
            assert provider.resource_limits['mem_limit'] == '2g'
            assert provider.docker_url == 'tcp://localhost:2376'
            mock_docker.DockerClient.assert_called_with(base_url='tcp://localhost:2376')
    
    @pytest.mark.asyncio
    async def test_create_session_success(self, docker_provider):
        """Test successful session creation."""
        session = await docker_provider.create_session(
            session_id="test-session",
            image="alpine:latest"
        )
        
        assert isinstance(session, DockerSession)
        assert session.session_id == "test-session"
        assert session.image == "alpine:latest"
        assert "test-session" in docker_provider._sessions
    
    @pytest.mark.asyncio
    async def test_create_session_auto_id(self, docker_provider):
        """Test session creation with auto-generated ID."""
        session = await docker_provider.create_session()
        
        assert session.session_id is not None
        assert len(session.session_id) > 0
        assert session.image == docker_provider.default_image
    
    @pytest.mark.asyncio
    async def test_create_session_duplicate_id(self, docker_provider):
        """Test creating session with duplicate ID."""
        await docker_provider.create_session(session_id="duplicate")
        
        with pytest.raises(ValueError, match="Session duplicate already exists"):
            await docker_provider.create_session(session_id="duplicate")
    
    @pytest.mark.asyncio
    async def test_destroy_session_success(self, docker_provider):
        """Test successful session destruction."""
        session = await docker_provider.create_session(session_id="test-session")
        
        with patch.object(session, 'stop', new_callable=AsyncMock) as mock_stop:
            result = await docker_provider.destroy_session("test-session")
            
            assert result is True
            assert "test-session" not in docker_provider._sessions
            mock_stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_destroy_session_not_found(self, docker_provider):
        """Test destroying non-existent session."""
        result = await docker_provider.destroy_session("nonexistent")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_session(self, docker_provider):
        """Test getting existing session."""
        session = await docker_provider.create_session(session_id="test-session")
        
        retrieved = await docker_provider.get_session("test-session")
        
        assert retrieved == session
    
    @pytest.mark.asyncio
    async def test_list_sessions(self, docker_provider):
        """Test listing sessions."""
        await docker_provider.create_session(session_id="session1")
        await docker_provider.create_session(session_id="session2")
        
        sessions = await docker_provider.list_sessions()
        
        assert len(sessions) == 2
        assert "session1" in sessions
        assert "session2" in sessions
    
    @pytest.mark.asyncio
    async def test_cleanup_all_sessions(self, docker_provider, mock_docker_client):
        """Test cleaning up all sessions."""
        # Create sessions
        session1 = await docker_provider.create_session(session_id="session1")
        session2 = await docker_provider.create_session(session_id="session2")
        
        # Mock containers list for orphan cleanup
        mock_docker_client.containers.list.return_value = []
        
        with patch.object(session1, 'stop', new_callable=AsyncMock) as mock_stop1, \
             patch.object(session2, 'stop', new_callable=AsyncMock) as mock_stop2:
            
            await docker_provider.cleanup_all_sessions()
            
            assert len(docker_provider._sessions) == 0
            mock_stop1.assert_called_once()
            mock_stop2.assert_called_once()


@pytest.mark.asyncio
async def test_session_context_manager():
    """Test session as async context manager."""
    with patch('grainchain.providers.docker.docker') as mock_docker:
        client = Mock()
        client.ping.return_value = True
        mock_docker.from_env.return_value = client
        
        provider = DockerProvider()
        session = await provider.create_session(session_id="context-test")
        
        with patch.object(session, 'start', new_callable=AsyncMock) as mock_start, \
             patch.object(session, 'stop', new_callable=AsyncMock) as mock_stop:
            
            async with session:
                mock_start.assert_called_once()
            
            mock_stop.assert_called_once()

