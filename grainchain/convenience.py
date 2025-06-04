"""
Convenience functions and classes for simplified grainchain usage.

This module provides additional convenience functions that make common
grainchain operations simpler and more intuitive.
"""

import asyncio
import threading
from typing import Any

from grainchain.core.config import SandboxConfig
from grainchain.core.sandbox import Sandbox


class QuickSandbox:
    """
    A simplified sandbox interface for users who don't need full async control.

    This class provides synchronous methods that handle async operations internally,
    making grainchain more accessible to users unfamiliar with async programming.
    """

    def __init__(self, provider: str = "local", **config_kwargs):
        """
        Initialize a QuickSandbox.

        Args:
            provider: Provider name (local, e2b, daytona, morph, modal)
            **config_kwargs: Configuration options
        """
        self.provider = provider
        self.config_kwargs = config_kwargs
        self._sandbox: Sandbox | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None

    def __enter__(self):
        """Enter context manager."""
        # Check if we're already in an async context
        try:
            # If this succeeds, we're in an async context
            asyncio.get_running_loop()
            # Use a thread to run the async code
            self._start_in_thread()
        except RuntimeError:
            # No running loop, we can create our own
            self._start_in_new_loop()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if self._thread:
            # Running in thread
            self._stop_in_thread()
        else:
            # Running in our own loop
            self._stop_in_loop()

    def _start_in_new_loop(self):
        """Start sandbox in a new event loop."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        config = SandboxConfig(**self.config_kwargs)
        self._sandbox = Sandbox(provider=self.provider, config=config)

        # Start the sandbox
        self._loop.run_until_complete(self._sandbox.__aenter__())

    def _stop_in_loop(self):
        """Stop sandbox in our event loop."""
        if self._sandbox and self._loop:
            self._loop.run_until_complete(self._sandbox.__aexit__(None, None, None))
        if self._loop:
            self._loop.close()

    def _start_in_thread(self):
        """Start sandbox in a separate thread."""
        import queue

        result_queue = queue.Queue()

        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                config = SandboxConfig(**self.config_kwargs)
                sandbox = Sandbox(provider=self.provider, config=config)

                # Start the sandbox
                loop.run_until_complete(sandbox.__aenter__())
                result_queue.put(("success", sandbox, loop))

                # Keep the loop running
                loop.run_forever()
            except Exception as e:
                result_queue.put(("error", e, None))
            finally:
                loop.close()

        self._thread = threading.Thread(target=run_async, daemon=True)
        self._thread.start()

        # Wait for initialization
        result_type, result, loop = result_queue.get(timeout=30)
        if result_type == "error":
            raise result

        self._sandbox = result
        self._loop = loop

    def _stop_in_thread(self):
        """Stop sandbox in thread."""
        if self._sandbox and self._loop:
            # Schedule cleanup and stop the loop
            asyncio.run_coroutine_threadsafe(
                self._sandbox.__aexit__(None, None, None), self._loop
            ).result(timeout=30)

            self._loop.call_soon_threadsafe(self._loop.stop)

        if self._thread:
            self._thread.join(timeout=30)

    def _run_async(self, coro):
        """Run an async coroutine, handling both thread and loop cases."""
        if self._thread:
            # Running in thread
            future = asyncio.run_coroutine_threadsafe(coro, self._loop)
            return future.result(timeout=30)
        else:
            # Running in our own loop
            return self._loop.run_until_complete(coro)

    def execute(self, command: str) -> Any:
        """
        Execute a command synchronously.

        Args:
            command: Command to execute

        Returns:
            Execution result
        """
        if not self._sandbox:
            raise RuntimeError("QuickSandbox not properly initialized")

        return self._run_async(self._sandbox.execute(command))

    def upload_file(self, path: str, content: str) -> None:
        """
        Upload a file synchronously.

        Args:
            path: File path in sandbox
            content: File content
        """
        if not self._sandbox:
            raise RuntimeError("QuickSandbox not properly initialized")

        self._run_async(self._sandbox.upload_file(path, content))

    def download_file(self, path: str) -> bytes:
        """
        Download a file synchronously.

        Args:
            path: File path in sandbox

        Returns:
            File content as bytes
        """
        if not self._sandbox:
            raise RuntimeError("QuickSandbox not properly initialized")

        return self._run_async(self._sandbox.download_file(path))

    def list_files(self, path: str = ".") -> list:
        """
        List files synchronously.

        Args:
            path: Directory path to list

        Returns:
            List of file information
        """
        if not self._sandbox:
            raise RuntimeError("QuickSandbox not properly initialized")

        return self._run_async(self._sandbox.list_files(path))


def quick_execute(command: str, provider: str = "local", **kwargs) -> Any:
    """
    Execute a single command quickly without managing context.

    Args:
        command: Command to execute
        provider: Provider to use
        **kwargs: Additional configuration options

    Returns:
        Execution result

    Example:
        >>> result = quick_execute("echo 'Hello World!'")
        >>> print(result.stdout)
    """
    with QuickSandbox(provider=provider, **kwargs) as sandbox:
        return sandbox.execute(command)


def quick_python(code: str, provider: str = "local", **kwargs) -> Any:
    """
    Execute Python code quickly.

    Args:
        code: Python code to execute
        provider: Provider to use
        **kwargs: Additional configuration options

    Returns:
        Execution result

    Example:
        >>> result = quick_python("print(2 + 2)")
        >>> print(result.stdout)
    """
    command = f"python3 -c '{code}'"
    return quick_execute(command, provider=provider, **kwargs)


def quick_script(
    script_content: str, filename: str = "script.py", provider: str = "local", **kwargs
) -> Any:
    """
    Upload and execute a script quickly.

    Args:
        script_content: Content of the script
        filename: Name of the script file
        provider: Provider to use
        **kwargs: Additional configuration options

    Returns:
        Execution result

    Example:
        >>> script = '''
        ... print("Hello from script!")
        ... print(f"2 + 2 = {2 + 2}")
        ... '''
        >>> result = quick_script(script)
        >>> print(result.stdout)
    """
    with QuickSandbox(provider=provider, **kwargs) as sandbox:
        sandbox.upload_file(filename, script_content)
        if filename.endswith(".py"):
            return sandbox.execute(f"python3 {filename}")
        else:
            return sandbox.execute(f"./{filename}")


class ConfigPresets:
    """Predefined configuration presets for common use cases."""

    @staticmethod
    def development() -> dict[str, Any]:
        """Configuration preset for development work."""
        return {
            "timeout": 300,  # 5 minutes
            "working_directory": ".",
            "auto_cleanup": True,
            "environment_vars": {"ENV": "development"},
        }

    @staticmethod
    def testing() -> dict[str, Any]:
        """Configuration preset for testing."""
        return {
            "timeout": 60,
            "working_directory": ".",
            "auto_cleanup": True,
            "environment_vars": {"ENV": "testing"},
        }

    @staticmethod
    def production() -> dict[str, Any]:
        """Configuration preset for production use."""
        return {
            "timeout": 30,
            "working_directory": ".",
            "auto_cleanup": True,
            "environment_vars": {"ENV": "production"},
        }

    @staticmethod
    def data_science() -> dict[str, Any]:
        """Configuration preset for data science work."""
        return {
            "timeout": 600,  # 10 minutes for long-running analysis
            "working_directory": ".",
            "auto_cleanup": False,  # Keep data around
            "environment_vars": {
                "ENV": "data_science",
                "PYTHONPATH": "/opt/conda/lib/python3.12/site-packages",
            },
        }


def create_dev_sandbox(provider: str = "local") -> Sandbox:
    """Create a sandbox configured for development work."""
    config = SandboxConfig(**ConfigPresets.development())
    return Sandbox(provider=provider, config=config)


def create_test_sandbox(provider: str = "local") -> Sandbox:
    """Create a sandbox configured for testing."""
    config = SandboxConfig(**ConfigPresets.testing())
    return Sandbox(provider=provider, config=config)


def create_data_sandbox(provider: str = "local") -> Sandbox:
    """Create a sandbox configured for data science work."""
    config = SandboxConfig(**ConfigPresets.data_science())
    return Sandbox(provider=provider, config=config)
