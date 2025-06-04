"""Tests for convenience functions and simplified API."""

from unittest.mock import MagicMock, patch

import pytest

from grainchain import (
    Providers,
    create_e2b_sandbox,
    create_local_sandbox,
    create_sandbox,
)
from grainchain.convenience import (
    ConfigPresets,
    QuickSandbox,
    create_data_sandbox,
    create_dev_sandbox,
    create_test_sandbox,
    quick_execute,
    quick_python,
    quick_script,
)
from grainchain.core.sandbox import Sandbox


class TestProviderConstants:
    """Test provider constants."""

    def test_provider_constants_exist(self):
        """Test that all expected provider constants exist."""
        assert hasattr(Providers, "LOCAL")
        assert hasattr(Providers, "E2B")
        assert hasattr(Providers, "DAYTONA")
        assert hasattr(Providers, "MORPH")
        assert hasattr(Providers, "MODAL")

    def test_provider_constant_values(self):
        """Test that provider constants have expected values."""
        assert Providers.LOCAL == "local"
        assert Providers.E2B == "e2b"
        assert Providers.DAYTONA == "daytona"
        assert Providers.MORPH == "morph"
        assert Providers.MODAL == "modal"


class TestFactoryFunctions:
    """Test convenience factory functions."""

    def test_create_local_sandbox_defaults(self):
        """Test create_local_sandbox with default parameters."""
        sandbox = create_local_sandbox()

        assert isinstance(sandbox, Sandbox)
        # Note: We can't easily test the internal config without accessing private attributes
        # In a real test, you might want to add a method to expose config for testing

    def test_create_local_sandbox_custom_params(self):
        """Test create_local_sandbox with custom parameters."""
        sandbox = create_local_sandbox(timeout=30, working_directory="/tmp")

        assert isinstance(sandbox, Sandbox)

    def test_create_e2b_sandbox_defaults(self):
        """Test create_e2b_sandbox with default parameters."""
        sandbox = create_e2b_sandbox()

        assert isinstance(sandbox, Sandbox)

    def test_create_e2b_sandbox_custom_template(self):
        """Test create_e2b_sandbox with custom template."""
        sandbox = create_e2b_sandbox(template="python", timeout=120)

        assert isinstance(sandbox, Sandbox)

    def test_create_sandbox_with_provider_constant(self):
        """Test create_sandbox using provider constants."""
        sandbox = create_sandbox(Providers.LOCAL)

        assert isinstance(sandbox, Sandbox)

    def test_create_sandbox_with_provider_string(self):
        """Test create_sandbox using provider string."""
        sandbox = create_sandbox("local")

        assert isinstance(sandbox, Sandbox)

    def test_create_sandbox_with_kwargs(self):
        """Test create_sandbox with additional kwargs."""
        sandbox = create_sandbox("local", timeout=45, auto_cleanup=False)

        assert isinstance(sandbox, Sandbox)


class TestConfigPresets:
    """Test configuration presets."""

    def test_development_preset(self):
        """Test development configuration preset."""
        config = ConfigPresets.development()

        assert isinstance(config, dict)
        assert config["timeout"] == 300
        assert config["auto_cleanup"] is True
        assert config["environment_vars"]["ENV"] == "development"

    def test_testing_preset(self):
        """Test testing configuration preset."""
        config = ConfigPresets.testing()

        assert isinstance(config, dict)
        assert config["timeout"] == 60
        assert config["auto_cleanup"] is True
        assert config["environment_vars"]["ENV"] == "testing"

    def test_production_preset(self):
        """Test production configuration preset."""
        config = ConfigPresets.production()

        assert isinstance(config, dict)
        assert config["timeout"] == 30
        assert config["auto_cleanup"] is True
        assert config["environment_vars"]["ENV"] == "production"

    def test_data_science_preset(self):
        """Test data science configuration preset."""
        config = ConfigPresets.data_science()

        assert isinstance(config, dict)
        assert config["timeout"] == 600
        assert config["auto_cleanup"] is False
        assert config["environment_vars"]["ENV"] == "data_science"


class TestPresetSandboxes:
    """Test preset sandbox creation functions."""

    def test_create_dev_sandbox(self):
        """Test create_dev_sandbox function."""
        sandbox = create_dev_sandbox()

        assert isinstance(sandbox, Sandbox)

    def test_create_test_sandbox(self):
        """Test create_test_sandbox function."""
        sandbox = create_test_sandbox()

        assert isinstance(sandbox, Sandbox)

    def test_create_data_sandbox(self):
        """Test create_data_sandbox function."""
        sandbox = create_data_sandbox()

        assert isinstance(sandbox, Sandbox)

    def test_preset_sandboxes_with_different_providers(self):
        """Test preset sandboxes with different providers."""
        dev_sandbox = create_dev_sandbox(provider="local")
        test_sandbox = create_test_sandbox(provider="local")
        data_sandbox = create_data_sandbox(provider="local")

        assert isinstance(dev_sandbox, Sandbox)
        assert isinstance(test_sandbox, Sandbox)
        assert isinstance(data_sandbox, Sandbox)


class TestQuickSandbox:
    """Test QuickSandbox synchronous wrapper."""

    @patch("asyncio.new_event_loop")
    @patch("asyncio.set_event_loop")
    def test_quick_sandbox_init(self, mock_set_loop, mock_new_loop):
        """Test QuickSandbox initialization."""
        mock_loop = MagicMock()
        mock_new_loop.return_value = mock_loop

        quick_sandbox = QuickSandbox()

        assert quick_sandbox.provider == "local"
        assert quick_sandbox.config_kwargs == {}

    @patch("asyncio.new_event_loop")
    @patch("asyncio.set_event_loop")
    def test_quick_sandbox_with_custom_params(self, mock_set_loop, mock_new_loop):
        """Test QuickSandbox with custom parameters."""
        mock_loop = MagicMock()
        mock_new_loop.return_value = mock_loop

        quick_sandbox = QuickSandbox(provider="e2b", timeout=30)

        assert quick_sandbox.provider == "e2b"
        assert quick_sandbox.config_kwargs == {"timeout": 30}


class TestQuickFunctions:
    """Test quick execution functions."""

    @patch("grainchain.convenience.QuickSandbox")
    def test_quick_execute(self, mock_quick_sandbox):
        """Test quick_execute function."""
        # Setup mock
        mock_sandbox_instance = MagicMock()
        mock_result = MagicMock()
        mock_sandbox_instance.execute.return_value = mock_result
        mock_quick_sandbox.return_value.__enter__.return_value = mock_sandbox_instance

        # Test
        result = quick_execute("echo 'test'")

        # Verify
        mock_quick_sandbox.assert_called_once_with(provider="local")
        mock_sandbox_instance.execute.assert_called_once_with("echo 'test'")
        assert result == mock_result

    @patch("grainchain.convenience.QuickSandbox")
    def test_quick_python(self, mock_quick_sandbox):
        """Test quick_python function."""
        # Setup mock
        mock_sandbox_instance = MagicMock()
        mock_result = MagicMock()
        mock_sandbox_instance.execute.return_value = mock_result
        mock_quick_sandbox.return_value.__enter__.return_value = mock_sandbox_instance

        # Test
        result = quick_python("print('hello')")

        # Verify
        mock_quick_sandbox.assert_called_once_with(provider="local")
        mock_sandbox_instance.execute.assert_called_once_with(
            "python3 -c 'print('hello')'"
        )
        assert result == mock_result

    @patch("grainchain.convenience.QuickSandbox")
    def test_quick_script(self, mock_quick_sandbox):
        """Test quick_script function."""
        # Setup mock
        mock_sandbox_instance = MagicMock()
        mock_result = MagicMock()
        mock_sandbox_instance.execute.return_value = mock_result
        mock_quick_sandbox.return_value.__enter__.return_value = mock_sandbox_instance

        # Test
        script_content = "print('hello from script')"
        result = quick_script(script_content, "test.py")

        # Verify
        mock_quick_sandbox.assert_called_once_with(provider="local")
        mock_sandbox_instance.upload_file.assert_called_once_with(
            "test.py", script_content
        )
        mock_sandbox_instance.execute.assert_called_once_with("python3 test.py")
        assert result == mock_result

    @patch("grainchain.convenience.QuickSandbox")
    def test_quick_script_non_python(self, mock_quick_sandbox):
        """Test quick_script function with non-Python file."""
        # Setup mock
        mock_sandbox_instance = MagicMock()
        mock_result = MagicMock()
        mock_sandbox_instance.execute.return_value = mock_result
        mock_quick_sandbox.return_value.__enter__.return_value = mock_sandbox_instance

        # Test
        script_content = "echo 'hello from shell'"
        result = quick_script(script_content, "test.sh")

        # Verify
        mock_quick_sandbox.assert_called_once_with(provider="local")
        mock_sandbox_instance.upload_file.assert_called_once_with(
            "test.sh", script_content
        )
        mock_sandbox_instance.execute.assert_called_once_with("./test.sh")
        assert result == mock_result


class TestBackwardCompatibility:
    """Test that existing API still works."""

    def test_original_import_still_works(self):
        """Test that original import pattern still works."""
        from grainchain import Sandbox, SandboxConfig

        config = SandboxConfig(timeout=60)
        sandbox = Sandbox(provider="local", config=config)

        assert isinstance(sandbox, Sandbox)

    def test_original_usage_pattern_still_works(self):
        """Test that original usage pattern still works."""
        from grainchain.core.config import SandboxConfig
        from grainchain.core.sandbox import Sandbox

        config = SandboxConfig(timeout=60, working_directory=".")
        sandbox = Sandbox(provider="local", config=config)

        assert isinstance(sandbox, Sandbox)


if __name__ == "__main__":
    pytest.main([__file__])
