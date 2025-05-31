"""Base provider implementation for Grainchain."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from grainchain.core.interfaces import (
    SandboxProvider, 
    SandboxSession, 
    SandboxConfig, 
    SandboxStatus,
    ExecutionResult,
    FileInfo
)
from grainchain.core.config import ProviderConfig
from grainchain.core.exceptions import ProviderError, ConfigurationError

logger = logging.getLogger(__name__)


class BaseSandboxProvider(SandboxProvider):
    """
    Base implementation for sandbox providers.
    
    Provides common functionality and enforces the provider interface.
    Concrete providers should inherit from this class.
    """
    
    def __init__(self, config: ProviderConfig):
        """
        Initialize the provider with configuration.
        
        Args:
            config: Provider-specific configuration
        """
        self.config = config
        self._sessions: Dict[str, SandboxSession] = {}
        self._closed = False
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name - must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def _create_session(self, config: SandboxConfig) -> SandboxSession:
        """
        Create a new sandbox session - must be implemented by subclasses.
        
        Args:
            config: Sandbox configuration
            
        Returns:
            New sandbox session instance
        """
        pass
    
    async def create_sandbox(self, config: SandboxConfig) -> SandboxSession:
        """
        Create a new sandbox session.
        
        Args:
            config: Sandbox configuration
            
        Returns:
            New sandbox session instance
        """
        if self._closed:
            raise ProviderError("Provider has been closed", self.name)
        
        try:
            session = await self._create_session(config)
            self._sessions[session.sandbox_id] = session
            logger.info(f"Created sandbox {session.sandbox_id} with provider {self.name}")
            return session
        except Exception as e:
            logger.error(f"Failed to create sandbox with provider {self.name}: {e}")
            raise ProviderError(f"Failed to create sandbox: {e}", self.name, e)
    
    async def list_sandboxes(self) -> List[str]:
        """List active sandbox IDs."""
        return list(self._sessions.keys())
    
    async def get_sandbox_status(self, sandbox_id: str) -> SandboxStatus:
        """Get the status of a sandbox."""
        if sandbox_id not in self._sessions:
            return SandboxStatus.UNKNOWN
        
        session = self._sessions[sandbox_id]
        return session.status
    
    async def cleanup(self) -> None:
        """Clean up provider resources."""
        if self._closed:
            return
        
        # Close all active sessions
        cleanup_tasks = []
        for session in self._sessions.values():
            cleanup_tasks.append(session.close())
        
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        self._sessions.clear()
        self._closed = True
        logger.info(f"Cleaned up provider {self.name}")
    
    def _remove_session(self, sandbox_id: str) -> None:
        """Remove a session from tracking (called by sessions on close)."""
        self._sessions.pop(sandbox_id, None)
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def require_config_value(self, key: str) -> Any:
        """Get a required configuration value, raising error if missing."""
        value = self.config.get(key)
        if value is None:
            raise ConfigurationError(f"Required configuration '{key}' not found for provider {self.name}")
        return value


class BaseSandboxSession(SandboxSession):
    """
    Base implementation for sandbox sessions.
    
    Provides common functionality for session management.
    Concrete sessions should inherit from this class.
    """
    
    def __init__(self, sandbox_id: str, provider: BaseSandboxProvider, config: SandboxConfig):
        """
        Initialize the session.
        
        Args:
            sandbox_id: Unique identifier for this sandbox
            provider: Provider that created this session
            config: Sandbox configuration
        """
        self._sandbox_id = sandbox_id
        self._provider = provider
        self._config = config
        self._status = SandboxStatus.CREATING
        self._closed = False
    
    @property
    def sandbox_id(self) -> str:
        """Unique identifier for this sandbox."""
        return self._sandbox_id
    
    @property
    def status(self) -> SandboxStatus:
        """Current sandbox status."""
        return self._status
    
    @property
    def config(self) -> SandboxConfig:
        """Sandbox configuration."""
        return self._config
    
    def _set_status(self, status: SandboxStatus) -> None:
        """Update sandbox status."""
        old_status = self._status
        self._status = status
        if old_status != status:
            logger.debug(f"Sandbox {self.sandbox_id} status changed: {old_status.value} -> {status.value}")
    
    async def close(self) -> None:
        """Close and cleanup the sandbox session."""
        if self._closed:
            return
        
        try:
            await self._cleanup()
            self._set_status(SandboxStatus.STOPPED)
        except Exception as e:
            logger.warning(f"Error during sandbox cleanup: {e}")
            self._set_status(SandboxStatus.ERROR)
        finally:
            self._closed = True
            self._provider._remove_session(self.sandbox_id)
            logger.info(f"Closed sandbox {self.sandbox_id}")
    
    @abstractmethod
    async def _cleanup(self) -> None:
        """Provider-specific cleanup logic - must be implemented by subclasses."""
        pass
    
    def _ensure_not_closed(self) -> None:
        """Ensure the session is not closed."""
        if self._closed:
            raise ProviderError(f"Sandbox {self.sandbox_id} is closed", self._provider.name)
    
    # Default implementations that can be overridden
    
    async def create_snapshot(self) -> str:
        """Create a snapshot of the current sandbox state."""
        self._ensure_not_closed()
        raise NotImplementedError(f"Snapshots not supported by provider {self._provider.name}")
    
    async def restore_snapshot(self, snapshot_id: str) -> None:
        """Restore sandbox to a previous snapshot."""
        self._ensure_not_closed()
        raise NotImplementedError(f"Snapshots not supported by provider {self._provider.name}")

