"""Local provider implementation for Grainchain (for development and testing)."""

import asyncio
import os
import shutil
import tempfile
import time
import uuid
from pathlib import Path

from grainchain.core.config import ProviderConfig
from grainchain.core.exceptions import ProviderError
from grainchain.core.interfaces import (
    ExecutionResult,
    FileInfo,
    SandboxConfig,
    SandboxStatus,
)
from grainchain.providers.base import BaseSandboxProvider, BaseSandboxSession


class LocalProvider(BaseSandboxProvider):
    """Local sandbox provider implementation using temporary directories."""

    def __init__(self, config: ProviderConfig):
        """Initialize Local provider."""
        super().__init__(config)
        self.base_dir = self.get_config_value("base_dir", tempfile.gettempdir())

    @property
    def name(self) -> str:
        """Provider name."""
        return "local"

    async def _create_session(self, config: SandboxConfig) -> "LocalSandboxSession":
        """Create a new local sandbox session."""
        try:
            # Create a temporary directory for this sandbox
            sandbox_dir = tempfile.mkdtemp(
                prefix="grainchain_local_", dir=self.base_dir
            )

            # Set up working directory
            working_dir = Path(sandbox_dir) / config.working_directory.lstrip("/")
            working_dir.mkdir(parents=True, exist_ok=True)

            session = LocalSandboxSession(
                sandbox_id=f"local_{uuid.uuid4().hex[:8]}",
                provider=self,
                config=config,
                sandbox_dir=sandbox_dir,
                working_dir=str(working_dir),
            )

            return session

        except Exception as e:
            raise ProviderError(
                f"Local sandbox creation failed: {e}", self.name, e
            ) from e


class LocalSandboxSession(BaseSandboxSession):
    """Local sandbox session implementation."""

    def __init__(
        self,
        sandbox_id: str,
        provider: LocalProvider,
        config: SandboxConfig,
        sandbox_dir: str,
        working_dir: str,
    ):
        """Initialize Local session."""
        super().__init__(sandbox_id, provider, config)
        self.sandbox_dir = sandbox_dir
        self.working_dir = working_dir
        self._snapshots: dict[str, str] = {}
        self._set_status(SandboxStatus.RUNNING)

    async def execute(
        self,
        command: str,
        timeout: int | None = None,
        working_dir: str | None = None,
        environment: dict[str, str] | None = None,
    ) -> ExecutionResult:
        """Execute a command in the local sandbox."""
        self._ensure_not_closed()

        start_time = time.time()

        try:
            # Determine working directory
            exec_dir = working_dir or self.working_dir

            # Prepare environment
            env = os.environ.copy()
            env.update(self.config.environment_vars)
            if environment:
                env.update(environment)

            # Create subprocess
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=exec_dir,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout or self.config.timeout
                )
            except TimeoutError:
                process.kill()
                await process.wait()
                raise ProviderError(
                    f"Command timed out after {timeout or self.config.timeout} seconds",
                    self._provider.name,
                ) from None

            execution_time = time.time() - start_time

            return ExecutionResult(
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                return_code=process.returncode,
                execution_time=execution_time,
                success=process.returncode == 0,
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
        self, path: str, content: str | bytes, mode: str = "w"
    ) -> None:
        """Upload a file to the local sandbox."""
        self._ensure_not_closed()

        try:
            # Resolve path relative to sandbox directory
            if path.startswith("/"):
                file_path = Path(self.sandbox_dir) / path.lstrip("/")
            else:
                file_path = Path(self.working_dir) / path

            # Create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            if isinstance(content, str):
                file_path.write_text(content, encoding="utf-8")
            else:
                file_path.write_bytes(content)

        except Exception as e:
            raise ProviderError(
                f"File upload failed: {e}", self._provider.name, e
            ) from e

    async def download_file(self, path: str) -> bytes:
        """Download a file from the local sandbox."""
        self._ensure_not_closed()

        try:
            # Resolve path relative to sandbox directory
            if path.startswith("/"):
                file_path = Path(self.sandbox_dir) / path.lstrip("/")
            else:
                file_path = Path(self.working_dir) / path

            if not file_path.exists():
                raise ProviderError(f"File not found: {path}", self._provider.name)

            return file_path.read_bytes()

        except Exception as e:
            raise ProviderError(
                f"File download failed: {e}", self._provider.name, e
            ) from e

    async def list_files(self, path: str = "/") -> list[FileInfo]:
        """List files in the local sandbox."""
        self._ensure_not_closed()

        try:
            # Resolve path relative to sandbox directory
            if path.startswith("/"):
                dir_path = Path(self.sandbox_dir) / path.lstrip("/")
            else:
                dir_path = Path(self.working_dir) / path

            if not dir_path.exists():
                raise ProviderError(f"Directory not found: {path}", self._provider.name)

            files = []
            for item in dir_path.iterdir():
                stat = item.stat()
                files.append(
                    FileInfo(
                        path=str(item.relative_to(self.sandbox_dir)),
                        name=item.name,
                        size=stat.st_size,
                        is_directory=item.is_dir(),
                        modified_time=stat.st_mtime,
                        permissions=oct(stat.st_mode)[-3:],
                    )
                )

            return files

        except Exception as e:
            raise ProviderError(
                f"File listing failed: {e}", self._provider.name, e
            ) from e

    async def create_snapshot(self) -> str:
        """Create a snapshot of the current local sandbox state."""
        self._ensure_not_closed()

        try:
            snapshot_id = f"local_snapshot_{int(time.time())}"
            snapshot_dir = f"{self.sandbox_dir}_snapshot_{snapshot_id}"

            # Copy entire sandbox directory
            shutil.copytree(self.sandbox_dir, snapshot_dir)
            self._snapshots[snapshot_id] = snapshot_dir

            return snapshot_id

        except Exception as e:
            raise ProviderError(
                f"Snapshot creation failed: {e}", self._provider.name, e
            ) from e

    async def restore_snapshot(self, snapshot_id: str) -> None:
        """Restore local sandbox to a previous snapshot."""
        self._ensure_not_closed()

        try:
            if snapshot_id not in self._snapshots:
                raise ProviderError(
                    f"Snapshot not found: {snapshot_id}", self._provider.name
                )

            snapshot_dir = self._snapshots[snapshot_id]

            if not os.path.exists(snapshot_dir):
                raise ProviderError(
                    f"Snapshot directory not found: {snapshot_dir}", self._provider.name
                )

            # Remove current sandbox directory
            shutil.rmtree(self.sandbox_dir)

            # Restore from snapshot
            shutil.copytree(snapshot_dir, self.sandbox_dir)

        except Exception as e:
            raise ProviderError(
                f"Snapshot restoration failed: {e}", self._provider.name, e
            ) from e

    async def _cleanup(self) -> None:
        """Clean up local sandbox resources."""
        try:
            # Remove sandbox directory
            if os.path.exists(self.sandbox_dir):
                shutil.rmtree(self.sandbox_dir)

            # Remove snapshots
            for snapshot_dir in self._snapshots.values():
                if os.path.exists(snapshot_dir):
                    shutil.rmtree(snapshot_dir)

        except Exception as e:
            # Log but don't raise - cleanup should be best effort
            import logging

            logging.getLogger(__name__).warning(f"Error cleaning up local sandbox: {e}")
