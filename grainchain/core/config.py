"""Configuration management for Grainchain."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union

import yaml
from dotenv import load_dotenv

from grainchain.core.exceptions import ConfigurationError

# Load environment variables from .env file
load_dotenv()


@dataclass
class ProviderConfig:
    """Configuration for a specific provider."""

    name: str
    config: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self.config[key] = value


@dataclass
class SandboxConfig:
    """Configuration for sandbox creation and management."""

    # Resource limits
    timeout: Optional[int] = 300  # seconds
    memory_limit: Optional[str] = None  # e.g., "2GB"
    cpu_limit: Optional[float] = None  # CPU cores

    # Environment
    image: Optional[str] = None
    working_directory: str = "/workspace"
    environment_vars: dict[str, str] = field(default_factory=dict)

    # Behavior
    auto_cleanup: bool = True
    keep_alive: bool = False

    # Provider-specific settings
    provider_config: dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """Manages configuration for Grainchain."""

    DEFAULT_CONFIG_PATHS = [
        "grainchain.yaml",
        "grainchain.yml",
        ".grainchain.yaml",
        ".grainchain.yml",
        "~/.grainchain.yaml",
        "~/.grainchain.yml",
    ]

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self.config_path = config_path
        self._config: dict[str, Any] = {}
        self._providers: dict[str, ProviderConfig] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Load from file
        if self.config_path:
            self._load_config_file(self.config_path)
        else:
            # Try default paths
            for path in self.DEFAULT_CONFIG_PATHS:
                expanded_path = Path(path).expanduser()
                if expanded_path.exists():
                    self._load_config_file(expanded_path)
                    break

        # Load from environment variables
        self._load_env_config()

        # Initialize providers
        self._init_providers()

    def _load_config_file(self, path: Union[str, Path]) -> None:
        """Load configuration from a YAML file."""
        try:
            with open(path) as f:
                file_config = yaml.safe_load(f) or {}
                self._config.update(file_config)
        except Exception as e:
            raise ConfigurationError(f"Failed to load config file {path}: {e}") from e

    def _load_env_config(self) -> None:
        """Load configuration from environment variables."""
        # Default provider
        if default_provider := os.getenv("GRAINCHAIN_DEFAULT_PROVIDER"):
            self._config["default_provider"] = default_provider

        # Provider-specific environment variables
        provider_env_vars = {
            "e2b": {
                "api_key": "E2B_API_KEY",
                "template": "E2B_TEMPLATE",
            },
            "modal": {
                "token_id": "MODAL_TOKEN_ID",
                "token_secret": "MODAL_TOKEN_SECRET",
            },
        }

        for provider, env_vars in provider_env_vars.items():
            provider_config = self._config.setdefault("providers", {}).setdefault(
                provider, {}
            )
            for config_key, env_var in env_vars.items():
                if value := os.getenv(env_var):
                    provider_config[config_key] = value

    def _init_providers(self) -> None:
        """Initialize provider configurations."""
        providers_config = self._config.get("providers", {})
        for name, config in providers_config.items():
            self._providers[name] = ProviderConfig(name=name, config=config)

    @property
    def default_provider(self) -> str:
        """Get the default provider name."""
        return self._config.get("default_provider", "e2b")

    def get_provider_config(self, provider_name: str) -> ProviderConfig:
        """Get configuration for a specific provider."""
        if provider_name not in self._providers:
            # Create empty config for unknown providers
            self._providers[provider_name] = ProviderConfig(name=provider_name)
        return self._providers[provider_name]

    def get_sandbox_defaults(self) -> SandboxConfig:
        """Get default sandbox configuration."""
        defaults = self._config.get("sandbox_defaults", {})
        return SandboxConfig(**defaults)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def set_config_manager(config_manager: ConfigManager) -> None:
    """Set the global configuration manager instance."""
    global _config_manager
    _config_manager = config_manager
