"""
LangChain tools for Grainchain sandbox integration.
"""

import asyncio
import logging
from typing import Any, Optional, Union

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from grainchain.core.interfaces import SandboxConfig
from grainchain.core.sandbox import Sandbox

logger = logging.getLogger(__name__)


class SandboxExecuteInput(BaseModel):
    """Input schema for sandbox execution tool."""

    command: str = Field(description="Command to execute in the sandbox")
    timeout: Optional[int] = Field(
        default=None, description="Timeout in seconds (optional)"
    )
    working_dir: Optional[str] = Field(
        default=None, description="Working directory for command execution (optional)"
    )


class SandboxTool(BaseTool):
    """
    A LangChain tool that executes commands in a Grainchain sandbox.

    This tool provides a LangGraph-compatible interface for executing
    commands in various sandbox providers through Grainchain's unified API.
    """

    name: str = "sandbox_execute"
    description: str = (
        "Execute commands in a secure sandbox environment. "
        "Use this tool to run shell commands, Python scripts, or any other "
        "executable code safely. The sandbox provides isolation and can "
        "handle file operations, package installations, and more."
    )
    args_schema: type[BaseModel] = SandboxExecuteInput

    def __init__(
        self,
        provider: Optional[Union[str, Any]] = None,
        config: Optional[SandboxConfig] = None,
        **kwargs,
    ):
        """
        Initialize the SandboxTool.

        Args:
            provider: Sandbox provider name or instance (e.g., 'local', 'e2b')
            config: Sandbox configuration
            **kwargs: Additional arguments passed to BaseTool
        """
        super().__init__(**kwargs)
        self._provider = provider
        self._config = config or SandboxConfig()
        self._sandbox: Optional[Sandbox] = None

    async def _arun(
        self,
        command: str,
        timeout: Optional[int] = None,
        working_dir: Optional[str] = None,
        run_manager: Optional[Any] = None,
    ) -> str:
        """
        Asynchronously execute a command in the sandbox.

        Args:
            command: Command to execute
            timeout: Execution timeout in seconds
            working_dir: Working directory for execution
            run_manager: LangChain run manager (unused)

        Returns:
            Command output as a string
        """
        try:
            # Create sandbox if not exists
            if self._sandbox is None:
                self._sandbox = Sandbox(provider=self._provider, config=self._config)
                await self._sandbox.create()

            # Execute command
            result = await self._sandbox.execute(
                command=command, timeout=timeout, working_dir=working_dir
            )

            # Format output
            output_parts = []
            if result.stdout:
                output_parts.append(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                output_parts.append(f"STDERR:\n{result.stderr}")

            output_parts.append(f"Return code: {result.return_code}")
            output_parts.append(f"Execution time: {result.execution_time:.2f}s")

            return "\n\n".join(output_parts)

        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            return f"Error executing command: {str(e)}"

    def _run(
        self,
        command: str,
        timeout: Optional[int] = None,
        working_dir: Optional[str] = None,
        run_manager: Optional[Any] = None,
    ) -> str:
        """
        Synchronously execute a command in the sandbox.

        This is a wrapper around the async implementation for compatibility
        with synchronous LangChain usage.
        """
        try:
            # Check if we're already in an async context
            try:
                asyncio.get_running_loop()
                # If we're in an async context, we can't use run_until_complete
                # Instead, we need to schedule the coroutine
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        lambda: asyncio.run(
                            self._arun(command, timeout, working_dir, run_manager)
                        )
                    )
                    return future.result()
            except RuntimeError:
                # No running loop, we can create one
                return asyncio.run(
                    self._arun(command, timeout, working_dir, run_manager)
                )
        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            return f"Error executing command: {str(e)}"

    async def cleanup(self) -> None:
        """Clean up the sandbox resources."""
        if self._sandbox:
            await self._sandbox.close()
            self._sandbox = None

    def __del__(self):
        """Cleanup when the tool is garbage collected."""
        if self._sandbox:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, schedule cleanup
                    loop.create_task(self.cleanup())
                else:
                    # If loop is not running, run cleanup
                    loop.run_until_complete(self.cleanup())
            except Exception:
                # Ignore cleanup errors during garbage collection
                pass


class SandboxFileUploadInput(BaseModel):
    """Input schema for sandbox file upload tool."""

    path: str = Field(description="Destination path in the sandbox")
    content: str = Field(description="File content to upload")
    mode: str = Field(
        default="w", description="File mode ('w' for text, 'wb' for binary)"
    )


class SandboxFileUploadTool(BaseTool):
    """
    A LangChain tool for uploading files to a Grainchain sandbox.
    """

    name: str = "sandbox_upload_file"
    description: str = (
        "Upload a file to the sandbox environment. "
        "Use this to create files, scripts, or data that can be used "
        "by subsequent sandbox commands."
    )
    args_schema: type[BaseModel] = SandboxFileUploadInput

    def __init__(self, sandbox_tool: SandboxTool, **kwargs):
        """
        Initialize the file upload tool.

        Args:
            sandbox_tool: The main SandboxTool instance to use for file operations
            **kwargs: Additional arguments passed to BaseTool
        """
        super().__init__(**kwargs)
        self._sandbox_tool = sandbox_tool

    async def _arun(
        self,
        path: str,
        content: str,
        mode: str = "w",
        run_manager: Optional[Any] = None,
    ) -> str:
        """
        Asynchronously upload a file to the sandbox.

        Args:
            path: Destination path in the sandbox
            content: File content
            mode: File mode
            run_manager: LangChain run manager (unused)

        Returns:
            Success message
        """
        try:
            # Ensure sandbox exists
            if self._sandbox_tool._sandbox is None:
                self._sandbox_tool._sandbox = Sandbox(
                    provider=self._sandbox_tool._provider,
                    config=self._sandbox_tool._config,
                )
                await self._sandbox_tool._sandbox.create()

            # Upload file
            await self._sandbox_tool._sandbox.upload_file(path, content, mode)

            return f"Successfully uploaded file to {path}"

        except Exception as e:
            logger.error(f"File upload failed: {e}")
            return f"Error uploading file: {str(e)}"

    def _run(
        self,
        path: str,
        content: str,
        mode: str = "w",
        run_manager: Optional[Any] = None,
    ) -> str:
        """
        Synchronously upload a file to the sandbox.
        """
        try:
            # Check if we're already in an async context
            try:
                asyncio.get_running_loop()
                # If we're in an async context, we can't use run_until_complete
                # Instead, we need to schedule the coroutine
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        lambda: asyncio.run(
                            self._arun(path, content, mode, run_manager)
                        )
                    )
                    return future.result()
            except RuntimeError:
                # No running loop, we can create one
                return asyncio.run(self._arun(path, content, mode, run_manager))
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            return f"Error uploading file: {str(e)}"


class SandboxSnapshotInput(BaseModel):
    """Input schema for sandbox snapshot tool."""

    action: str = Field(
        description="Action to perform: 'create' to create a snapshot, 'restore' to restore from snapshot_id"
    )
    snapshot_id: Optional[str] = Field(
        default=None,
        description="Snapshot ID to restore (required when action='restore')",
    )


class SandboxSnapshotTool(BaseTool):
    """
    A LangChain tool for creating and restoring sandbox snapshots.
    """

    name: str = "sandbox_snapshot"
    description: str = (
        "Create or restore sandbox snapshots. "
        "Use 'create' action to save the current state, "
        "or 'restore' action with a snapshot_id to revert to a previous state."
    )
    args_schema: type[BaseModel] = SandboxSnapshotInput

    def __init__(self, sandbox_tool: SandboxTool, **kwargs):
        """
        Initialize the snapshot tool.

        Args:
            sandbox_tool: The main SandboxTool instance to use for snapshot operations
            **kwargs: Additional arguments passed to BaseTool
        """
        super().__init__(**kwargs)
        self._sandbox_tool = sandbox_tool

    async def _arun(
        self,
        action: str,
        snapshot_id: Optional[str] = None,
        run_manager: Optional[Any] = None,
    ) -> str:
        """
        Asynchronously perform snapshot operations.

        Args:
            action: 'create' or 'restore'
            snapshot_id: Snapshot ID for restore operations
            run_manager: LangChain run manager (unused)

        Returns:
            Operation result message
        """
        try:
            # Ensure sandbox exists
            if self._sandbox_tool._sandbox is None:
                self._sandbox_tool._sandbox = Sandbox(
                    provider=self._sandbox_tool._provider,
                    config=self._sandbox_tool._config,
                )
                await self._sandbox_tool._sandbox.create()

            if action == "create":
                snapshot_id = await self._sandbox_tool._sandbox.create_snapshot()
                return f"Created snapshot with ID: {snapshot_id}"
            elif action == "restore":
                if not snapshot_id:
                    return "Error: snapshot_id is required for restore action"
                await self._sandbox_tool._sandbox.restore_snapshot(snapshot_id)
                return f"Restored snapshot: {snapshot_id}"
            else:
                return f"Error: Unknown action '{action}'. Use 'create' or 'restore'."

        except Exception as e:
            logger.error(f"Snapshot operation failed: {e}")
            return f"Error performing snapshot operation: {str(e)}"

    def _run(
        self,
        action: str,
        snapshot_id: Optional[str] = None,
        run_manager: Optional[Any] = None,
    ) -> str:
        """
        Synchronously perform snapshot operations.
        """
        try:
            # Check if we're already in an async context
            try:
                asyncio.get_running_loop()
                # If we're in an async context, we can't use run_until_complete
                # Instead, we need to schedule the coroutine
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        lambda: asyncio.run(
                            self._arun(action, snapshot_id, run_manager)
                        )
                    )
                    return future.result()
            except RuntimeError:
                # No running loop, we can create one
                return asyncio.run(self._arun(action, snapshot_id, run_manager))
        except Exception as e:
            logger.error(f"Snapshot operation failed: {e}")
            return f"Error performing snapshot operation: {str(e)}"
