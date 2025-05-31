"""Morph.so provider implementation for Grainchain."""

import asyncio
import time
import uuid
from typing import Optional, Union

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
    from morphcloud.api import ApiError as MorphApiError
    from morphcloud.api import MorphCloudClient

    MORPH_AVAILABLE = True
except ImportError:
    MORPH_AVAILABLE = False


class MorphProvider(BaseSandboxProvider):
    """Morph.so sandbox provider implementation."""

    def __init__(self, config: ProviderConfig):
        """Initialize Morph provider."""
        if not MORPH_AVAILABLE:
            raise ImportError(
                "Morph provider requires the 'morphcloud' package. "
                "Install it with: pip install morphcloud"
            )

        super().__init__(config)

        # Validate required configuration
        self.api_key = self.require_config_value("api_key")

        # Optional configuration with defaults
        self.image_id = self.get_config_value("image_id", "morphvm-minimal")
        self.vcpus = self.get_config_value("vcpus", 1)
        self.memory = self.get_config_value("memory", 1024)  # MB
        self.disk_size = self.get_config_value("disk_size", 8192)  # MB

        # Initialize client
        self.client = MorphCloudClient(api_key=self.api_key)

    @property
    def name(self) -> str:
        """Provider name."""
        return "morph"

    async def _create_session(self, config: SandboxConfig) -> "MorphSandboxSession":
        """Create a new Morph sandbox session."""
        try:
            # Use custom image if specified in config
            image_id = config.provider_config.get("image_id", self.image_id)
            vcpus = config.provider_config.get("vcpus", self.vcpus)
            memory = config.provider_config.get("memory", self.memory)
            disk_size = config.provider_config.get("disk_size", self.disk_size)

            # Create a snapshot first (this is how Morph works - snapshots are templates)
            snapshot = self.client.snapshots.create(
                vcpus=vcpus,
                memory=memory,
                disk_size=disk_size,
                image_id=image_id,
                digest=f"grainchain-{uuid.uuid4().hex[:8]}",
            )

            # Start an instance from the snapshot
            instance = self.client.instances.start(snapshot_id=snapshot.id)

            session = MorphSandboxSession(
                sandbox_id=instance.id,
                provider=self,
                config=config,
                instance=instance,
                snapshot=snapshot,
            )

            return session

        except MorphApiError as e:
            raise AuthenticationError(
                f"Morph authentication failed: {e}", self.name
            ) from e
        except Exception as e:
            raise ProviderError(
                f"Morph sandbox creation failed: {e}", self.name, e
            ) from e


class MorphSandboxSession(BaseSandboxSession):
    """Morph sandbox session implementation."""

    def __init__(
        self,
        sandbox_id: str,
        provider: MorphProvider,
        config: SandboxConfig,
        instance,
        snapshot,
    ):
        """Initialize Morph session."""
        super().__init__(sandbox_id, provider, config)
        self.instance = instance
        self.snapshot = snapshot
        self._ssh_connection = None
        self._set_status(SandboxStatus.RUNNING)

    async def _get_ssh_connection(self):
        """Get or create SSH connection."""
        if self._ssh_connection is None:
            # Run in thread pool since SSH connection is synchronous
            loop = asyncio.get_event_loop()
            self._ssh_connection = await loop.run_in_executor(None, self.instance.ssh)
        return self._ssh_connection

    async def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        working_dir: Optional[str] = None,
        environment: Optional[dict[str, str]] = None,
    ) -> ExecutionResult:
        """Execute a command in the Morph sandbox."""
        start_time = time.time()

        try:
            ssh = await self._get_ssh_connection()

            # Prepare command with working directory and environment
            full_command = command
            if working_dir:
                full_command = f"cd {working_dir} && {command}"

            if environment:
                env_vars = " ".join([f"{k}={v}" for k, v in environment.items()])
                full_command = f"env {env_vars} {full_command}"

            # Execute command using SSH
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: ssh.run(["/bin/bash", "-c", full_command])
            )

            execution_time = time.time() - start_time

            return ExecutionResult(
                stdout=result.stdout or "",
                stderr=result.stderr or "",
                return_code=result.returncode,
                execution_time=execution_time,
                success=result.returncode == 0,
                command=command,
            )

        except Exception as e:
            execution_time = time.time() - start_time

            # Handle timeout and other errors
            if timeout and execution_time > timeout:
                return ExecutionResult(
                    stdout="",
                    stderr=f"Command timed out after {timeout} seconds",
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
        """Upload a file to the Morph sandbox."""
        try:
            ssh = await self._get_ssh_connection()

            # Create a temporary file locally
            import os
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="wb" if mode == "binary" else "w", delete=False
            ) as tmp_file:
                if isinstance(content, str):
                    if mode == "binary":
                        tmp_file.write(content.encode("utf-8"))
                    else:
                        tmp_file.write(content)
                else:
                    tmp_file.write(content)
                tmp_file_path = tmp_file.name

            try:
                # Copy file to instance using SSH
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None, lambda: ssh.copy_to(tmp_file_path, path)
                )
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)

        except Exception as e:
            raise ProviderError(
                f"File upload failed: {e}", self._provider.name, e
            ) from e

    async def download_file(self, path: str) -> str:
        """Download a file from the Morph sandbox."""
        try:
            ssh = await self._get_ssh_connection()

            # Create a temporary file locally
            import os
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file_path = tmp_file.name

            try:
                # Copy file from instance using SSH
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None, lambda: ssh.copy_from(path, tmp_file_path)
                )

                # Read the file content
                with open(tmp_file_path) as f:
                    content = f.read()

                return content
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)

        except Exception as e:
            raise ProviderError(
                f"File download failed: {e}", self._provider.name, e
            ) from e

    async def list_files(self, path: str = ".") -> list[FileInfo]:
        """List files in the Morph sandbox."""
        try:
            # Use ls command to list files
            result = await self.execute(f"ls -la {path}")
            if not result.success:
                raise ProviderError(
                    f"Failed to list files: {result.stderr}", self._provider.name
                )

            # Parse ls output
            file_infos = []
            lines = result.stdout.strip().split("\n")

            for line in lines[1:]:  # Skip the "total" line
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
                                    modified_time=time.time(),  # Placeholder
                                    permissions=parts[0],
                                )
                            )

            return file_infos

        except Exception as e:
            raise ProviderError(
                f"File listing failed: {e}", self._provider.name, e
            ) from e

    async def create_snapshot(self) -> str:
        """Create a snapshot of the current sandbox state."""
        try:
            # Create snapshot from current instance
            loop = asyncio.get_event_loop()
            snapshot = await loop.run_in_executor(
                None,
                lambda: self.instance.snapshot(
                    digest=f"grainchain-snapshot-{uuid.uuid4().hex[:8]}"
                ),
            )
            return snapshot.id
        except Exception as e:
            raise ProviderError(
                f"Morph snapshot creation failed: {e}", self._provider.name, e
            ) from e

    async def restore_snapshot(self, snapshot_id: str) -> None:
        """Restore sandbox to a previous snapshot state."""
        try:
            # Stop current instance
            await self.terminate()

            # Start new instance from snapshot
            loop = asyncio.get_event_loop()
            new_instance = await loop.run_in_executor(
                None,
                lambda: self._provider.client.instances.start(snapshot_id=snapshot_id),
            )

            # Update our instance reference
            self.instance = new_instance
            self._sandbox_id = new_instance.id  # Update the internal sandbox ID
            self._ssh_connection = None  # Reset SSH connection
            self._set_status(SandboxStatus.RUNNING)

        except Exception as e:
            raise ProviderError(
                f"Morph snapshot restoration failed: {e}", self._provider.name, e
            ) from e

    async def terminate(self) -> None:
        """Terminate the sandbox while preserving snapshots."""
        try:
            if self.status == SandboxStatus.RUNNING:
                # Close SSH connection
                if self._ssh_connection:
                    self._ssh_connection.close()
                    self._ssh_connection = None

                # Stop the instance
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None, lambda: self._provider.client.instances.stop(self.instance.id)
                )

                self._set_status(SandboxStatus.STOPPED)

        except Exception as e:
            raise ProviderError(
                f"Morph sandbox termination failed: {e}", self._provider.name, e
            ) from e

    async def wake_up(self, snapshot_id: Optional[str] = None) -> None:
        """Wake up a terminated sandbox, optionally from a specific snapshot."""
        try:
            if snapshot_id:
                # Start from specific snapshot
                await self.restore_snapshot(snapshot_id)
            else:
                # For Morph, we can't just "wake up" an instance - we need to start from a snapshot
                # This is because Morph's architecture is snapshot-based
                raise ProviderError(
                    "Morph requires a snapshot_id to wake up. Use wake_up(snapshot_id) instead.",
                    self._provider.name,
                    None,
                )

        except Exception as e:
            raise ProviderError(
                f"Morph sandbox wake up failed: {e}", self._provider.name, e
            ) from e

    async def _cleanup(self) -> None:
        """Clean up Morph sandbox resources."""
        try:
            # Close SSH connection if it exists
            if self._ssh_connection:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: self._ssh_connection.close())
                self._ssh_connection = None

            # Stop the instance
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, lambda: self._provider.client.instances.stop(self.instance.id)
            )

        except Exception as e:
            # Log but don't raise - cleanup should be best effort
            import logging

            logging.getLogger(__name__).warning(f"Error cleaning up Morph sandbox: {e}")
