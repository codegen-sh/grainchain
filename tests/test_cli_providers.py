"""Tests for the CLI providers command."""

from unittest.mock import Mock, patch

from click.testing import CliRunner

from grainchain.cli.main import main
from grainchain.core.providers_info import ProviderInfo


class TestProvidersCommand:
    """Test the providers CLI command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_providers_command_basic(self):
        """Test basic providers command."""
        # Mock provider discovery at the module level where it's imported
        with patch("grainchain.cli.main.ProviderDiscovery") as mock_discovery_class:
            # Mock provider discovery
            mock_discovery = Mock()
            mock_config = Mock()
            mock_config.default_provider = "local"
            mock_discovery.config_manager = mock_config

            mock_providers = {
                "local": ProviderInfo(
                    name="local",
                    available=True,
                    dependencies_installed=True,
                    configured=True,
                    missing_config=[],
                ),
                "e2b": ProviderInfo(
                    name="e2b",
                    available=False,
                    dependencies_installed=False,
                    configured=False,
                    missing_config=["E2B_API_KEY"],
                    install_command="pip install grainchain[e2b]",
                ),
            }

            mock_discovery.get_all_providers_info.return_value = mock_providers
            mock_discovery_class.return_value = mock_discovery

            result = self.runner.invoke(main, ["providers"])

            assert result.exit_code == 0
            assert "Grainchain Sandbox Providers" in result.output
            assert "LOCAL" in result.output
            assert "E2B" in result.output
            assert "Default provider: local" in result.output
            assert (
                "2/2 providers available" in result.output
                or "1/2 providers available" in result.output
            )

    @patch("grainchain.cli.main.ProviderDiscovery")
    def test_providers_command_verbose(self, mock_discovery_class):
        """Test providers command with verbose flag."""
        mock_discovery = Mock()
        mock_config = Mock()
        mock_config.default_provider = "local"
        mock_discovery.config_manager = mock_config

        mock_providers = {
            "local": ProviderInfo(
                name="local",
                available=True,
                dependencies_installed=True,
                configured=True,
                missing_config=[],
            )
        }

        mock_discovery.get_all_providers_info.return_value = mock_providers
        mock_discovery_class.return_value = mock_discovery

        result = self.runner.invoke(main, ["providers", "--verbose"])

        assert result.exit_code == 0
        assert "Dependencies:" in result.output
        assert "Configuration:" in result.output

    @patch("grainchain.cli.main.ProviderDiscovery")
    def test_providers_command_check_specific(self, mock_discovery_class):
        """Test providers command checking specific provider."""
        mock_discovery = Mock()

        mock_info = ProviderInfo(
            name="e2b",
            available=False,
            dependencies_installed=True,
            configured=False,
            missing_config=["E2B_API_KEY"],
            config_instructions=[
                "Set the following environment variables:",
                "  export E2B_API_KEY='your-key'",
            ],
        )

        mock_discovery.get_provider_info.return_value = mock_info
        mock_discovery_class.return_value = mock_discovery

        result = self.runner.invoke(main, ["providers", "--check", "e2b"])

        assert result.exit_code == 0
        assert "E2B" in result.output
        assert "Missing: E2B_API_KEY" in result.output
        assert "Setup:" in result.output

    @patch("grainchain.cli.main.ProviderDiscovery")
    def test_providers_command_available_only(self, mock_discovery_class):
        """Test providers command with available-only flag."""
        mock_discovery = Mock()
        mock_config = Mock()
        mock_config.default_provider = "local"
        mock_discovery.config_manager = mock_config

        mock_providers = {
            "local": ProviderInfo(
                name="local",
                available=True,
                dependencies_installed=True,
                configured=True,
                missing_config=[],
            ),
            "e2b": ProviderInfo(
                name="e2b",
                available=False,
                dependencies_installed=False,
                configured=False,
                missing_config=["E2B_API_KEY"],
            ),
        }

        mock_discovery.get_all_providers_info.return_value = mock_providers
        mock_discovery_class.return_value = mock_discovery

        result = self.runner.invoke(main, ["providers", "--available-only"])

        assert result.exit_code == 0
        assert "LOCAL" in result.output
        assert "E2B" not in result.output

    @patch("grainchain.cli.main.ProviderDiscovery")
    def test_providers_command_no_available(self, mock_discovery_class):
        """Test providers command when no providers are available."""
        mock_discovery = Mock()
        mock_config = Mock()
        mock_config.default_provider = "e2b"
        mock_discovery.config_manager = mock_config

        mock_providers = {
            "e2b": ProviderInfo(
                name="e2b",
                available=False,
                dependencies_installed=False,
                configured=False,
                missing_config=["E2B_API_KEY"],
            )
        }

        mock_discovery.get_all_providers_info.return_value = mock_providers
        mock_discovery_class.return_value = mock_discovery

        result = self.runner.invoke(main, ["providers", "--available-only"])

        assert result.exit_code == 0
        assert "No providers are currently available" in result.output

    @patch("grainchain.cli.main.ProviderDiscovery")
    def test_providers_command_import_error(self, mock_discovery_class):
        """Test providers command with import error."""
        mock_discovery_class.side_effect = ImportError(
            "Cannot import ProviderDiscovery"
        )

        result = self.runner.invoke(main, ["providers"])

        assert result.exit_code == 1
        assert "Error importing provider discovery" in result.output

    @patch("grainchain.cli.main.ProviderDiscovery")
    def test_providers_command_general_error(self, mock_discovery_class):
        """Test providers command with general error."""
        mock_discovery = Mock()
        mock_discovery.get_all_providers_info.side_effect = Exception("General error")
        mock_discovery_class.return_value = mock_discovery

        result = self.runner.invoke(main, ["providers"])

        assert result.exit_code == 1
        assert "Error checking providers" in result.output


class TestDisplayProviderInfo:
    """Test the _display_provider_info helper function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("grainchain.cli.main.ProviderDiscovery")
    def test_display_available_provider(self, mock_discovery_class):
        """Test displaying an available provider."""
        mock_discovery = Mock()
        mock_config = Mock()
        mock_config.default_provider = "local"
        mock_discovery.config_manager = mock_config

        mock_providers = {
            "local": ProviderInfo(
                name="local",
                available=True,
                dependencies_installed=True,
                configured=True,
                missing_config=[],
            )
        }

        mock_discovery.get_all_providers_info.return_value = mock_providers
        mock_discovery_class.return_value = mock_discovery

        result = self.runner.invoke(main, ["providers"])

        assert result.exit_code == 0
        assert "✅ LOCAL" in result.output

    @patch("grainchain.cli.main.ProviderDiscovery")
    def test_display_missing_deps_provider(self, mock_discovery_class):
        """Test displaying a provider with missing dependencies."""
        mock_discovery = Mock()
        mock_config = Mock()
        mock_config.default_provider = "e2b"
        mock_discovery.config_manager = mock_config

        mock_providers = {
            "e2b": ProviderInfo(
                name="e2b",
                available=False,
                dependencies_installed=False,
                configured=False,
                missing_config=["E2B_API_KEY"],
                install_command="pip install grainchain[e2b]",
            )
        }

        mock_discovery.get_all_providers_info.return_value = mock_providers
        mock_discovery_class.return_value = mock_discovery

        result = self.runner.invoke(main, ["providers"])

        assert result.exit_code == 0
        assert "❌ E2B" in result.output
        assert "Install: pip install grainchain[e2b]" in result.output

    @patch("grainchain.cli.main.ProviderDiscovery")
    def test_display_needs_config_provider(self, mock_discovery_class):
        """Test displaying a provider that needs configuration."""
        mock_discovery = Mock()
        mock_config = Mock()
        mock_config.default_provider = "e2b"
        mock_discovery.config_manager = mock_config

        mock_providers = {
            "e2b": ProviderInfo(
                name="e2b",
                available=False,
                dependencies_installed=True,
                configured=False,
                missing_config=["E2B_API_KEY"],
                config_instructions=[
                    "Set the following environment variables:",
                    "  export E2B_API_KEY='your-key'",
                ],
            )
        }

        mock_discovery.get_all_providers_info.return_value = mock_providers
        mock_discovery_class.return_value = mock_discovery

        result = self.runner.invoke(main, ["providers"])

        assert result.exit_code == 0
        assert "⚠️ E2B" in result.output
        assert "Missing: E2B_API_KEY" in result.output
        assert "Setup:" in result.output
