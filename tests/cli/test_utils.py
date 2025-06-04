"""Tests for CLI utilities."""

import subprocess
from unittest.mock import MagicMock, patch

from grainchain.cli.utils import (
    check_dependency,
    format_duration,
    format_table,
)


class TestFormatDuration:
    """Test duration formatting."""

    def test_milliseconds(self):
        assert format_duration(0.5) == "500ms"
        assert format_duration(0.123) == "123ms"

    def test_seconds(self):
        assert format_duration(1.5) == "1.50s"
        assert format_duration(30.25) == "30.25s"

    def test_minutes(self):
        assert format_duration(60) == "1m 0.0s"
        assert format_duration(90.5) == "1m 30.5s"
        assert format_duration(125.75) == "2m 5.8s"


class TestFormatTable:
    """Test table formatting."""

    def test_empty_table(self):
        result = format_table(["A", "B"], [])
        assert result == "No data to display"

    def test_simple_table(self):
        headers = ["Name", "Status"]
        rows = [["Test1", "PASS"], ["Test2", "FAIL"]]
        result = format_table(headers, rows)

        lines = result.split("\n")
        # Check that headers are present
        assert any("Name" in line and "Status" in line for line in lines)
        assert "Test1" in result and "PASS" in result
        assert "Test2" in result and "FAIL" in result

    def test_table_with_title(self):
        headers = ["Col1", "Col2"]
        rows = [["A", "B"]]
        result = format_table(headers, rows, title="Test Table")

        assert "Test Table" in result
        assert any("Col1" in line and "Col2" in line for line in result.split("\n"))


class TestCheckDependency:
    """Test dependency checking."""

    @patch("subprocess.run")
    def test_dependency_available(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)

        result = check_dependency("docker", "Docker")
        assert result is True
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_dependency_not_available(self, mock_run):
        mock_run.side_effect = FileNotFoundError()

        result = check_dependency("nonexistent", "NonExistent")
        assert result is False

    @patch("subprocess.run")
    def test_dependency_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 5)

        result = check_dependency("slow-cmd", "SlowCommand")
        assert result is False
