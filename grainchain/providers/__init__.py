"""Sandbox providers for Grainchain."""

from grainchain.providers.base import BaseSandboxProvider

__all__ = [
    "BaseSandboxProvider",
]

# Provider imports are done lazily to avoid import errors
# when optional dependencies are not installed


def get_e2b_provider():
    """Get E2B provider (lazy import)."""
    try:
        from grainchain.providers.e2b import E2BProvider

        return E2BProvider
    except ImportError as e:
        raise ImportError(
            "E2B provider requires the 'e2b' package. "
            "Install it with: pip install grainchain[e2b]"
        ) from e


def get_modal_provider():
    """Get Modal provider (lazy import)."""
    try:
        from grainchain.providers.modal import ModalProvider

        return ModalProvider
    except ImportError as e:
        raise ImportError(
            "Modal provider requires the 'modal' package. "
            "Install it with: pip install grainchain[modal]"
        ) from e


def get_daytona_provider():
    """Get Daytona provider (lazy import)."""
    try:
        from grainchain.providers.daytona import DaytonaProvider

        return DaytonaProvider
    except ImportError as e:
        raise ImportError(
            "Daytona provider requires the 'daytona-sdk' package. "
            "Install it with: pip install daytona-sdk"
        ) from e


def get_local_provider():
    """Get Local provider."""
    from grainchain.providers.local import LocalProvider

    return LocalProvider
