"""Integration tests for E2B provider."""

import pytest

from grainchain import Sandbox, SandboxConfig
from grainchain.core.config import ProviderConfig
from grainchain.core.exceptions import ConfigurationError, ProviderError, SandboxError


class TestE2BProviderIntegration:
    """Integration tests for E2B provider."""

    @pytest.mark.integration
    @pytest.mark.e2b
    @pytest.mark.skipif(
        not pytest.importorskip("e2b", reason="E2B not installed"),
        reason="E2B package not available",
    )
    async def test_e2b_provider_real_connection(self, e2b_available):
        """Test real E2B provider connection (requires API key)."""
        if not e2b_available:
            pytest.skip("E2B API key not available")

        config = SandboxConfig(timeout=60)

        async with Sandbox(provider="e2b", config=config) as sandbox:
            assert sandbox.provider_name == "e2b"
            assert sandbox.sandbox_id is not None

            # Test basic command execution
            result = await sandbox.execute("echo 'Hello from E2B!'")
            assert result.return_code == 0
            assert "Hello from E2B!" in result.stdout

    @pytest.mark.integration
    @pytest.mark.e2b
    @pytest.mark.skipif(
        not pytest.importorskip("e2b", reason="E2B not installed"),
        reason="E2B package not available",
    )
    async def test_e2b_python_execution(self, e2b_available):
        """Test Python code execution on E2B."""
        if not e2b_available:
            pytest.skip("E2B API key not available")

        config = SandboxConfig(timeout=60)

        async with Sandbox(provider="e2b", config=config) as sandbox:
            # Test Python execution
            python_code = "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}')"
            result = await sandbox.execute(f'python3 -c "{python_code}"')

            assert result.return_code == 0
            assert "Python" in result.stdout

    @pytest.mark.integration
    @pytest.mark.e2b
    @pytest.mark.skipif(
        not pytest.importorskip("e2b", reason="E2B not installed"),
        reason="E2B package not available",
    )
    async def test_e2b_file_operations(self, e2b_available):
        """Test file operations with E2B provider."""
        if not e2b_available:
            pytest.skip("E2B API key not available")

        config = SandboxConfig(timeout=60)

        async with Sandbox(provider="e2b", config=config) as sandbox:
            # Upload a file
            test_content = "Hello, E2B file system!"
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
    @pytest.mark.e2b
    @pytest.mark.skipif(
        not pytest.importorskip("e2b", reason="E2B not installed"),
        reason="E2B package not available",
    )
    async def test_e2b_package_installation(self, e2b_available):
        """Test package installation on E2B."""
        if not e2b_available:
            pytest.skip("E2B API key not available")

        config = SandboxConfig(timeout=120)  # Longer timeout for package installation

        async with Sandbox(provider="e2b", config=config) as sandbox:
            # Install a package
            result = await sandbox.execute("pip install requests")
            assert result.return_code == 0

            # Test the package
            result = await sandbox.execute(
                "python3 -c 'import requests; print(requests.__version__)'"
            )
            assert result.return_code == 0
            assert len(result.stdout.strip()) > 0

    @pytest.mark.integration
    @pytest.mark.e2b
    @pytest.mark.skipif(
        not pytest.importorskip("e2b", reason="E2B not installed"),
        reason="E2B package not available",
    )
    async def test_e2b_error_handling(self, e2b_available):
        """Test error handling with E2B provider."""
        if not e2b_available:
            pytest.skip("E2B API key not available")

        config = SandboxConfig(timeout=30)

        async with Sandbox(provider="e2b", config=config) as sandbox:
            # Test command that fails
            result = await sandbox.execute("exit 1")
            assert result.return_code == 1

            # Test non-existent command
            result = await sandbox.execute("nonexistent_command_12345")
            assert result.return_code != 0

    @pytest.mark.integration
    @pytest.mark.e2b
    @pytest.mark.skipif(
        not pytest.importorskip("e2b", reason="E2B not installed"),
        reason="E2B package not available",
    )
    async def test_e2b_timeout_handling(self, e2b_available):
        """Test timeout handling with E2B provider."""
        if not e2b_available:
            pytest.skip("E2B API key not available")

        config = SandboxConfig(timeout=5)  # Short timeout

        async with Sandbox(provider="e2b", config=config) as sandbox:
            # This should timeout
            with pytest.raises(SandboxError):  # Could be TimeoutError or SandboxError
                await sandbox.execute("sleep 10")

    @pytest.mark.integration
    @pytest.mark.e2b
    async def test_e2b_invalid_api_key(self):
        """Test E2B provider with invalid API key."""
        # Create config with invalid API key
        provider_config = ProviderConfig("e2b", {"api_key": "invalid_key"})

        from grainchain.providers.e2b import E2BProvider

        provider = E2BProvider(provider_config)
        config = SandboxConfig(timeout=30)

        with pytest.raises(ProviderError):
            await provider.create_sandbox(config)

    @pytest.mark.integration
    @pytest.mark.e2b
    async def test_e2b_missing_api_key(self):
        """Test E2B provider without API key."""
        provider_config = ProviderConfig("e2b", {})

        with pytest.raises(ConfigurationError, match="E2B API key is required"):
            from grainchain.providers.e2b import E2BProvider

            E2BProvider(provider_config)

    @pytest.mark.integration
    @pytest.mark.e2b
    @pytest.mark.skipif(
        not pytest.importorskip("e2b", reason="E2B not installed"),
        reason="E2B package not available",
    )
    async def test_e2b_custom_template(self, e2b_available):
        """Test E2B provider with custom template."""
        if not e2b_available:
            pytest.skip("E2B API key not available")

        # Test with Python template (should be available)
        provider_config = ProviderConfig(
            "e2b",
            {
                "api_key": pytest.importorskip("os").getenv("E2B_API_KEY"),
                "template": "python3",
            },
        )

        from grainchain.providers.e2b import E2BProvider

        provider = E2BProvider(provider_config)
        config = SandboxConfig(timeout=60)

        session = await provider.create_sandbox(config)
        try:
            # Test that Python is available
            result = await session.execute("python3 --version")
            assert result.return_code == 0
            assert "Python" in result.stdout
        finally:
            await session.close()

    @pytest.mark.integration
    @pytest.mark.e2b
    @pytest.mark.slow
    @pytest.mark.skipif(
        not pytest.importorskip("e2b", reason="E2B not installed"),
        reason="E2B package not available",
    )
    async def test_e2b_multiple_sessions(self, e2b_available):
        """Test creating multiple E2B sessions."""
        if not e2b_available:
            pytest.skip("E2B API key not available")

        config = SandboxConfig(timeout=60)

        # Create multiple sandboxes concurrently
        sandbox1 = Sandbox(provider="e2b", config=config)
        sandbox2 = Sandbox(provider="e2b", config=config)

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
    @pytest.mark.e2b
    @pytest.mark.skipif(
        not pytest.importorskip("e2b", reason="E2B not installed"),
        reason="E2B package not available",
    )
    async def test_e2b_environment_variables(self, e2b_available):
        """Test environment variables with E2B provider."""
        if not e2b_available:
            pytest.skip("E2B API key not available")

        config = SandboxConfig(
            timeout=60,
            environment_vars={"TEST_VAR": "test_value", "ANOTHER_VAR": "another_value"},
        )

        async with Sandbox(provider="e2b", config=config) as sandbox:
            # Test environment variables
            result = await sandbox.execute("echo $TEST_VAR")
            assert result.return_code == 0
            assert "test_value" in result.stdout

            result = await sandbox.execute("echo $ANOTHER_VAR")
            assert result.return_code == 0
            assert "another_value" in result.stdout

    @pytest.mark.integration
    @pytest.mark.e2b
    @pytest.mark.skipif(
        not pytest.importorskip("e2b", reason="E2B not installed"),
        reason="E2B package not available",
    )
    async def test_e2b_working_directory(self, e2b_available):
        """Test working directory with E2B provider."""
        if not e2b_available:
            pytest.skip("E2B API key not available")

        config = SandboxConfig(timeout=60, working_directory="/tmp")

        async with Sandbox(provider="e2b", config=config) as sandbox:
            # Test working directory
            result = await sandbox.execute("pwd")
            assert result.return_code == 0
            assert "/tmp" in result.stdout.strip()

    @pytest.mark.integration
    @pytest.mark.e2b
    @pytest.mark.skipif(
        not pytest.importorskip("e2b", reason="E2B not installed"),
        reason="E2B package not available",
    )
    async def test_e2b_large_output(self, e2b_available):
        """Test handling of large command output."""
        if not e2b_available:
            pytest.skip("E2B API key not available")

        config = SandboxConfig(timeout=60)

        async with Sandbox(provider="e2b", config=config) as sandbox:
            # Generate large output
            result = await sandbox.execute("python3 -c 'print(\"x\" * 10000)'")
            assert result.return_code == 0
            assert len(result.stdout) >= 10000

    @pytest.mark.integration
    @pytest.mark.e2b
    @pytest.mark.skipif(
        not pytest.importorskip("e2b", reason="E2B not installed"),
        reason="E2B package not available",
    )
    async def test_e2b_binary_file_operations(self, e2b_available):
        """Test binary file operations with E2B provider."""
        if not e2b_available:
            pytest.skip("E2B API key not available")

        config = SandboxConfig(timeout=60)

        async with Sandbox(provider="e2b", config=config) as sandbox:
            # Create binary content
            binary_content = bytes(range(256))

            # Upload binary file
            await sandbox.upload_file("/tmp/binary_test.bin", binary_content, mode="wb")

            # Download and verify
            downloaded = await sandbox.download_file("/tmp/binary_test.bin")
            assert downloaded == binary_content
