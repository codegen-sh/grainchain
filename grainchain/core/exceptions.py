"""Exception classes for Grainchain."""


class GrainchainError(Exception):
    """Base exception for all Grainchain errors."""

    pass


class SandboxError(GrainchainError):
    """Sandbox operation failed."""

    pass


class ProviderError(GrainchainError):
    """Provider-specific error."""

    def __init__(self, message: str, provider: str, original_error: Exception = None):
        super().__init__(message)
        self.provider = provider
        self.original_error = original_error


class ConfigurationError(GrainchainError):
    """Configuration error."""

    pass


class TimeoutError(GrainchainError):
    """Operation timed out."""

    def __init__(self, message: str, timeout_seconds: int):
        super().__init__(message)
        self.timeout_seconds = timeout_seconds


class AuthenticationError(GrainchainError):
    """Authentication failed."""

    def __init__(self, message: str, provider: str):
        super().__init__(message)
        self.provider = provider


class ResourceError(GrainchainError):
    """Resource allocation or management error."""

    pass


class NetworkError(GrainchainError):
    """Network-related error."""

    pass
