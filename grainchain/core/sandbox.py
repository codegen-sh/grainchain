"""Main Sandbox class - the primary interface for Grainchain."""

import logging

from grainchain.core.config import get_config_manager
from grainchain.core.exceptions import ConfigurationError, SandboxError
from grainchain.core.interfaces import (
    ExecutionResult,
    FileInfo,
    SandboxConfig,
    SandboxProvider,
    SandboxSession,
    SandboxStatus,
)

logger = logging.getLogger(__name__)


class Sandbox:
    """
    Main sandbox interface that provides a unified API across different providers.

    This class acts as a facade that delegates operations to the underlying
    provider-specific implementations while providing a consistent interface.
    """

    def __init__(
        self,
        provider: str | SandboxProvider | None = None,
        config: SandboxConfig | None = None,
    ):
        """
        Initialize a new Sandbox instance.

        Args:
            provider: Provider instance or name. If None, uses default from config.
            config: Sandbox configuration. If None, uses defaults from config.
        """
        self._config_manager = get_config_manager()
        self._provider = self._resolve_provider(provider)
        self._config = config or self._config_manager.get_sandbox_defaults()
        self._session: SandboxSession | None = None
        self._closed = False

    def _resolve_provider(
        self, provider: str | SandboxProvider | None
    ) -> SandboxProvider:
        """Resolve provider from string name or return provider instance."""
        if provider is None:
            provider_name = self._config_manager.default_provider
            return self._create_provider(provider_name)
        elif isinstance(provider, str):
            return self._create_provider(provider)
        elif isinstance(provider, SandboxProvider):
            return provider
        else:
            raise ConfigurationError(f"Invalid provider type: {type(provider)}")

    def _create_provider(self, provider_name: str) -> SandboxProvider:
        """Create a provider instance from name."""
        provider_config = self._config_manager.get_provider_config(provider_name)

        if provider_name == "e2b":
            from grainchain.providers.e2b import E2BProvider

            return E2BProvider(provider_config)
        elif provider_name == "modal":
            from grainchain.providers.modal import ModalProvider

            return ModalProvider(provider_config)
        elif provider_name == "daytona":
            from grainchain.providers.daytona import DaytonaProvider

            return DaytonaProvider(provider_config)
        elif provider_name == "morph":
            from grainchain.providers.morph import MorphProvider

            return MorphProvider(provider_config)
        elif provider_name == "local":
            from grainchain.providers.local import LocalProvider

            return LocalProvider(provider_config)
        else:
            raise ConfigurationError(f"Unknown provider: {provider_name}")

    async def __aenter__(self) -> "Sandbox":
        """Async context manager entry - creates the sandbox session."""
        if self._closed:
            raise SandboxError("Cannot reuse a closed sandbox")

        try:
            self._session = await self._provider.create_sandbox(self._config)
            logger.info(
                f"Created sandbox {self._session.sandbox_id} using provider {self._provider.name}"
            )
            return self
        except Exception as e:
            logger.error(f"Failed to create sandbox: {e}")
            raise SandboxError(f"Failed to create sandbox: {e}") from e

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit - cleans up the sandbox session."""
        await self.close()

    async def close(self) -> None:
        """Close the sandbox session and clean up resources."""
        if self._session and not self._closed:
            try:
                await self._session.close()
                logger.info(f"Closed sandbox {self._session.sandbox_id}")
            except Exception as e:
                logger.warning(f"Error closing sandbox: {e}")
            finally:
                self._session = None
                self._closed = True

    def _ensure_session(self) -> SandboxSession:
        """Ensure we have an active session."""
        if self._session is None:
            raise SandboxError(
                "Sandbox session not initialized. Use 'async with Sandbox()' or call create() first."
            )
        return self._session

    async def create(self) -> "Sandbox":
        """Explicitly create the sandbox session (alternative to context manager)."""
        if self._session is not None:
            raise SandboxError("Sandbox session already exists")

        self._session = await self._provider.create_sandbox(self._config)
        logger.info(
            f"Created sandbox {self._session.sandbox_id} using provider {self._provider.name}"
        )
        return self

    async def execute(
        self,
        command: str,
        timeout: int | None = None,
        working_dir: str | None = None,
        environment: dict[str, str] | None = None,
    ) -> ExecutionResult:
        """
        Execute a command in the sandbox.

        Args:
            command: Command to execute
            timeout: Execution timeout in seconds (overrides config default)
            working_dir: Working directory for command execution
            environment: Additional environment variables

        Returns:
            ExecutionResult with command output and metadata
        """
        session = self._ensure_session()

        # Use provided timeout or fall back to config default
        effective_timeout = timeout or self._config.timeout

        try:
            result = await session.execute(
                command=command,
                timeout=effective_timeout,
                working_dir=working_dir,
                environment=environment,
            )
            logger.debug(
                f"Executed command '{command}' with return code {result.return_code}"
            )
            return result
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise SandboxError(f"Command execution failed: {e}") from e

    async def upload_file(
        self, path: str, content: str | bytes, mode: str = "w"
    ) -> None:
        """
        Upload a file to the sandbox.

        Args:
            path: Destination path in the sandbox
            content: File content (string or bytes)
            mode: File mode ('w' for text, 'wb' for binary)
        """
        session = self._ensure_session()

        try:
            await session.upload_file(path, content, mode)
            logger.debug(f"Uploaded file to {path}")
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise SandboxError(f"File upload failed: {e}") from e

    async def download_file(self, path: str) -> bytes:
        """
        Download a file from the sandbox.

        Args:
            path: Path to file in the sandbox

        Returns:
            File content as bytes
        """
        session = self._ensure_session()

        try:
            content = await session.download_file(path)
            logger.debug(f"Downloaded file from {path}")
            return content
        except Exception as e:
            logger.error(f"File download failed: {e}")
            raise SandboxError(f"File download failed: {e}") from e

    async def list_files(self, path: str = "/") -> list[FileInfo]:
        """
        List files in the sandbox.

        Args:
            path: Directory path to list

        Returns:
            List of FileInfo objects
        """
        session = self._ensure_session()

        try:
            files = await session.list_files(path)
            logger.debug(f"Listed {len(files)} files in {path}")
            return files
        except Exception as e:
            logger.error(f"File listing failed: {e}")
            raise SandboxError(f"File listing failed: {e}") from e

    async def create_snapshot(self) -> str:
        """
        Create a snapshot of the current sandbox state.

        Returns:
            Snapshot ID
        """
        session = self._ensure_session()

        try:
            snapshot_id = await session.create_snapshot()
            logger.info(f"Created snapshot {snapshot_id}")
            return snapshot_id
        except Exception as e:
            logger.error(f"Snapshot creation failed: {e}")
            raise SandboxError(f"Snapshot creation failed: {e}") from e

    async def restore_snapshot(self, snapshot_id: str) -> None:
        """Restore sandbox to a previous snapshot."""
        try:
            await self._session.restore_snapshot(snapshot_id)
        except Exception as e:
            raise SandboxError(f"Snapshot restoration failed: {e}") from e

    async def terminate(self) -> None:
        """Terminate the sandbox while preserving snapshots."""
        try:
            await self._session.terminate()
        except Exception as e:
            raise SandboxError(f"Sandbox termination failed: {e}") from e

    async def wake_up(self, snapshot_id: str | None = None) -> None:
        """Wake up a terminated sandbox, optionally from a specific snapshot."""
        try:
            await self._session.wake_up(snapshot_id)
        except Exception as e:
            raise SandboxError(f"Sandbox wake up failed: {e}") from e

    @property
    def status(self) -> SandboxStatus:
        """Get current sandbox status."""
        if self._session is None:
            return SandboxStatus.UNKNOWN
        return self._session.status

    @property
    def sandbox_id(self) -> str | None:
        """Get sandbox ID if session exists."""
        return self._session.sandbox_id if self._session else None

    @property
    def provider_name(self) -> str:
        """Get the name of the current provider."""
        return self._provider.name

    def __repr__(self) -> str:
        """String representation of the sandbox."""
        status = self.status.value if self._session else "not_created"
        return f"Sandbox(provider={self.provider_name}, status={status}, id={self.sandbox_id})"
