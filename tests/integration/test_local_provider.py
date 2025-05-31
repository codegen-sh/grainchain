"""Integration tests for Local provider."""

import asyncio

import pytest

from grainchain import Sandbox, SandboxConfig
from grainchain.core.exceptions import SandboxError


class TestLocalProviderIntegration:
    """Integration tests for Local provider."""

    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_provider_basic_functionality(self, temp_dir):
        """Test basic Local provider functionality."""
        config = SandboxConfig(timeout=30, working_directory=str(temp_dir))

        async with Sandbox(provider="local", config=config) as sandbox:
            assert sandbox.provider_name == "local"
            assert sandbox.sandbox_id is not None

            # Test basic command execution
            result = await sandbox.execute("echo 'Hello from Local!'")
            assert result.return_code == 0
            assert "Hello from Local!" in result.stdout

    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_python_execution(self, temp_dir):
        """Test Python code execution with Local provider."""
        config = SandboxConfig(timeout=30, working_directory=str(temp_dir))

        async with Sandbox(provider="local", config=config) as sandbox:
            # Test Python execution
            python_code = "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}')"
            result = await sandbox.execute(f'python3 -c "{python_code}"')

            assert result.return_code == 0
            assert "Python" in result.stdout

    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_file_operations(self, temp_dir):
        """Test file operations with Local provider."""
        config = SandboxConfig(timeout=30, working_directory=str(temp_dir))

        async with Sandbox(provider="local", config=config) as sandbox:
            # Upload a file
            test_content = "Hello, Local file system!"
            await sandbox.upload_file("test_file.txt", test_content)

            # Verify file exists on disk
            file_path = temp_dir / "test_file.txt"
            assert file_path.exists()
            assert file_path.read_text() == test_content

            # Download the file
            downloaded = await sandbox.download_file("test_file.txt")
            assert downloaded.decode() == test_content

            # List files
            files = await sandbox.list_files(".")
            file_names = [f.name for f in files]
            assert "test_file.txt" in file_names

    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_binary_file_operations(self, temp_dir):
        """Test binary file operations with Local provider."""
        config = SandboxConfig(timeout=30, working_directory=str(temp_dir))

        async with Sandbox(provider="local", config=config) as sandbox:
            # Create binary content
            binary_content = bytes(range(256))

            # Upload binary file
            await sandbox.upload_file("binary_test.bin", binary_content, mode="wb")

            # Verify file exists on disk
            file_path = temp_dir / "binary_test.bin"
            assert file_path.exists()
            assert file_path.read_bytes() == binary_content

            # Download and verify
            downloaded = await sandbox.download_file("binary_test.bin")
            assert downloaded == binary_content

    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_directory_operations(self, temp_dir):
        """Test directory operations with Local provider."""
        config = SandboxConfig(timeout=30, working_directory=str(temp_dir))

        async with Sandbox(provider="local", config=config) as sandbox:
            # Create directory structure
            await sandbox.execute("mkdir -p subdir/nested")

            # Upload files to different directories
            await sandbox.upload_file("subdir/file1.txt", "File 1 content")
            await sandbox.upload_file("subdir/nested/file2.txt", "File 2 content")

            # List files in subdirectory
            files = await sandbox.list_files("subdir")
            file_names = [f.name for f in files]
            assert "file1.txt" in file_names
            assert "nested" in file_names

            # List files in nested directory
            nested_files = await sandbox.list_files("subdir/nested")
            nested_file_names = [f.name for f in nested_files]
            assert "file2.txt" in nested_file_names

    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_command_with_pipes(self, temp_dir):
        """Test command execution with pipes and redirects."""
        config = SandboxConfig(timeout=30, working_directory=str(temp_dir))

        async with Sandbox(provider="local", config=config) as sandbox:
            # Test pipe operations
            result = await sandbox.execute("echo 'hello world' | grep 'world'")
            assert result.return_code == 0
            assert "world" in result.stdout

            # Test output redirection
            result = await sandbox.execute("echo 'test content' > output.txt")
            assert result.return_code == 0

            # Verify file was created
            result = await sandbox.execute("cat output.txt")
            assert result.return_code == 0
            assert "test content" in result.stdout

    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_environment_variables(self, temp_dir):
        """Test environment variables with Local provider."""
        config = SandboxConfig(
            timeout=30,
            working_directory=str(temp_dir),
            environment_vars={"TEST_VAR": "test_value", "ANOTHER_VAR": "another_value"},
        )

        async with Sandbox(provider="local", config=config) as sandbox:
            # Test environment variables
            result = await sandbox.execute("echo $TEST_VAR")
            assert result.return_code == 0
            assert "test_value" in result.stdout

            result = await sandbox.execute("echo $ANOTHER_VAR")
            assert result.return_code == 0
            assert "another_value" in result.stdout

    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_working_directory(self, temp_dir):
        """Test working directory with Local provider."""
        subdir = temp_dir / "workdir"
        subdir.mkdir()

        config = SandboxConfig(timeout=30, working_directory=str(subdir))

        async with Sandbox(provider="local", config=config) as sandbox:
            # Test working directory
            result = await sandbox.execute("pwd")
            assert result.return_code == 0
            assert str(subdir) in result.stdout.strip()

    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_error_handling(self, temp_dir):
        """Test error handling with Local provider."""
        config = SandboxConfig(timeout=30, working_directory=str(temp_dir))

        async with Sandbox(provider="local", config=config) as sandbox:
            # Test command that fails
            result = await sandbox.execute("exit 1")
            assert result.return_code == 1

            # Test non-existent command
            result = await sandbox.execute("nonexistent_command_12345")
            assert result.return_code != 0

    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_timeout_handling(self, temp_dir):
        """Test timeout handling with Local provider."""
        config = SandboxConfig(
            timeout=2,  # Very short timeout
            working_directory=str(temp_dir),
        )

        async with Sandbox(provider="local", config=config) as sandbox:
            # This should timeout
            with pytest.raises(SandboxError, match="Command execution failed"):
                await sandbox.execute("sleep 5")

    @pytest.mark.integration
    @pytest.mark.local
    @pytest.mark.snapshot
    async def test_local_snapshot_functionality(self, temp_dir):
        """Test snapshot functionality with Local provider."""
        config = SandboxConfig(timeout=30, working_directory=str(temp_dir))

        async with Sandbox(provider="local", config=config) as sandbox:
            # Create initial state
            await sandbox.upload_file("initial.txt", "Initial content")
            await sandbox.execute("mkdir initial_dir")

            # Create snapshot
            snapshot_id = await sandbox.create_snapshot()
            assert isinstance(snapshot_id, str)
            assert len(snapshot_id) > 0

            # Make changes after snapshot
            await sandbox.upload_file("after_snapshot.txt", "After snapshot content")
            await sandbox.execute("mkdir after_dir")

            # Verify changes exist
            files = await sandbox.list_files(".")
            file_names = [f.name for f in files]
            assert "after_snapshot.txt" in file_names
            assert "after_dir" in file_names

            # Restore snapshot
            await sandbox.restore_snapshot(snapshot_id)

            # Verify restoration
            files = await sandbox.list_files(".")
            file_names = [f.name for f in files]
            assert "initial.txt" in file_names
            assert "initial_dir" in file_names
            assert "after_snapshot.txt" not in file_names
            assert "after_dir" not in file_names

    @pytest.mark.integration
    @pytest.mark.local
    @pytest.mark.snapshot
    async def test_local_multiple_snapshots(self, temp_dir):
        """Test multiple snapshots with Local provider."""
        config = SandboxConfig(timeout=30, working_directory=str(temp_dir))

        async with Sandbox(provider="local", config=config) as sandbox:
            # State 1
            await sandbox.upload_file("state1.txt", "State 1")
            snapshot1 = await sandbox.create_snapshot()

            # State 2
            await sandbox.upload_file("state2.txt", "State 2")
            snapshot2 = await sandbox.create_snapshot()

            # State 3
            await sandbox.upload_file("state3.txt", "State 3")

            # Restore to state 1
            await sandbox.restore_snapshot(snapshot1)
            files = await sandbox.list_files(".")
            file_names = [f.name for f in files]
            assert "state1.txt" in file_names
            assert "state2.txt" not in file_names
            assert "state3.txt" not in file_names

            # Restore to state 2
            await sandbox.restore_snapshot(snapshot2)
            files = await sandbox.list_files(".")
            file_names = [f.name for f in files]
            assert "state1.txt" in file_names
            assert "state2.txt" in file_names
            assert "state3.txt" not in file_names

    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_concurrent_operations(self, temp_dir):
        """Test concurrent operations within a Local sandbox."""
        config = SandboxConfig(timeout=30, working_directory=str(temp_dir))

        async with Sandbox(provider="local", config=config) as sandbox:
            # Upload multiple files concurrently
            upload_tasks = []
            for i in range(10):
                content = f"File {i} content"
                task = sandbox.upload_file(f"file_{i}.txt", content)
                upload_tasks.append(task)

            await asyncio.gather(*upload_tasks)

            # Verify all files were uploaded
            files = await sandbox.list_files(".")
            file_names = [f.name for f in files]

            for i in range(10):
                assert f"file_{i}.txt" in file_names

    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_large_file_operations(self, temp_dir):
        """Test operations with large files."""
        config = SandboxConfig(
            timeout=60,  # Longer timeout for large files
            working_directory=str(temp_dir),
        )

        async with Sandbox(provider="local", config=config) as sandbox:
            # Create large content (1MB)
            large_content = "x" * (1024 * 1024)

            # Upload large file
            await sandbox.upload_file("large_file.txt", large_content)

            # Verify file size
            result = await sandbox.execute("wc -c large_file.txt")
            assert result.return_code == 0
            assert "1048576" in result.stdout  # 1MB in bytes

            # Download and verify
            downloaded = await sandbox.download_file("large_file.txt")
            assert len(downloaded) == 1024 * 1024
            assert downloaded.decode() == large_content

    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_package_installation(self, temp_dir):
        """Test package installation with Local provider."""
        config = SandboxConfig(
            timeout=120,  # Longer timeout for package installation
            working_directory=str(temp_dir),
        )

        async with Sandbox(provider="local", config=config) as sandbox:
            # Install a package (if pip is available)
            result = await sandbox.execute("python3 -m pip --version")
            if result.return_code == 0:
                # pip is available, test installation
                result = await sandbox.execute("python3 -m pip install --user requests")
                assert result.return_code == 0

                # Test the package
                result = await sandbox.execute(
                    "python3 -c 'import requests; print(requests.__version__)'"
                )
                assert result.return_code == 0
                assert len(result.stdout.strip()) > 0

    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_script_execution(self, temp_dir):
        """Test script execution with Local provider."""
        config = SandboxConfig(timeout=30, working_directory=str(temp_dir))

        async with Sandbox(provider="local", config=config) as sandbox:
            # Create a Python script
            script_content = """#!/usr/bin/env python3
import sys
import json

def main():
    data = {
        "message": "Hello from script!",
        "args": sys.argv[1:],
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}"
    }
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()
"""

            await sandbox.upload_file("test_script.py", script_content)

            # Make script executable
            result = await sandbox.execute("chmod +x test_script.py")
            assert result.return_code == 0

            # Run script
            result = await sandbox.execute("python3 test_script.py arg1 arg2")
            assert result.return_code == 0
            assert "Hello from script!" in result.stdout
            assert "arg1" in result.stdout
            assert "arg2" in result.stdout

    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_multiple_sessions(self, temp_dir):
        """Test creating multiple Local sessions."""
        config = SandboxConfig(timeout=30, working_directory=str(temp_dir))

        # Create multiple sandboxes
        sandbox1 = Sandbox(provider="local", config=config)
        sandbox2 = Sandbox(provider="local", config=config)

        async with sandbox1:
            async with sandbox2:
                # Both should work independently
                result1 = await sandbox1.execute("echo 'Sandbox 1'")
                result2 = await sandbox2.execute("echo 'Sandbox 2'")

                assert result1.return_code == 0
                assert result2.return_code == 0
                assert "Sandbox 1" in result1.stdout
                assert "Sandbox 2" in result2.stdout

                # They should have different IDs
                assert sandbox1.sandbox_id != sandbox2.sandbox_id

    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_file_permissions(self, temp_dir):
        """Test file permissions with Local provider."""
        config = SandboxConfig(timeout=30, working_directory=str(temp_dir))

        async with Sandbox(provider="local", config=config) as sandbox:
            # Create a file and set permissions
            await sandbox.upload_file("test_permissions.txt", "Test content")

            # Make file executable
            result = await sandbox.execute("chmod +x test_permissions.txt")
            assert result.return_code == 0

            # Check permissions
            result = await sandbox.execute("ls -l test_permissions.txt")
            assert result.return_code == 0
            assert "x" in result.stdout  # Should have execute permission

    @pytest.mark.integration
    @pytest.mark.local
    async def test_local_symlink_operations(self, temp_dir):
        """Test symbolic link operations with Local provider."""
        config = SandboxConfig(timeout=30, working_directory=str(temp_dir))

        async with Sandbox(provider="local", config=config) as sandbox:
            # Create a file
            await sandbox.upload_file("original.txt", "Original content")

            # Create symbolic link
            result = await sandbox.execute("ln -s original.txt link.txt")
            assert result.return_code == 0

            # Read through symlink
            result = await sandbox.execute("cat link.txt")
            assert result.return_code == 0
            assert "Original content" in result.stdout

            # List files to see symlink
            files = await sandbox.list_files(".")
            file_names = [f.name for f in files]
            assert "original.txt" in file_names
            assert "link.txt" in file_names
