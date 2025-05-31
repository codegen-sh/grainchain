"""
Docker provider for sandbox execution.
"""

import asyncio
import time
import uuid
import tarfile
import io
import os
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import logging

try:
    import docker
    from docker.errors import DockerException, APIError, ContainerError, ImageNotFound
except ImportError:
    raise ImportError(
        "Docker library not found. Install with: pip install docker"
    )

from .base import BaseSandboxProvider, BaseSandboxSession

logger = logging.getLogger(__name__)


class DockerSession(BaseSandboxSession):
    """Docker-based sandbox session."""
    
    def __init__(
        self, 
        session_id: str, 
        provider: 'DockerProvider',
        image: str = "ubuntu:20.04",
        **kwargs
    ):
        super().__init__(session_id, provider)
        self.image = image
        self.container = None
        self.docker_client = provider.docker_client
        self.container_config = kwargs
        
        # Default container configuration
        self.default_config = {
            'detach': True,
            'tty': True,
            'stdin_open': True,
            'working_dir': '/workspace',
            'environment': {},
            'volumes': {},
            'network_mode': 'bridge',
            'mem_limit': '1g',
            'cpu_count': 1,
        }
        
        # Merge with provided config
        self.container_config = {**self.default_config, **self.container_config}
    
    async def start(self) -> None:
        """Start the Docker container."""
        if self._is_active:
            return
        
        try:
            # Ensure image exists
            await self._ensure_image()
            
            # Create and start container
            self.container = self.docker_client.containers.run(
                image=self.image,
                name=f"grainchain-{self.session_id}",
                command="tail -f /dev/null",  # Keep container running
                **self.container_config
            )
            
            self._is_active = True
            logger.info(f"Started Docker container {self.container.id} for session {self.session_id}")
            
        except Exception as e:
            logger.error(f"Failed to start Docker container: {e}")
            raise RuntimeError(f"Failed to start Docker container: {e}")
    
    async def stop(self) -> None:
        """Stop and remove the Docker container."""
        if not self._is_active or not self.container:
            return
        
        try:
            self.container.stop(timeout=10)
            self.container.remove()
            self._is_active = False
            logger.info(f"Stopped Docker container for session {self.session_id}")
            
        except Exception as e:
            logger.error(f"Failed to stop Docker container: {e}")
            # Try to force remove
            try:
                self.container.remove(force=True)
                self._is_active = False
            except Exception as force_error:
                logger.error(f"Failed to force remove container: {force_error}")
                raise RuntimeError(f"Failed to stop Docker container: {e}")
    
    async def execute_command(
        self, 
        command: str, 
        working_dir: Optional[str] = None,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Execute a command in the Docker container."""
        if not self._is_active or not self.container:
            raise RuntimeError("Session is not active")
        
        start_time = time.time()
        
        try:
            # Prepare environment
            exec_env = self.container_config.get('environment', {}).copy()
            if env:
                exec_env.update(env)
            
            # Execute command
            exec_result = self.container.exec_run(
                cmd=command,
                workdir=working_dir or self.container_config.get('working_dir', '/workspace'),
                environment=exec_env,
                demux=True,
                tty=False
            )
            
            execution_time = time.time() - start_time
            
            # Parse output
            stdout = exec_result.output[0].decode('utf-8') if exec_result.output[0] else ""
            stderr = exec_result.output[1].decode('utf-8') if exec_result.output[1] else ""
            
            return {
                'stdout': stdout,
                'stderr': stderr,
                'exit_code': exec_result.exit_code,
                'execution_time': execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Command execution failed: {e}")
            return {
                'stdout': "",
                'stderr': str(e),
                'exit_code': -1,
                'execution_time': execution_time
            }
    
    async def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload a file to the Docker container."""
        if not self._is_active or not self.container:
            raise RuntimeError("Session is not active")
        
        try:
            local_path = Path(local_path)
            if not local_path.exists():
                logger.error(f"Local file does not exist: {local_path}")
                return False
            
            # Create tar archive in memory
            tar_stream = io.BytesIO()
            with tarfile.open(fileobj=tar_stream, mode='w') as tar:
                tar.add(local_path, arcname=Path(remote_path).name)
            
            tar_stream.seek(0)
            
            # Upload to container
            remote_dir = str(Path(remote_path).parent)
            self.container.put_archive(remote_dir, tar_stream.getvalue())
            
            logger.info(f"Uploaded {local_path} to {remote_path}")
            return True
            
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            return False
    
    async def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download a file from the Docker container."""
        if not self._is_active or not self.container:
            raise RuntimeError("Session is not active")
        
        try:
            # Get file from container
            tar_stream, _ = self.container.get_archive(remote_path)
            
            # Extract from tar
            tar_data = b''.join(tar_stream)
            tar_file = tarfile.open(fileobj=io.BytesIO(tar_data))
            
            # Extract to local path
            local_dir = Path(local_path).parent
            local_dir.mkdir(parents=True, exist_ok=True)
            
            tar_file.extractall(local_dir)
            
            # Rename extracted file to desired name
            extracted_name = tar_file.getnames()[0]
            extracted_path = local_dir / extracted_name
            final_path = Path(local_path)
            
            if extracted_path != final_path:
                extracted_path.rename(final_path)
            
            logger.info(f"Downloaded {remote_path} to {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"File download failed: {e}")
            return False
    
    async def list_files(self, path: str = "/") -> List[Dict[str, Any]]:
        """List files in a directory."""
        if not self._is_active or not self.container:
            raise RuntimeError("Session is not active")
        
        try:
            # Use ls command to list files
            result = await self.execute_command(f"ls -la {path}")
            
            if result['exit_code'] != 0:
                logger.error(f"Failed to list files: {result['stderr']}")
                return []
            
            files = []
            lines = result['stdout'].strip().split('\n')[1:]  # Skip total line
            
            for line in lines:
                if not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) >= 9:
                    files.append({
                        'name': ' '.join(parts[8:]),  # Handle filenames with spaces
                        'permissions': parts[0],
                        'size': parts[4],
                        'modified': ' '.join(parts[5:8]),
                        'is_directory': parts[0].startswith('d')
                    })
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    async def _ensure_image(self) -> None:
        """Ensure the Docker image is available."""
        try:
            self.docker_client.images.get(self.image)
        except ImageNotFound:
            logger.info(f"Pulling Docker image: {self.image}")
            self.docker_client.images.pull(self.image)


class DockerProvider(BaseSandboxProvider):
    """Docker-based sandbox provider."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Docker configuration
        self.docker_url = self.config.get('docker_url', None)  # Use default
        self.default_image = self.config.get('default_image', 'ubuntu:20.04')
        self.resource_limits = self.config.get('resource_limits', {
            'mem_limit': '1g',
            'cpu_count': 1
        })
        self.network_config = self.config.get('network_config', {
            'network_mode': 'bridge'
        })
        self.volume_mounts = self.config.get('volume_mounts', {})
        
        # Initialize Docker client
        try:
            if self.docker_url:
                self.docker_client = docker.DockerClient(base_url=self.docker_url)
            else:
                self.docker_client = docker.from_env()
            
            # Test connection
            self.docker_client.ping()
            logger.info("Connected to Docker daemon")
            
        except Exception as e:
            logger.error(f"Failed to connect to Docker: {e}")
            raise RuntimeError(f"Failed to connect to Docker: {e}")
    
    async def create_session(
        self, 
        session_id: Optional[str] = None,
        image: Optional[str] = None,
        **kwargs
    ) -> DockerSession:
        """Create a new Docker sandbox session."""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if session_id in self._sessions:
            raise ValueError(f"Session {session_id} already exists")
        
        # Use provided image or default
        image = image or self.default_image
        
        # Merge configuration
        session_config = {
            **self.resource_limits,
            **self.network_config,
            'volumes': self.volume_mounts.copy(),
            **kwargs
        }
        
        # Create session
        session = DockerSession(
            session_id=session_id,
            provider=self,
            image=image,
            **session_config
        )
        
        self._register_session(session)
        logger.info(f"Created Docker session {session_id}")
        
        return session
    
    async def destroy_session(self, session_id: str) -> bool:
        """Destroy a Docker sandbox session."""
        session = self._sessions.get(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return False
        
        try:
            await session.stop()
            self._unregister_session(session_id)
            logger.info(f"Destroyed Docker session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to destroy session {session_id}: {e}")
            return False
    
    async def cleanup_all_sessions(self) -> None:
        """Clean up all Docker sessions."""
        await super().cleanup_all_sessions()
        
        # Also clean up any orphaned containers
        try:
            containers = self.docker_client.containers.list(
                filters={'name': 'grainchain-'}
            )
            for container in containers:
                try:
                    container.stop(timeout=5)
                    container.remove()
                    logger.info(f"Cleaned up orphaned container {container.id}")
                except Exception as e:
                    logger.error(f"Failed to clean up container {container.id}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to clean up orphaned containers: {e}")
    
    def __del__(self):
        """Cleanup when provider is destroyed."""
        try:
            if hasattr(self, 'docker_client'):
                self.docker_client.close()
        except Exception:
            pass

