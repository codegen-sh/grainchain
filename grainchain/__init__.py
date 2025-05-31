"""
Grainchain: Langchain for Sandboxes

A unified interface for sandbox providers, enabling developers to write code once
and run it across multiple sandbox environments.
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
from grainchain.core.sandbox import Sandbox

# LangGraph integration (optional import)
try:
    from grainchain import langgraph  # noqa: F401

    _LANGGRAPH_AVAILABLE = True
except ImportError:
    _LANGGRAPH_AVAILABLE = False

__all__ = [
    "Sandbox",
    "SandboxConfig",
    "GrainchainError",
    "SandboxError",
    "ProviderError",
    "ConfigurationError",
    "TimeoutError",
    "AuthenticationError",
]

# Add langgraph to __all__ if available
if _LANGGRAPH_AVAILABLE:
    __all__.append("langgraph")
