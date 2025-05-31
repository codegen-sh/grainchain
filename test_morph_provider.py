#!/usr/bin/env python3
"""
Test script for Morph provider functionality.
"""

import asyncio
import os

from grainchain.core.interfaces import SandboxConfig
from grainchain.core.sandbox import Sandbox


async def test_morph_provider():
    """Test basic Morph provider functionality"""

    # Make sure API key is set
    if not os.getenv("MORPH_API_KEY"):
        print("❌ MORPH_API_KEY environment variable not set")
        return False

    print("🚀 Testing Morph provider...")

    try:
        # Create sandbox config
        config = SandboxConfig(
            timeout=300,
            provider_config={
                "image_id": "morphvm-minimal",  # Use minimal image for faster testing
                "vcpus": 1,
                "memory": 1024,  # 1GB
                "disk_size": 8192,  # 8GB
            },
        )

        # Create sandbox using the factory (this will use environment variables)
        async with Sandbox(provider="morph", config=config) as sandbox:
            print(f"✅ Created Morph sandbox: {sandbox.sandbox_id}")

            # Test basic command execution
            print("🔧 Testing command execution...")
            result = await sandbox.execute("echo 'Hello from Morph!'")
            print(f"✅ Command result: {result.stdout.strip()}")
            print(f"   Return code: {result.return_code}")
            print(f"   Success: {result.success}")

            # Test Python execution
            print("🐍 Testing Python execution...")
            result = await sandbox.execute(
                "python3 -c \"print('Python works in Morph!')\""
            )
            print(f"✅ Python result: {result.stdout.strip()}")

            # Test file operations
            print("📁 Testing file operations...")
            await sandbox.upload_file("/tmp/test.txt", "Hello Morph from Grainchain!")
            result = await sandbox.execute("cat /tmp/test.txt")
            print(f"✅ File content: {result.stdout.strip()}")

            # Test file listing
            print("📋 Testing file listing...")
            files = await sandbox.list_files("/tmp")
            test_files = [f for f in files if f.name == "test.txt"]
            if test_files:
                print(f"✅ Found test file: {test_files[0].name}")

            # Test snapshot functionality (key feature of Morph)
            print("📸 Testing snapshot creation...")
            snapshot_id = await sandbox.create_snapshot()
            print(f"✅ Created snapshot: {snapshot_id}")

            # Clean up
            print("🧹 Cleaning up...")
            await sandbox.close()
            print("✅ Session closed successfully")

            print("\n🎉 All tests passed! Morph provider is working correctly.")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(test_morph_provider())
    exit(0 if success else 1)
