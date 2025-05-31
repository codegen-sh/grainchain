#!/usr/bin/env python3
"""
Simple test script for Daytona provider
"""

import asyncio

from grainchain.core.config import ProviderConfig
from grainchain.core.interfaces import SandboxConfig
from grainchain.providers.daytona import DaytonaProvider


async def test_daytona_provider():
    """Test basic Daytona provider functionality"""

    # Set up configuration with the provided API key
    config = ProviderConfig({
        "api_key": "dtn_7ff34af9c746f96e2f43ffe698e0b97af87bb5cc47b2376a1873935ac12f416a",
        "api_url": "https://api.daytona.io",
        "target": "us"
    })

    # Create provider
    provider = DaytonaProvider(config)
    print(f"✅ Created Daytona provider: {provider.name}")

    # Create sandbox configuration
    sandbox_config = SandboxConfig(
        timeout=60,
        working_directory="/workspace"
    )

    try:
        # Create sandbox session
        print("🚀 Creating Daytona sandbox...")
        session = await provider.create_sandbox(sandbox_config)
        print(f"✅ Created sandbox: {session.sandbox_id}")

        # Test basic command execution
        print("🔧 Testing command execution...")
        result = await session.execute("echo 'Hello from Daytona!'")
        print(f"✅ Command result: {result.stdout.strip()}")
        print(f"   Return code: {result.return_code}")
        print(f"   Success: {result.success}")

        # Test Python execution
        print("🐍 Testing Python execution...")
        result = await session.execute("python3 -c \"print('Python works in Daytona!')\"")
        print(f"✅ Python result: {result.stdout.strip()}")

        # Test file operations
        print("📁 Testing file operations...")
        await session.upload_file("/tmp/test.txt", "Hello Daytona from Grainchain!")
        result = await session.execute("cat /tmp/test.txt")
        print(f"✅ File content: {result.stdout.strip()}")

        # Test file listing
        print("📋 Testing file listing...")
        files = await session.list_files("/tmp")
        test_files = [f for f in files if f.name == "test.txt"]
        if test_files:
            print(f"✅ Found test file: {test_files[0].name}")

        # Clean up
        print("🧹 Cleaning up...")
        await session.close()
        print("✅ Session closed successfully")

        print("\n🎉 All tests passed! Daytona provider is working correctly.")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(test_daytona_provider())
    exit(0 if success else 1)

