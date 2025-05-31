"""
Example usage of the Docker provider for Grainchain.

This example demonstrates how to:
1. Create a Docker provider
2. Create and manage sessions
3. Execute commands
4. Upload and download files
5. Handle errors and cleanup
"""

import asyncio
import tempfile
import os
from pathlib import Path

from grainchain.providers.docker import DockerProvider


async def basic_usage_example():
    """Basic usage example."""
    print("=== Basic Docker Provider Usage ===")
    
    # Create provider with custom configuration
    config = {
        'default_image': 'python:3.9-slim',
        'resource_limits': {
            'mem_limit': '512m',
            'cpu_count': 1
        },
        'network_config': {
            'network_mode': 'bridge'
        }
    }
    
    provider = DockerProvider(config)
    
    try:
        # Create a session
        session = await provider.create_session(
            session_id="example-session",
            image="python:3.9-slim"
        )
        
        print(f"Created session: {session.session_id}")
        
        # Start the session
        await session.start()
        print("Session started successfully")
        
        # Execute some commands
        print("\n--- Executing Commands ---")
        
        # Basic command
        result = await session.execute_command("python --version")
        print(f"Python version: {result['stdout'].strip()}")
        
        # Command with working directory
        result = await session.execute_command("pwd", working_dir="/tmp")
        print(f"Working directory: {result['stdout'].strip()}")
        
        # Command with environment variables
        result = await session.execute_command(
            "echo $MY_VAR", 
            env={'MY_VAR': 'Hello from environment!'}
        )
        print(f"Environment variable: {result['stdout'].strip()}")
        
        # Stop the session
        await session.stop()
        print("Session stopped successfully")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup all sessions
        await provider.cleanup_all_sessions()


async def file_operations_example():
    """File operations example."""
    print("\n=== File Operations Example ===")
    
    provider = DockerProvider({'default_image': 'alpine:latest'})
    
    try:
        # Create session using context manager
        session = await provider.create_session(image="alpine:latest")
        
        async with session:
            print("Session started with context manager")
            
            # Create a local test file
            test_content = """
# Test Python Script
print("Hello from uploaded file!")
for i in range(5):
    print(f"Count: {i}")
"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_content)
                local_file = f.name
            
            try:
                # Upload file
                remote_path = "/tmp/test_script.py"
                upload_success = await session.upload_file(local_file, remote_path)
                print(f"File upload successful: {upload_success}")
                
                # Execute the uploaded script (install python first)
                await session.execute_command("apk add --no-cache python3")
                result = await session.execute_command(f"python3 {remote_path}")
                print(f"Script output:\n{result['stdout']}")
                
                # List files in directory
                files = await session.list_files("/tmp")
                print("\nFiles in /tmp:")
                for file_info in files:
                    file_type = "DIR" if file_info['is_directory'] else "FILE"
                    print(f"  {file_type}: {file_info['name']} ({file_info['size']} bytes)")
                
                # Download the file back
                with tempfile.NamedTemporaryFile(delete=False) as f:
                    download_path = f.name
                
                try:
                    download_success = await session.download_file(remote_path, download_path)
                    print(f"File download successful: {download_success}")
                    
                    # Verify downloaded content
                    with open(download_path, 'r') as f:
                        downloaded_content = f.read()
                    print(f"Downloaded file matches: {test_content.strip() in downloaded_content}")
                    
                finally:
                    os.unlink(download_path)
                    
            finally:
                os.unlink(local_file)
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await provider.cleanup_all_sessions()


async def multiple_sessions_example():
    """Multiple sessions example."""
    print("\n=== Multiple Sessions Example ===")
    
    provider = DockerProvider({'default_image': 'alpine:latest'})
    
    try:
        # Create multiple sessions with different configurations
        sessions = []
        
        for i in range(3):
            session = await provider.create_session(
                session_id=f"worker-{i}",
                image="alpine:latest",
                environment={'WORKER_ID': str(i)}
            )
            sessions.append(session)
            await session.start()
            print(f"Started worker session {i}")
        
        # Execute commands in parallel
        print("\n--- Parallel Execution ---")
        
        async def worker_task(session, task_id):
            """Simulate work in a session."""
            # Simulate some work
            await session.execute_command(f"sleep {task_id + 1}")
            
            # Get worker info
            result = await session.execute_command("echo Worker $WORKER_ID completed task")
            return result['stdout'].strip()
        
        # Run tasks in parallel
        tasks = [worker_task(session, i) for i, session in enumerate(sessions)]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            print(f"  {result}")
        
        # List all active sessions
        session_ids = await provider.list_sessions()
        print(f"\nActive sessions: {session_ids}")
        
        # Stop all sessions
        for session in sessions:
            await session.stop()
            print(f"Stopped session: {session.session_id}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await provider.cleanup_all_sessions()


async def error_handling_example():
    """Error handling example."""
    print("\n=== Error Handling Example ===")
    
    provider = DockerProvider()
    
    try:
        session = await provider.create_session(image="alpine:latest")
        
        async with session:
            # Command that fails
            result = await session.execute_command("nonexistent-command")
            print(f"Failed command exit code: {result['exit_code']}")
            print(f"Error output: {result['stderr'].strip()}")
            
            # File operation that fails
            upload_success = await session.upload_file("/nonexistent/file.txt", "/tmp/test")
            print(f"Failed upload result: {upload_success}")
            
            # Successful command after failure
            result = await session.execute_command("echo 'Recovery successful'")
            print(f"Recovery command: {result['stdout'].strip()}")
            
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        await provider.cleanup_all_sessions()


async def advanced_configuration_example():
    """Advanced configuration example."""
    print("\n=== Advanced Configuration Example ===")
    
    # Advanced provider configuration
    config = {
        'default_image': 'ubuntu:20.04',
        'resource_limits': {
            'mem_limit': '1g',
            'cpu_count': 2
        },
        'network_config': {
            'network_mode': 'bridge'
        },
        'volume_mounts': {
            '/host/data': {'bind': '/container/data', 'mode': 'rw'}
        }
    }
    
    provider = DockerProvider(config)
    
    try:
        # Create session with custom configuration
        session = await provider.create_session(
            image="ubuntu:20.04",
            working_dir="/workspace",
            environment={
                'PROJECT_NAME': 'grainchain-demo',
                'DEBUG': 'true'
            }
        )
        
        async with session:
            # Install some tools
            print("Installing development tools...")
            result = await session.execute_command(
                "apt-get update && apt-get install -y python3 python3-pip git",
                timeout=120
            )
            
            if result['exit_code'] == 0:
                print("Tools installed successfully")
                
                # Create a development environment
                await session.execute_command("mkdir -p /workspace/project")
                await session.execute_command(
                    "echo 'print(\"Hello from $PROJECT_NAME!\")' > /workspace/project/hello.py",
                    working_dir="/workspace"
                )
                
                # Run the script
                result = await session.execute_command(
                    "python3 project/hello.py",
                    working_dir="/workspace"
                )
                print(f"Script output: {result['stdout'].strip()}")
                
            else:
                print(f"Failed to install tools: {result['stderr']}")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await provider.cleanup_all_sessions()


async def main():
    """Run all examples."""
    print("Grainchain Docker Provider Examples")
    print("=" * 40)
    
    try:
        await basic_usage_example()
        await file_operations_example()
        await multiple_sessions_example()
        await error_handling_example()
        await advanced_configuration_example()
        
        print("\n" + "=" * 40)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Example failed: {e}")


if __name__ == "__main__":
    # Check if Docker is available
    try:
        import docker
        client = docker.from_env()
        client.ping()
        print("Docker is available, running examples...\n")
        asyncio.run(main())
    except Exception as e:
        print(f"Docker is not available: {e}")
        print("Please ensure Docker is installed and running.")

