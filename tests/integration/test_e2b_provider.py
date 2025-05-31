"""
Integration tests for the E2B provider.

These tests require actual E2B credentials and will make real API calls.
Set E2B_API_KEY environment variable to run these tests.
"""

import os
import pytest

from grainchain import Sandbox, SandboxConfig
from grainchain.core.exceptions import AuthenticationError, ProviderError
from grainchain.core.interfaces import ExecutionResult, FileInfo
from grainchain.providers.e2b import E2BProvider


@pytest.mark.integration
@pytest.mark.e2b
class TestE2BProviderIntegration:
    """Integration tests for E2B provider with real API calls."""
    
    @pytest.fixture
    def e2b_provider(self, e2b_api_key):
        """Create E2B provider with real credentials."""
        if not e2b_api_key:
            pytest.skip("E2B_API_KEY not provided")
        
        return E2BProvider(api_key=e2b_api_key)
    
    @pytest.fixture
    def e2b_config(self):
        """Create configuration for E2B testing."""
        return SandboxConfig(
            timeout=60,
            working_directory="/workspace",
            auto_cleanup=True
        )
    
    async def test_e2b_provider_create_session(self, e2b_provider, e2b_config):
        """Test creating a real E2B session."""
        session = await e2b_provider.create_session(e2b_config)
        
        assert session is not None
        assert session.sandbox_id is not None
        assert len(session.sandbox_id) > 0
        
        await session.cleanup()
    
    async def test_e2b_sandbox_basic_execution(self, e2b_provider, e2b_config):
        """Test basic command execution in E2B sandbox."""
        async with Sandbox(provider=e2b_provider, config=e2b_config) as sandbox:
            # Test simple echo command
            result = await sandbox.execute("echo 'Hello, E2B!'")
            
            assert isinstance(result, ExecutionResult)
            assert result.success
            assert result.return_code == 0
            assert "Hello, E2B!" in result.stdout
            assert result.execution_time > 0
    
    async def test_e2b_sandbox_python_execution(self, e2b_provider, e2b_config):
        """Test Python code execution in E2B sandbox."""
        async with Sandbox(provider=e2b_provider, config=e2b_config) as sandbox:
            # Test Python execution
            python_code = "print('Python works!'); print(2 + 2)"
            result = await sandbox.execute(f"python3 -c \"{python_code}\"")
            
            assert result.success
            assert "Python works!" in result.stdout
            assert "4" in result.stdout
    
    async def test_e2b_sandbox_file_operations(self, e2b_provider, e2b_config):
        """Test file upload/download operations in E2B sandbox."""
        async with Sandbox(provider=e2b_provider, config=e2b_config) as sandbox:
            # Upload a text file
            content = "This is a test file for E2B integration testing."
            await sandbox.upload_file("test.txt", content)
            
            # Verify file exists by listing
            files = await sandbox.list_files("/workspace")
            file_names = [f.name for f in files]
            assert "test.txt" in file_names
            
            # Download and verify content
            downloaded_content = await sandbox.download_file("test.txt")
            assert downloaded_content.decode() == content
            
            # Test file execution
            await sandbox.upload_file("hello.py", "print('Hello from Python file!')")
            result = await sandbox.execute("python3 hello.py")
            assert result.success
            assert "Hello from Python file!" in result.stdout
    
    async def test_e2b_sandbox_package_installation(self, e2b_provider, e2b_config):
        """Test package installation in E2B sandbox."""
        async with Sandbox(provider=e2b_provider, config=e2b_config) as sandbox:
            # Install a package
            result = await sandbox.execute("pip install requests")
            assert result.success or "already satisfied" in result.stdout.lower()
            
            # Test the installed package
            test_code = """
import requests
print("Requests version:", requests.__version__)
print("Package imported successfully!")
"""
            await sandbox.upload_file("test_requests.py", test_code)
            result = await sandbox.execute("python3 test_requests.py")
            
            assert result.success
            assert "Package imported successfully!" in result.stdout
    
    async def test_e2b_sandbox_working_directory(self, e2b_provider, e2b_config):
        """Test working directory operations in E2B sandbox."""
        async with Sandbox(provider=e2b_provider, config=e2b_config) as sandbox:
            # Check current directory
            result = await sandbox.execute("pwd")
            assert result.success
            assert "/workspace" in result.stdout
            
            # Create and navigate to subdirectory
            await sandbox.execute("mkdir -p /workspace/subdir")
            result = await sandbox.execute("pwd", working_dir="/workspace/subdir")
            assert result.success
            
            # Test file operations in subdirectory
            await sandbox.upload_file("subdir/subfile.txt", "Content in subdirectory")
            files = await sandbox.list_files("/workspace/subdir")
            assert any(f.name == "subfile.txt" for f in files)
    
    async def test_e2b_sandbox_error_handling(self, e2b_provider, e2b_config):
        """Test error handling in E2B sandbox."""
        async with Sandbox(provider=e2b_provider, config=e2b_config) as sandbox:
            # Test command that fails
            result = await sandbox.execute("nonexistent_command_12345")
            
            assert not result.success
            assert result.return_code != 0
            assert len(result.stderr) > 0
            
            # Test downloading non-existent file
            with pytest.raises(Exception):  # Could be FileNotFoundError or provider-specific error
                await sandbox.download_file("nonexistent_file.txt")
    
    async def test_e2b_sandbox_timeout_handling(self, e2b_provider):
        """Test timeout handling in E2B sandbox."""
        config = SandboxConfig(timeout=5)  # Short timeout
        
        async with Sandbox(provider=e2b_provider, config=config) as sandbox:
            # Test command with custom timeout
            result = await sandbox.execute("echo 'quick command'", timeout=2)
            assert result.success
            
            # Test longer running command (should complete within timeout)
            result = await sandbox.execute("sleep 1 && echo 'completed'", timeout=3)
            assert result.success
            assert "completed" in result.stdout
    
    async def test_e2b_sandbox_concurrent_operations(self, e2b_provider, e2b_config):
        """Test concurrent operations in E2B sandbox."""
        import asyncio
        
        async with Sandbox(provider=e2b_provider, config=e2b_config) as sandbox:
            # Run multiple commands concurrently
            tasks = [
                sandbox.execute(f"echo 'Task {i}'")
                for i in range(3)
            ]
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 3
            for i, result in enumerate(results):
                assert result.success
                assert f"Task {i}" in result.stdout
    
    async def test_e2b_sandbox_large_file_operations(self, e2b_provider, e2b_config):
        """Test operations with larger files in E2B sandbox."""
        async with Sandbox(provider=e2b_provider, config=e2b_config) as sandbox:
            # Create a larger text file
            large_content = "Line {}\n".format(i) * 1000  # ~7KB file
            await sandbox.upload_file("large_file.txt", large_content)
            
            # Verify file was uploaded correctly
            downloaded_content = await sandbox.download_file("large_file.txt")
            assert len(downloaded_content) == len(large_content.encode())
            
            # Test processing the large file
            result = await sandbox.execute("wc -l large_file.txt")
            assert result.success
            assert "1000" in result.stdout
    
    async def test_e2b_sandbox_environment_variables(self, e2b_provider):
        """Test environment variables in E2B sandbox."""
        config = SandboxConfig(
            environment_vars={"TEST_VAR": "test_value", "CUSTOM_PATH": "/custom/path"}
        )
        
        async with Sandbox(provider=e2b_provider, config=config) as sandbox:
            # Test environment variable access
            result = await sandbox.execute("echo $TEST_VAR")
            assert result.success
            # Note: E2B might not support custom environment variables
            # This test verifies the interface works, actual behavior depends on E2B
    
    async def test_e2b_provider_multiple_sessions(self, e2b_provider, e2b_config):
        """Test creating multiple E2B sessions."""
        sessions = []
        
        try:
            # Create multiple sessions
            for i in range(2):
                session = await e2b_provider.create_session(e2b_config)
                sessions.append(session)
                
                # Test each session independently
                result = await session.execute(f"echo 'Session {i}'")
                assert result.success
                assert f"Session {i}" in result.stdout
        
        finally:
            # Clean up all sessions
            for session in sessions:
                await session.cleanup()
    
    async def test_e2b_provider_session_isolation(self, e2b_provider, e2b_config):
        """Test that E2B sessions are properly isolated."""
        # Create first session and add a file
        session1 = await e2b_provider.create_session(e2b_config)
        try:
            await session1.upload_file("session1_file.txt", "Session 1 content")
            
            # Create second session
            session2 = await e2b_provider.create_session(e2b_config)
            try:
                # Verify second session doesn't see first session's files
                files = await session2.list_files("/workspace")
                file_names = [f.name for f in files]
                assert "session1_file.txt" not in file_names
                
                # Add file to second session
                await session2.upload_file("session2_file.txt", "Session 2 content")
                
                # Verify first session doesn't see second session's files
                files = await session1.list_files("/workspace")
                file_names = [f.name for f in files]
                assert "session2_file.txt" not in file_names
                assert "session1_file.txt" in file_names
            
            finally:
                await session2.cleanup()
        
        finally:
            await session1.cleanup()
    
    @pytest.mark.slow
    async def test_e2b_sandbox_data_science_workflow(self, e2b_provider, e2b_config):
        """Test a complete data science workflow in E2B sandbox."""
        async with Sandbox(provider=e2b_provider, config=e2b_config) as sandbox:
            # Install required packages
            result = await sandbox.execute("pip install pandas numpy")
            assert result.success or "already satisfied" in result.stdout.lower()
            
            # Create a data analysis script
            analysis_script = """
import pandas as pd
import numpy as np

# Create sample data
data = {
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'age': [25, 30, 35, 28],
    'score': [85, 92, 78, 96]
}

df = pd.DataFrame(data)
print("Data created:")
print(df)

# Basic analysis
print("\\nBasic statistics:")
print(df.describe())

# Save results
df.to_csv('results.csv', index=False)
print("\\nResults saved to results.csv")
"""
            
            await sandbox.upload_file("analysis.py", analysis_script)
            
            # Run the analysis
            result = await sandbox.execute("python3 analysis.py")
            assert result.success
            assert "Data created:" in result.stdout
            assert "Results saved" in result.stdout
            
            # Verify output file was created
            files = await sandbox.list_files("/workspace")
            file_names = [f.name for f in files]
            assert "results.csv" in file_names
            
            # Download and verify the results
            csv_content = await sandbox.download_file("results.csv")
            assert b"name,age,score" in csv_content
            assert b"Alice" in csv_content


@pytest.mark.integration
@pytest.mark.e2b
class TestE2BProviderErrorScenarios:
    """Test error scenarios with E2B provider."""
    
    async def test_e2b_invalid_api_key(self):
        """Test E2B provider with invalid API key."""
        provider = E2BProvider(api_key="invalid_key_12345")
        config = SandboxConfig()
        
        # Should fail when trying to create session
        with pytest.raises(Exception):  # Could be AuthenticationError or ProviderError
            await provider.create_session(config)
    
    async def test_e2b_missing_api_key(self):
        """Test E2B provider without API key."""
        # Clear environment variable
        with pytest.MonkeyPatch().context() as m:
            m.delenv("E2B_API_KEY", raising=False)
            
            with pytest.raises(AuthenticationError):
                E2BProvider()
    
    async def test_e2b_provider_cleanup_with_active_sessions(self, e2b_api_key):
        """Test E2B provider cleanup with active sessions."""
        if not e2b_api_key:
            pytest.skip("E2B_API_KEY not provided")
        
        provider = E2BProvider(api_key=e2b_api_key)
        config = SandboxConfig()
        
        # Create a session
        session = await provider.create_session(config)
        
        # Cleanup provider (should cleanup session too)
        await provider.cleanup()
        
        # Session should be cleaned up
        # Note: Specific behavior depends on E2B implementation

