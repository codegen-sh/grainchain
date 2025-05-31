"""Tests for CLI functionality."""

import subprocess
import sys
from unittest.mock import patch


def test_cli_help():
    """Test that the CLI help command works."""
    result = subprocess.run(
        [sys.executable, "-m", "grainchain.cli.main", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Grainchain CLI" in result.stdout


def test_cli_version():
    """Test that the CLI version command works."""
    result = subprocess.run(
        [sys.executable, "-m", "grainchain.cli.main", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


@patch("subprocess.run")
def test_lint_command(mock_run):
    """Test the lint command."""
    from click.testing import CliRunner

    from grainchain.cli.main import main

    mock_run.return_value.returncode = 0

    runner = CliRunner()
    result = runner.invoke(main, ["lint", "."])

    assert result.exit_code == 0
    mock_run.assert_called_once()


@patch("subprocess.run")
def test_format_command(mock_run):
    """Test the format command."""
    from click.testing import CliRunner

    from grainchain.cli.main import main

    mock_run.return_value.returncode = 0

    runner = CliRunner()
    result = runner.invoke(main, ["format", "."])

    assert result.exit_code == 0
    assert mock_run.call_count == 2  # ruff check --fix, ruff format


def test_basic_import():
    """Test that basic imports work."""
    import grainchain
    import grainchain.cli.benchmark
    import grainchain.cli.main

    assert grainchain is not None
