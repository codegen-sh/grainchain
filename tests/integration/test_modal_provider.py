"""Integration tests for Modal provider."""

import pytest

from grainchain import Sandbox, SandboxConfig
from grainchain.core.config import ProviderConfig
from grainchain.core.exceptions import ConfigurationError, ProviderError, SandboxError


class TestModalProviderIntegration:
    """Integration tests for Modal provider."""

    @pytest.mark.integration
    @pytest.mark.modal
    @pytest.mark.skipif(
        not pytest.importorskip("modal", reason="Modal not installed"),
        reason="Modal package not available",
    )
    async def test_modal_provider_real_connection(self, modal_available):
        """Test real Modal provider connection (requires credentials)."""
        if not modal_available:
            pytest.skip("Modal credentials not available")

        config = SandboxConfig(timeout=60)

        async with Sandbox(provider="modal", config=config) as sandbox:
            assert sandbox.provider_name == "modal"
            assert sandbox.sandbox_id is not None

            # Test basic command execution
            result = await sandbox.execute("echo 'Hello from Modal!'")
            assert result.return_code == 0
            assert "Hello from Modal!" in result.stdout

    @pytest.mark.integration
    @pytest.mark.modal
    @pytest.mark.skipif(
        not pytest.importorskip("modal", reason="Modal not installed"),
        reason="Modal package not available",
    )
    async def test_modal_python_execution(self, modal_available):
        """Test Python code execution on Modal."""
        if not modal_available:
            pytest.skip("Modal credentials not available")

        config = SandboxConfig(timeout=60)

        async with Sandbox(provider="modal", config=config) as sandbox:
            # Test Python execution
            python_code = "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}')"
            result = await sandbox.execute(f'python -c "{python_code}"')

            assert result.return_code == 0
            assert "Python" in result.stdout

    @pytest.mark.integration
    @pytest.mark.modal
    @pytest.mark.skipif(
        not pytest.importorskip("modal", reason="Modal not installed"),
        reason="Modal package not available",
    )
    async def test_modal_file_operations(self, modal_available):
        """Test file operations with Modal provider."""
        if not modal_available:
            pytest.skip("Modal credentials not available")

        config = SandboxConfig(timeout=60)

        async with Sandbox(provider="modal", config=config) as sandbox:
            # Upload a file
            test_content = "Hello, Modal file system!"
            await sandbox.upload_file("/tmp/test_file.txt", test_content)

            # Verify file exists
            result = await sandbox.execute("cat /tmp/test_file.txt")
            assert result.return_code == 0
            assert test_content in result.stdout

            # Download the file
            downloaded = await sandbox.download_file("/tmp/test_file.txt")
            assert downloaded.decode() == test_content

            # List files
            files = await sandbox.list_files("/tmp")
            file_names = [f.name for f in files]
            assert "test_file.txt" in file_names

    @pytest.mark.integration
    @pytest.mark.modal
    @pytest.mark.skipif(
        not pytest.importorskip("modal", reason="Modal not installed"),
        reason="Modal package not available",
    )
    async def test_modal_package_installation(self, modal_available):
        """Test package installation on Modal."""
        if not modal_available:
            pytest.skip("Modal credentials not available")

        config = SandboxConfig(timeout=120)  # Longer timeout for package installation

        async with Sandbox(provider="modal", config=config) as sandbox:
            # Install a package
            result = await sandbox.execute("pip install requests")
            assert result.return_code == 0

            # Test the package
            result = await sandbox.execute(
                "python -c 'import requests; print(requests.__version__)'"
            )
            assert result.return_code == 0
            assert len(result.stdout.strip()) > 0

    @pytest.mark.integration
    @pytest.mark.modal
    @pytest.mark.skipif(
        not pytest.importorskip("modal", reason="Modal not installed"),
        reason="Modal package not available",
    )
    async def test_modal_error_handling(self, modal_available):
        """Test error handling with Modal provider."""
        if not modal_available:
            pytest.skip("Modal credentials not available")

        config = SandboxConfig(timeout=30)

        async with Sandbox(provider="modal", config=config) as sandbox:
            # Test command that fails
            result = await sandbox.execute("exit 1")
            assert result.return_code == 1

            # Test non-existent command
            result = await sandbox.execute("nonexistent_command_12345")
            assert result.return_code != 0

    @pytest.mark.integration
    @pytest.mark.modal
    @pytest.mark.skipif(
        not pytest.importorskip("modal", reason="Modal not installed"),
        reason="Modal package not available",
    )
    async def test_modal_timeout_handling(self, modal_available):
        """Test timeout handling with Modal provider."""
        if not modal_available:
            pytest.skip("Modal credentials not available")

        config = SandboxConfig(timeout=5)  # Short timeout

        async with Sandbox(provider="modal", config=config) as sandbox:
            # This should timeout
            with pytest.raises(SandboxError):  # Could be TimeoutError or SandboxError
                await sandbox.execute("sleep 10")

    @pytest.mark.integration
    @pytest.mark.modal
    async def test_modal_invalid_credentials(self):
        """Test Modal provider with invalid credentials."""
        # Create config with invalid credentials
        provider_config = ProviderConfig(
            "modal", {"token_id": "invalid_id", "token_secret": "invalid_secret"}
        )

        from grainchain.providers.modal import ModalProvider

        provider = ModalProvider(provider_config)
        config = SandboxConfig(timeout=30)

        with pytest.raises(ProviderError):
            await provider.create_sandbox(config)

    @pytest.mark.integration
    @pytest.mark.modal
    async def test_modal_missing_credentials(self):
        """Test Modal provider without credentials."""
        provider_config = ProviderConfig("modal", {})

        with pytest.raises(ConfigurationError, match="Modal credentials are required"):
            from grainchain.providers.modal import ModalProvider

            ModalProvider(provider_config)

    @pytest.mark.integration
    @pytest.mark.modal
    @pytest.mark.skipif(
        not pytest.importorskip("modal", reason="Modal not installed"),
        reason="Modal package not available",
    )
    async def test_modal_custom_image(self, modal_available):
        """Test Modal provider with custom image."""
        if not modal_available:
            pytest.skip("Modal credentials not available")

        config = SandboxConfig(
            timeout=60,
            image="python:3.11",  # Custom Python image
        )

        async with Sandbox(provider="modal", config=config) as sandbox:
            # Test that Python is available
            result = await sandbox.execute("python --version")
            assert result.return_code == 0
            assert "Python" in result.stdout

    @pytest.mark.integration
    @pytest.mark.modal
    @pytest.mark.slow
    @pytest.mark.skipif(
        not pytest.importorskip("modal", reason="Modal not installed"),
        reason="Modal package not available",
    )
    async def test_modal_multiple_sessions(self, modal_available):
        """Test creating multiple Modal sessions."""
        if not modal_available:
            pytest.skip("Modal credentials not available")

        config = SandboxConfig(timeout=60)

        # Create multiple sandboxes concurrently
        sandbox1 = Sandbox(provider="modal", config=config)
        sandbox2 = Sandbox(provider="modal", config=config)

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
    @pytest.mark.modal
    @pytest.mark.skipif(
        not pytest.importorskip("modal", reason="Modal not installed"),
        reason="Modal package not available",
    )
    async def test_modal_environment_variables(self, modal_available):
        """Test environment variables with Modal provider."""
        if not modal_available:
            pytest.skip("Modal credentials not available")

        config = SandboxConfig(
            timeout=60,
            environment_vars={"TEST_VAR": "test_value", "ANOTHER_VAR": "another_value"},
        )

        async with Sandbox(provider="modal", config=config) as sandbox:
            # Test environment variables
            result = await sandbox.execute("echo $TEST_VAR")
            assert result.return_code == 0
            assert "test_value" in result.stdout

            result = await sandbox.execute("echo $ANOTHER_VAR")
            assert result.return_code == 0
            assert "another_value" in result.stdout

    @pytest.mark.integration
    @pytest.mark.modal
    @pytest.mark.skipif(
        not pytest.importorskip("modal", reason="Modal not installed"),
        reason="Modal package not available",
    )
    async def test_modal_working_directory(self, modal_available):
        """Test working directory with Modal provider."""
        if not modal_available:
            pytest.skip("Modal credentials not available")

        config = SandboxConfig(timeout=60, working_directory="/tmp")

        async with Sandbox(provider="modal", config=config) as sandbox:
            # Test working directory
            result = await sandbox.execute("pwd")
            assert result.return_code == 0
            assert "/tmp" in result.stdout.strip()

    @pytest.mark.integration
    @pytest.mark.modal
    @pytest.mark.skipif(
        not pytest.importorskip("modal", reason="Modal not installed"),
        reason="Modal package not available",
    )
    async def test_modal_resource_limits(self, modal_available):
        """Test resource limits with Modal provider."""
        if not modal_available:
            pytest.skip("Modal credentials not available")

        config = SandboxConfig(timeout=60, memory_limit="1GB", cpu_limit=1.0)

        async with Sandbox(provider="modal", config=config) as sandbox:
            # Test that sandbox respects resource limits
            result = await sandbox.execute("echo 'Resource limits test'")
            assert result.return_code == 0

    @pytest.mark.integration
    @pytest.mark.modal
    @pytest.mark.skipif(
        not pytest.importorskip("modal", reason="Modal not installed"),
        reason="Modal package not available",
    )
    async def test_modal_large_output(self, modal_available):
        """Test handling of large command output."""
        if not modal_available:
            pytest.skip("Modal credentials not available")

        config = SandboxConfig(timeout=60)

        async with Sandbox(provider="modal", config=config) as sandbox:
            # Generate large output
            result = await sandbox.execute("python -c 'print(\"x\" * 10000)'")
            assert result.return_code == 0
            assert len(result.stdout) >= 10000

    @pytest.mark.integration
    @pytest.mark.modal
    @pytest.mark.skipif(
        not pytest.importorskip("modal", reason="Modal not installed"),
        reason="Modal package not available",
    )
    async def test_modal_binary_file_operations(self, modal_available):
        """Test binary file operations with Modal provider."""
        if not modal_available:
            pytest.skip("Modal credentials not available")

        config = SandboxConfig(timeout=60)

        async with Sandbox(provider="modal", config=config) as sandbox:
            # Create binary content
            binary_content = bytes(range(256))

            # Upload binary file
            await sandbox.upload_file("/tmp/binary_test.bin", binary_content, mode="wb")

            # Download and verify
            downloaded = await sandbox.download_file("/tmp/binary_test.bin")
            assert downloaded == binary_content

    @pytest.mark.integration
    @pytest.mark.modal
    @pytest.mark.skipif(
        not pytest.importorskip("modal", reason="Modal not installed"),
        reason="Modal package not available",
    )
    async def test_modal_concurrent_operations(self, modal_available):
        """Test concurrent operations within a Modal sandbox."""
        if not modal_available:
            pytest.skip("Modal credentials not available")

        config = SandboxConfig(timeout=60)

        async with Sandbox(provider="modal", config=config) as sandbox:
            # Upload multiple files concurrently
            import asyncio

            upload_tasks = []
            for i in range(5):
                content = f"File {i} content"
                task = sandbox.upload_file(f"/tmp/file_{i}.txt", content)
                upload_tasks.append(task)

            await asyncio.gather(*upload_tasks)

            # Verify all files were uploaded
            files = await sandbox.list_files("/tmp")
            file_names = [f.name for f in files]

            for i in range(5):
                assert f"file_{i}.txt" in file_names

    @pytest.mark.integration
    @pytest.mark.modal
    @pytest.mark.skipif(
        not pytest.importorskip("modal", reason="Modal not installed"),
        reason="Modal package not available",
    )
    async def test_modal_data_science_workflow(self, modal_available):
        """Test a typical data science workflow on Modal."""
        if not modal_available:
            pytest.skip("Modal credentials not available")

        config = SandboxConfig(timeout=120)

        async with Sandbox(provider="modal", config=config) as sandbox:
            # Install data science packages
            result = await sandbox.execute("pip install numpy pandas")
            assert result.return_code == 0

            # Create a simple data analysis script
            script_content = """
import numpy as np
import pandas as pd

# Create sample data
data = np.random.randn(100, 3)
df = pd.DataFrame(data, columns=['A', 'B', 'C'])

# Basic analysis
print(f"Shape: {df.shape}")
print(f"Mean: {df.mean().to_dict()}")
print("Analysis complete!")
"""

            await sandbox.upload_file("/tmp/analysis.py", script_content)

            # Run the analysis
            result = await sandbox.execute("python /tmp/analysis.py")
            assert result.return_code == 0
            assert "Shape: (100, 3)" in result.stdout
            assert "Analysis complete!" in result.stdout
