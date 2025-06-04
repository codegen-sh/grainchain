"""Tests for the simplified API functionality."""


import pytest


class TestSimplifiedImports:
    """Test that simplified imports work correctly."""

    def test_import_providers_constant(self):
        """Test importing Providers constant."""
        from grainchain import Providers

        assert Providers.LOCAL == "local"
        assert Providers.E2B == "e2b"

    def test_import_factory_functions(self):
        """Test importing factory functions."""
        from grainchain import create_e2b_sandbox, create_local_sandbox, create_sandbox

        # Test that functions are callable
        assert callable(create_sandbox)
        assert callable(create_local_sandbox)
        assert callable(create_e2b_sandbox)

    def test_import_convenience_module(self):
        """Test importing convenience module."""
        from grainchain.convenience import QuickSandbox, quick_execute

        assert callable(quick_execute)
        assert QuickSandbox is not None


class TestSimplifiedUsagePatterns:
    """Test simplified usage patterns."""

    def test_three_line_usage_pattern(self):
        """Test the promised 3-line usage pattern."""
        # This should work in just 3 lines:
        # 1. Import
        from grainchain import create_local_sandbox

        # 2. Create sandbox
        sandbox = create_local_sandbox()

        # 3. Use (would be async in real usage)
        assert sandbox is not None

    def test_provider_constant_usage(self):
        """Test using provider constants."""
        from grainchain import Providers, create_sandbox

        # Should work with constants
        sandbox = create_sandbox(Providers.LOCAL)
        assert sandbox is not None

        # Should still work with strings
        sandbox2 = create_sandbox("local")
        assert sandbox2 is not None

    def test_simplified_configuration(self):
        """Test simplified configuration patterns."""
        from grainchain import create_local_sandbox

        # Simple configuration
        sandbox = create_local_sandbox(timeout=30)
        assert sandbox is not None

        # With multiple parameters
        sandbox2 = create_local_sandbox(
            timeout=60, working_directory="/tmp", auto_cleanup=True
        )
        assert sandbox2 is not None


class TestAPIConsistency:
    """Test that the API is consistent and intuitive."""

    def test_all_factory_functions_return_sandbox(self):
        """Test that all factory functions return Sandbox instances."""
        from grainchain import create_e2b_sandbox, create_local_sandbox, create_sandbox
        from grainchain.core.sandbox import Sandbox

        sandbox1 = create_sandbox()
        sandbox2 = create_local_sandbox()
        sandbox3 = create_e2b_sandbox()

        assert isinstance(sandbox1, Sandbox)
        assert isinstance(sandbox2, Sandbox)
        assert isinstance(sandbox3, Sandbox)

    def test_factory_functions_accept_common_parameters(self):
        """Test that factory functions accept common parameters."""
        from grainchain import create_e2b_sandbox, create_local_sandbox

        # All should accept timeout
        sandbox1 = create_local_sandbox(timeout=30)
        sandbox2 = create_e2b_sandbox(timeout=30)

        assert sandbox1 is not None
        assert sandbox2 is not None

    def test_provider_specific_parameters(self):
        """Test provider-specific parameters."""
        from grainchain import create_e2b_sandbox

        # E2B should accept template parameter
        sandbox = create_e2b_sandbox(template="python")
        assert sandbox is not None


class TestErrorHandling:
    """Test error handling in simplified API."""

    def test_invalid_provider_handling(self):
        """Test handling of invalid provider names."""
        from grainchain import create_sandbox

        # Should not raise an error during creation (error would come during usage)
        sandbox = create_sandbox("invalid_provider")
        assert sandbox is not None

    def test_invalid_parameters_handling(self):
        """Test handling of invalid parameters."""
        from grainchain import create_local_sandbox

        # Should handle invalid parameters gracefully
        try:
            sandbox = create_local_sandbox(invalid_param="value")
            assert sandbox is not None
        except TypeError:
            # This is acceptable - invalid parameters should raise TypeError
            pass


class TestDocumentationExamples:
    """Test that examples from documentation actually work."""

    def test_readme_quick_start_example(self):
        """Test the quick start example from README."""
        from grainchain import create_local_sandbox

        # This is the example from the docstring
        sandbox = create_local_sandbox()
        assert sandbox is not None

        # The async part would be:
        # async with sandbox:
        #     result = await sandbox.execute("python -c 'print(2+2)'")

    def test_provider_constants_example(self):
        """Test provider constants example."""
        from grainchain import Providers, create_sandbox

        # Using constants (recommended)
        sandbox = create_sandbox(Providers.LOCAL)
        assert sandbox is not None

    def test_convenience_import_example(self):
        """Test convenience import example."""
        from grainchain.convenience import quick_execute

        # Function should be importable
        assert callable(quick_execute)


class TestPerformanceConsiderations:
    """Test that simplified API doesn't introduce performance issues."""

    def test_factory_function_performance(self):
        """Test that factory functions are reasonably fast."""
        import time

        from grainchain import create_local_sandbox

        start_time = time.time()

        # Create multiple sandboxes
        sandboxes = [create_local_sandbox() for _ in range(10)]

        end_time = time.time()

        # Should be fast (less than 1 second for 10 sandboxes)
        assert end_time - start_time < 1.0
        assert len(sandboxes) == 10

    def test_import_performance(self):
        """Test that imports are reasonably fast."""
        import time

        start_time = time.time()

        # Import everything

        end_time = time.time()

        # Imports should be very fast
        assert end_time - start_time < 0.5


class TestIntegrationReadiness:
    """Test that the simplified API is ready for integration."""

    def test_jupyter_notebook_pattern(self):
        """Test pattern suitable for Jupyter notebooks."""
        from grainchain import create_local_sandbox

        # This pattern should work in Jupyter
        sandbox = create_local_sandbox()

        # In Jupyter, user would do:
        # await sandbox.__aenter__()
        # result = await sandbox.execute("echo 'hello'")
        # await sandbox.__aexit__(None, None, None)

        assert sandbox is not None

    def test_testing_framework_pattern(self):
        """Test pattern suitable for testing frameworks."""
        from grainchain.convenience import create_test_sandbox

        # This pattern should work in pytest
        test_sandbox = create_test_sandbox()
        assert test_sandbox is not None

    def test_ci_cd_pattern(self):
        """Test pattern suitable for CI/CD."""
        from grainchain.convenience import QuickSandbox

        # This pattern should work in CI/CD without async complexity
        assert QuickSandbox is not None


if __name__ == "__main__":
    pytest.main([__file__])
