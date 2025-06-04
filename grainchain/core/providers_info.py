"""Provider information and discovery utilities for Grainchain."""

import os
from dataclasses import dataclass, field

from grainchain.core.config import get_config_manager


@dataclass
class ProviderInfo:
    """Information about a provider's availability and configuration status."""

    name: str
    available: bool
    dependencies_installed: bool
    configured: bool
    missing_config: list[str] = field(default_factory=list)
    install_command: str | None = None
    config_instructions: list[str] | None = None
    error_message: str | None = None


class ProviderDiscovery:
    """Utility class for discovering available providers and their status."""

    # Provider metadata
    PROVIDERS = {
        "local": {
            "dependencies": [],
            "env_vars": [],
            "install_command": None,
            "description": "Local Docker-based sandbox provider",
        },
        "e2b": {
            "dependencies": ["e2b"],
            "env_vars": ["E2B_API_KEY"],
            "optional_env_vars": ["E2B_TEMPLATE"],
            "install_command": "pip install grainchain[e2b]",
            "description": "E2B cloud sandbox provider",
        },
        "modal": {
            "dependencies": ["modal"],
            "env_vars": ["MODAL_TOKEN_ID", "MODAL_TOKEN_SECRET"],
            "install_command": "pip install grainchain[modal]",
            "description": "Modal cloud compute provider",
        },
        "daytona": {
            "dependencies": ["daytona"],
            "env_vars": ["DAYTONA_API_KEY"],
            "install_command": "pip install daytona-sdk",
            "description": "Daytona development environment provider",
        },
        "morph": {
            "dependencies": ["morphcloud"],
            "env_vars": ["MORPH_API_KEY"],
            "install_command": "pip install morphcloud",
            "description": "Morph.so cloud sandbox provider",
        },
    }

    def __init__(self):
        self.config_manager = get_config_manager()

    def check_provider_dependencies(self, provider_name: str) -> bool:
        """Check if a provider's dependencies are installed."""
        provider_meta = self.PROVIDERS.get(provider_name, {})
        dependencies = provider_meta.get("dependencies", [])

        if not dependencies:
            return True

        for dep in dependencies:
            try:
                __import__(dep)
            except ImportError:
                return False
        return True

    def check_provider_config(self, provider_name: str) -> tuple[bool, list[str]]:
        """Check if a provider is properly configured."""
        provider_meta = self.PROVIDERS.get(provider_name, {})
        required_env_vars = provider_meta.get("env_vars", [])

        missing = []
        for env_var in required_env_vars:
            if not os.getenv(env_var):
                missing.append(env_var)

        return len(missing) == 0, missing

    def get_provider_info(self, provider_name: str) -> ProviderInfo:
        """Get comprehensive information about a provider."""
        if provider_name not in self.PROVIDERS:
            return ProviderInfo(
                name=provider_name,
                available=False,
                dependencies_installed=False,
                configured=False,
                missing_config=[],
                error_message=f"Unknown provider: {provider_name}",
            )

        provider_meta = self.PROVIDERS[provider_name]

        # Check dependencies
        deps_installed = self.check_provider_dependencies(provider_name)

        # Check configuration
        configured, missing_config = self.check_provider_config(provider_name)

        # Determine overall availability
        available = deps_installed and configured

        # Generate configuration instructions
        config_instructions = []
        if missing_config:
            config_instructions.append("Set the following environment variables:")
            for env_var in missing_config:
                config_instructions.append(
                    f"  export {env_var}='your-{env_var.lower().replace('_', '-')}-here'"
                )

        # Add optional environment variables info
        optional_vars = provider_meta.get("optional_env_vars", [])
        if optional_vars and configured:
            config_instructions.append("\nOptional environment variables:")
            for env_var in optional_vars:
                status = "✓ set" if os.getenv(env_var) else "○ not set"
                config_instructions.append(f"  {env_var} ({status})")

        return ProviderInfo(
            name=provider_name,
            available=available,
            dependencies_installed=deps_installed,
            configured=configured,
            missing_config=missing_config,
            install_command=provider_meta.get("install_command"),
            config_instructions=config_instructions,
        )

    def get_all_providers_info(self) -> dict[str, ProviderInfo]:
        """Get information about all known providers."""
        return {name: self.get_provider_info(name) for name in self.PROVIDERS.keys()}

    def get_available_providers(self) -> list[str]:
        """Get list of fully available (installed and configured) providers."""
        return [
            name
            for name, info in self.get_all_providers_info().items()
            if info.available
        ]

    def get_default_provider_info(self) -> ProviderInfo:
        """Get information about the default provider."""
        default_provider = self.config_manager.default_provider
        return self.get_provider_info(default_provider)


def get_providers_info() -> dict[str, ProviderInfo]:
    """
    Get information about all available providers.

    Returns:
        Dictionary mapping provider names to ProviderInfo objects.

    Example:
        >>> from grainchain.core.providers_info import get_providers_info
        >>> providers = get_providers_info()
        >>> for name, info in providers.items():
        ...     print(f"{name}: {'✓' if info.available else '✗'}")
    """
    discovery = ProviderDiscovery()
    return discovery.get_all_providers_info()


def get_available_providers() -> list[str]:
    """
    Get list of fully available (installed and configured) provider names.

    Returns:
        List of provider names that are ready to use.

    Example:
        >>> from grainchain.core.providers_info import get_available_providers
        >>> available = get_available_providers()
        >>> print(f"Available providers: {', '.join(available)}")
    """
    discovery = ProviderDiscovery()
    return discovery.get_available_providers()


def check_provider(provider_name: str) -> ProviderInfo:
    """
    Check the status of a specific provider.

    Args:
        provider_name: Name of the provider to check.

    Returns:
        ProviderInfo object with detailed status information.

    Example:
        >>> from grainchain.core.providers_info import check_provider
        >>> info = check_provider("e2b")
        >>> if not info.available:
        ...     print(f"Setup needed: {info.missing_config}")
    """
    discovery = ProviderDiscovery()
    return discovery.get_provider_info(provider_name)
