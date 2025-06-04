"""Daytona provider implementation for Grainchain."""

import time
from typing import Any

from grainchain.core.config import ProviderConfig
from grainchain.core.exceptions import AuthenticationError, ProviderError
from grainchain.core.interfaces import (
    ExecutionResult,
    FileInfo,
    SandboxConfig,
    SandboxStatus,
)
from grainchain.providers.base import BaseSandboxProvider, BaseSandboxSession

try:
    from daytona_sdk import Daytona, DaytonaConfig

    DAYTONA_AVAILABLE = True
except ImportError:
    DAYTONA_AVAILABLE = False


class DaytonaProvider(BaseSandboxProvider):
    """Daytona sandbox provider implementation."""

    def __init__(self, config: ProviderConfig):
        """Initialize Daytona provider."""
        if not DAYTONA_AVAILABLE:
            raise ImportError(
                "Daytona provider requires the 'daytona-sdk' package. "
                "Install it with: pip install daytona-sdk"
            )

        super().__init__(config)

        # Validate required configuration - only need API key
        self.api_key = self.require_config_value("api_key")

    @property
    def name(self) -> str:
        """Provider name."""
        return "daytona"

    async def _create_session(self, config: SandboxConfig) -> "DaytonaSandboxSession":
        """Create a new Daytona sandbox session."""
        try:
            # Create Daytona client configuration (just API key)
            daytona_config = DaytonaConfig(api_key=self.api_key)

            # Initialize Daytona client
            daytona = Daytona(daytona_config)

            # Create sandbox
            sandbox = daytona.create()

            session = DaytonaSandboxSession(
                sandbox_id=sandbox.id,
                provider=self,
                config=config,
                daytona_sandbox=sandbox,
                daytona_client=daytona,
            )

            return session

        except Exception as e:
            error_str = str(e).lower()

            # Check for SSL certificate issues
            if "ssl" in error_str and "certificate" in error_str:
                raise ProviderError(
                    f"Daytona SSL certificate error. This usually means:\n"
                    f"  1. The API endpoint has certificate issues\n"
                    f"  2. You might be using a development/staging environment\n"
                    f"  3. Your API key might be for a different environment\n"
                    f"  Original error: {e}",
                    self.name,
                    e,
                ) from e

            # Check if it's an authentication error
            elif "authentication" in error_str or "unauthorized" in error_str:
                raise AuthenticationError(
                    f"Daytona authentication failed: {e}", self.name
                ) from e
            else:
                raise ProviderError(
                    f"Daytona sandbox creation failed: {e}", self.name, e
                ) from e


class DaytonaSandboxSession(BaseSandboxSession):
    """Daytona sandbox session implementation."""

    def __init__(
        self,
        sandbox_id: str,
        provider: DaytonaProvider,
        config: SandboxConfig,
        daytona_sandbox: Any,
        daytona_client: Any,
    ):
        """Initialize Daytona session."""
        super().__init__(sandbox_id, provider, config)
        self.daytona_sandbox = daytona_sandbox
        self.daytona_client = daytona_client
        self._set_status(SandboxStatus.RUNNING)

    async def execute(
        self,
        command: str,
        timeout: int | None = None,
        working_dir: str | None = None,
        environment: dict[str, str] | None = None,
    ) -> ExecutionResult:
        """Execute a command in the Daytona sandbox."""
        start_time = time.time()

        try:
            # Use the configured working directory if no specific one is provided
            work_dir = working_dir or self._config.working_directory or "~"

            # Daytona's code_run expects Python code, so we need to wrap shell commands
            # in a subprocess call
            python_code = f"""
import subprocess
import os

# Set working directory (expand ~ to home directory)
work_dir = {repr(work_dir)}
if work_dir == '~':
    work_dir = os.path.expanduser('~')
os.chdir(work_dir)

# Set environment variables if provided
env = dict(os.environ)
if {repr(environment or {})}:
    env.update({repr(environment or {})})

# Execute the command
try:
    result = subprocess.run(
        {repr(command)},
        shell=True,
        capture_output=True,
        text=True,
        timeout={timeout or self._config.timeout},
        env=env
    )
    print("STDOUT:" + result.stdout)
    print("STDERR:" + result.stderr)
    print("RETURNCODE:" + str(result.returncode))
except subprocess.TimeoutExpired:
    print("STDOUT:")
    print("STDERR:Command timed out")
    print("RETURNCODE:-1")
except Exception as e:
    print("STDOUT:")
    print("STDERR:" + str(e))
    print("RETURNCODE:-1")
"""

            # Execute the Python code that runs our shell command
            response = self.daytona_sandbox.process.code_run(python_code)

            execution_time = time.time() - start_time

            # Parse the response - look for our custom output format
            result_text = getattr(response, "result", "") or ""

            # Extract stdout, stderr, and return code from our custom format
            stdout = ""
            stderr = ""
            return_code = 0

            if (
                "STDOUT:" in result_text
                and "STDERR:" in result_text
                and "RETURNCODE:" in result_text
            ):
                lines = result_text.split("\n")
                for _, line in enumerate(lines):
                    if line.startswith("STDOUT:"):
                        # Extract content from the same line after the marker
                        stdout = line[7:]  # Remove "STDOUT:" prefix
                    elif line.startswith("STDERR:"):
                        # Extract content from the same line after the marker
                        stderr = line[7:]  # Remove "STDERR:" prefix
                    elif line.startswith("RETURNCODE:"):
                        try:
                            return_code = int(line[11:])  # Remove "RETURNCODE:" prefix
                        except ValueError:
                            return_code = -1
            else:
                # Fallback - if our format parsing failed, check if it's a Python execution error
                if getattr(response, "exit_code", 0) != 0:
                    stderr = result_text
                    return_code = getattr(response, "exit_code", 1)
                else:
                    stdout = result_text

            return ExecutionResult(
                stdout=stdout,
                stderr=stderr,
                return_code=return_code,
                execution_time=execution_time,
                success=return_code == 0,
                command=command,
            )

        except Exception as e:
            execution_time = time.time() - start_time

            return ExecutionResult(
                stdout="",
                stderr=str(e),
                return_code=-1,
                execution_time=execution_time,
                success=False,
                command=command,
            )

    async def upload_file(
        self, path: str, content: str | bytes, mode: str = "text"
    ) -> None:
        """Upload a file to the Daytona sandbox."""
        try:
            # Make sure the path is in the correct working directory
            work_dir = self._config.working_directory or "~"
            if not path.startswith("/"):
                # Relative path - make it relative to working directory
                if work_dir == "~":
                    # Upload to home directory (default)
                    upload_path = path
                else:
                    # Upload to specific working directory
                    upload_path = f"{work_dir.rstrip('/')}/{path}"
            else:
                upload_path = path

            # Use Daytona's file system upload_file method
            if isinstance(content, bytes):
                # Handle binary content - write to temp file first
                import tempfile

                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(content)
                    temp_file_path = temp_file.name

                # Upload the temp file
                self.daytona_sandbox.fs.upload_file(temp_file_path, upload_path)

                # Clean up temp file
                import os

                os.unlink(temp_file_path)
            else:
                # Handle text content - write to temp file first
                import tempfile

                with tempfile.NamedTemporaryFile(
                    mode="w", delete=False, encoding="utf-8"
                ) as temp_file:
                    temp_file.write(content)
                    temp_file_path = temp_file.name

                # Upload the temp file
                self.daytona_sandbox.fs.upload_file(temp_file_path, upload_path)

                # Clean up temp file
                import os

                os.unlink(temp_file_path)

        except Exception as e:
            raise ProviderError(
                f"File upload failed: {e}", self._provider.name, e
            ) from e

    async def download_file(self, path: str) -> str:
        """Download a file from the Daytona sandbox."""
        try:
            # The Daytona SDK's download_file method has a bug, so use shell commands instead
            result = await self.execute(f"cat {path}")
            if result.success:
                return result.stdout
            else:
                raise Exception(f"Failed to read file: {result.stderr}")
        except Exception as e:
            raise ProviderError(
                f"File download failed: {e}", self._provider.name, e
            ) from e

    async def list_files(self, path: str = ".") -> list[FileInfo]:
        """List files in the Daytona sandbox."""
        try:
            # Use Daytona's file system list_files method
            files = self.daytona_sandbox.fs.list_files(path)
            file_infos = []

            for file in files:
                # Handle different possible file object structures
                if hasattr(file, "name"):
                    name = file.name
                    file_path = getattr(file, "path", f"{path}/{name}")
                    size = getattr(file, "size", 0)
                    is_directory = getattr(file, "is_directory", False)
                    modified_time = getattr(file, "modified_time", None)
                else:
                    # Fallback if file is just a string
                    name = str(file)
                    file_path = f"{path}/{name}" if path != "." else name
                    size = 0
                    is_directory = False
                    modified_time = None

                if name not in [".", ".."]:
                    file_infos.append(
                        FileInfo(
                            name=name,
                            path=file_path,
                            size=size,
                            is_directory=is_directory,
                            modified_time=modified_time,
                        )
                    )

            return file_infos

        except Exception as e:
            raise ProviderError(
                f"Failed to list files: {e}", self._provider.name, e
            ) from e

    async def create_snapshot(self) -> str:
        """Create a snapshot of the current Daytona sandbox state."""
        self._ensure_not_closed()

        try:
            # Daytona doesn't have built-in snapshots, so we'll simulate with a timestamp
            snapshot_id = f"daytona_snapshot_{int(time.time())}"

            # Create a marker file to indicate snapshot
            await self.execute(
                f"echo 'Snapshot created at {time.time()}' > /tmp/grainchain_snapshot_{snapshot_id}"
            )

            return snapshot_id

        except Exception as e:
            raise ProviderError(
                f"Snapshot creation failed: {e}", self._provider.name, e
            ) from e

    async def restore_snapshot(self, snapshot_id: str) -> None:
        """Restore Daytona sandbox to a previous snapshot."""
        self._ensure_not_closed()

        # Daytona doesn't support true snapshots, so this is a placeholder
        raise NotImplementedError(
            "Daytona provider does not support snapshot restoration"
        )

    async def _cleanup(self) -> None:
        """Clean up Daytona sandbox resources."""
        try:
            # Stop the sandbox
            self.daytona_sandbox.stop()
        except Exception as e:
            # Log but don't raise - cleanup should be best effort
            import logging

            logging.getLogger(__name__).warning(f"Error stopping Daytona sandbox: {e}")

    async def close(self) -> None:
        """Close the Daytona sandbox session."""
        if self.daytona_sandbox and not self._closed:
            try:
                # Clean up using the recommended pattern
                self.daytona_client.remove(self.daytona_sandbox)
            except Exception as e:
                # Log error but don't raise - cleanup should be best effort
                print(f"Error closing Daytona sandbox: {e}")
            finally:
                self._closed = True
