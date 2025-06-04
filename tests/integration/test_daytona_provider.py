"""Integration tests for Daytona provider."""

import pytest

from grainchain import Sandbox, SandboxConfig
from grainchain.core.config import ProviderConfig
from grainchain.core.exceptions import ConfigurationError, ProviderError, SandboxError


class TestDaytonaProviderIntegration:
    """Integration tests for Daytona provider."""

    @pytest.mark.integration
    @pytest.mark.daytona
    @pytest.mark.skipif(
        not pytest.importorskip("daytona_sdk", reason="Daytona SDK not installed"),
        reason="Daytona SDK not available",
    )
    async def test_daytona_provider_real_connection(self, daytona_available):
        """Test real Daytona provider connection (requires API key)."""
        if not daytona_available:
            pytest.skip("Daytona API key not available")

        config = SandboxConfig(timeout=60)

        async with Sandbox(provider="daytona", config=config) as sandbox:
            assert sandbox.provider_name == "daytona"
            assert sandbox.sandbox_id is not None

            # Test basic command execution
            result = await sandbox.execute("echo 'Hello from Daytona!'")
            assert result.return_code == 0
            assert "Hello from Daytona!" in result.stdout

    @pytest.mark.integration
    @pytest.mark.daytona
    @pytest.mark.skipif(
        not pytest.importorskip("daytona_sdk", reason="Daytona SDK not installed"),
        reason="Daytona SDK not available",
    )
    async def test_daytona_development_environment(self, daytona_available):
        """Test Daytona development environment features."""
        if not daytona_available:
            pytest.skip("Daytona API key not available")

        config = SandboxConfig(timeout=60)

        async with Sandbox(provider="daytona", config=config) as sandbox:
            # Test common development tools
            tools_to_test = ["git", "curl", "wget", "vim"]

            for tool in tools_to_test:
                result = await sandbox.execute(f"which {tool}")
                assert result.return_code == 0, f"{tool} not available"

    @pytest.mark.integration
    @pytest.mark.daytona
    @pytest.mark.skipif(
        not pytest.importorskip("daytona_sdk", reason="Daytona SDK not installed"),
        reason="Daytona SDK not available",
    )
    async def test_daytona_python_execution(self, daytona_available):
        """Test Python code execution on Daytona."""
        if not daytona_available:
            pytest.skip("Daytona API key not available")

        config = SandboxConfig(timeout=60)

        async with Sandbox(provider="daytona", config=config) as sandbox:
            # Test Python execution
            python_code = "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}')"
            result = await sandbox.execute(f'python3 -c "{python_code}"')

            assert result.return_code == 0
            assert "Python" in result.stdout

    @pytest.mark.integration
    @pytest.mark.daytona
    @pytest.mark.skipif(
        not pytest.importorskip("daytona_sdk", reason="Daytona SDK not installed"),
        reason="Daytona SDK not available",
    )
    async def test_daytona_file_operations(self, daytona_available):
        """Test file operations with Daytona provider."""
        if not daytona_available:
            pytest.skip("Daytona API key not available")

        config = SandboxConfig(timeout=60)

        async with Sandbox(provider="daytona", config=config) as sandbox:
            # Upload a file
            test_content = "Hello, Daytona file system!"
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
    @pytest.mark.daytona
    @pytest.mark.skipif(
        not pytest.importorskip("daytona_sdk", reason="Daytona SDK not installed"),
        reason="Daytona SDK not available",
    )
    async def test_daytona_git_operations(self, daytona_available):
        """Test Git operations in Daytona workspace."""
        if not daytona_available:
            pytest.skip("Daytona API key not available")

        config = SandboxConfig(timeout=120)  # Git operations might take longer

        async with Sandbox(provider="daytona", config=config) as sandbox:
            # Initialize a git repository
            result = await sandbox.execute("git init /tmp/test_repo")
            assert result.return_code == 0

            # Configure git
            await sandbox.execute(
                "cd /tmp/test_repo && git config user.email 'test@example.com'"
            )
            await sandbox.execute(
                "cd /tmp/test_repo && git config user.name 'Test User'"
            )

            # Create and commit a file
            await sandbox.upload_file("/tmp/test_repo/README.md", "# Test Repository")
            result = await sandbox.execute("cd /tmp/test_repo && git add README.md")
            assert result.return_code == 0

            result = await sandbox.execute(
                "cd /tmp/test_repo && git commit -m 'Initial commit'"
            )
            assert result.return_code == 0

    @pytest.mark.integration
    @pytest.mark.daytona
    @pytest.mark.skipif(
        not pytest.importorskip("daytona_sdk", reason="Daytona SDK not installed"),
        reason="Daytona SDK not available",
    )
    async def test_daytona_package_installation(self, daytona_available):
        """Test package installation on Daytona."""
        if not daytona_available:
            pytest.skip("Daytona API key not available")

        config = SandboxConfig(timeout=120)  # Longer timeout for package installation

        async with Sandbox(provider="daytona", config=config) as sandbox:
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
    @pytest.mark.daytona
    @pytest.mark.skipif(
        not pytest.importorskip("daytona_sdk", reason="Daytona SDK not installed"),
        reason="Daytona SDK not available",
    )
    async def test_daytona_error_handling(self, daytona_available):
        """Test error handling with Daytona provider."""
        if not daytona_available:
            pytest.skip("Daytona API key not available")

        config = SandboxConfig(timeout=30)

        async with Sandbox(provider="daytona", config=config) as sandbox:
            # Test command that fails
            result = await sandbox.execute("exit 1")
            assert result.return_code == 1

            # Test non-existent command
            result = await sandbox.execute("nonexistent_command_12345")
            assert result.return_code != 0

    @pytest.mark.integration
    @pytest.mark.daytona
    @pytest.mark.skipif(
        not pytest.importorskip("daytona_sdk", reason="Daytona SDK not installed"),
        reason="Daytona SDK not available",
    )
    async def test_daytona_timeout_handling(self, daytona_available):
        """Test timeout handling with Daytona provider."""
        if not daytona_available:
            pytest.skip("Daytona API key not available")

        config = SandboxConfig(timeout=5)  # Short timeout

        async with Sandbox(provider="daytona", config=config) as sandbox:
            # This should timeout
            with pytest.raises(SandboxError):  # Could be TimeoutError or SandboxError
                await sandbox.execute("sleep 10")

    @pytest.mark.integration
    @pytest.mark.daytona
    async def test_daytona_invalid_api_key(self):
        """Test Daytona provider with invalid API key."""
        # Create config with invalid API key
        provider_config = ProviderConfig("daytona", {"api_key": "invalid_key"})

        from grainchain.providers.daytona import DaytonaProvider

        provider = DaytonaProvider(provider_config)
        config = SandboxConfig(timeout=30)

        with pytest.raises(ProviderError):
            await provider.create_sandbox(config)

    @pytest.mark.integration
    @pytest.mark.daytona
    async def test_daytona_missing_api_key(self):
        """Test Daytona provider without API key."""
        provider_config = ProviderConfig("daytona", {})

        with pytest.raises(ConfigurationError, match="Daytona API key is required"):
            from grainchain.providers.daytona import DaytonaProvider

            DaytonaProvider(provider_config)

    @pytest.mark.integration
    @pytest.mark.daytona
    @pytest.mark.skipif(
        not pytest.importorskip("daytona_sdk", reason="Daytona SDK not installed"),
        reason="Daytona SDK not available",
    )
    async def test_daytona_workspace_template(self, daytona_available):
        """Test Daytona provider with workspace template."""
        if not daytona_available:
            pytest.skip("Daytona API key not available")

        # Test with a development template
        provider_config = ProviderConfig(
            "daytona",
            {
                "api_key": pytest.importorskip("os").getenv("DAYTONA_API_KEY"),
                "workspace_template": "python-dev",
            },
        )

        from grainchain.providers.daytona import DaytonaProvider

        provider = DaytonaProvider(provider_config)
        config = SandboxConfig(timeout=60)

        session = await provider.create_sandbox(config)
        try:
            # Test that Python development tools are available
            result = await session.execute("python3 --version")
            assert result.return_code == 0
            assert "Python" in result.stdout

            result = await session.execute("pip --version")
            assert result.return_code == 0
        finally:
            await session.close()

    @pytest.mark.integration
    @pytest.mark.daytona
    @pytest.mark.slow
    @pytest.mark.skipif(
        not pytest.importorskip("daytona_sdk", reason="Daytona SDK not installed"),
        reason="Daytona SDK not available",
    )
    async def test_daytona_multiple_workspaces(self, daytona_available):
        """Test creating multiple Daytona workspaces."""
        if not daytona_available:
            pytest.skip("Daytona API key not available")

        config = SandboxConfig(timeout=60)

        # Create multiple sandboxes concurrently
        sandbox1 = Sandbox(provider="daytona", config=config)
        sandbox2 = Sandbox(provider="daytona", config=config)

        async with sandbox1:
            async with sandbox2:
                # Both should work independently
                result1 = await sandbox1.execute("echo 'Workspace 1'")
                result2 = await sandbox2.execute("echo 'Workspace 2'")

                assert result1.return_code == 0
                assert result2.return_code == 0
                assert "Workspace 1" in result1.stdout
                assert "Workspace 2" in result2.stdout

                # They should have different IDs
                assert sandbox1.sandbox_id != sandbox2.sandbox_id

    @pytest.mark.integration
    @pytest.mark.daytona
    @pytest.mark.skipif(
        not pytest.importorskip("daytona_sdk", reason="Daytona SDK not installed"),
        reason="Daytona SDK not available",
    )
    async def test_daytona_environment_variables(self, daytona_available):
        """Test environment variables with Daytona provider."""
        if not daytona_available:
            pytest.skip("Daytona API key not available")

        config = SandboxConfig(
            timeout=60,
            environment_vars={"TEST_VAR": "test_value", "ANOTHER_VAR": "another_value"},
        )

        async with Sandbox(provider="daytona", config=config) as sandbox:
            # Test environment variables
            result = await sandbox.execute("echo $TEST_VAR")
            assert result.return_code == 0
            assert "test_value" in result.stdout

            result = await sandbox.execute("echo $ANOTHER_VAR")
            assert result.return_code == 0
            assert "another_value" in result.stdout

    @pytest.mark.integration
    @pytest.mark.daytona
    @pytest.mark.skipif(
        not pytest.importorskip("daytona_sdk", reason="Daytona SDK not installed"),
        reason="Daytona SDK not available",
    )
    async def test_daytona_working_directory(self, daytona_available):
        """Test working directory with Daytona provider."""
        if not daytona_available:
            pytest.skip("Daytona API key not available")

        config = SandboxConfig(timeout=60, working_directory="/workspace")

        async with Sandbox(provider="daytona", config=config) as sandbox:
            # Test working directory
            result = await sandbox.execute("pwd")
            assert result.return_code == 0
            assert "/workspace" in result.stdout.strip()

    @pytest.mark.integration
    @pytest.mark.daytona
    @pytest.mark.skipif(
        not pytest.importorskip("daytona_sdk", reason="Daytona SDK not installed"),
        reason="Daytona SDK not available",
    )
    async def test_daytona_development_workflow(self, daytona_available):
        """Test a complete development workflow on Daytona."""
        if not daytona_available:
            pytest.skip("Daytona API key not available")

        config = SandboxConfig(timeout=120)

        async with Sandbox(provider="daytona", config=config) as sandbox:
            # Create a simple Python project
            project_structure = {
                "main.py": """
def greet(name):
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("Daytona"))
""",
                "requirements.txt": "requests==2.31.0",
                "README.md": "# Test Project\n\nA simple test project for Daytona.",
            }

            # Upload project files
            for filename, content in project_structure.items():
                await sandbox.upload_file(f"/workspace/{filename}", content)

            # Install dependencies
            result = await sandbox.execute(
                "cd /workspace && pip install -r requirements.txt"
            )
            assert result.return_code == 0

            # Run the main script
            result = await sandbox.execute("cd /workspace && python main.py")
            assert result.return_code == 0
            assert "Hello, Daytona!" in result.stdout

            # Test that requirements were installed
            result = await sandbox.execute(
                "python -c 'import requests; print(\"Requests available\")'"
            )
            assert result.return_code == 0
            assert "Requests available" in result.stdout

    @pytest.mark.integration
    @pytest.mark.daytona
    @pytest.mark.skipif(
        not pytest.importorskip("daytona_sdk", reason="Daytona SDK not installed"),
        reason="Daytona SDK not available",
    )
    async def test_daytona_large_output(self, daytona_available):
        """Test handling of large command output."""
        if not daytona_available:
            pytest.skip("Daytona API key not available")

        config = SandboxConfig(timeout=60)

        async with Sandbox(provider="daytona", config=config) as sandbox:
            # Generate large output
            result = await sandbox.execute("python3 -c 'print(\"x\" * 10000)'")
            assert result.return_code == 0
            assert len(result.stdout) >= 10000

    @pytest.mark.integration
    @pytest.mark.daytona
    @pytest.mark.skipif(
        not pytest.importorskip("daytona_sdk", reason="Daytona SDK not installed"),
        reason="Daytona SDK not available",
    )
    async def test_daytona_binary_file_operations(self, daytona_available):
        """Test binary file operations with Daytona provider."""
        if not daytona_available:
            pytest.skip("Daytona API key not available")

        config = SandboxConfig(timeout=60)

        async with Sandbox(provider="daytona", config=config) as sandbox:
            # Create binary content
            binary_content = bytes(range(256))

            # Upload binary file
            await sandbox.upload_file(
                "/workspace/binary_test.bin", binary_content, mode="wb"
            )

            # Download and verify
            downloaded = await sandbox.download_file("/workspace/binary_test.bin")
            assert downloaded == binary_content

    @pytest.mark.integration
    @pytest.mark.daytona
    @pytest.mark.skipif(
        not pytest.importorskip("daytona_sdk", reason="Daytona SDK not installed"),
        reason="Daytona SDK not available",
    )
    async def test_daytona_persistent_workspace(self, daytona_available):
        """Test workspace persistence features."""
        if not daytona_available:
            pytest.skip("Daytona API key not available")

        config = SandboxConfig(timeout=60, keep_alive=True)

        async with Sandbox(provider="daytona", config=config) as sandbox:
            # Create a file that should persist
            await sandbox.upload_file(
                "/workspace/persistent_file.txt", "This should persist"
            )

            # Verify file exists
            result = await sandbox.execute("cat /workspace/persistent_file.txt")
            assert result.return_code == 0
            assert "This should persist" in result.stdout

            # Note: In a real scenario, we would test that the workspace
            # persists across sessions, but that's complex for automated tests
