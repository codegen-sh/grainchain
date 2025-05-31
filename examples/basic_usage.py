"""
Basic usage examples for Grainchain.

This example demonstrates the core functionality of Grainchain
with different sandbox providers.
"""

import asyncio

from grainchain import Sandbox, SandboxConfig


async def basic_example():
    """Basic sandbox usage example."""
    print("🚀 Basic Grainchain Example")

    # Create a sandbox with default provider
    async with Sandbox() as sandbox:
        print(f"Created sandbox: {sandbox.sandbox_id} using {sandbox.provider_name}")

        # Execute a simple command
        result = await sandbox.execute("echo 'Hello, Grainchain!'")
        print(f"Output: {result.stdout.strip()}")

        # Execute Python code
        result = await sandbox.execute("python3 -c 'print(2 + 2)'")
        print(f"Python result: {result.stdout.strip()}")

        # Upload a file
        await sandbox.upload_file("hello.py", "print('Hello from uploaded file!')")

        # Execute the uploaded file
        result = await sandbox.execute("python3 hello.py")
        print(f"Uploaded file output: {result.stdout.strip()}")

        # List files
        files = await sandbox.list_files("/workspace")
        print(f"Files in workspace: {[f.name for f in files]}")


async def provider_specific_example():
    """Example using specific providers."""
    print("\n🔧 Provider-Specific Examples")

    # Use local provider for development
    print("Using local provider:")
    async with Sandbox(provider="local") as sandbox:
        result = await sandbox.execute("pwd")
        print(f"Working directory: {result.stdout.strip()}")

        # Create and read a file
        await sandbox.upload_file("test.txt", "Local provider test")
        content = await sandbox.download_file("test.txt")
        print(f"File content: {content.decode()}")


async def configuration_example():
    """Example with custom configuration."""
    print("\n⚙️ Configuration Example")

    # Custom configuration
    config = SandboxConfig(
        timeout=60,
        working_directory="/tmp",
        environment_vars={"MY_VAR": "test_value"},
        auto_cleanup=True,
    )

    async with Sandbox(provider="local", config=config) as sandbox:
        # Test environment variable
        result = await sandbox.execute("echo $MY_VAR")
        print(f"Environment variable: {result.stdout.strip()}")

        # Test working directory
        result = await sandbox.execute("pwd")
        print(f"Working directory: {result.stdout.strip()}")


async def error_handling_example():
    """Example demonstrating error handling."""
    print("\n❌ Error Handling Example")

    async with Sandbox(provider="local") as sandbox:
        # Execute a command that will fail
        result = await sandbox.execute("nonexistent_command")

        if result.success:
            print(f"Command succeeded: {result.stdout}")
        else:
            print(f"Command failed with code {result.return_code}")
            print(f"Error: {result.stderr}")

        # Try to download a non-existent file
        try:
            await sandbox.download_file("nonexistent.txt")
        except Exception as e:
            print(f"Expected error: {e}")


async def snapshot_example():
    """Example demonstrating snapshots (local provider only)."""
    print("\n📸 Snapshot Example")

    async with Sandbox(provider="local") as sandbox:
        # Create some files
        await sandbox.upload_file("file1.txt", "Original content")
        await sandbox.upload_file("file2.txt", "More content")

        # Create a snapshot
        snapshot_id = await sandbox.create_snapshot()
        print(f"Created snapshot: {snapshot_id}")

        # Modify files
        await sandbox.upload_file("file1.txt", "Modified content")
        await sandbox.execute("rm file2.txt")

        # Check current state
        result = await sandbox.execute("ls -la")
        print("After modifications:")
        print(result.stdout)

        # Restore snapshot
        await sandbox.restore_snapshot(snapshot_id)
        print("Restored snapshot")

        # Check restored state
        result = await sandbox.execute("ls -la")
        print("After restoration:")
        print(result.stdout)


async def main():
    """Run all examples."""
    try:
        await basic_example()
        await provider_specific_example()
        await configuration_example()
        await error_handling_example()
        await snapshot_example()

        print("\n✅ All examples completed successfully!")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
