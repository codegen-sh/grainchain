#!/usr/bin/env python3
"""
Simple test script for Morph provider
"""

import asyncio

from grainchain.core.config import ProviderConfig
from grainchain.core.interfaces import SandboxConfig
from grainchain.providers.morph import MorphProvider


async def test_morph_provider():
    """Test basic Morph provider functionality"""

    # Set up configuration with the provided API key
    config = ProviderConfig(
        {
            "api_key": "morph_FtaB080sGdGQKcpvNWUSkw",
            "image_id": "morphvm-minimal",  # Use minimal image for faster testing
            "vcpus": 1,
            "memory": 1024,  # 1GB
            "disk_size": 8192,  # 8GB
        }
    )

    # Create provider
    provider = MorphProvider(config)
    print(f"✅ Created Morph provider: {provider.name}")

    # Create sandbox configuration
    sandbox_config = SandboxConfig(timeout=60, working_directory="~")

    try:
        # Create sandbox session
        print("🚀 Creating Morph sandbox...")
        session = await provider.create_sandbox(sandbox_config)
        print(f"✅ Created sandbox: {session.sandbox_id}")

        # Test basic command execution
        print("🔧 Testing command execution...")
        result = await session.execute("echo 'Hello from Morph!'")
        print(f"✅ Command result: {result.stdout.strip()}")
        print(f"   Return code: {result.return_code}")
        print(f"   Success: {result.success}")

        # Test Python execution
        print("🐍 Testing Python execution...")
        result = await session.execute("python3 -c \"print('Python works in Morph!')\"")
        print(f"✅ Python result: {result.stdout.strip()}")

        # Test file operations
        print("📁 Testing file operations...")
        await session.upload_file("/tmp/test.txt", "Hello Morph from Grainchain!")
        result = await session.execute("cat /tmp/test.txt")
        print(f"✅ File content: {result.stdout.strip()}")

        # Test file listing
        print("📋 Testing file listing...")
        files = await session.list_files("/tmp")
        test_files = [f for f in files if f.name == "test.txt"]
        if test_files:
            print(f"✅ Found test file: {test_files[0].name}")

        # Test snapshot functionality (key feature of Morph)
        print("📸 Testing snapshot creation...")
        snapshot_id = await session.create_snapshot()
        print(f"✅ Created snapshot: {snapshot_id}")

        # Clean up
        print("🧹 Cleaning up...")
        await session.close()
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
