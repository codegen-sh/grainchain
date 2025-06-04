"""Tests for CLI exceptions."""

from unittest.mock import patch

from grainchain.cli.exceptions import (
    BenchmarkError,
    CliError,
    DependencyError,
    ProviderError,
    ValidationError,
    handle_cli_error,
)


class TestCliError:
    """Test base CLI error."""

    def test_basic_error(self):
        error = CliError("Test message")
        assert str(error) == "Test message"
        assert error.message == "Test message"
        assert error.suggestion is None
        assert error.exit_code == 1

    def test_error_with_suggestion(self):
        error = CliError("Test message", "Try this fix", 2)
        assert error.suggestion == "Try this fix"
        assert error.exit_code == 2


class TestDependencyError:
    """Test dependency error."""

    def test_basic_dependency_error(self):
        error = DependencyError("docker")
        assert "docker is required but not available" in str(error)
        assert error.exit_code == 127

    def test_dependency_error_with_install(self):
        error = DependencyError("docker", "apt install docker")
        assert error.suggestion is not None
        assert "apt install docker" in error.suggestion

    def test_dependency_error_with_docs(self):
        error = DependencyError("docker", docs_url="https://docs.docker.com")
        assert error.suggestion is not None
        assert "https://docs.docker.com" in error.suggestion


class TestProviderError:
    """Test provider error."""

    def test_local_provider_error(self):
        error = ProviderError("local", "connection")
        assert "local provider failed during connection" in str(error)
        assert "Docker" in error.suggestion

    def test_e2b_provider_error(self):
        error = ProviderError("e2b", "authentication")
        assert "e2b provider failed during authentication" in str(error)
        assert "API key" in error.suggestion

    def test_provider_error_with_original(self):
        error = ProviderError("test", "operation", "Connection timeout")
        assert "Connection timeout" in str(error)


class TestBenchmarkError:
    """Test benchmark error."""

    def test_basic_benchmark_error(self):
        error = BenchmarkError("test_name", "local")
        assert "test_name" in str(error)
        assert "local provider" in str(error)
        assert "--verbose" in error.suggestion

    def test_benchmark_error_with_details(self):
        error = BenchmarkError("test_name", "local", "Timeout occurred")
        assert "Timeout occurred" in str(error)


class TestValidationError:
    """Test validation error."""

    def test_validation_error(self):
        error = ValidationError("provider", "invalid", "local|e2b|daytona")
        assert "Invalid provider: 'invalid'" in str(error)
        assert "local|e2b|daytona" in error.suggestion
        assert error.exit_code == 2


class TestHandleCliError:
    """Test error handling."""

    @patch("grainchain.cli.utils.error")
    @patch("grainchain.cli.utils.info")
    @patch("sys.exit")
    def test_handle_cli_error(self, mock_exit, mock_info, mock_print_error):
        error = CliError("Test error", "Test suggestion", 42)

        handle_cli_error(error)

        mock_print_error.assert_called_once_with("Test error")
        mock_info.assert_called_once_with("💡 Test suggestion")
        mock_exit.assert_called_once_with(42)

    @patch("grainchain.cli.utils.error")
    @patch("sys.exit")
    def test_handle_generic_error(self, mock_exit, mock_print_error):
        error = ValueError("Generic error")

        handle_cli_error(error)

        mock_print_error.assert_called_once_with("Unexpected error: Generic error")
        mock_exit.assert_called_once_with(1)

    @patch("grainchain.cli.utils.error")
    @patch("grainchain.cli.utils.verbose_echo")
    @patch("sys.exit")
    def test_handle_error_verbose(self, mock_exit, mock_verbose, mock_print_error):
        error = CliError("Test error")

        handle_cli_error(error, verbose=True)

        mock_print_error.assert_called_once()
        # verbose_echo should be called for underlying error if it exists
        mock_exit.assert_called_once_with(1)
