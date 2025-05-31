"""Daytona provider implementation for Grainchain."""

import time
from typing import Any, Optional, Union

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

        # Validate required configuration
        self.api_key = self.require_config_value("api_key")
        self.api_url = self.get_config_value("api_url", "https://api.daytona.io")
        self.target = self.get_config_value("target", "us")

    @property
    def name(self) -> str:
        """Provider name."""
        return "daytona"

    async def _create_session(self, config: SandboxConfig) -> "DaytonaSandboxSession":
        """Create a new Daytona sandbox session."""
        try:
            # Create Daytona client configuration
            daytona_config = DaytonaConfig(
                api_key=self.api_key, api_url=self.api_url, target=self.target
            )

            # Initialize Daytona client
            daytona = Daytona(daytona_config)

            # Create sandbox
            sandbox = daytona.create()

            # Start the sandbox and wait for it to be ready
            sandbox.start(timeout=config.timeout)

            session = DaytonaSandboxSession(
                sandbox_id=sandbox.id,
                provider=self,
                config=config,
                daytona_sandbox=sandbox,
                daytona_client=daytona,
            )

            return session

        except Exception as e:
            # Check if it's an authentication error
            if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
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
        timeout: Optional[int] = None,
        working_dir: Optional[str] = None,
        environment: Optional[dict[str, str]] = None,
    ) -> ExecutionResult:
        """Execute a command in the Daytona sandbox."""
        start_time = time.time()

        try:
            # Prepare the command with working directory if specified
            if working_dir:
                command = f"cd {working_dir} && {command}"

            # Set environment variables if provided
            if environment:
                env_vars = " ".join([f"{k}={v}" for k, v in environment.items()])
                command = f"{env_vars} {command}"

            # Execute command using Daytona's process interface
            # Note: Daytona's code_run might be for code execution, we'll use shell commands
            result = self.daytona_sandbox.process.code_run(command)

            execution_time = time.time() - start_time

            # Parse the result - Daytona returns different structure than E2B
            stdout = getattr(result, "result", "") or getattr(result, "stdout", "")
            stderr = getattr(result, "error", "") or getattr(result, "stderr", "")
            return_code = getattr(result, "exit_code", 0) or (1 if stderr else 0)

            return ExecutionResult(
                stdout=str(stdout),
                stderr=str(stderr),
                return_code=return_code,
                execution_time=execution_time,
                success=return_code == 0,
                command=command,
            )

        except Exception as e:
            execution_time = time.time() - start_time

            # Handle timeout and other errors
            if "timeout" in str(e).lower():
                return ExecutionResult(
                    stdout="",
                    stderr=f"Command timed out after {timeout or self._config.timeout} seconds",
                    return_code=-1,
                    execution_time=execution_time,
                    success=False,
                    command=command,
                )
            else:
                return ExecutionResult(
                    stdout="",
                    stderr=str(e),
                    return_code=-1,
                    execution_time=execution_time,
                    success=False,
                    command=command,
                )

    async def upload_file(
        self, path: str, content: Union[str, bytes], mode: str = "text"
    ) -> None:
        """Upload a file to the Daytona sandbox."""
        try:
            # Use Daytona's file system interface
            if mode == "text":
                # Upload text content directly
                self.daytona_sandbox.fs.write_file(path, content)
            else:
                # Handle binary content
                if isinstance(content, str):
                    content = content.encode("utf-8")
                # For binary files, we might need to encode and decode
                import base64

                encoded_content = base64.b64encode(content).decode("utf-8")
                temp_path = f"{path}.b64"
                self.daytona_sandbox.fs.write_file(temp_path, encoded_content)
                # Decode the file using base64 command
                await self.execute(f"base64 -d {temp_path} > {path} && rm {temp_path}")

        except Exception as e:
            raise ProviderError(
                f"File upload failed: {e}", self._provider.name, e
            ) from e

    async def download_file(self, path: str) -> str:
        """Download a file from the Daytona sandbox."""
        try:
            content = self.daytona_sandbox.fs.read_file(path)
            return content
        except Exception as e:
            raise ProviderError(
                f"File download failed: {e}", self._provider.name, e
            ) from e

    async def list_files(self, path: str = ".") -> list[FileInfo]:
        """List files in the Daytona sandbox."""
        try:
            # Try to use Daytona's file system API if available
            try:
                files = self.daytona_sandbox.fs.list_files(path)
                file_infos = []
                for file in files:
                    file_infos.append(
                        FileInfo(
                            name=getattr(file, "name", str(file)),
                            path=getattr(file, "path", f"{path}/{file}"),
                            size=getattr(file, "size", 0),
                            is_directory=getattr(file, "is_directory", False),
                            modified_time=getattr(file, "modified_time", None),
                        )
                    )
                return file_infos
            except AttributeError:
                # Fallback to using ls command if fs.list_files doesn't exist
                result = await self.execute(f"ls -la {path}")
                if not result.success:
                    raise ProviderError(
                        f"Failed to list files: {result.stderr}", self._provider.name
                    ) from None

                # Parse ls output (basic implementation)
                file_infos = []
                lines = result.stdout.strip().split("\n")[1:]  # Skip total line
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 9:
                            name = " ".join(parts[8:])
                            if name not in [".", ".."]:
                                file_infos.append(
                                    FileInfo(
                                        name=name,
                                        path=f"{path}/{name}" if path != "." else name,
                                        size=int(parts[4]) if parts[4].isdigit() else 0,
                                        is_directory=parts[0].startswith("d"),
                                        modified_time=None,
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
                # Remove/delete the sandbox
                self.daytona_client.remove(self.daytona_sandbox)
            except Exception as e:
                # Log error but don't raise - cleanup should be best effort
                print(f"Error closing Daytona sandbox: {e}")
            finally:
                self._closed = True
