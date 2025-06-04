"""Modal provider implementation for Grainchain."""

import time
import uuid

from grainchain.core.config import ProviderConfig
from grainchain.core.exceptions import ProviderError
from grainchain.core.interfaces import (
    ExecutionResult,
    FileInfo,
    SandboxConfig,
    SandboxStatus,
)
from grainchain.providers.base import BaseSandboxProvider, BaseSandboxSession

try:
    import modal
    from modal import App
    from modal import Sandbox as ModalSandbox

    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False


class ModalProvider(BaseSandboxProvider):
    """Modal sandbox provider implementation."""

    def __init__(self, config: ProviderConfig):
        """Initialize Modal provider."""
        if not MODAL_AVAILABLE:
            raise ImportError(
                "Modal provider requires the 'modal' package. "
                "Install it with: pip install grainchain[modal]"
            )

        super().__init__(config)

        # Modal authentication is typically handled via environment variables
        # or modal token files, so we don't require explicit credentials here
        self.image_name = self.get_config_value("image", "python:3.12")
        self.cpu = self.get_config_value("cpu", 1.0)
        self.memory = self.get_config_value("memory", "1GB")

        # Create Modal app using lookup for lazy initialization
        # self.app = App(f"grainchain-{uuid.uuid4().hex[:8]}")

    @property
    def name(self) -> str:
        """Provider name."""
        return "modal"

    async def _create_session(self, config: SandboxConfig) -> "ModalSandboxSession":
        """Create a new Modal sandbox session."""
        try:
            # Configure Modal image
            image = modal.Image.from_registry("ubuntu:22.04")

            # Add any additional packages or setup
            if config.environment_vars:
                # Modal handles environment variables differently
                pass

            # Create Modal app using lookup for lazy initialization
            app_name = f"grainchain-{uuid.uuid4().hex[:8]}"
            app = modal.App.lookup(app_name, create_if_missing=True)

            # Create Modal sandbox
            modal_sandbox = ModalSandbox.create(
                image=image,
                app=app,
                timeout=config.timeout,
                cpu=config.cpu_limit or self.cpu,
                # memory=config.memory_limit or self.memory,  # Uncomment when Modal supports it
            )

            session = ModalSandboxSession(
                sandbox_id=f"modal_{uuid.uuid4().hex[:8]}",
                provider=self,
                config=config,
                modal_sandbox=modal_sandbox,
            )

            return session

        except Exception as e:
            raise ProviderError(
                f"Modal sandbox creation failed: {e}", self.name, e
            ) from e


class ModalSandboxSession(BaseSandboxSession):
    """Modal sandbox session implementation."""

    def __init__(
        self,
        sandbox_id: str,
        provider: ModalProvider,
        config: SandboxConfig,
        modal_sandbox: "ModalSandbox",
    ):
        """Initialize Modal session."""
        super().__init__(sandbox_id, provider, config)
        self.modal_sandbox = modal_sandbox
        self._set_status(SandboxStatus.RUNNING)

    async def execute(
        self,
        command: str,
        timeout: int | None = None,
        working_dir: str | None = None,
        environment: dict[str, str] | None = None,
    ) -> ExecutionResult:
        """Execute a command in the Modal sandbox."""
        self._ensure_not_closed()

        start_time = time.time()

        try:
            # Prepare the command with working directory and environment
            full_command = []

            # Set environment variables
            if environment:
                for key, value in environment.items():
                    full_command.append(f"export {key}='{value}'")

            # Change directory if specified
            if working_dir:
                full_command.append(f"cd {working_dir}")

            # Add the actual command
            full_command.append(command)

            # Join with && to ensure proper execution order
            final_command = " && ".join(full_command)

            # Execute via Modal sandbox
            process = self.modal_sandbox.exec(
                "bash", "-c", final_command, timeout=timeout or self.config.timeout
            )

            # Wait for completion and get results
            result = process.wait()

            execution_time = time.time() - start_time

            return ExecutionResult(
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode,
                execution_time=execution_time,
                success=result.returncode == 0,
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
        """Upload a file to the Modal sandbox."""
        self._ensure_not_closed()

        try:
            # Modal file operations are typically done through volumes or direct exec
            if isinstance(content, str):
                # Write text content
                escaped_content = content.replace("'", "'\"'\"'")
                await self.execute(f"echo '{escaped_content}' > {path}")
            else:
                # For binary content, use base64 encoding
                import base64

                encoded_content = base64.b64encode(content).decode("utf-8")
                await self.execute(f"echo '{encoded_content}' | base64 -d > {path}")

        except Exception as e:
            raise ProviderError(
                f"File upload failed: {e}", self._provider.name, e
            ) from e

    async def download_file(self, path: str) -> bytes:
        """Download a file from the Modal sandbox."""
        self._ensure_not_closed()

        try:
            # Read file content via cat command
            result = await self.execute(f"cat {path}")

            if not result.success:
                raise ProviderError(
                    f"Failed to read file: {result.stderr}", self._provider.name
                )

            return result.stdout.encode("utf-8")

        except Exception as e:
            raise ProviderError(
                f"File download failed: {e}", self._provider.name, e
            ) from e

    async def list_files(self, path: str = "/") -> list[FileInfo]:
        """List files in the Modal sandbox."""
        self._ensure_not_closed()

        try:
            # Use ls command to get file information
            result = await self.execute(f"ls -la {path}")

            if not result.success:
                raise ProviderError(
                    f"Failed to list files: {result.stderr}", self._provider.name
                )

            files = []
            lines = result.stdout.strip().split("\n")[1:]  # Skip total line

            for line in lines:
                if not line.strip():
                    continue

                parts = line.split()
                if len(parts) >= 9:
                    permissions = parts[0]
                    size = int(parts[4]) if parts[4].isdigit() else 0
                    name = " ".join(parts[8:])
                    is_directory = permissions.startswith("d")

                    files.append(
                        FileInfo(
                            path=f"{path.rstrip('/')}/{name}",
                            name=name,
                            size=size,
                            is_directory=is_directory,
                            modified_time=time.time(),  # Modal doesn't provide exact time
                            permissions=permissions,
                        )
                    )

            return files

        except Exception as e:
            raise ProviderError(
                f"File listing failed: {e}", self._provider.name, e
            ) from e

    async def create_snapshot(self) -> str:
        """Create a snapshot of the current Modal sandbox state."""
        self._ensure_not_closed()

        # Modal doesn't have built-in snapshots, so this is a placeholder
        snapshot_id = f"modal_snapshot_{int(time.time())}"

        try:
            # Create a marker to indicate snapshot
            await self.execute(
                f"echo 'Snapshot {snapshot_id} created at {time.time()}' > /tmp/grainchain_snapshot_{snapshot_id}"
            )
            return snapshot_id

        except Exception as e:
            raise ProviderError(
                f"Snapshot creation failed: {e}", self._provider.name, e
            ) from e

    async def restore_snapshot(self, snapshot_id: str) -> None:
        """Restore Modal sandbox to a previous snapshot."""
        self._ensure_not_closed()

        # Modal doesn't support true snapshots, so this is a placeholder
        raise NotImplementedError(
            "Modal provider does not support snapshot restoration"
        )

    async def _cleanup(self) -> None:
        """Clean up Modal sandbox resources."""
        try:
            # Modal sandboxes are automatically cleaned up
            # but we can explicitly terminate if needed
            if hasattr(self.modal_sandbox, "terminate"):
                self.modal_sandbox.terminate()
        except Exception as e:
            # Log but don't raise - cleanup should be best effort
            import logging

            logging.getLogger(__name__).warning(f"Error closing Modal sandbox: {e}")
