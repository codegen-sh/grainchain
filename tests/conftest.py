"""
Pytest configuration and fixtures for Grainchain tests.

This module provides common fixtures and configuration for both unit and integration tests.
"""

import asyncio
import os
import tempfile
import uuid
from pathlib import Path
from typing import AsyncGenerator, Dict, Generator, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from grainchain import Sandbox, SandboxConfig
from grainchain.core.interfaces import ExecutionResult, FileInfo, SandboxProvider, SandboxSession
from grainchain.providers.local import LocalProvider


class MockSandboxProvider(SandboxProvider):
    """Mock sandbox provider for testing."""
    
    def __init__(self, name: str = "mock"):
        self.name = name
        self.sessions: Dict[str, "MockSandboxSession"] = {}
        self.should_fail = False
        self.fail_message = "Mock provider failure"
    
    @property
    def provider_name(self) -> str:
        return self.name
    
    async def create_session(self, config: SandboxConfig) -> "MockSandboxSession":
        if self.should_fail:
            raise Exception(self.fail_message)
        
        session_id = str(uuid.uuid4())
        session = MockSandboxSession(session_id, config)
        self.sessions[session_id] = session
        return session
    
    async def cleanup(self) -> None:
        """Clean up all sessions."""
        for session in self.sessions.values():
            await session.cleanup()
        self.sessions.clear()


class MockSandboxSession(SandboxSession):
    """Mock sandbox session for testing."""
    
    def __init__(self, session_id: str, config: SandboxConfig):
        self.session_id = session_id
        self.config = config
        self.files: Dict[str, bytes] = {}
        self.snapshots: Dict[str, Dict[str, bytes]] = {}
        self.is_active = True
        self.execution_results: Dict[str, ExecutionResult] = {}
        self.should_fail_execute = False
        self.should_fail_upload = False
        self.should_fail_download = False
    
    async def execute(
        self, 
        command: str, 
        timeout: Optional[int] = None,
        working_dir: Optional[str] = None
    ) -> ExecutionResult:
        if self.should_fail_execute:
            return ExecutionResult(
                stdout="",
                stderr="Mock execution failure",
                return_code=1,
                execution_time=0.1,
                success=False
            )
        
        # Mock some common commands
        if command == "echo 'Hello, World!'":
            return ExecutionResult(
                stdout="Hello, World!\n",
                stderr="",
                return_code=0,
                execution_time=0.1,
                success=True
            )
        elif command == "pwd":
            return ExecutionResult(
                stdout=working_dir or "/workspace\n",
                stderr="",
                return_code=0,
                execution_time=0.1,
                success=True
            )
        elif command.startswith("python"):
            return ExecutionResult(
                stdout="Python execution result\n",
                stderr="",
                return_code=0,
                execution_time=0.2,
                success=True
            )
        else:
            return ExecutionResult(
                stdout=f"Mock output for: {command}\n",
                stderr="",
                return_code=0,
                execution_time=0.1,
                success=True
            )
    
    async def upload_file(self, path: str, content: bytes) -> None:
        if self.should_fail_upload:
            raise Exception("Mock upload failure")
        self.files[path] = content
    
    async def download_file(self, path: str) -> bytes:
        if self.should_fail_download:
            raise Exception("Mock download failure")
        if path not in self.files:
            raise FileNotFoundError(f"File not found: {path}")
        return self.files[path]
    
    async def list_files(self, path: str = "/") -> list[FileInfo]:
        files = []
        for file_path in self.files.keys():
            if file_path.startswith(path):
                files.append(FileInfo(
                    name=Path(file_path).name,
                    path=file_path,
                    size=len(self.files[file_path]),
                    is_directory=False,
                    modified_time=None
                ))
        return files
    
    async def create_snapshot(self) -> str:
        snapshot_id = str(uuid.uuid4())
        self.snapshots[snapshot_id] = self.files.copy()
        return snapshot_id
    
    async def restore_snapshot(self, snapshot_id: str) -> None:
        if snapshot_id not in self.snapshots:
            raise ValueError(f"Snapshot not found: {snapshot_id}")
        self.files = self.snapshots[snapshot_id].copy()
    
    async def cleanup(self) -> None:
        self.is_active = False
        self.files.clear()
        self.snapshots.clear()


@pytest.fixture
def mock_provider() -> MockSandboxProvider:
    """Provide a mock sandbox provider for testing."""
    return MockSandboxProvider()


@pytest.fixture
def sandbox_config() -> SandboxConfig:
    """Provide a basic sandbox configuration for testing."""
    return SandboxConfig(
        timeout=60,
        working_directory="/workspace",
        environment_vars={"TEST_VAR": "test_value"},
        auto_cleanup=True
    )


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
async def mock_sandbox(mock_provider: MockSandboxProvider, sandbox_config: SandboxConfig) -> AsyncGenerator[Sandbox, None]:
    """Provide a sandbox with mock provider for testing."""
    sandbox = Sandbox(provider=mock_provider, config=sandbox_config)
    async with sandbox:
        yield sandbox


@pytest.fixture
async def local_sandbox(temp_dir: Path) -> AsyncGenerator[Sandbox, None]:
    """Provide a local sandbox for integration testing."""
    config = SandboxConfig(
        working_directory=str(temp_dir),
        timeout=30,
        auto_cleanup=True
    )
    
    sandbox = Sandbox(provider=LocalProvider(), config=config)
    async with sandbox:
        yield sandbox


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_python_code() -> str:
    """Provide sample Python code for testing."""
    return """
import json
import sys

def main():
    data = {"message": "Hello from Python!", "status": "success"}
    print(json.dumps(data))
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""


@pytest.fixture
def sample_text_file() -> str:
    """Provide sample text content for file operations testing."""
    return "This is a test file.\nIt has multiple lines.\nUsed for testing file operations."


@pytest.fixture
def sample_binary_data() -> bytes:
    """Provide sample binary data for testing."""
    return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"


# Environment variable fixtures for integration tests
@pytest.fixture
def e2b_api_key() -> Optional[str]:
    """Get E2B API key from environment for integration tests."""
    return os.getenv("E2B_API_KEY")


@pytest.fixture
def modal_token_id() -> Optional[str]:
    """Get Modal token ID from environment for integration tests."""
    return os.getenv("MODAL_TOKEN_ID")


@pytest.fixture
def modal_token_secret() -> Optional[str]:
    """Get Modal token secret from environment for integration tests."""
    return os.getenv("MODAL_TOKEN_SECRET")


# Skip markers for integration tests
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "e2b: mark test as requiring E2B credentials"
    )
    config.addinivalue_line(
        "markers", "modal: mark test as requiring Modal credentials"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add skip markers based on environment."""
    skip_e2b = pytest.mark.skip(reason="E2B_API_KEY not set")
    skip_modal = pytest.mark.skip(reason="MODAL_TOKEN_ID or MODAL_TOKEN_SECRET not set")
    
    for item in items:
        if "e2b" in item.keywords:
            if not os.getenv("E2B_API_KEY"):
                item.add_marker(skip_e2b)
        
        if "modal" in item.keywords:
            if not (os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET")):
                item.add_marker(skip_modal)

