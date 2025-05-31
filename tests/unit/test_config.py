"""Unit tests for configuration management."""

import os
import tempfile
from unittest.mock import patch

import pytest
import yaml

from grainchain.core.config import (
    ConfigManager,
    ProviderConfig,
    SandboxConfig,
    get_config_manager,
    set_config_manager,
)
from grainchain.core.exceptions import ConfigurationError


class TestProviderConfig:
    """Test cases for ProviderConfig."""

    @pytest.mark.unit
    def test_provider_config_init(self):
        """Test ProviderConfig initialization."""
        config = ProviderConfig("test_provider")

        assert config.name == "test_provider"
        assert config.config == {}

    @pytest.mark.unit
    def test_provider_config_with_data(self):
        """Test ProviderConfig with initial data."""
        data = {"api_key": "test_key", "timeout": 30}
        config = ProviderConfig("test_provider", data)

        assert config.name == "test_provider"
        assert config.config == data

    @pytest.mark.unit
    def test_provider_config_get(self):
        """Test getting configuration values."""
        config = ProviderConfig("test", {"key1": "value1", "key2": "value2"})

        assert config.get("key1") == "value1"
        assert config.get("key2") == "value2"
        assert config.get("missing") is None
        assert config.get("missing", "default") == "default"

    @pytest.mark.unit
    def test_provider_config_set(self):
        """Test setting configuration values."""
        config = ProviderConfig("test")

        config.set("new_key", "new_value")
        assert config.get("new_key") == "new_value"

        config.set("new_key", "updated_value")
        assert config.get("new_key") == "updated_value"


class TestSandboxConfig:
    """Test cases for SandboxConfig."""

    @pytest.mark.unit
    def test_sandbox_config_defaults(self):
        """Test SandboxConfig default values."""
        config = SandboxConfig()

        assert config.timeout == 300
        assert config.memory_limit is None
        assert config.cpu_limit is None
        assert config.image is None
        assert config.working_directory == "~"
        assert config.environment_vars == {}
        assert config.auto_cleanup is True
        assert config.keep_alive is False
        assert config.provider_config == {}

    @pytest.mark.unit
    def test_sandbox_config_custom_values(self):
        """Test SandboxConfig with custom values."""
        env_vars = {"TEST_VAR": "test_value"}
        provider_config = {"custom_setting": "custom_value"}

        config = SandboxConfig(
            timeout=600,
            memory_limit="2GB",
            cpu_limit=2.0,
            image="custom:latest",
            working_directory="/workspace",
            environment_vars=env_vars,
            auto_cleanup=False,
            keep_alive=True,
            provider_config=provider_config,
        )

        assert config.timeout == 600
        assert config.memory_limit == "2GB"
        assert config.cpu_limit == 2.0
        assert config.image == "custom:latest"
        assert config.working_directory == "/workspace"
        assert config.environment_vars == env_vars
        assert config.auto_cleanup is False
        assert config.keep_alive is True
        assert config.provider_config == provider_config

    @pytest.mark.unit
    def test_sandbox_config_mutable_defaults(self):
        """Test that mutable defaults are properly handled."""
        config1 = SandboxConfig()
        config2 = SandboxConfig()

        # Modify one config's environment vars
        config1.environment_vars["TEST"] = "value"

        # Other config should not be affected
        assert "TEST" not in config2.environment_vars


class TestConfigManager:
    """Test cases for ConfigManager."""

    @pytest.mark.unit
    def test_config_manager_init_empty(self):
        """Test ConfigManager initialization without config file."""
        with patch.object(ConfigManager, "_load_config_file"):
            with patch.object(ConfigManager, "_load_env_config"):
                manager = ConfigManager()
                assert manager._config == {}

    @pytest.mark.unit
    def test_config_manager_default_provider(self):
        """Test default provider configuration."""
        manager = ConfigManager()
        assert manager.default_provider == "e2b"  # Default fallback

    @pytest.mark.unit
    def test_config_manager_custom_default_provider(self):
        """Test custom default provider."""
        manager = ConfigManager()
        manager._config["default_provider"] = "custom"
        assert manager.default_provider == "custom"

    @pytest.mark.unit
    def test_get_provider_config_existing(self):
        """Test getting existing provider configuration."""
        manager = ConfigManager()
        manager._providers["test"] = ProviderConfig("test", {"key": "value"})

        config = manager.get_provider_config("test")
        assert config.name == "test"
        assert config.get("key") == "value"

    @pytest.mark.unit
    def test_get_provider_config_new(self):
        """Test getting configuration for new provider."""
        manager = ConfigManager()

        config = manager.get_provider_config("new_provider")
        assert config.name == "new_provider"
        assert config.config == {}

    @pytest.mark.unit
    def test_get_sandbox_defaults(self):
        """Test getting sandbox defaults."""
        manager = ConfigManager()
        manager._config["sandbox_defaults"] = {
            "timeout": 600,
            "working_directory": "/custom",
        }

        config = manager.get_sandbox_defaults()
        assert config.timeout == 600
        assert config.working_directory == "/custom"

    @pytest.mark.unit
    def test_get_sandbox_defaults_empty(self):
        """Test getting sandbox defaults when none configured."""
        manager = ConfigManager()

        config = manager.get_sandbox_defaults()
        assert isinstance(config, SandboxConfig)
        assert config.timeout == 300  # Default value

    @pytest.mark.unit
    def test_config_get_set(self):
        """Test getting and setting configuration values."""
        manager = ConfigManager()

        assert manager.get("missing") is None
        assert manager.get("missing", "default") == "default"

        manager.set("test_key", "test_value")
        assert manager.get("test_key") == "test_value"

    @pytest.mark.unit
    def test_load_config_file_yaml(self):
        """Test loading configuration from YAML file."""
        config_data = {
            "default_provider": "test",
            "providers": {
                "test": {"api_key": "test_key"},
            },
            "sandbox_defaults": {"timeout": 600},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            manager = ConfigManager(config_path)
            assert manager.default_provider == "test"
            assert manager.get_provider_config("test").get("api_key") == "test_key"
            assert manager.get_sandbox_defaults().timeout == 600
        finally:
            os.unlink(config_path)

    @pytest.mark.unit
    def test_load_config_file_invalid(self):
        """Test loading invalid configuration file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_path = f.name

        try:
            with pytest.raises(ConfigurationError, match="Failed to load config file"):
                ConfigManager(config_path)
        finally:
            os.unlink(config_path)

    @pytest.mark.unit
    def test_load_config_file_not_found(self):
        """Test loading non-existent configuration file."""
        # Should not raise error, just use defaults
        manager = ConfigManager("/nonexistent/config.yaml")
        assert manager.default_provider == "e2b"

    @pytest.mark.unit
    def test_load_env_config(self, env_vars):
        """Test loading configuration from environment variables."""
        manager = ConfigManager()

        assert manager.default_provider == "test"
        assert manager.get_provider_config("e2b").get("api_key") == "test_e2b_key"
        assert manager.get_provider_config("modal").get("token_id") == "test_modal_id"
        assert (
            manager.get_provider_config("modal").get("token_secret")
            == "test_modal_secret"
        )
        assert (
            manager.get_provider_config("daytona").get("api_key") == "test_daytona_key"
        )

    @pytest.mark.unit
    def test_init_providers(self):
        """Test provider initialization from config."""
        manager = ConfigManager()
        manager._config = {
            "providers": {
                "provider1": {"key1": "value1"},
                "provider2": {"key2": "value2"},
            }
        }
        manager._init_providers()

        assert "provider1" in manager._providers
        assert "provider2" in manager._providers
        assert manager._providers["provider1"].get("key1") == "value1"
        assert manager._providers["provider2"].get("key2") == "value2"

    @pytest.mark.unit
    def test_default_config_paths(self):
        """Test default configuration file paths."""
        expected_paths = [
            "grainchain.yaml",
            "grainchain.yml",
            ".grainchain.yaml",
            ".grainchain.yml",
            "~/.grainchain.yaml",
            "~/.grainchain.yml",
        ]

        assert ConfigManager.DEFAULT_CONFIG_PATHS == expected_paths

    @pytest.mark.unit
    def test_load_config_from_default_paths(self):
        """Test loading config from default paths."""
        config_data = {"default_provider": "from_file"}

        # Create a config file in current directory
        with open("grainchain.yaml", "w") as f:
            yaml.dump(config_data, f)

        try:
            manager = ConfigManager()
            assert manager.default_provider == "from_file"
        finally:
            os.unlink("grainchain.yaml")


class TestGlobalConfigManager:
    """Test cases for global config manager functions."""

    @pytest.mark.unit
    def test_get_config_manager_singleton(self):
        """Test that get_config_manager returns singleton."""
        manager1 = get_config_manager()
        manager2 = get_config_manager()

        assert manager1 is manager2

    @pytest.mark.unit
    def test_set_config_manager(self):
        """Test setting custom config manager."""
        original_manager = get_config_manager()
        custom_manager = ConfigManager()

        set_config_manager(custom_manager)

        assert get_config_manager() is custom_manager

        # Restore original for other tests
        set_config_manager(original_manager)

    @pytest.mark.unit
    def test_config_manager_reset(self):
        """Test resetting config manager."""
        # Get initial manager
        manager1 = get_config_manager()

        # Set a custom one
        custom_manager = ConfigManager()
        set_config_manager(custom_manager)

        # Reset to None and get new one
        set_config_manager(None)
        manager2 = get_config_manager()

        # Should be a new instance
        assert manager2 is not manager1
        assert manager2 is not custom_manager


class TestConfigurationIntegration:
    """Integration tests for configuration system."""

    @pytest.mark.unit
    def test_full_config_integration(self, temp_dir):
        """Test full configuration integration."""
        # Create config file
        config_file = temp_dir / "test_config.yaml"
        config_data = {
            "default_provider": "e2b",
            "providers": {
                "e2b": {
                    "api_key": "file_e2b_key",
                    "template": "python",
                },
                "local": {
                    "working_dir": "/tmp",
                },
            },
            "sandbox_defaults": {
                "timeout": 900,
                "memory_limit": "4GB",
                "auto_cleanup": False,
            },
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Set environment variables (should override file values)
        with patch.dict(
            os.environ,
            {
                "E2B_API_KEY": "env_e2b_key",
                "GRAINCHAIN_DEFAULT_PROVIDER": "local",
            },
        ):
            manager = ConfigManager(str(config_file))

            # Environment should override file for default provider
            assert manager.default_provider == "local"

            # Environment should override file for API key
            e2b_config = manager.get_provider_config("e2b")
            assert e2b_config.get("api_key") == "env_e2b_key"
            assert e2b_config.get("template") == "python"  # From file

            # Sandbox defaults from file
            sandbox_config = manager.get_sandbox_defaults()
            assert sandbox_config.timeout == 900
            assert sandbox_config.memory_limit == "4GB"
            assert sandbox_config.auto_cleanup is False

    @pytest.mark.unit
    def test_config_precedence(self, temp_dir):
        """Test configuration precedence (env > file > defaults)."""
        # Create config file
        config_file = temp_dir / "precedence_test.yaml"
        config_data = {
            "default_provider": "file_provider",
            "providers": {
                "test": {
                    "file_only": "file_value",
                    "both_file_env": "file_value",
                },
            },
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Set environment variables
        with patch.dict(
            os.environ,
            {
                "GRAINCHAIN_DEFAULT_PROVIDER": "env_provider",
                "E2B_API_KEY": "env_e2b_key",
            },
        ):
            manager = ConfigManager(str(config_file))

            # Environment wins over file
            assert manager.default_provider == "env_provider"

            # File values are preserved when no env override
            test_config = manager.get_provider_config("test")
            assert test_config.get("file_only") == "file_value"

            # Environment values are added
            e2b_config = manager.get_provider_config("e2b")
            assert e2b_config.get("api_key") == "env_e2b_key"

    @pytest.mark.unit
    def test_config_error_handling(self):
        """Test configuration error handling."""
        # Test with directory instead of file
        with pytest.raises(ConfigurationError):
            ConfigManager("/tmp")  # Directory, not file

        # Test with permission denied (simulate)
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with pytest.raises(ConfigurationError, match="Failed to load config file"):
                ConfigManager("test.yaml")

    @pytest.mark.unit
    def test_empty_config_file(self, temp_dir):
        """Test handling of empty configuration file."""
        config_file = temp_dir / "empty.yaml"
        config_file.write_text("")

        manager = ConfigManager(str(config_file))

        # Should use defaults
        assert manager.default_provider == "e2b"
        assert isinstance(manager.get_sandbox_defaults(), SandboxConfig)
