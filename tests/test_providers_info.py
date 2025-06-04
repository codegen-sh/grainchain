"""Tests for provider information utilities."""

import os
from unittest.mock import Mock, patch

from grainchain.core.providers_info import ProviderDiscovery, ProviderInfo


class TestProviderDiscovery:
    """Test the ProviderDiscovery class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = ProviderDiscovery()

    def test_check_provider_dependencies_local(self):
        """Test that local provider has no dependencies."""
        result = self.discovery.check_provider_dependencies("local")
        assert result is True

    @patch("builtins.__import__")
    def test_check_provider_dependencies_missing(self, mock_import):
        """Test dependency check with missing package."""

        def import_side_effect(name, *args, **kwargs):
            if name == "e2b":
                raise ImportError("No module named 'e2b'")
            return __import__(name, *args, **kwargs)

        mock_import.side_effect = import_side_effect

        result = self.discovery.check_provider_dependencies("e2b")
        assert result is False

    @patch("builtins.__import__")
    def test_check_provider_dependencies_available(self, mock_import):
        """Test dependency check with available package."""

        def import_side_effect(name, *args, **kwargs):
            if name == "e2b":
                return Mock()
            return __import__(name, *args, **kwargs)

        mock_import.side_effect = import_side_effect

        result = self.discovery.check_provider_dependencies("e2b")
        assert result is True

    def test_check_provider_config_local(self):
        """Test that local provider needs no configuration."""
        configured, missing = self.discovery.check_provider_config("local")
        assert configured is True
        assert missing == []

    @patch.dict(os.environ, {}, clear=True)
    def test_check_provider_config_missing_env_vars(self):
        """Test configuration check with missing environment variables."""
        configured, missing = self.discovery.check_provider_config("e2b")
        assert configured is False
        assert "E2B_API_KEY" in missing

    @patch.dict(os.environ, {"E2B_API_KEY": "test-key"})
    def test_check_provider_config_with_env_vars(self):
        """Test configuration check with environment variables set."""
        configured, missing = self.discovery.check_provider_config("e2b")
        assert configured is True
        assert missing == []

    def test_get_provider_info_unknown(self):
        """Test getting info for unknown provider."""
        info = self.discovery.get_provider_info("unknown")

        assert info.name == "unknown"
        assert info.available is False
        assert info.dependencies_installed is False
        assert info.configured is False
        assert "Unknown provider" in info.error_message

    @patch.dict(os.environ, {}, clear=True)
    def test_get_provider_info_missing_deps(self):
        """Test getting info for provider with missing dependencies."""
        # Create a new discovery instance and mock its dependency check method
        discovery = ProviderDiscovery()

        # Mock the dependency check to return False
        with patch.object(discovery, "check_provider_dependencies", return_value=False):
            info = discovery.get_provider_info("e2b")

        assert info.name == "e2b"
        assert info.available is False
        assert info.dependencies_installed is False
        assert info.configured is False
        assert "E2B_API_KEY" in info.missing_config

    @patch.dict(os.environ, {"E2B_API_KEY": "test-key"})
    def test_get_provider_info_available(self):
        """Test getting info for fully available provider."""
        # Create a new discovery instance and mock its dependency check method
        discovery = ProviderDiscovery()

        # Mock the dependency check to return True
        with patch.object(discovery, "check_provider_dependencies", return_value=True):
            info = discovery.get_provider_info("e2b")

        assert info.name == "e2b"
        assert info.available is True
        assert info.dependencies_installed is True
        assert info.configured is True
        assert info.missing_config == []

    def test_get_all_providers_info(self):
        """Test getting info for all providers."""
        all_info = self.discovery.get_all_providers_info()

        # Should have all known providers
        expected_providers = {"local", "e2b", "modal", "daytona", "morph"}
        assert set(all_info.keys()) == expected_providers

        # All should be ProviderInfo objects
        for info in all_info.values():
            assert isinstance(info, ProviderInfo)

    @patch.dict(os.environ, {}, clear=True)
    @patch("builtins.__import__")
    def test_get_available_providers_none(self, mock_import):
        """Test getting available providers when none are configured."""

        # Mock all imports to fail except local
        def import_side_effect(name, *args, **kwargs):
            if name in ["e2b", "modal", "daytona", "morphcloud"]:
                raise ImportError(f"No module named '{name}'")
            return __import__(name, *args, **kwargs)

        mock_import.side_effect = import_side_effect

        available = self.discovery.get_available_providers()
        # Only local should be available (no deps, no config needed)
        assert available == ["local"]

    @patch("grainchain.core.providers_info.get_config_manager")
    def test_get_default_provider_info(self, mock_get_config):
        """Test getting default provider info."""
        mock_config = Mock()
        mock_config.default_provider = "local"
        mock_get_config.return_value = mock_config

        # Create new discovery instance to use mocked config
        discovery = ProviderDiscovery()
        info = discovery.get_default_provider_info()

        assert info.name == "local"


class TestProviderInfo:
    """Test the ProviderInfo dataclass."""

    def test_provider_info_creation(self):
        """Test creating a ProviderInfo object."""
        info = ProviderInfo(
            name="test",
            available=True,
            dependencies_installed=True,
            configured=True,
            missing_config=[],
            install_command="pip install test",
            config_instructions=["Set TEST_KEY"],
            error_message=None,
        )

        assert info.name == "test"
        assert info.available is True
        assert info.dependencies_installed is True
        assert info.configured is True
        assert info.missing_config == []
        assert info.install_command == "pip install test"
        assert info.config_instructions == ["Set TEST_KEY"]
        assert info.error_message is None


# Integration tests for the public functions
class TestPublicFunctions:
    """Test the public API functions."""

    @patch("grainchain.core.providers_info.ProviderDiscovery")
    def test_get_providers_info(self, mock_discovery_class):
        """Test get_providers_info function."""
        from grainchain.core.providers_info import get_providers_info

        mock_discovery = Mock()
        mock_discovery.get_all_providers_info.return_value = {"test": "info"}
        mock_discovery_class.return_value = mock_discovery

        result = get_providers_info()

        assert result == {"test": "info"}
        mock_discovery.get_all_providers_info.assert_called_once()

    @patch("grainchain.core.providers_info.ProviderDiscovery")
    def test_get_available_providers(self, mock_discovery_class):
        """Test get_available_providers function."""
        from grainchain.core.providers_info import get_available_providers

        mock_discovery = Mock()
        mock_discovery.get_available_providers.return_value = ["local", "e2b"]
        mock_discovery_class.return_value = mock_discovery

        result = get_available_providers()

        assert result == ["local", "e2b"]
        mock_discovery.get_available_providers.assert_called_once()

    @patch("grainchain.core.providers_info.ProviderDiscovery")
    def test_check_provider(self, mock_discovery_class):
        """Test check_provider function."""
        from grainchain.core.providers_info import check_provider

        mock_discovery = Mock()
        mock_info = ProviderInfo(
            name="test",
            available=True,
            dependencies_installed=True,
            configured=True,
            missing_config=[],
        )
        mock_discovery.get_provider_info.return_value = mock_info
        mock_discovery_class.return_value = mock_discovery

        result = check_provider("test")

        assert result == mock_info
        mock_discovery.get_provider_info.assert_called_once_with("test")
