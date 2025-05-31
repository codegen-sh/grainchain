"""
Unit tests for Grainchain exception classes.

Tests all custom exception types and their behavior.
"""

import pytest

from grainchain.core.exceptions import (
    GrainchainError,
    SandboxError,
    ProviderError,
    ConfigurationError,
    TimeoutError,
    AuthenticationError,
    ResourceError,
    NetworkError
)


class TestGrainchainError:
    """Test cases for the base GrainchainError."""
    
    def test_grainchain_error_creation(self):
        """Test creating a GrainchainError."""
        error = GrainchainError("Test error message")
        
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
    
    def test_grainchain_error_inheritance(self):
        """Test that GrainchainError inherits from Exception."""
        error = GrainchainError("Test")
        
        assert isinstance(error, Exception)
        assert isinstance(error, GrainchainError)
    
    def test_grainchain_error_with_no_message(self):
        """Test creating GrainchainError with no message."""
        error = GrainchainError()
        
        assert str(error) == ""
    
    def test_grainchain_error_with_args(self):
        """Test creating GrainchainError with multiple arguments."""
        error = GrainchainError("Message", 123, "extra")
        
        assert error.args == ("Message", 123, "extra")
        assert str(error) == "Message"


class TestSandboxError:
    """Test cases for SandboxError."""
    
    def test_sandbox_error_creation(self):
        """Test creating a SandboxError."""
        error = SandboxError("Sandbox operation failed")
        
        assert str(error) == "Sandbox operation failed"
        assert isinstance(error, GrainchainError)
        assert isinstance(error, SandboxError)
    
    def test_sandbox_error_inheritance(self):
        """Test SandboxError inheritance chain."""
        error = SandboxError("Test")
        
        assert isinstance(error, Exception)
        assert isinstance(error, GrainchainError)
        assert isinstance(error, SandboxError)
    
    def test_sandbox_error_with_details(self):
        """Test SandboxError with additional details."""
        error = SandboxError("Command execution failed", "exit_code", 1)
        
        assert "Command execution failed" in str(error)
        assert error.args == ("Command execution failed", "exit_code", 1)


class TestProviderError:
    """Test cases for ProviderError."""
    
    def test_provider_error_creation(self):
        """Test creating a ProviderError."""
        error = ProviderError("E2B", "API request failed")
        
        assert str(error) == "E2B: API request failed"
        assert isinstance(error, GrainchainError)
        assert isinstance(error, ProviderError)
    
    def test_provider_error_inheritance(self):
        """Test ProviderError inheritance chain."""
        error = ProviderError("Modal", "Connection failed")
        
        assert isinstance(error, Exception)
        assert isinstance(error, GrainchainError)
        assert isinstance(error, ProviderError)
    
    def test_provider_error_properties(self):
        """Test ProviderError properties."""
        error = ProviderError("TestProvider", "Test message")
        
        assert error.provider == "TestProvider"
        assert error.message == "Test message"
    
    def test_provider_error_with_none_provider(self):
        """Test ProviderError with None provider."""
        error = ProviderError(None, "Test message")
        
        assert str(error) == "Unknown Provider: Test message"
        assert error.provider is None
    
    def test_provider_error_with_empty_message(self):
        """Test ProviderError with empty message."""
        error = ProviderError("TestProvider", "")
        
        assert str(error) == "TestProvider: "
        assert error.message == ""


class TestConfigurationError:
    """Test cases for ConfigurationError."""
    
    def test_configuration_error_creation(self):
        """Test creating a ConfigurationError."""
        error = ConfigurationError("Invalid configuration file")
        
        assert str(error) == "Invalid configuration file"
        assert isinstance(error, GrainchainError)
        assert isinstance(error, ConfigurationError)
    
    def test_configuration_error_inheritance(self):
        """Test ConfigurationError inheritance chain."""
        error = ConfigurationError("Test")
        
        assert isinstance(error, Exception)
        assert isinstance(error, GrainchainError)
        assert isinstance(error, ConfigurationError)
    
    def test_configuration_error_with_file_path(self):
        """Test ConfigurationError with file path information."""
        error = ConfigurationError("Parse error in /path/to/config.yaml")
        
        assert "config.yaml" in str(error)


class TestTimeoutError:
    """Test cases for TimeoutError."""
    
    def test_timeout_error_creation(self):
        """Test creating a TimeoutError."""
        error = TimeoutError("Command", 30)
        
        assert str(error) == "Operation 'Command' timed out after 30 seconds"
        assert isinstance(error, GrainchainError)
        assert isinstance(error, TimeoutError)
    
    def test_timeout_error_inheritance(self):
        """Test TimeoutError inheritance chain."""
        error = TimeoutError("Test", 10)
        
        assert isinstance(error, Exception)
        assert isinstance(error, GrainchainError)
        assert isinstance(error, TimeoutError)
    
    def test_timeout_error_properties(self):
        """Test TimeoutError properties."""
        error = TimeoutError("TestOperation", 60)
        
        assert error.operation == "TestOperation"
        assert error.timeout == 60
    
    def test_timeout_error_with_float_timeout(self):
        """Test TimeoutError with float timeout."""
        error = TimeoutError("Operation", 30.5)
        
        assert str(error) == "Operation 'Operation' timed out after 30.5 seconds"
        assert error.timeout == 30.5
    
    def test_timeout_error_with_zero_timeout(self):
        """Test TimeoutError with zero timeout."""
        error = TimeoutError("Operation", 0)
        
        assert str(error) == "Operation 'Operation' timed out after 0 seconds"
        assert error.timeout == 0


class TestAuthenticationError:
    """Test cases for AuthenticationError."""
    
    def test_authentication_error_creation(self):
        """Test creating an AuthenticationError."""
        error = AuthenticationError("E2B", "Invalid API key")
        
        assert str(error) == "Authentication failed for E2B: Invalid API key"
        assert isinstance(error, GrainchainError)
        assert isinstance(error, AuthenticationError)
    
    def test_authentication_error_inheritance(self):
        """Test AuthenticationError inheritance chain."""
        error = AuthenticationError("Modal", "Invalid token")
        
        assert isinstance(error, Exception)
        assert isinstance(error, GrainchainError)
        assert isinstance(error, AuthenticationError)
    
    def test_authentication_error_properties(self):
        """Test AuthenticationError properties."""
        error = AuthenticationError("TestProvider", "Test reason")
        
        assert error.provider == "TestProvider"
        assert error.reason == "Test reason"
    
    def test_authentication_error_with_none_provider(self):
        """Test AuthenticationError with None provider."""
        error = AuthenticationError(None, "No credentials")
        
        assert str(error) == "Authentication failed for Unknown: No credentials"
        assert error.provider is None
    
    def test_authentication_error_with_empty_reason(self):
        """Test AuthenticationError with empty reason."""
        error = AuthenticationError("Provider", "")
        
        assert str(error) == "Authentication failed for Provider: "
        assert error.reason == ""


class TestResourceError:
    """Test cases for ResourceError."""
    
    def test_resource_error_creation(self):
        """Test creating a ResourceError."""
        error = ResourceError("Insufficient memory available")
        
        assert str(error) == "Insufficient memory available"
        assert isinstance(error, GrainchainError)
        assert isinstance(error, ResourceError)
    
    def test_resource_error_inheritance(self):
        """Test ResourceError inheritance chain."""
        error = ResourceError("Test")
        
        assert isinstance(error, Exception)
        assert isinstance(error, GrainchainError)
        assert isinstance(error, ResourceError)
    
    def test_resource_error_with_resource_type(self):
        """Test ResourceError with resource type information."""
        error = ResourceError("CPU limit exceeded: 2.0 cores")
        
        assert "CPU limit exceeded" in str(error)
        assert "2.0 cores" in str(error)


class TestNetworkError:
    """Test cases for NetworkError."""
    
    def test_network_error_creation(self):
        """Test creating a NetworkError."""
        error = NetworkError("Connection refused")
        
        assert str(error) == "Connection refused"
        assert isinstance(error, GrainchainError)
        assert isinstance(error, NetworkError)
    
    def test_network_error_inheritance(self):
        """Test NetworkError inheritance chain."""
        error = NetworkError("Test")
        
        assert isinstance(error, Exception)
        assert isinstance(error, GrainchainError)
        assert isinstance(error, NetworkError)
    
    def test_network_error_with_url(self):
        """Test NetworkError with URL information."""
        error = NetworkError("Failed to connect to https://api.example.com")
        
        assert "api.example.com" in str(error)


class TestExceptionChaining:
    """Test cases for exception chaining and context."""
    
    def test_exception_chaining_with_cause(self):
        """Test exception chaining with explicit cause."""
        original_error = ValueError("Original error")
        
        try:
            raise SandboxError("Sandbox failed") from original_error
        except SandboxError as e:
            assert e.__cause__ is original_error
            assert isinstance(e.__cause__, ValueError)
    
    def test_exception_chaining_with_context(self):
        """Test exception chaining with implicit context."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError:
                raise ProviderError("Provider", "Provider failed")
        except ProviderError as e:
            assert isinstance(e.__context__, ValueError)
            assert str(e.__context__) == "Original error"
    
    def test_nested_grainchain_exceptions(self):
        """Test nesting Grainchain exceptions."""
        try:
            try:
                raise AuthenticationError("E2B", "Invalid key")
            except AuthenticationError:
                raise ProviderError("E2B", "Provider initialization failed")
        except ProviderError as e:
            assert isinstance(e.__context__, AuthenticationError)
            assert e.__context__.provider == "E2B"


class TestExceptionUsagePatterns:
    """Test cases for common exception usage patterns."""
    
    def test_catching_base_exception(self):
        """Test catching all Grainchain exceptions with base class."""
        exceptions_to_test = [
            SandboxError("test"),
            ProviderError("provider", "test"),
            ConfigurationError("test"),
            TimeoutError("op", 30),
            AuthenticationError("provider", "test"),
            ResourceError("test"),
            NetworkError("test")
        ]
        
        for exception in exceptions_to_test:
            try:
                raise exception
            except GrainchainError as e:
                assert isinstance(e, GrainchainError)
                assert isinstance(e, type(exception))
    
    def test_exception_with_additional_context(self):
        """Test exceptions with additional context information."""
        # Test with dictionary context
        context = {"sandbox_id": "sb_123", "command": "pip install numpy"}
        error = SandboxError("Command failed", context)
        
        assert error.args[0] == "Command failed"
        assert error.args[1] == context
    
    def test_exception_string_representation(self):
        """Test string representations of exceptions."""
        exceptions_and_expected = [
            (GrainchainError("base error"), "base error"),
            (SandboxError("sandbox error"), "sandbox error"),
            (ProviderError("E2B", "provider error"), "E2B: provider error"),
            (ConfigurationError("config error"), "config error"),
            (TimeoutError("operation", 30), "Operation 'operation' timed out after 30 seconds"),
            (AuthenticationError("Modal", "auth error"), "Authentication failed for Modal: auth error"),
            (ResourceError("resource error"), "resource error"),
            (NetworkError("network error"), "network error")
        ]
        
        for exception, expected in exceptions_and_expected:
            assert str(exception) == expected
    
    def test_exception_equality(self):
        """Test exception equality comparison."""
        error1 = SandboxError("test message")
        error2 = SandboxError("test message")
        error3 = SandboxError("different message")
        error4 = ProviderError("provider", "test message")
        
        # Same type and message should be equal
        assert str(error1) == str(error2)
        
        # Different messages should not be equal
        assert str(error1) != str(error3)
        
        # Different types should not be equal
        assert str(error1) != str(error4)
    
    def test_exception_with_none_values(self):
        """Test exceptions with None values."""
        # Test exceptions that handle None gracefully
        provider_error = ProviderError(None, None)
        assert "Unknown Provider" in str(provider_error)
        
        auth_error = AuthenticationError(None, None)
        assert "Unknown" in str(auth_error)
        
        timeout_error = TimeoutError(None, None)
        assert "None" in str(timeout_error)

