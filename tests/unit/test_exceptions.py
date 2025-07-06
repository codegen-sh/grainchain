"""Unit tests for exception classes."""

import pytest

from grainchain.core.exceptions import (
    AuthenticationError,
    ConfigurationError,
    GrainchainError,
    NetworkError,
    ProviderError,
    ResourceError,
    SandboxError,
)
from grainchain.core.exceptions import (
    TimeoutError as GrainchainTimeoutError,
)


class TestGrainchainError:
    """Test cases for base GrainchainError."""

    @pytest.mark.unit
    def test_grainchain_error_basic(self):
        """Test basic GrainchainError functionality."""
        error = GrainchainError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    @pytest.mark.unit
    def test_grainchain_error_inheritance(self):
        """Test that all custom exceptions inherit from GrainchainError."""
        # Test exceptions with simple constructors
        exceptions = [
            SandboxError,
            ConfigurationError,
            ResourceError,
            NetworkError,
        ]

        for exc_class in exceptions:
            error = exc_class("Test message")
            assert isinstance(error, GrainchainError)
            assert isinstance(error, Exception)
            assert str(error) == "Test message"

        # Test ProviderError separately due to different constructor
        provider_error = ProviderError("Test message", "test_provider")
        assert isinstance(provider_error, GrainchainError)
        assert isinstance(provider_error, Exception)
        assert str(provider_error) == "Test message"
        assert provider_error.provider == "test_provider"

        # Test TimeoutError separately due to different constructor
        timeout_error = GrainchainTimeoutError("Test timeout", 30)
        assert isinstance(timeout_error, GrainchainError)
        assert isinstance(timeout_error, Exception)
        assert str(timeout_error) == "Test timeout"
        assert timeout_error.timeout_seconds == 30

        # Test AuthenticationError separately due to different constructor
        auth_error = AuthenticationError("Test auth error", "test_provider")
        assert isinstance(auth_error, GrainchainError)
        assert isinstance(auth_error, Exception)
        assert str(auth_error) == "Test auth error"
        assert auth_error.provider == "test_provider"


class TestSandboxError:
    """Test cases for SandboxError."""

    @pytest.mark.unit
    def test_sandbox_error_basic(self):
        """Test basic SandboxError functionality."""
        error = SandboxError("Sandbox operation failed")
        assert str(error) == "Sandbox operation failed"
        assert isinstance(error, GrainchainError)

    @pytest.mark.unit
    def test_sandbox_error_with_details(self):
        """Test SandboxError with detailed message."""
        error = SandboxError("Command execution failed: exit code 1")
        assert "Command execution failed" in str(error)
        assert "exit code 1" in str(error)


class TestProviderError:
    """Test cases for ProviderError."""

    @pytest.mark.unit
    def test_provider_error_basic(self):
        """Test basic ProviderError functionality."""
        error = ProviderError("Provider failed", "test_provider")
        assert str(error) == "Provider failed"
        assert error.provider == "test_provider"
        assert error.original_error is None

    @pytest.mark.unit
    def test_provider_error_with_original(self):
        """Test ProviderError with original exception."""
        original = ValueError("Original error")
        error = ProviderError("Provider failed", "test_provider", original)

        assert str(error) == "Provider failed"
        assert error.provider == "test_provider"
        assert error.original_error is original

    @pytest.mark.unit
    def test_provider_error_attributes(self):
        """Test ProviderError attributes."""
        error = ProviderError("Test message", "e2b")
        assert hasattr(error, "provider")
        assert hasattr(error, "original_error")
        assert error.provider == "e2b"


class TestConfigurationError:
    """Test cases for ConfigurationError."""

    @pytest.mark.unit
    def test_configuration_error_basic(self):
        """Test basic ConfigurationError functionality."""
        error = ConfigurationError("Invalid configuration")
        assert str(error) == "Invalid configuration"
        assert isinstance(error, GrainchainError)

    @pytest.mark.unit
    def test_configuration_error_missing_key(self):
        """Test ConfigurationError for missing configuration key."""
        error = ConfigurationError("Required configuration 'api_key' not found")
        assert "api_key" in str(error)
        assert "Required configuration" in str(error)


class TestTimeoutError:
    """Test cases for TimeoutError."""

    @pytest.mark.unit
    def test_timeout_error_basic(self):
        """Test basic TimeoutError functionality."""
        error = GrainchainTimeoutError("Operation timed out", 30)
        assert str(error) == "Operation timed out"
        assert error.timeout_seconds == 30

    @pytest.mark.unit
    def test_timeout_error_attributes(self):
        """Test TimeoutError attributes."""
        error = GrainchainTimeoutError("Command timeout", 60)
        assert hasattr(error, "timeout_seconds")
        assert error.timeout_seconds == 60

    @pytest.mark.unit
    def test_timeout_error_different_timeouts(self):
        """Test TimeoutError with different timeout values."""
        error1 = GrainchainTimeoutError("Short timeout", 5)
        error2 = GrainchainTimeoutError("Long timeout", 300)

        assert error1.timeout_seconds == 5
        assert error2.timeout_seconds == 300


class TestAuthenticationError:
    """Test cases for AuthenticationError."""

    @pytest.mark.unit
    def test_authentication_error_basic(self):
        """Test basic AuthenticationError functionality."""
        error = AuthenticationError("Authentication failed", "e2b")
        assert str(error) == "Authentication failed"
        assert error.provider == "e2b"

    @pytest.mark.unit
    def test_authentication_error_attributes(self):
        """Test AuthenticationError attributes."""
        error = AuthenticationError("Invalid API key", "modal")
        assert hasattr(error, "provider")
        assert error.provider == "modal"

    @pytest.mark.unit
    def test_authentication_error_different_providers(self):
        """Test AuthenticationError with different providers."""
        error1 = AuthenticationError("Auth failed", "e2b")
        error2 = AuthenticationError("Auth failed", "daytona")

        assert error1.provider == "e2b"
        assert error2.provider == "daytona"


class TestResourceError:
    """Test cases for ResourceError."""

    @pytest.mark.unit
    def test_resource_error_basic(self):
        """Test basic ResourceError functionality."""
        error = ResourceError("Resource allocation failed")
        assert str(error) == "Resource allocation failed"
        assert isinstance(error, GrainchainError)

    @pytest.mark.unit
    def test_resource_error_memory_limit(self):
        """Test ResourceError for memory limit."""
        error = ResourceError("Memory limit exceeded: 2GB")
        assert "Memory limit exceeded" in str(error)
        assert "2GB" in str(error)

    @pytest.mark.unit
    def test_resource_error_cpu_limit(self):
        """Test ResourceError for CPU limit."""
        error = ResourceError("CPU limit exceeded: 2.0 cores")
        assert "CPU limit exceeded" in str(error)
        assert "2.0 cores" in str(error)


class TestNetworkError:
    """Test cases for NetworkError."""

    @pytest.mark.unit
    def test_network_error_basic(self):
        """Test basic NetworkError functionality."""
        error = NetworkError("Network connection failed")
        assert str(error) == "Network connection failed"
        assert isinstance(error, GrainchainError)

    @pytest.mark.unit
    def test_network_error_connection_timeout(self):
        """Test NetworkError for connection timeout."""
        error = NetworkError("Connection timeout to provider API")
        assert "Connection timeout" in str(error)
        assert "provider API" in str(error)

    @pytest.mark.unit
    def test_network_error_dns_resolution(self):
        """Test NetworkError for DNS resolution."""
        error = NetworkError("DNS resolution failed for api.example.com")
        assert "DNS resolution failed" in str(error)
        assert "api.example.com" in str(error)


class TestExceptionChaining:
    """Test exception chaining and context."""

    @pytest.mark.unit
    def test_exception_chaining_with_cause(self):
        """Test exception chaining with __cause__."""
        original = ValueError("Original error")

        try:
            raise original
        except ValueError as e:
            try:
                raise SandboxError("Sandbox failed") from e
            except SandboxError as chained:
                assert chained.__cause__ is original

    @pytest.mark.unit
    def test_exception_chaining_with_context(self):
        """Test exception chaining with __context__."""
        try:
            raise ValueError("Original error")
        except ValueError:
            try:
                raise SandboxError("Sandbox failed")
            except SandboxError as e:
                assert isinstance(e.__context__, ValueError)

    @pytest.mark.unit
    def test_provider_error_chaining(self):
        """Test ProviderError with original exception."""
        original = ConnectionError("Network unreachable")
        provider_error = ProviderError("Provider connection failed", "e2b", original)

        assert provider_error.original_error is original
        assert str(provider_error) == "Provider connection failed"


class TestExceptionMessages:
    """Test exception message formatting."""

    @pytest.mark.unit
    def test_detailed_error_messages(self):
        """Test that error messages contain useful information."""
        # Test with detailed context
        error = SandboxError(
            "Command 'python script.py' failed with exit code 1 in sandbox 'test_123'"
        )
        message = str(error)

        assert "python script.py" in message
        assert "exit code 1" in message
        assert "test_123" in message

    @pytest.mark.unit
    def test_configuration_error_messages(self):
        """Test ConfigurationError message formatting."""
        error = ConfigurationError(
            "Required configuration 'api_key' not found for provider 'e2b'"
        )
        message = str(error)

        assert "api_key" in message
        assert "e2b" in message
        assert "Required configuration" in message

    @pytest.mark.unit
    def test_timeout_error_messages(self):
        """Test TimeoutError message formatting."""
        error = GrainchainTimeoutError(
            "Command execution timed out after 30 seconds", 30
        )
        message = str(error)

        assert "timed out" in message
        assert "30 seconds" in message
        assert error.timeout_seconds == 30


class TestExceptionUsagePatterns:
    """Test common exception usage patterns."""

    @pytest.mark.unit
    def test_exception_in_try_except(self):
        """Test exception handling in try-except blocks."""

        def failing_function():
            raise SandboxError("Test failure")

        with pytest.raises(SandboxError, match="Test failure"):
            failing_function()

    @pytest.mark.unit
    def test_exception_inheritance_catching(self):
        """Test catching exceptions by base class."""

        def failing_function():
            raise ProviderError("Provider failed", "test")

        # Should be caught by GrainchainError
        with pytest.raises(GrainchainError):
            failing_function()

    @pytest.mark.unit
    def test_multiple_exception_types(self):
        """Test handling multiple exception types."""

        def maybe_failing_function(error_type):
            if error_type == "sandbox":
                raise SandboxError("Sandbox error")
            elif error_type == "provider":
                raise ProviderError("Provider error", "test")
            elif error_type == "config":
                raise ConfigurationError("Config error")
            else:
                return "success"

        # Test each exception type
        with pytest.raises(SandboxError):
            maybe_failing_function("sandbox")

        with pytest.raises(ProviderError):
            maybe_failing_function("provider")

        with pytest.raises(ConfigurationError):
            maybe_failing_function("config")

        # Test success case
        result = maybe_failing_function("none")
        assert result == "success"

    @pytest.mark.unit
    def test_exception_with_additional_context(self):
        """Test exceptions with additional context information."""
        context = {
            "sandbox_id": "test_123",
            "command": "python script.py",
            "working_dir": "/tmp",
            "timeout": 30,
        }

        error_msg = f"Command '{context['command']}' failed in sandbox '{context['sandbox_id']}'"
        error = SandboxError(error_msg)

        assert context["command"] in str(error)
        assert context["sandbox_id"] in str(error)
