"""E2B provider implementation for Grainchain."""

import time

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
    from e2b import AsyncSandbox as E2BSandbox
    from e2b.exceptions import AuthenticationException as E2BAuthError
    from e2b.exceptions import SandboxException as E2BError

    E2B_AVAILABLE = True
except ImportError:
    E2B_AVAILABLE = False


class E2BProvider(BaseSandboxProvider):
    """E2B sandbox provider implementation."""

    def __init__(self, config: ProviderConfig):
        """Initialize E2B provider."""
        if not E2B_AVAILABLE:
            raise ImportError(
                "E2B provider requires the 'e2b' package. "
                "Install it with: pip install grainchain[e2b]"
            )

        super().__init__(config)

        # Validate required configuration
        self.api_key = self.require_config_value("api_key")
        self.template = self.get_config_value("template", "base")

    @property
    def name(self) -> str:
        """Provider name."""
        return "e2b"

    async def _create_session(self, config: SandboxConfig) -> "E2BSandboxSession":
        """Create a new E2B sandbox session."""
        try:
            # Create E2B sandbox using the create() class method
            e2b_sandbox = await E2BSandbox.create(
                template=self.template, api_key=self.api_key, timeout=config.timeout
            )

            session = E2BSandboxSession(
                sandbox_id=e2b_sandbox.sandbox_id,
                provider=self,
                config=config,
                e2b_sandbox=e2b_sandbox,
            )

            return session

        except E2BAuthError as e:
            raise AuthenticationError(
                f"E2B authentication failed: {e}", self.name
            ) from e
        except E2BError as e:
            raise ProviderError(
                f"E2B sandbox creation failed: {e}", self.name, e
            ) from e


class E2BSandboxSession(BaseSandboxSession):
    """E2B sandbox session implementation."""

    def __init__(
        self,
        sandbox_id: str,
        provider: E2BProvider,
        config: SandboxConfig,
        e2b_sandbox: "E2BSandbox",
    ):
        """Initialize E2B session."""
        super().__init__(sandbox_id, provider, config)
        self.e2b_sandbox = e2b_sandbox
        self._set_status(SandboxStatus.RUNNING)

    async def execute(
        self,
        command: str,
        timeout: int | None = None,
        working_dir: str | None = None,
        environment: dict[str, str] | None = None,
    ) -> ExecutionResult:
        """Execute a command in the E2B sandbox."""
        import time

        start_time = time.time()

        try:
            # Use E2B commands API
            result = await self.e2b_sandbox.commands.run(
                cmd=command,
                timeout=timeout or self._config.timeout,
                cwd=working_dir,
                envs=environment or {},
            )

            execution_time = time.time() - start_time

            return ExecutionResult(
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.exit_code,
                execution_time=execution_time,
                success=result.exit_code == 0,
                command=command,
            )

        except Exception as e:
            execution_time = time.time() - start_time

            # Handle E2B-specific errors
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
        self, path: str, content: str | bytes, mode: str = "text"
    ) -> None:
        """Upload a file to the E2B sandbox."""
        try:
            if mode == "text":
                # Upload text content directly
                await self.e2b_sandbox.files.write(path, content)
            else:
                # Handle binary content
                if isinstance(content, str):
                    content = content.encode("utf-8")
                # For binary files, we need to encode and decode
                import base64

                encoded_content = base64.b64encode(content).decode("utf-8")
                await self.e2b_sandbox.files.write(f"{path}.b64", encoded_content)
                # Decode the file using base64 command
                await self.execute(f"base64 -d {path}.b64 > {path} && rm {path}.b64")

        except Exception as e:
            raise ProviderError(
                f"File upload failed: {e}", self._provider.name, e
            ) from e

    async def download_file(self, path: str) -> str:
        """Download a file from the E2B sandbox."""
        try:
            content = await self.e2b_sandbox.files.read(path)
            return content
        except Exception as e:
            raise ProviderError(
                f"File download failed: {e}", self._provider.name, e
            ) from e

    async def list_files(self, path: str = ".") -> list[FileInfo]:
        """List files in the E2B sandbox."""
        try:
            # Use E2B files API to list directory contents
            files = await self.e2b_sandbox.files.list(path)

            file_infos = []
            for file in files:
                file_infos.append(
                    FileInfo(
                        name=file.name,
                        path=file.path,
                        size=getattr(file, "size", 0),
                        is_directory=file.type == "dir",
                        modified_time=getattr(file, "modified_time", None),
                    )
                )

            return file_infos

        except Exception as e:
            # Fallback to using ls command
            result = await self.execute(f"ls -la {path}")
            if not result.success:
                raise ProviderError(
                    f"Failed to list files: {e}", self._provider.name, e
                ) from e

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

    async def create_snapshot(self) -> str:
        """Create a snapshot of the current E2B sandbox state."""
        self._ensure_not_closed()

        try:
            # E2B doesn't have built-in snapshots, so we'll simulate with a timestamp
            snapshot_id = f"e2b_snapshot_{int(time.time())}"

            # Create a marker file to indicate snapshot
            await self.e2b_sandbox.filesystem.write(
                f"/tmp/grainchain_snapshot_{snapshot_id}",
                f"Snapshot created at {time.time()}",
            )

            return snapshot_id

        except Exception as e:
            raise ProviderError(
                f"Snapshot creation failed: {e}", self._provider.name, e
            ) from e

    async def restore_snapshot(self, snapshot_id: str) -> None:
        """Restore E2B sandbox to a previous snapshot."""
        self._ensure_not_closed()

        # E2B doesn't support true snapshots, so this is a placeholder
        raise NotImplementedError("E2B provider does not support snapshot restoration")

    async def _cleanup(self) -> None:
        """Clean up E2B sandbox resources."""
        try:
            await self.e2b_sandbox.close()
        except Exception as e:
            # Log but don't raise - cleanup should be best effort
            import logging

            logging.getLogger(__name__).warning(f"Error closing E2B sandbox: {e}")

    async def close(self) -> None:
        """Close the E2B sandbox session."""
        if self.e2b_sandbox and not self._closed:
            try:
                await self.e2b_sandbox.kill()
            except Exception as e:
                # Log error but don't raise - cleanup should be best effort
                print(f"Error closing E2B sandbox: {e}")
            finally:
                self._closed = True
