"""
Integration tests for Docker provider.

These tests require a running Docker daemon.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path

from grainchain.providers.docker import DockerProvider, DockerSession

# Skip all tests if Docker is not available
docker = pytest.importorskip("docker")

try:
    client = docker.from_env()
    client.ping()
    DOCKER_AVAILABLE = True
except Exception:
    DOCKER_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not DOCKER_AVAILABLE, 
    reason="Docker daemon not available"
)


class TestDockerProviderIntegration:
    """Integration tests for Docker provider with real Docker daemon."""
    
    @pytest.fixture
    async def docker_provider(self):
        """Create a Docker provider for integration testing."""
        provider = DockerProvider({
            'default_image': 'alpine:latest',  # Smaller image for faster tests
            'resource_limits': {
                'mem_limit': '128m',
                'cpu_count': 1
            }
        })
        yield provider
        # Cleanup after test
        await provider.cleanup_all_sessions()
    
    @pytest.mark.asyncio
    async def test_full_session_lifecycle(self, docker_provider):
        """Test complete session lifecycle."""
        # Create session
        session = await docker_provider.create_session(
            session_id="integration-test",
            image="alpine:latest"
        )
        
        assert isinstance(session, DockerSession)
        assert session.session_id == "integration-test"
        assert not session.is_active
        
        try:
            # Start session
            await session.start()
            assert session.is_active
            assert session.container is not None
            
            # Execute simple command
            result = await session.execute_command("echo 'Hello World'")
            assert result['exit_code'] == 0
            assert "Hello World" in result['stdout']
            assert result['stderr'] == ""
            
            # Execute command with error
            result = await session.execute_command("nonexistent-command")
            assert result['exit_code'] != 0
            assert result['stderr'] != ""
            
        finally:
            # Stop session
            await session.stop()
            assert not session.is_active
    
    @pytest.mark.asyncio
    async def test_file_operations(self, docker_provider):
        """Test file upload and download operations."""
        session = await docker_provider.create_session(image="alpine:latest")
        
        try:
            await session.start()
            
            # Create a test file
            test_content = "This is a test file for integration testing."
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(test_content)
                local_file = f.name
            
            try:
                # Upload file
                remote_path = "/tmp/test_file.txt"
                upload_success = await session.upload_file(local_file, remote_path)
                assert upload_success
                
                # Verify file exists in container
                result = await session.execute_command(f"cat {remote_path}")
                assert result['exit_code'] == 0
                assert test_content in result['stdout']
                
                # Download file
                with tempfile.NamedTemporaryFile(delete=False) as f:
                    download_file = f.name
                
                try:
                    download_success = await session.download_file(remote_path, download_file)
                    assert download_success
                    
                    # Verify downloaded content
                    with open(download_file, 'r') as f:
                        downloaded_content = f.read()
                    assert test_content in downloaded_content
                    
                finally:
                    os.unlink(download_file)
                    
            finally:
                os.unlink(local_file)
                
        finally:
            await session.stop()
    
    @pytest.mark.asyncio
    async def test_directory_listing(self, docker_provider):
        """Test directory listing functionality."""
        session = await docker_provider.create_session(image="alpine:latest")
        
        try:
            await session.start()
            
            # Create some files and directories
            await session.execute_command("mkdir -p /tmp/test_dir")
            await session.execute_command("touch /tmp/test_dir/file1.txt")
            await session.execute_command("touch /tmp/test_dir/file2.txt")
            await session.execute_command("mkdir /tmp/test_dir/subdir")
            
            # List directory
            files = await session.list_files("/tmp/test_dir")
            
            # Should have at least the files we created
            file_names = [f['name'] for f in files]
            assert 'file1.txt' in file_names
            assert 'file2.txt' in file_names
            assert 'subdir' in file_names
            
            # Check file types
            subdir_info = next(f for f in files if f['name'] == 'subdir')
            assert subdir_info['is_directory']
            
            file_info = next(f for f in files if f['name'] == 'file1.txt')
            assert not file_info['is_directory']
            
        finally:
            await session.stop()
    
    @pytest.mark.asyncio
    async def test_environment_variables(self, docker_provider):
        """Test environment variable handling."""
        session = await docker_provider.create_session(
            image="alpine:latest",
            environment={'TEST_VAR': 'test_value'}
        )
        
        try:
            await session.start()
            
            # Test container environment
            result = await session.execute_command("echo $TEST_VAR")
            assert result['exit_code'] == 0
            assert "test_value" in result['stdout']
            
            # Test command-specific environment
            result = await session.execute_command(
                "echo $COMMAND_VAR", 
                env={'COMMAND_VAR': 'command_value'}
            )
            assert result['exit_code'] == 0
            assert "command_value" in result['stdout']
            
        finally:
            await session.stop()
    
    @pytest.mark.asyncio
    async def test_working_directory(self, docker_provider):
        """Test working directory functionality."""
        session = await docker_provider.create_session(
            image="alpine:latest",
            working_dir="/tmp"
        )
        
        try:
            await session.start()
            
            # Test default working directory
            result = await session.execute_command("pwd")
            assert result['exit_code'] == 0
            assert "/tmp" in result['stdout']
            
            # Test command-specific working directory
            result = await session.execute_command("pwd", working_dir="/usr")
            assert result['exit_code'] == 0
            assert "/usr" in result['stdout']
            
        finally:
            await session.stop()
    
    @pytest.mark.asyncio
    async def test_multiple_sessions(self, docker_provider):
        """Test managing multiple concurrent sessions."""
        sessions = []
        
        try:
            # Create multiple sessions
            for i in range(3):
                session = await docker_provider.create_session(
                    session_id=f"multi-test-{i}",
                    image="alpine:latest"
                )
                sessions.append(session)
                await session.start()
            
            # Verify all sessions are active
            for session in sessions:
                assert session.is_active
                
                # Test each session independently
                result = await session.execute_command(f"echo 'Session {session.session_id}'")
                assert result['exit_code'] == 0
                assert session.session_id in result['stdout']
            
            # List all sessions
            session_ids = await docker_provider.list_sessions()
            assert len(session_ids) == 3
            for session in sessions:
                assert session.session_id in session_ids
                
        finally:
            # Cleanup all sessions
            for session in sessions:
                await session.stop()
    
    @pytest.mark.asyncio
    async def test_session_context_manager(self, docker_provider):
        """Test session as async context manager."""
        session = await docker_provider.create_session(image="alpine:latest")
        
        # Use session as context manager
        async with session:
            assert session.is_active
            
            result = await session.execute_command("echo 'Context manager test'")
            assert result['exit_code'] == 0
            assert "Context manager test" in result['stdout']
        
        # Session should be stopped after context
        assert not session.is_active
    
    @pytest.mark.asyncio
    async def test_error_handling(self, docker_provider):
        """Test error handling scenarios."""
        # Test with non-existent image
        with pytest.raises(RuntimeError):
            session = await docker_provider.create_session(image="nonexistent:image")
            await session.start()
    
    @pytest.mark.asyncio
    async def test_resource_limits(self, docker_provider):
        """Test resource limit enforcement."""
        session = await docker_provider.create_session(
            image="alpine:latest",
            mem_limit="64m",
            cpu_count=1
        )
        
        try:
            await session.start()
            
            # Verify container is running with limits
            assert session.is_active
            
            # Test basic functionality still works
            result = await session.execute_command("echo 'Resource test'")
            assert result['exit_code'] == 0
            
        finally:
            await session.stop()


@pytest.mark.asyncio
async def test_provider_cleanup():
    """Test provider cleanup functionality."""
    provider = DockerProvider({'default_image': 'alpine:latest'})
    
    try:
        # Create some sessions
        session1 = await provider.create_session(session_id="cleanup-1")
        session2 = await provider.create_session(session_id="cleanup-2")
        
        await session1.start()
        await session2.start()
        
        assert len(await provider.list_sessions()) == 2
        
        # Cleanup all
        await provider.cleanup_all_sessions()
        
        assert len(await provider.list_sessions()) == 0
        assert not session1.is_active
        assert not session2.is_active
        
    finally:
        # Ensure cleanup even if test fails
        await provider.cleanup_all_sessions()

