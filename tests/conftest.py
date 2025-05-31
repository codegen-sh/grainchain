"""Pytest configuration and fixtures for Grainchain tests."""

import asyncio
import os
import tempfile
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest

from grainchain import Sandbox, SandboxConfig
from grainchain.core.config import ConfigManager, ProviderConfig
from grainchain.core.exceptions import GrainchainError
from grainchain.core.interfaces import (
    ExecutionResult,
    FileInfo,
    SandboxSession,
    SandboxStatus,
)
from grainchain.providers.base import BaseSandboxProvider, BaseSandboxSession


# Test configuration
@pytest.fixture
def test_config() -> SandboxConfig:
    """Create a test sandbox configuration."""
    return SandboxConfig(
        timeout=30,
        memory_limit="1GB",
        cpu_limit=1.0,
        working_directory="/tmp",
        environment_vars={"TEST_ENV": "test_value"},
        auto_cleanup=True,
    )


@pytest.fixture
def provider_config() -> ProviderConfig:
    """Create a test provider configuration."""
    return ProviderConfig(
        name="test_provider",
        config={
            "api_key": "test_key",
            "timeout": 30,
            "test_setting": "test_value",
        },
    )


@pytest.fixture
def config_manager() -> ConfigManager:
    """Create a test configuration manager."""
    # Create a temporary config file
    config_data = {
        "default_provider": "test",
        "providers": {
            "test": {
                "api_key": "test_key",
                "timeout": 30,
            },
            "e2b": {
                "api_key": "test_e2b_key",
                "template": "python",
            },
            "modal": {
                "token_id": "test_modal_id",
                "token_secret": "test_modal_secret",
            },
            "daytona": {
                "api_key": "test_daytona_key",
            },
            "local": {},
        },
        "sandbox_defaults": {
            "timeout": 180,
            "working_directory": "/workspace",
            "auto_cleanup": True,
        },
    }

    manager = ConfigManager()
    manager._config = config_data
    manager._init_providers()
    return manager


# Mock providers and sessions
class MockSandboxSession(BaseSandboxSession):
    """Mock sandbox session for testing."""

    def __init__(
        self, sandbox_id: str, provider: "MockSandboxProvider", config: SandboxConfig
    ):
        super().__init__(sandbox_id, provider, config)
        self._set_status(SandboxStatus.RUNNING)
        self.executed_commands = []
        self.uploaded_files = {}
        self.snapshots = {}

    async def execute(
        self,
        command: str,
        timeout: int = None,
        working_dir: str = None,
        environment: dict[str, str] = None,
    ) -> ExecutionResult:
        """Mock command execution."""
        self._ensure_not_closed()

        # Record the command
        self.executed_commands.append(
            {
                "command": command,
                "timeout": timeout,
                "working_dir": working_dir,
                "environment": environment,
            }
        )

        # Simulate different command responses
        if command == "echo 'Hello, World!'":
            return ExecutionResult(
                command=command,
                return_code=0,
                stdout="Hello, World!\n",
                stderr="",
                execution_time=0.1,
            )
        elif command.startswith("python -c"):
            return ExecutionResult(
                command=command,
                return_code=0,
                stdout="Python output\n",
                stderr="",
                execution_time=0.2,
            )
        elif command == "exit 1":
            return ExecutionResult(
                command=command,
                return_code=1,
                stdout="",
                stderr="Command failed\n",
                execution_time=0.1,
            )
        elif "timeout" in command:
            # Simulate timeout
            raise asyncio.TimeoutError("Command timed out")
        else:
            return ExecutionResult(
                command=command,
                return_code=0,
                stdout=f"Output for: {command}\n",
                stderr="",
                execution_time=0.1,
            )

    async def upload_file(
        self, path: str, content: bytes | str, mode: str = "w"
    ) -> None:
        """Mock file upload."""
        self._ensure_not_closed()
        if isinstance(content, str):
            content = content.encode()
        self.uploaded_files[path] = {"content": content, "mode": mode}

    async def download_file(self, path: str) -> bytes:
        """Mock file download."""
        self._ensure_not_closed()
        if path in self.uploaded_files:
            return self.uploaded_files[path]["content"]
        elif path == "/test/existing_file.txt":
            return b"Existing file content"
        else:
            raise FileNotFoundError(f"File not found: {path}")

    async def list_files(self, path: str = "/") -> list[FileInfo]:
        """Mock file listing."""
        self._ensure_not_closed()
        files = []
        for file_path in self.uploaded_files:
            if file_path.startswith(path):
                content = self.uploaded_files[file_path]["content"]
                files.append(
                    FileInfo(
                        name=Path(file_path).name,
                        path=file_path,
                        size=len(content),
                        is_directory=False,
                        modified_time=None,
                    )
                )

        # Add some default files
        if path == "/" or path == "/test":
            files.append(
                FileInfo(
                    name="existing_file.txt",
                    path="/test/existing_file.txt",
                    size=20,
                    is_directory=False,
                    modified_time=None,
                )
            )

        return files

    async def create_snapshot(self) -> str:
        """Mock snapshot creation."""
        self._ensure_not_closed()
        snapshot_id = f"snapshot_{len(self.snapshots)}"
        self.snapshots[snapshot_id] = {
            "files": self.uploaded_files.copy(),
            "commands": self.executed_commands.copy(),
        }
        return snapshot_id

    async def restore_snapshot(self, snapshot_id: str) -> None:
        """Mock snapshot restoration."""
        self._ensure_not_closed()
        if snapshot_id not in self.snapshots:
            raise ValueError(f"Snapshot not found: {snapshot_id}")

        snapshot = self.snapshots[snapshot_id]
        self.uploaded_files = snapshot["files"].copy()
        # Note: We don't restore commands as they're historical

    async def _cleanup(self) -> None:
        """Mock cleanup."""
        pass


class MockSandboxProvider(BaseSandboxProvider):
    """Mock sandbox provider for testing."""

    def __init__(self, config: ProviderConfig, name: str = "mock"):
        super().__init__(config)
        self._name = name
        self.created_sessions = []

    @property
    def name(self) -> str:
        return self._name

    async def _create_session(self, config: SandboxConfig) -> SandboxSession:
        """Create a mock sandbox session."""
        sandbox_id = f"mock_sandbox_{len(self.created_sessions)}"
        session = MockSandboxSession(sandbox_id, self, config)
        self.created_sessions.append(session)
        return session


@pytest.fixture
def mock_provider(provider_config: ProviderConfig) -> MockSandboxProvider:
    """Create a mock sandbox provider."""
    return MockSandboxProvider(provider_config)


@pytest.fixture
async def mock_session(
    mock_provider: MockSandboxProvider, test_config: SandboxConfig
) -> AsyncGenerator[MockSandboxSession, None]:
    """Create a mock sandbox session."""
    session = await mock_provider._create_session(test_config)
    try:
        yield session
    finally:
        await session.close()


@pytest.fixture
async def mock_sandbox(
    mock_provider: MockSandboxProvider, test_config: SandboxConfig
) -> AsyncGenerator[Sandbox, None]:
    """Create a mock sandbox instance."""
    sandbox = Sandbox(provider=mock_provider, config=test_config)
    async with sandbox:
        yield sandbox


# Environment fixtures
@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def env_vars() -> Generator[dict[str, str], None, None]:
    """Set up test environment variables."""
    original_env = os.environ.copy()
    test_env = {
        "GRAINCHAIN_DEFAULT_PROVIDER": "test",
        "E2B_API_KEY": "test_e2b_key",
        "MODAL_TOKEN_ID": "test_modal_id",
        "MODAL_TOKEN_SECRET": "test_modal_secret",
        "DAYTONA_API_KEY": "test_daytona_key",
    }

    # Set test environment variables
    for key, value in test_env.items():
        os.environ[key] = value

    try:
        yield test_env
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)


# Error simulation fixtures
@pytest.fixture
def failing_provider(provider_config: ProviderConfig) -> MockSandboxProvider:
    """Create a provider that fails operations."""

    class FailingProvider(MockSandboxProvider):
        async def _create_session(self, config: SandboxConfig) -> SandboxSession:
            raise GrainchainError("Simulated provider failure")

    return FailingProvider(provider_config, "failing")


@pytest.fixture
def timeout_provider(provider_config: ProviderConfig) -> MockSandboxProvider:
    """Create a provider that times out."""

    class TimeoutProvider(MockSandboxProvider):
        async def _create_session(self, config: SandboxConfig) -> SandboxSession:
            await asyncio.sleep(10)  # This will timeout in tests
            return await super()._create_session(config)

    return TimeoutProvider(provider_config, "timeout")


# Integration test fixtures (only if providers are available)
@pytest.fixture
def e2b_available() -> bool:
    """Check if E2B provider is available."""
    try:
        import e2b  # noqa: F401

        return bool(os.getenv("E2B_API_KEY"))
    except ImportError:
        return False


@pytest.fixture
def modal_available() -> bool:
    """Check if Modal provider is available."""
    try:
        import modal  # noqa: F401

        return bool(os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET"))
    except ImportError:
        return False


@pytest.fixture
def daytona_available() -> bool:
    """Check if Daytona provider is available."""
    try:
        import daytona_sdk  # noqa: F401

        return bool(os.getenv("DAYTONA_API_KEY"))
    except ImportError:
        return False


# Async test utilities
@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Test data fixtures
@pytest.fixture
def sample_python_code() -> str:
    """Sample Python code for testing."""
    return """
import sys
import json

def main():
    data = {"message": "Hello from Python!", "version": sys.version}
    print(json.dumps(data))

if __name__ == "__main__":
    main()
"""


@pytest.fixture
def sample_files() -> dict[str, str]:
    """Sample files for testing."""
    return {
        "hello.py": "print('Hello, World!')",
        "data.json": '{"test": "data", "numbers": [1, 2, 3]}',
        "script.sh": "#!/bin/bash\necho 'Shell script executed'",
        "requirements.txt": "requests==2.31.0\npandas==2.0.3",
    }


# Performance testing fixtures
@pytest.fixture
def performance_config() -> SandboxConfig:
    """Configuration optimized for performance testing."""
    return SandboxConfig(
        timeout=10,  # Shorter timeout for performance tests
        memory_limit="512MB",
        cpu_limit=0.5,
        working_directory="/tmp",
        auto_cleanup=True,
    )
