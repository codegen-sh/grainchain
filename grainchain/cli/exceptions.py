"""Custom exceptions for CLI operations with actionable error messages."""


class CliError(Exception):
    """Base exception for CLI operations."""

    def __init__(self, message: str, suggestion: str | None = None, exit_code: int = 1):
        self.message = message
        self.suggestion = suggestion
        self.exit_code = exit_code
        super().__init__(message)


class DependencyError(CliError):
    """Raised when a required dependency is missing or not working."""

    def __init__(
        self,
        dependency: str,
        install_command: str | None = None,
        docs_url: str | None = None,
    ):
        message = f"{dependency} is required but not available"

        suggestions = []
        if install_command:
            suggestions.append(f"Install it with: {install_command}")
        if docs_url:
            suggestions.append(f"See documentation: {docs_url}")

        suggestion = " | ".join(suggestions) if suggestions else None

        super().__init__(message, suggestion, exit_code=127)
        self.dependency = dependency


class ConfigurationError(CliError):
    """Raised when configuration is missing or invalid."""

    def __init__(
        self,
        config_item: str,
        expected_format: str | None = None,
        config_file: str | None = None,
    ):
        message = f"Configuration error: {config_item}"

        suggestions = []
        if expected_format:
            suggestions.append(f"Expected format: {expected_format}")
        if config_file:
            suggestions.append(f"Check configuration file: {config_file}")

        suggestion = " | ".join(suggestions) if suggestions else None

        super().__init__(message, suggestion, exit_code=78)
        self.config_item = config_item


class ProviderError(CliError):
    """Raised when a sandbox provider fails."""

    def __init__(
        self,
        provider: str,
        operation: str,
        original_error: str | None = None,
        troubleshooting_url: str | None = None,
    ):
        message = f"{provider} provider failed during {operation}"
        if original_error:
            message += f": {original_error}"

        suggestions = []

        # Provider-specific suggestions
        if provider.lower() == "local":
            suggestions.append("Check if Docker is running and accessible")
            suggestions.append("Verify Docker permissions for your user")
        elif provider.lower() == "e2b":
            suggestions.append("Check your E2B API key in environment variables")
            suggestions.append("Verify your E2B account has sufficient credits")
        elif provider.lower() == "daytona":
            suggestions.append("Check your Daytona configuration and API access")
            suggestions.append("Verify Daytona service is running and accessible")
        elif provider.lower() == "morph":
            suggestions.append("Check your Morph API credentials")
            suggestions.append("Verify network connectivity to Morph services")

        if troubleshooting_url:
            suggestions.append(f"See troubleshooting guide: {troubleshooting_url}")

        suggestion = " | ".join(suggestions) if suggestions else None

        super().__init__(message, suggestion, exit_code=1)
        self.provider = provider
        self.operation = operation


class BenchmarkError(CliError):
    """Raised when benchmark operations fail."""

    def __init__(self, test_name: str, provider: str, details: str | None = None):
        message = f"Benchmark test '{test_name}' failed on {provider} provider"
        if details:
            message += f": {details}"

        suggestions = [
            "Try running with --verbose for more details",
            "Check provider-specific configuration and credentials",
            "Verify network connectivity and service availability",
        ]

        suggestion = " | ".join(suggestions)

        super().__init__(message, suggestion, exit_code=1)
        self.test_name = test_name
        self.provider = provider


class ValidationError(CliError):
    """Raised when input validation fails."""

    def __init__(self, field: str, value: str, expected: str):
        message = f"Invalid {field}: '{value}'"
        suggestion = f"Expected: {expected}"

        super().__init__(message, suggestion, exit_code=2)
        self.field = field
        self.value = value


def handle_cli_error(error: Exception, verbose: bool = False) -> None:
    """
    Handle CLI errors with appropriate formatting and exit codes.

    Args:
        error: The exception to handle
        verbose: Whether to show verbose error information
    """
    from .utils import error as print_error
    from .utils import info, verbose_echo

    if isinstance(error, CliError):
        print_error(error.message)
        if error.suggestion:
            info(f"💡 {error.suggestion}")

        if verbose and hasattr(error, "__cause__") and error.__cause__:
            verbose_echo(f"Underlying error: {error.__cause__}")

        exit_code = error.exit_code
    else:
        print_error(f"Unexpected error: {error}")
        if verbose:
            import traceback

            verbose_echo("Full traceback:")
            verbose_echo(traceback.format_exc())
        exit_code = 1

    import sys

    sys.exit(exit_code)
