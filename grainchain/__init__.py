"""
Grainchain: Langchain for Sandboxes

A unified interface for sandbox providers, enabling developers to write code once
and run it across multiple sandbox environments.

Quick Start:
    >>> from grainchain import Sandbox
    >>> async with Sandbox() as sandbox:
    ...     result = await sandbox.execute("echo 'Hello, Grainchain!'")
    ...     print(result.stdout)

Simple Usage:
    >>> from grainchain import create_local_sandbox
    >>> sandbox = create_local_sandbox()
    >>> result = await sandbox.execute("python -c 'print(2+2)'")
"""

__version__ = "0.1.0"

from grainchain.core.config import SandboxConfig
from grainchain.core.exceptions import (
    AuthenticationError,
    ConfigurationError,
    GrainchainError,
    ProviderError,
    SandboxError,
    TimeoutError,
)

# Provider information utilities
from grainchain.core.providers_info import (
    ProviderInfo,
    check_provider,
    get_available_providers,
    get_providers_info,
)
from grainchain.core.sandbox import Sandbox


# Provider constants for easier usage
class Providers:
    """Provider constants for easier provider selection."""

    LOCAL = "local"
    E2B = "e2b"
    DAYTONA = "daytona"
    MORPH = "morph"
    MODAL = "modal"


# Convenience factory functions
def create_local_sandbox(
    timeout: int = 60, working_directory: str = ".", **kwargs
) -> Sandbox:
    """
    Create a local sandbox with sensible defaults.

    Args:
        timeout: Command timeout in seconds (default: 60)
        working_directory: Working directory for commands (default: ".")
        **kwargs: Additional configuration options

    Returns:
        Configured Sandbox instance using local provider

    Example:
        >>> sandbox = create_local_sandbox(timeout=30)
        >>> async with sandbox:
        ...     result = await sandbox.execute("echo 'Hello!'")
    """
    config = SandboxConfig(
        timeout=timeout, working_directory=working_directory, **kwargs
    )
    return Sandbox(provider=Providers.LOCAL, config=config)


def create_e2b_sandbox(template: str = "base", timeout: int = 60, **kwargs) -> Sandbox:
    """
    Create an E2B sandbox with sensible defaults.

    Args:
        template: E2B template to use (default: "base")
        timeout: Command timeout in seconds (default: 60)
        **kwargs: Additional configuration options

    Returns:
        Configured Sandbox instance using E2B provider

    Example:
        >>> sandbox = create_e2b_sandbox(template="python")
        >>> async with sandbox:
        ...     result = await sandbox.execute("python --version")
    """
    # Merge template into environment_vars if not already specified
    env_vars = kwargs.get("environment_vars", {})
    if "E2B_TEMPLATE" not in env_vars:
        env_vars["E2B_TEMPLATE"] = template

    config = SandboxConfig(
        timeout=timeout,
        environment_vars=env_vars,
        **{k: v for k, v in kwargs.items() if k != "environment_vars"},
    )
    return Sandbox(provider=Providers.E2B, config=config)


def create_sandbox(provider: str = "local", **kwargs) -> Sandbox:
    """
    Create a sandbox with the specified provider and smart defaults.

    Args:
        provider: Provider name (local, e2b, daytona, morph, modal)
        **kwargs: Configuration options passed to SandboxConfig

    Returns:
        Configured Sandbox instance

    Example:
        >>> sandbox = create_sandbox("local", timeout=30)
        >>> async with sandbox:
        ...     result = await sandbox.execute("pwd")
    """
    # Set smart defaults based on provider
    defaults = {
        "timeout": 60,
        "working_directory": ".",
        "auto_cleanup": True,
    }

    # Provider-specific defaults
    if provider == Providers.E2B:
        defaults["environment_vars"] = {"E2B_TEMPLATE": "base"}
    elif provider == Providers.LOCAL:
        defaults["working_directory"] = "."

    # Merge user kwargs with defaults
    config_kwargs = {**defaults, **kwargs}
    config = SandboxConfig(**config_kwargs)

    return Sandbox(provider=provider, config=config)


# Import convenience functions (optional, for easier access)
try:
    from grainchain.convenience import (
        ConfigPresets,  # noqa: F401
        QuickSandbox,  # noqa: F401
        create_data_sandbox,  # noqa: F401
        create_dev_sandbox,  # noqa: F401
        create_test_sandbox,  # noqa: F401
        quick_execute,  # noqa: F401
        quick_python,  # noqa: F401
        quick_script,  # noqa: F401
    )

    _CONVENIENCE_AVAILABLE = True
except ImportError:
    _CONVENIENCE_AVAILABLE = False

# LangGraph integration (optional import)
try:
    from grainchain import langgraph  # noqa: F401

    _LANGGRAPH_AVAILABLE = True
except ImportError:
    _LANGGRAPH_AVAILABLE = False

__all__ = [
    # Core classes
    "Sandbox",
    "SandboxConfig",
    # Exceptions
    "GrainchainError",
    "SandboxError",
    "ProviderError",
    "ConfigurationError",
    "TimeoutError",
    "AuthenticationError",
    # Provider information
    "ProviderInfo",
    "get_providers_info",
    "get_available_providers",
    "check_provider",
    # Provider constants
    "Providers",
    # Convenience functions
    "create_sandbox",
    "create_local_sandbox",
    "create_e2b_sandbox",
]

# Add convenience functions to __all__ if available
if _CONVENIENCE_AVAILABLE:
    __all__.extend(
        [
            "QuickSandbox",
            "quick_execute",
            "quick_python",
            "quick_script",
            "ConfigPresets",
            "create_dev_sandbox",
            "create_test_sandbox",
            "create_data_sandbox",
        ]
    )

# Add langgraph to __all__ if available
if _LANGGRAPH_AVAILABLE:
    __all__.append("langgraph")
