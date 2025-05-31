"""Unit tests for provider implementations."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from grainchain.core.config import ProviderConfig
from grainchain.core.exceptions import (
    ConfigurationError,
    ProviderError,
)
from grainchain.core.interfaces import SandboxConfig, SandboxStatus
from grainchain.providers.base import BaseSandboxProvider, BaseSandboxSession


class TestBaseSandboxProvider:
    """Test cases for the base sandbox provider."""

    @pytest.mark.unit
    def test_provider_init(self, provider_config):
        """Test provider initialization."""

        class TestProvider(BaseSandboxProvider):
            @property
            def name(self) -> str:
                return "test"

            async def _create_session(self, config: SandboxConfig):
                return MagicMock()

        provider = TestProvider(provider_config)
        assert provider.config == provider_config
        assert provider.name == "test"
        assert not provider._closed

    @pytest.mark.unit
    async def test_create_sandbox_success(self, mock_provider, test_config):
        """Test successful sandbox creation."""
        session = await mock_provider.create_sandbox(test_config)

        assert session is not None
        assert session.sandbox_id in mock_provider._sessions
        assert len(mock_provider.created_sessions) == 1

    @pytest.mark.unit
    async def test_create_sandbox_after_close(self, mock_provider, test_config):
        """Test sandbox creation after provider is closed."""
        await mock_provider.cleanup()

        with pytest.raises(ProviderError, match="Provider has been closed"):
            await mock_provider.create_sandbox(test_config)

    @pytest.mark.unit
    async def test_list_sandboxes(self, mock_provider, test_config):
        """Test listing sandboxes."""
        # Create some sessions
        session1 = await mock_provider.create_sandbox(test_config)
        session2 = await mock_provider.create_sandbox(test_config)

        # List sandboxes
        sandboxes = await mock_provider.list_sandboxes()
        assert len(sandboxes) == 2
        assert session1.sandbox_id in sandboxes
        assert session2.sandbox_id in sandboxes

    @pytest.mark.unit
    async def test_get_sandbox_status(self, mock_provider, test_config):
        """Test getting sandbox status."""
        # Unknown sandbox
        status = await mock_provider.get_sandbox_status("unknown_id")
        assert status == SandboxStatus.UNKNOWN

        # Known sandbox
        session = await mock_provider.create_sandbox(test_config)
        status = await mock_provider.get_sandbox_status(session.sandbox_id)
        assert status == SandboxStatus.RUNNING

    @pytest.mark.unit
    async def test_provider_cleanup(self, mock_provider, test_config):
        """Test provider cleanup."""
        # Create some sessions
        await mock_provider.create_sandbox(test_config)
        await mock_provider.create_sandbox(test_config)

        # Cleanup
        await mock_provider.cleanup()

        # Verify cleanup was called
        assert mock_provider.cleanup_called

    @pytest.mark.unit
    def test_get_config_value(self, mock_provider):
        """Test getting configuration values."""
        value = mock_provider.get_config_value("api_key")
        assert value == "test_key"

        default_value = mock_provider.get_config_value("nonexistent", "default")
        assert default_value == "default"

    @pytest.mark.unit
    def test_require_config_value(self, mock_provider):
        """Test requiring configuration values."""
        value = mock_provider.require_config_value("api_key")
        assert value == "test_key"

        with pytest.raises(ConfigurationError, match="Required configuration"):
            mock_provider.require_config_value("nonexistent")

    @pytest.mark.unit
    async def test_session_removal_on_close(self, mock_provider, test_config):
        """Test that sessions are removed from provider when closed."""
        session = await mock_provider.create_sandbox(test_config)
        sandbox_id = session.sandbox_id

        assert sandbox_id in mock_provider._sessions

        await session.close()

        assert sandbox_id not in mock_provider._sessions


class TestBaseSandboxSession:
    """Test cases for the base sandbox session."""

    @pytest.mark.unit
    def test_session_init(self, mock_provider, test_config):
        """Test session initialization."""
        session = BaseSandboxSession("test_id", mock_provider, test_config)

        assert session.sandbox_id == "test_id"
        assert session.config == test_config
        assert session.status == SandboxStatus.CREATING
        assert not session._closed

    @pytest.mark.unit
    async def test_session_close(self, mock_session):
        """Test session closing."""
        sandbox_id = mock_session.sandbox_id
        provider = mock_session._provider

        await mock_session.close()

        assert mock_session._closed
        assert mock_session.status == SandboxStatus.STOPPED
        assert sandbox_id not in provider._sessions

    @pytest.mark.unit
    async def test_session_double_close(self, mock_session):
        """Test that double closing doesn't cause issues."""
        await mock_session.close()
        await mock_session.close()  # Should not raise

        assert mock_session._closed

    @pytest.mark.unit
    async def test_ensure_not_closed(self, mock_session):
        """Test operations on closed session."""
        await mock_session.close()

        with pytest.raises(ProviderError, match="is closed"):
            mock_session._ensure_not_closed()

    @pytest.mark.unit
    async def test_default_snapshot_not_implemented(self, mock_session):
        """Test that default snapshot methods raise NotImplementedError."""
        # Override the mock implementation to test base class
        session = BaseSandboxSession(
            "test", mock_session._provider, mock_session._config
        )

        with pytest.raises(NotImplementedError, match="Snapshots not supported"):
            await session.create_snapshot()

        with pytest.raises(NotImplementedError, match="Snapshots not supported"):
            await session.restore_snapshot("test_id")


class TestE2BProvider:
    """Test cases for E2B provider."""

    @pytest.mark.unit
    @patch("grainchain.providers.e2b.e2b")
    def test_e2b_provider_init(self, mock_e2b, provider_config):
        """Test E2B provider initialization."""
        from grainchain.providers.e2b import E2BProvider

        provider = E2BProvider(provider_config)
        assert provider.name == "e2b"

    @pytest.mark.unit
    @patch("grainchain.providers.e2b.e2b")
    def test_e2b_provider_missing_api_key(self, mock_e2b):
        """Test E2B provider with missing API key."""
        from grainchain.providers.e2b import E2BProvider

        config = ProviderConfig("e2b", {})

        with pytest.raises(ConfigurationError, match="E2B API key is required"):
            E2BProvider(config)

    @pytest.mark.unit
    @patch("grainchain.providers.e2b.e2b")
    async def test_e2b_session_creation(self, mock_e2b, provider_config, test_config):
        """Test E2B session creation."""
        from grainchain.providers.e2b import E2BProvider

        # Mock E2B sandbox
        mock_sandbox = AsyncMock()
        mock_sandbox.id = "e2b_test_id"
        mock_e2b.Sandbox.create.return_value = mock_sandbox

        provider = E2BProvider(provider_config)
        session = await provider._create_session(test_config)

        assert session.sandbox_id == "e2b_test_id"
        mock_e2b.Sandbox.create.assert_called_once()


class TestModalProvider:
    """Test cases for Modal provider."""

    @pytest.mark.unit
    @patch("grainchain.providers.modal.modal")
    def test_modal_provider_init(self, mock_modal, provider_config):
        """Test Modal provider initialization."""
        from grainchain.providers.modal import ModalProvider

        provider = ModalProvider(provider_config)
        assert provider.name == "modal"

    @pytest.mark.unit
    @patch("grainchain.providers.modal.modal")
    def test_modal_provider_missing_credentials(self, mock_modal):
        """Test Modal provider with missing credentials."""
        from grainchain.providers.modal import ModalProvider

        config = ProviderConfig("modal", {})

        with pytest.raises(ConfigurationError, match="Modal credentials are required"):
            ModalProvider(config)


class TestDaytonaProvider:
    """Test cases for Daytona provider."""

    @pytest.mark.unit
    @patch("grainchain.providers.daytona.DaytonaClient")
    def test_daytona_provider_init(self, mock_client, provider_config):
        """Test Daytona provider initialization."""
        from grainchain.providers.daytona import DaytonaProvider

        provider = DaytonaProvider(provider_config)
        assert provider.name == "daytona"

    @pytest.mark.unit
    @patch("grainchain.providers.daytona.DaytonaClient")
    def test_daytona_provider_missing_api_key(self, mock_client):
        """Test Daytona provider with missing API key."""
        from grainchain.providers.daytona import DaytonaProvider

        config = ProviderConfig("daytona", {})

        with pytest.raises(ConfigurationError, match="Daytona API key is required"):
            DaytonaProvider(config)


class TestLocalProvider:
    """Test cases for Local provider."""

    @pytest.mark.unit
    def test_local_provider_init(self, provider_config):
        """Test Local provider initialization."""
        from grainchain.providers.local import LocalProvider

        provider = LocalProvider(provider_config)
        assert provider.name == "local"

    @pytest.mark.unit
    async def test_local_session_creation(self, provider_config, test_config):
        """Test Local session creation."""
        from grainchain.providers.local import LocalProvider

        provider = LocalProvider(provider_config)
        session = await provider._create_session(test_config)

        assert session.sandbox_id.startswith("local_")
        assert session.status == SandboxStatus.RUNNING

        await session.close()

    @pytest.mark.unit
    async def test_local_command_execution(self, provider_config, test_config):
        """Test Local provider command execution."""
        from grainchain.providers.local import LocalProvider

        provider = LocalProvider(provider_config)
        session = await provider._create_session(test_config)

        try:
            result = await session.execute("echo 'test'")
            assert result.return_code == 0
            assert "test" in result.stdout
        finally:
            await session.close()

    @pytest.mark.unit
    async def test_local_file_operations(self, provider_config, test_config, temp_dir):
        """Test Local provider file operations."""
        from grainchain.providers.local import LocalProvider

        # Override working directory to use temp dir
        test_config.working_directory = str(temp_dir)

        provider = LocalProvider(provider_config)
        session = await provider._create_session(test_config)

        try:
            # Upload file
            await session.upload_file("test.txt", "test content")

            # Download file
            content = await session.download_file("test.txt")
            assert content == b"test content"

            # List files
            files = await session.list_files(".")
            file_names = [f.name for f in files]
            assert "test.txt" in file_names
        finally:
            await session.close()


class TestProviderErrorHandling:
    """Test error handling across providers."""

    @pytest.mark.unit
    async def test_provider_error_propagation(self, failing_provider, test_config):
        """Test that provider errors are properly propagated."""
        with pytest.raises(ProviderError, match="Failed to create sandbox"):
            await failing_provider.create_sandbox(test_config)

    @pytest.mark.unit
    async def test_timeout_error_handling(self, timeout_provider, test_config):
        """Test timeout error handling."""
        with pytest.raises(ProviderError):
            # Use a very short timeout to trigger the error
            await asyncio.wait_for(
                timeout_provider.create_sandbox(test_config), timeout=0.1
            )

    @pytest.mark.unit
    @patch("grainchain.providers.e2b.e2b")
    async def test_authentication_error(self, mock_e2b, provider_config, test_config):
        """Test authentication error handling."""
        from grainchain.providers.e2b import E2BProvider

        # Mock authentication failure
        mock_e2b.Sandbox.create.side_effect = Exception("Authentication failed")

        provider = E2BProvider(provider_config)

        with pytest.raises(ProviderError, match="Failed to create sandbox"):
            await provider._create_session(test_config)

    @pytest.mark.unit
    async def test_network_error_handling(self, mock_provider, test_config):
        """Test network error handling."""

        class NetworkErrorProvider(BaseSandboxProvider):
            @property
            def name(self) -> str:
                return "network_error"

            async def _create_session(self, config: SandboxConfig):
                raise ConnectionError("Network unreachable")

        provider = NetworkErrorProvider(ProviderConfig("test", {}))

        with pytest.raises(ProviderError, match="Failed to create sandbox"):
            await provider.create_sandbox(test_config)

    @pytest.mark.unit
    async def test_resource_exhaustion_error(self, mock_provider, test_config):
        """Test resource exhaustion error handling."""

        class ResourceErrorProvider(BaseSandboxProvider):
            @property
            def name(self) -> str:
                return "resource_error"

            async def _create_session(self, config: SandboxConfig):
                raise Exception("Resource limit exceeded")

        provider = ResourceErrorProvider(ProviderConfig("test", {}))

        with pytest.raises(ProviderError, match="Failed to create sandbox"):
            await provider.create_sandbox(test_config)


class TestProviderConfiguration:
    """Test provider configuration handling."""

    @pytest.mark.unit
    def test_provider_config_validation(self):
        """Test provider configuration validation."""
        config = ProviderConfig("test", {"key": "value"})

        assert config.name == "test"
        assert config.get("key") == "value"
        assert config.get("missing", "default") == "default"

    @pytest.mark.unit
    def test_provider_config_modification(self):
        """Test provider configuration modification."""
        config = ProviderConfig("test", {})

        config.set("new_key", "new_value")
        assert config.get("new_key") == "new_value"

    @pytest.mark.unit
    def test_sandbox_config_defaults(self):
        """Test sandbox configuration defaults."""
        config = SandboxConfig()

        assert config.timeout == 300
        assert config.working_directory == "~"
        assert config.auto_cleanup is True
        assert config.keep_alive is False

    @pytest.mark.unit
    def test_sandbox_config_customization(self):
        """Test sandbox configuration customization."""
        config = SandboxConfig(
            timeout=600,
            memory_limit="4GB",
            cpu_limit=2.0,
            working_directory="/custom",
            environment_vars={"CUSTOM": "value"},
            auto_cleanup=False,
        )

        assert config.timeout == 600
        assert config.memory_limit == "4GB"
        assert config.cpu_limit == 2.0
        assert config.working_directory == "/custom"
        assert config.environment_vars["CUSTOM"] == "value"
        assert config.auto_cleanup is False
