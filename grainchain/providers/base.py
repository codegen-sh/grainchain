"""
Base classes for sandbox providers and sessions.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
import os
from pathlib import Path


class BaseSandboxSession(ABC):
    """Base class for sandbox sessions."""
    
    def __init__(self, session_id: str, provider: 'BaseSandboxProvider'):
        self.session_id = session_id
        self.provider = provider
        self._is_active = False
    
    @property
    def is_active(self) -> bool:
        """Check if the session is active."""
        return self._is_active
    
    @abstractmethod
    async def start(self) -> None:
        """Start the sandbox session."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the sandbox session."""
        pass
    
    @abstractmethod
    async def execute_command(
        self, 
        command: str, 
        working_dir: Optional[str] = None,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a command in the sandbox.
        
        Args:
            command: Command to execute
            working_dir: Working directory for the command
            timeout: Command timeout in seconds
            env: Environment variables
            
        Returns:
            Dict containing:
                - stdout: Command output
                - stderr: Command errors
                - exit_code: Exit code
                - execution_time: Time taken to execute
        """
        pass
    
    @abstractmethod
    async def upload_file(self, local_path: str, remote_path: str) -> bool:
        """
        Upload a file to the sandbox.
        
        Args:
            local_path: Path to local file
            remote_path: Path in sandbox
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def download_file(self, remote_path: str, local_path: str) -> bool:
        """
        Download a file from the sandbox.
        
        Args:
            remote_path: Path in sandbox
            local_path: Path to save locally
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_files(self, path: str = "/") -> List[Dict[str, Any]]:
        """
        List files in a directory.
        
        Args:
            path: Directory path
            
        Returns:
            List of file information dictionaries
        """
        pass
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()


class BaseSandboxProvider(ABC):
    """Base class for sandbox providers."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._sessions: Dict[str, BaseSandboxSession] = {}
    
    @abstractmethod
    async def create_session(
        self, 
        session_id: Optional[str] = None,
        image: Optional[str] = None,
        **kwargs
    ) -> BaseSandboxSession:
        """
        Create a new sandbox session.
        
        Args:
            session_id: Optional session identifier
            image: Container/VM image to use
            **kwargs: Additional provider-specific options
            
        Returns:
            New sandbox session
        """
        pass
    
    @abstractmethod
    async def destroy_session(self, session_id: str) -> bool:
        """
        Destroy a sandbox session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    async def get_session(self, session_id: str) -> Optional[BaseSandboxSession]:
        """Get an existing session by ID."""
        return self._sessions.get(session_id)
    
    async def list_sessions(self) -> List[str]:
        """List all active session IDs."""
        return list(self._sessions.keys())
    
    async def cleanup_all_sessions(self) -> None:
        """Clean up all active sessions."""
        for session_id in list(self._sessions.keys()):
            await self.destroy_session(session_id)
    
    def _register_session(self, session: BaseSandboxSession) -> None:
        """Register a session with the provider."""
        self._sessions[session.session_id] = session
    
    def _unregister_session(self, session_id: str) -> None:
        """Unregister a session from the provider."""
        self._sessions.pop(session_id, None)

