"""Unit tests for core interfaces and data structures."""

from datetime import datetime

import pytest

from grainchain.core.interfaces import (
    ExecutionResult,
    FileInfo,
    SandboxConfig,
    SandboxStatus,
)


class TestExecutionResult:
    """Test cases for ExecutionResult."""

    @pytest.mark.unit
    def test_execution_result_basic(self):
        """Test basic ExecutionResult creation."""
        result = ExecutionResult(
            command="echo 'hello'",
            return_code=0,
            stdout="hello\n",
            stderr="",
            execution_time=0.1,
        )

        assert result.command == "echo 'hello'"
        assert result.return_code == 0
        assert result.stdout == "hello\n"
        assert result.stderr == ""
        assert result.execution_time == 0.1

    @pytest.mark.unit
    def test_execution_result_with_error(self):
        """Test ExecutionResult with error output."""
        result = ExecutionResult(
            command="exit 1",
            return_code=1,
            stdout="",
            stderr="Command failed\n",
            execution_time=0.05,
        )

        assert result.command == "exit 1"
        assert result.return_code == 1
        assert result.stdout == ""
        assert result.stderr == "Command failed\n"
        assert result.execution_time == 0.05

    @pytest.mark.unit
    def test_execution_result_success_property(self):
        """Test ExecutionResult success property."""
        # Successful command
        success_result = ExecutionResult(
            command="echo 'test'",
            return_code=0,
            stdout="test\n",
            stderr="",
            execution_time=0.1,
        )
        assert success_result.success is True

        # Failed command
        failed_result = ExecutionResult(
            command="exit 1",
            return_code=1,
            stdout="",
            stderr="error\n",
            execution_time=0.1,
        )
        assert failed_result.success is False

    @pytest.mark.unit
    def test_execution_result_with_long_output(self):
        """Test ExecutionResult with long output."""
        long_output = "x" * 10000
        result = ExecutionResult(
            command="python -c 'print(\"x\" * 10000)'",
            return_code=0,
            stdout=long_output,
            stderr="",
            execution_time=0.5,
        )

        assert len(result.stdout) == 10000
        assert result.stdout == long_output

    @pytest.mark.unit
    def test_execution_result_with_unicode(self):
        """Test ExecutionResult with Unicode characters."""
        unicode_output = "Hello 世界 🌍"
        result = ExecutionResult(
            command="echo 'Hello 世界 🌍'",
            return_code=0,
            stdout=unicode_output,
            stderr="",
            execution_time=0.1,
        )

        assert result.stdout == unicode_output

    @pytest.mark.unit
    def test_execution_result_repr(self):
        """Test ExecutionResult string representation."""
        result = ExecutionResult(
            command="echo 'test'",
            return_code=0,
            stdout="test\n",
            stderr="",
            execution_time=0.1,
        )

        repr_str = repr(result)
        assert "ExecutionResult" in repr_str
        assert "return_code=0" in repr_str

    @pytest.mark.unit
    def test_execution_result_equality(self):
        """Test ExecutionResult equality comparison."""
        result1 = ExecutionResult(
            command="echo 'test'",
            return_code=0,
            stdout="test\n",
            stderr="",
            execution_time=0.1,
        )

        result2 = ExecutionResult(
            command="echo 'test'",
            return_code=0,
            stdout="test\n",
            stderr="",
            execution_time=0.1,
        )

        result3 = ExecutionResult(
            command="echo 'different'",
            return_code=0,
            stdout="different\n",
            stderr="",
            execution_time=0.1,
        )

        assert result1 == result2
        assert result1 != result3


class TestFileInfo:
    """Test cases for FileInfo."""

    @pytest.mark.unit
    def test_file_info_basic(self):
        """Test basic FileInfo creation."""
        file_info = FileInfo(
            name="test.txt",
            path="/tmp/test.txt",
            size=1024,
            is_directory=False,
            modified_time=None,
        )

        assert file_info.name == "test.txt"
        assert file_info.path == "/tmp/test.txt"
        assert file_info.size == 1024
        assert file_info.is_directory is False
        assert file_info.modified_time is None

    @pytest.mark.unit
    def test_file_info_directory(self):
        """Test FileInfo for directory."""
        dir_info = FileInfo(
            name="mydir",
            path="/tmp/mydir",
            size=4096,
            is_directory=True,
            modified_time=datetime.now(),
        )

        assert dir_info.name == "mydir"
        assert dir_info.path == "/tmp/mydir"
        assert dir_info.size == 4096
        assert dir_info.is_directory is True
        assert isinstance(dir_info.modified_time, datetime)

    @pytest.mark.unit
    def test_file_info_with_timestamp(self):
        """Test FileInfo with modification timestamp."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        file_info = FileInfo(
            name="timestamped.txt",
            path="/tmp/timestamped.txt",
            size=512,
            is_directory=False,
            modified_time=timestamp,
        )

        assert file_info.modified_time == timestamp

    @pytest.mark.unit
    def test_file_info_large_file(self):
        """Test FileInfo for large file."""
        large_size = 1024 * 1024 * 1024  # 1GB
        file_info = FileInfo(
            name="large_file.bin",
            path="/tmp/large_file.bin",
            size=large_size,
            is_directory=False,
            modified_time=None,
        )

        assert file_info.size == large_size

    @pytest.mark.unit
    def test_file_info_repr(self):
        """Test FileInfo string representation."""
        file_info = FileInfo(
            name="test.txt",
            path="/tmp/test.txt",
            size=1024,
            is_directory=False,
            modified_time=None,
        )

        repr_str = repr(file_info)
        assert "FileInfo" in repr_str
        assert "test.txt" in repr_str

    @pytest.mark.unit
    def test_file_info_equality(self):
        """Test FileInfo equality comparison."""
        file1 = FileInfo(
            name="test.txt",
            path="/tmp/test.txt",
            size=1024,
            is_directory=False,
            modified_time=None,
        )

        file2 = FileInfo(
            name="test.txt",
            path="/tmp/test.txt",
            size=1024,
            is_directory=False,
            modified_time=None,
        )

        file3 = FileInfo(
            name="different.txt",
            path="/tmp/different.txt",
            size=1024,
            is_directory=False,
            modified_time=None,
        )

        assert file1 == file2
        assert file1 != file3


class TestSandboxStatus:
    """Test cases for SandboxStatus enum."""

    @pytest.mark.unit
    def test_sandbox_status_values(self):
        """Test SandboxStatus enum values."""
        assert SandboxStatus.CREATING.value == "creating"
        assert SandboxStatus.RUNNING.value == "running"
        assert SandboxStatus.STOPPED.value == "stopped"
        assert SandboxStatus.ERROR.value == "error"
        assert SandboxStatus.UNKNOWN.value == "unknown"

    @pytest.mark.unit
    def test_sandbox_status_comparison(self):
        """Test SandboxStatus comparison."""
        assert SandboxStatus.CREATING == SandboxStatus.CREATING
        assert SandboxStatus.RUNNING != SandboxStatus.STOPPED
        assert SandboxStatus.ERROR != SandboxStatus.UNKNOWN

    @pytest.mark.unit
    def test_sandbox_status_string_representation(self):
        """Test SandboxStatus string representation."""
        assert str(SandboxStatus.RUNNING) == "SandboxStatus.RUNNING"
        assert SandboxStatus.RUNNING.value == "running"

    @pytest.mark.unit
    def test_sandbox_status_iteration(self):
        """Test iterating over SandboxStatus values."""
        statuses = list(SandboxStatus)
        expected = [
            SandboxStatus.CREATING,
            SandboxStatus.RUNNING,
            SandboxStatus.STOPPED,
            SandboxStatus.ERROR,
            SandboxStatus.UNKNOWN,
        ]

        assert len(statuses) == len(expected)
        for status in expected:
            assert status in statuses


class TestSandboxConfig:
    """Test cases for SandboxConfig (already tested in test_config.py, but interface-specific tests here)."""

    @pytest.mark.unit
    def test_sandbox_config_as_interface(self):
        """Test SandboxConfig as part of the interface."""
        config = SandboxConfig(
            timeout=300,
            memory_limit="2GB",
            cpu_limit=2.0,
            working_directory="/workspace",
            environment_vars={"TEST": "value"},
            auto_cleanup=True,
        )

        # Test that it can be used as expected in interfaces
        assert isinstance(config.timeout, int)
        assert isinstance(config.memory_limit, str)
        assert isinstance(config.cpu_limit, float)
        assert isinstance(config.working_directory, str)
        assert isinstance(config.environment_vars, dict)
        assert isinstance(config.auto_cleanup, bool)

    @pytest.mark.unit
    def test_sandbox_config_optional_fields(self):
        """Test SandboxConfig with optional fields."""
        config = SandboxConfig()

        # Optional fields should be None or have defaults
        assert config.memory_limit is None
        assert config.cpu_limit is None
        assert config.image is None
        assert config.timeout == 300  # Default
        assert config.working_directory == "~"  # Default
        assert config.environment_vars == {}  # Default
        assert config.auto_cleanup is True  # Default


class TestInterfaceIntegration:
    """Test integration between different interface components."""

    @pytest.mark.unit
    def test_execution_result_in_context(self):
        """Test ExecutionResult in realistic context."""
        # Simulate a command execution scenario
        command = "python -c 'import sys; print(sys.version)'"

        # Successful execution
        success_result = ExecutionResult(
            command=command,
            return_code=0,
            stdout="Python 3.9.0\n",
            stderr="",
            execution_time=0.25,
        )

        assert success_result.success
        assert "Python" in success_result.stdout
        assert success_result.execution_time > 0

    @pytest.mark.unit
    def test_file_info_listing_scenario(self):
        """Test FileInfo in file listing scenario."""
        # Simulate a directory listing
        files = [
            FileInfo(
                name="script.py",
                path="/workspace/script.py",
                size=1024,
                is_directory=False,
                modified_time=datetime.now(),
            ),
            FileInfo(
                name="data",
                path="/workspace/data",
                size=4096,
                is_directory=True,
                modified_time=datetime.now(),
            ),
            FileInfo(
                name="output.txt",
                path="/workspace/output.txt",
                size=512,
                is_directory=False,
                modified_time=datetime.now(),
            ),
        ]

        # Test filtering
        python_files = [f for f in files if f.name.endswith(".py")]
        directories = [f for f in files if f.is_directory]

        assert len(python_files) == 1
        assert len(directories) == 1
        assert python_files[0].name == "script.py"
        assert directories[0].name == "data"

    @pytest.mark.unit
    def test_sandbox_status_workflow(self):
        """Test SandboxStatus in workflow scenario."""
        # Simulate sandbox lifecycle
        statuses = [
            SandboxStatus.CREATING,
            SandboxStatus.RUNNING,
            SandboxStatus.STOPPED,
        ]

        # Test status transitions
        assert statuses[0] == SandboxStatus.CREATING
        assert statuses[1] == SandboxStatus.RUNNING
        assert statuses[2] == SandboxStatus.STOPPED

        # Test that we can check for specific states
        current_status = SandboxStatus.RUNNING
        assert current_status in [SandboxStatus.RUNNING, SandboxStatus.CREATING]
        assert current_status not in [SandboxStatus.STOPPED, SandboxStatus.ERROR]

    @pytest.mark.unit
    def test_config_with_execution_context(self):
        """Test SandboxConfig in execution context."""
        config = SandboxConfig(
            timeout=60,
            working_directory="/tmp",
            environment_vars={"PYTHONPATH": "/custom/path"},
        )

        # Simulate using config for command execution

        # The config should provide the context for execution
        assert config.timeout == 60
        assert config.working_directory == "/tmp"
        assert "PYTHONPATH" in config.environment_vars
        assert config.environment_vars["PYTHONPATH"] == "/custom/path"


class TestInterfaceValidation:
    """Test interface validation and edge cases."""

    @pytest.mark.unit
    def test_execution_result_edge_cases(self):
        """Test ExecutionResult edge cases."""
        # Empty command
        result = ExecutionResult(
            command="", return_code=0, stdout="", stderr="", execution_time=0.0
        )
        assert result.command == ""
        assert result.execution_time == 0.0

        # Negative return code
        result = ExecutionResult(
            command="test",
            return_code=-1,
            stdout="",
            stderr="Signal terminated",
            execution_time=0.1,
        )
        assert result.return_code == -1
        assert not result.success

    @pytest.mark.unit
    def test_file_info_edge_cases(self):
        """Test FileInfo edge cases."""
        # Zero-size file
        file_info = FileInfo(
            name="empty.txt",
            path="/tmp/empty.txt",
            size=0,
            is_directory=False,
            modified_time=None,
        )
        assert file_info.size == 0

        # File with special characters in name
        file_info = FileInfo(
            name="file with spaces & symbols!.txt",
            path="/tmp/file with spaces & symbols!.txt",
            size=100,
            is_directory=False,
            modified_time=None,
        )
        assert " " in file_info.name
        assert "&" in file_info.name

    @pytest.mark.unit
    def test_sandbox_config_edge_cases(self):
        """Test SandboxConfig edge cases."""
        # Very short timeout
        config = SandboxConfig(timeout=1)
        assert config.timeout == 1

        # Very long timeout
        config = SandboxConfig(timeout=86400)  # 24 hours
        assert config.timeout == 86400

        # Empty environment variables
        config = SandboxConfig(environment_vars={})
        assert config.environment_vars == {}

        # Many environment variables
        many_vars = {f"VAR_{i}": f"value_{i}" for i in range(100)}
        config = SandboxConfig(environment_vars=many_vars)
        assert len(config.environment_vars) == 100
