"""
Unit tests for the configuration management system.

Tests configuration loading, validation, and provider configuration.
"""

import os
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch

import pytest

from grainchain.core.config import ConfigManager, ProviderConfig, SandboxConfig
from grainchain.core.exceptions import ConfigurationError


class TestProviderConfig:
    """Test cases for ProviderConfig."""
    
    def test_provider_config_creation(self):
        """Test creating a provider configuration."""
        config = ProviderConfig(
            name="test_provider",
            config={"api_key": "test_key", "timeout": 300, "custom_param": "value"}
        )
        
        assert config.name == "test_provider"
        assert config.get("api_key") == "test_key"
        assert config.get("timeout") == 300
        assert config.get("custom_param") == "value"
    
    def test_provider_config_defaults(self):
        """Test provider configuration with defaults."""
        config = ProviderConfig(name="test")
        
        assert config.name == "test"
        assert config.config == {}
        assert config.get("api_key") is None
        assert config.get("timeout") is None
    
    def test_provider_config_get_set(self):
        """Test getting and setting configuration values."""
        config = ProviderConfig(name="test")
        
        # Test default value
        assert config.get("nonexistent", "default") == "default"
        
        # Test setting and getting
        config.set("api_key", "new_key")
        assert config.get("api_key") == "new_key"
        
        # Test overwriting
        config.set("api_key", "updated_key")
        assert config.get("api_key") == "updated_key"


class TestSandboxConfig:
    """Test cases for SandboxConfig."""
    
    def test_sandbox_config_creation(self):
        """Test creating a sandbox configuration."""
        config = SandboxConfig(
            timeout=300,
            working_directory="/workspace",
            environment_vars={"VAR1": "value1", "VAR2": "value2"},
            auto_cleanup=True
        )
        
        assert config.timeout == 300
        assert config.working_directory == "/workspace"
        assert config.environment_vars == {"VAR1": "value1", "VAR2": "value2"}
        assert config.auto_cleanup is True
    
    def test_sandbox_config_defaults(self):
        """Test sandbox configuration with defaults."""
        config = SandboxConfig()
        
        assert config.timeout == 300
        assert config.working_directory == "/workspace"
        assert config.environment_vars == {}
        assert config.auto_cleanup is True
    
    def test_sandbox_config_optional_fields(self):
        """Test sandbox configuration optional fields."""
        config = SandboxConfig(
            memory_limit="2GB",
            cpu_limit=2.0,
            image="python:3.11",
            keep_alive=True
        )
        
        assert config.memory_limit == "2GB"
        assert config.cpu_limit == 2.0
        assert config.image == "python:3.11"
        assert config.keep_alive is True


class TestConfigManager:
    """Test cases for ConfigManager."""
    
    def test_config_manager_creation(self):
        """Test ConfigManager creation."""
        manager = ConfigManager()
        
        assert manager._config is not None
        assert manager._providers is not None
        assert isinstance(manager._config, dict)
        assert isinstance(manager._providers, dict)
    
    def test_config_manager_default_provider(self):
        """Test getting default provider."""
        manager = ConfigManager()
        
        # Default should be e2b
        assert manager.default_provider == "e2b"
    
    def test_config_manager_with_env_default_provider(self):
        """Test getting default provider from environment variable."""
        with patch.dict(os.environ, {"GRAINCHAIN_DEFAULT_PROVIDER": "modal"}):
            manager = ConfigManager()
            assert manager.default_provider == "modal"
    
    def test_get_provider_config(self):
        """Test getting provider configuration."""
        manager = ConfigManager()
        
        # Get config for unknown provider
        provider_config = manager.get_provider_config("unknown")
        
        assert isinstance(provider_config, ProviderConfig)
        assert provider_config.name == "unknown"
        assert provider_config.config == {}
    
    def test_get_provider_config_with_env_vars(self):
        """Test getting provider configuration with environment variables."""
        with patch.dict(os.environ, {
            "E2B_API_KEY": "test_key",
            "E2B_TEMPLATE": "python-basic"
        }):
            manager = ConfigManager()
            provider_config = manager.get_provider_config("e2b")
            
            assert provider_config.get("api_key") == "test_key"
            assert provider_config.get("template") == "python-basic"
    
    def test_get_sandbox_defaults(self):
        """Test getting sandbox defaults."""
        manager = ConfigManager()
        
        sandbox_config = manager.get_sandbox_defaults()
        
        assert isinstance(sandbox_config, SandboxConfig)
        assert sandbox_config.timeout == 300
        assert sandbox_config.working_directory == "/workspace"
        assert sandbox_config.auto_cleanup is True
    
    def test_config_manager_get_set(self):
        """Test getting and setting configuration values."""
        manager = ConfigManager()
        
        # Test default value
        assert manager.get("nonexistent", "default") == "default"
        
        # Test setting and getting
        manager.set("test_key", "test_value")
        assert manager.get("test_key") == "test_value"
    
    def test_load_config_from_file(self, temp_dir):
        """Test loading configuration from YAML file."""
        config_data = {
            "default_provider": "modal",
            "providers": {
                "e2b": {
                    "api_key": "test_key",
                    "template": "python-data-science"
                }
            },
            "sandbox_defaults": {
                "timeout": 240,
                "working_directory": "/app"
            }
        }
        
        config_file = temp_dir / "grainchain.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        
        manager = ConfigManager(config_path=str(config_file))
        
        assert manager.default_provider == "modal"
        
        e2b_config = manager.get_provider_config("e2b")
        assert e2b_config.get("api_key") == "test_key"
        assert e2b_config.get("template") == "python-data-science"
        
        sandbox_config = manager.get_sandbox_defaults()
        assert sandbox_config.timeout == 240
        assert sandbox_config.working_directory == "/app"
    
    def test_load_config_file_not_found(self):
        """Test loading configuration when file doesn't exist."""
        # When no config path is provided, it should use defaults without error
        manager = ConfigManager(config_path=None)
        
        # Should not raise an error, just use defaults
        assert manager.default_provider == "e2b"
        
        # When an explicit path is provided that doesn't exist, it should raise an error
        with pytest.raises(ConfigurationError, match="Failed to load config file"):
            ConfigManager(config_path="nonexistent.yaml")
    
    def test_load_config_invalid_yaml(self, temp_dir):
        """Test loading configuration with invalid YAML."""
        config_file = temp_dir / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: [")
        
        with pytest.raises(ConfigurationError, match="Failed to load config file"):
            ConfigManager(config_path=str(config_file))
    
    def test_modal_provider_env_vars(self):
        """Test Modal provider environment variables."""
        with patch.dict(os.environ, {
            "MODAL_TOKEN_ID": "test_id",
            "MODAL_TOKEN_SECRET": "test_secret"
        }):
            manager = ConfigManager()
            modal_config = manager.get_provider_config("modal")
            
            assert modal_config.get("token_id") == "test_id"
            assert modal_config.get("token_secret") == "test_secret"
    
    def test_global_config_manager(self):
        """Test global config manager functions."""
        from grainchain.core.config import get_config_manager, set_config_manager
        
        # Get default global manager
        manager1 = get_config_manager()
        manager2 = get_config_manager()
        
        # Should return the same instance
        assert manager1 is manager2
        
        # Set custom manager
        custom_manager = ConfigManager()
        set_config_manager(custom_manager)
        
        # Should return the custom manager
        assert get_config_manager() is custom_manager
    
    def test_config_file_discovery(self, temp_dir):
        """Test automatic config file discovery."""
        # Create config file in current directory
        config_data = {"default_provider": "test_provider"}
        config_file = temp_dir / "grainchain.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        
        # Change to temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            manager = ConfigManager()
            assert manager.default_provider == "test_provider"
        finally:
            os.chdir(original_cwd)
    
    def test_sandbox_defaults_with_overrides(self, temp_dir):
        """Test sandbox defaults with configuration overrides."""
        config_data = {
            "sandbox_defaults": {
                "timeout": 600,
                "memory_limit": "4GB",
                "auto_cleanup": False
            }
        }
        
        config_file = temp_dir / "grainchain.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)
        
        manager = ConfigManager(config_path=str(config_file))
        sandbox_config = manager.get_sandbox_defaults()
        
        assert sandbox_config.timeout == 600
        assert sandbox_config.memory_limit == "4GB"
        assert sandbox_config.auto_cleanup is False
        assert sandbox_config.working_directory == "/workspace"  # Default value
