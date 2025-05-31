"""E2B provider implementation for Grainchain."""

import asyncio
import time
from typing import List, Optional, Dict, Any, Union

from grainchain.core.interfaces import SandboxConfig, ExecutionResult, FileInfo, SandboxStatus
from grainchain.core.config import ProviderConfig
from grainchain.core.exceptions import ProviderError, AuthenticationError
from grainchain.providers.base import BaseSandboxProvider, BaseSandboxSession

try:
    from e2b import Sandbox as E2BSandbox
    from e2b.exceptions import E2BError, AuthenticationError as E2BAuthError
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
            # Create E2B sandbox
            e2b_sandbox = await E2BSandbox.create(
                template=self.template,
                api_key=self.api_key,
                timeout=config.timeout
            )
            
            session = E2BSandboxSession(
                sandbox_id=e2b_sandbox.id,
                provider=self,
                config=config,
                e2b_sandbox=e2b_sandbox
            )
            
            return session
            
        except E2BAuthError as e:
            raise AuthenticationError(f"E2B authentication failed: {e}", self.name)
        except E2BError as e:
            raise ProviderError(f"E2B sandbox creation failed: {e}", self.name, e)


class E2BSandboxSession(BaseSandboxSession):
    """E2B sandbox session implementation."""
    
    def __init__(
        self, 
        sandbox_id: str, 
        provider: E2BProvider, 
        config: SandboxConfig,
        e2b_sandbox: "E2BSandbox"
    ):
        """Initialize E2B session."""
        super().__init__(sandbox_id, provider, config)
        self.e2b_sandbox = e2b_sandbox
        self._set_status(SandboxStatus.RUNNING)
    
    async def execute(
        self, 
        command: str, 
        timeout: Optional[int] = None,
        working_dir: Optional[str] = None,
        environment: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        """Execute a command in the E2B sandbox."""
        self._ensure_not_closed()
        
        start_time = time.time()
        
        try:
            # Set working directory if specified
            if working_dir:
                await self.e2b_sandbox.filesystem.write(
                    f"/tmp/grainchain_workdir", 
                    working_dir
                )
                command = f"cd {working_dir} && {command}"
            
            # Set environment variables if specified
            if environment:
                env_commands = []
                for key, value in environment.items():
                    env_commands.append(f"export {key}='{value}'")
                if env_commands:
                    command = " && ".join(env_commands) + " && " + command
            
            # Execute command
            result = await self.e2b_sandbox.process.start_and_wait(
                cmd=command,
                timeout=timeout or self.config.timeout
            )
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.exit_code,
                execution_time=execution_time,
                success=result.exit_code == 0,
                command=command
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                stdout="",
                stderr=str(e),
                return_code=-1,
                execution_time=execution_time,
                success=False,
                command=command
            )
    
    async def upload_file(
        self, 
        path: str, 
        content: Union[str, bytes],
        mode: str = "w"
    ) -> None:
        """Upload a file to the E2B sandbox."""
        self._ensure_not_closed()
        
        try:
            if isinstance(content, str):
                await self.e2b_sandbox.filesystem.write(path, content)
            else:
                # For binary content, write as text with base64 encoding
                import base64
                encoded_content = base64.b64encode(content).decode('utf-8')
                await self.e2b_sandbox.filesystem.write(f"{path}.b64", encoded_content)
                # Decode on the sandbox side
                await self.execute(f"base64 -d {path}.b64 > {path} && rm {path}.b64")
                
        except Exception as e:
            raise ProviderError(f"File upload failed: {e}", self._provider.name, e)
    
    async def download_file(self, path: str) -> bytes:
        """Download a file from the E2B sandbox."""
        self._ensure_not_closed()
        
        try:
            content = await self.e2b_sandbox.filesystem.read(path)
            if isinstance(content, str):
                return content.encode('utf-8')
            return content
            
        except Exception as e:
            raise ProviderError(f"File download failed: {e}", self._provider.name, e)
    
    async def list_files(self, path: str = "/") -> List[FileInfo]:
        """List files in the E2B sandbox."""
        self._ensure_not_closed()
        
        try:
            # Use ls command to get file information
            result = await self.execute(f"ls -la {path}")
            
            if not result.success:
                raise ProviderError(f"Failed to list files: {result.stderr}", self._provider.name)
            
            files = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip total line
            
            for line in lines:
                if not line.strip():
                    continue
                    
                parts = line.split()
                if len(parts) >= 9:
                    permissions = parts[0]
                    size = int(parts[4]) if parts[4].isdigit() else 0
                    name = ' '.join(parts[8:])
                    is_directory = permissions.startswith('d')
                    
                    files.append(FileInfo(
                        path=f"{path.rstrip('/')}/{name}",
                        name=name,
                        size=size,
                        is_directory=is_directory,
                        modified_time=time.time(),  # E2B doesn't provide exact time
                        permissions=permissions
                    ))
            
            return files
            
        except Exception as e:
            raise ProviderError(f"File listing failed: {e}", self._provider.name, e)
    
    async def create_snapshot(self) -> str:
        """Create a snapshot of the current E2B sandbox state."""
        self._ensure_not_closed()
        
        try:
            # E2B doesn't have built-in snapshots, so we'll simulate with a timestamp
            snapshot_id = f"e2b_snapshot_{int(time.time())}"
            
            # Create a marker file to indicate snapshot
            await self.e2b_sandbox.filesystem.write(
                f"/tmp/grainchain_snapshot_{snapshot_id}", 
                f"Snapshot created at {time.time()}"
            )
            
            return snapshot_id
            
        except Exception as e:
            raise ProviderError(f"Snapshot creation failed: {e}", self._provider.name, e)
    
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

