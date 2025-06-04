"""Core interfaces and data structures for Grainchain."""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SandboxStatus(Enum):
    """Sandbox status enumeration."""

    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class ExecutionResult:
    """Result of command execution in a sandbox."""

    stdout: str
    stderr: str
    return_code: int
    execution_time: float
    success: bool
    command: str
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    @property
    def output(self) -> str:
        """Combined stdout and stderr."""
        return f"{self.stdout}\n{self.stderr}".strip()

    @property
    def failed(self) -> bool:
        """Whether the execution failed."""
        return not self.success


@dataclass
class FileInfo:
    """Information about a file in the sandbox."""

    path: str
    name: str
    size: int
    is_directory: bool
    modified_time: float
    permissions: str = ""

    @property
    def is_file(self) -> bool:
        """Whether this is a file (not a directory)."""
        return not self.is_directory


@dataclass
class SandboxConfig:
    """Configuration for sandbox creation and management."""

    # Resource limits
    timeout: int | None = 300  # seconds
    memory_limit: str | None = None  # e.g., "2GB"
    cpu_limit: float | None = None  # CPU cores

    # Environment
    image: str | None = None
    working_directory: str = "~"
    environment_vars: dict[str, str] = field(default_factory=dict)

    # Behavior
    auto_cleanup: bool = True
    keep_alive: bool = False

    # Provider-specific settings
    provider_config: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.environment_vars is None:
            self.environment_vars = {}


class SandboxProvider(ABC):
    """Abstract base class for sandbox providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass

    @abstractmethod
    async def create_sandbox(self, config: SandboxConfig) -> "SandboxSession":
        """Create a new sandbox session."""
        pass

    @abstractmethod
    async def list_sandboxes(self) -> list[str]:
        """List active sandbox IDs."""
        pass

    @abstractmethod
    async def get_sandbox_status(self, sandbox_id: str) -> SandboxStatus:
        """Get the status of a sandbox."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up provider resources."""
        pass


class SandboxSession(ABC):
    """Abstract base class for sandbox sessions."""

    @property
    @abstractmethod
    def sandbox_id(self) -> str:
        """Unique identifier for this sandbox."""
        pass

    @property
    @abstractmethod
    def status(self) -> SandboxStatus:
        """Current sandbox status."""
        pass

    @abstractmethod
    async def execute(
        self,
        command: str,
        timeout: int | None = None,
        working_dir: str | None = None,
        environment: dict[str, str] | None = None,
    ) -> ExecutionResult:
        """Execute a command in the sandbox."""
        pass

    @abstractmethod
    async def upload_file(
        self, path: str, content: str | bytes, mode: str = "w"
    ) -> None:
        """Upload a file to the sandbox."""
        pass

    @abstractmethod
    async def download_file(self, path: str) -> bytes:
        """Download a file from the sandbox."""
        pass

    @abstractmethod
    async def list_files(self, path: str = "/") -> list[FileInfo]:
        """List files in the sandbox."""
        pass

    async def create_snapshot(self) -> str:
        """Create a snapshot of the current sandbox state.

        Returns:
            str: Snapshot ID that can be used to restore the state
        """
        raise NotImplementedError("Snapshot creation not implemented")

    async def restore_snapshot(self, snapshot_id: str) -> None:
        """Restore sandbox to a previous snapshot state.

        Args:
            snapshot_id: ID of the snapshot to restore
        """
        raise NotImplementedError("Snapshot restoration not implemented")

    async def terminate(self) -> None:
        """Terminate the sandbox while preserving snapshots.

        This stops the sandbox instance but keeps snapshots available
        for later restoration via wake_up().
        """
        raise NotImplementedError("Sandbox termination not implemented")

    async def wake_up(self, snapshot_id: str | None = None) -> None:
        """Wake up a terminated sandbox, optionally from a specific snapshot.

        Args:
            snapshot_id: Optional snapshot ID to restore from. If None,
                        wakes up from the most recent state.
        """
        raise NotImplementedError("Sandbox wake up not implemented")

    @abstractmethod
    async def close(self) -> None:
        """Close and cleanup the sandbox session."""
        pass

    async def __aenter__(self) -> "SandboxSession":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
