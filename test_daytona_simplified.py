#!/usr/bin/env python3
"""
Test script demonstrating the simplified Daytona configuration.

This script shows the correct usage pattern for Daytona with grainchain.
If you see SSL certificate errors, it's an issue with the Daytona API endpoint,
not with our implementation.
"""

import asyncio
import os

from grainchain import Sandbox
from grainchain.core.interfaces import SandboxConfig


async def test_daytona_simplified():
    """Test Daytona with simplified configuration (just API key)."""

    # Check if API key is set
    api_key = os.getenv("DAYTONA_API_KEY")
    if not api_key:
        print("❌ DAYTONA_API_KEY environment variable not set")
        print("   Set it with: export DAYTONA_API_KEY=your-api-key")
        return False

    print("🚀 Testing Daytona with simplified configuration...")
    print(f"📋 Using API key: {api_key[:20]}...")

    try:
        # Create sandbox configuration
        config = SandboxConfig(timeout=60, working_directory="~")

        # Test sandbox creation and basic operation
        async with Sandbox(provider="daytona", config=config) as sandbox:
            print(f"✅ Sandbox created: {sandbox.sandbox_id}")

            # Test basic command
            result = await sandbox.execute("echo 'Hello from Daytona!'")
            if result.success:
                print(f"✅ Command executed: {result.stdout.strip()}")
            else:
                print(f"❌ Command failed: {result.stderr}")
                return False

            # Test Python execution
            result = await sandbox.execute("python3 -c \"print('Python works!')\"")
            if result.success:
                print(f"✅ Python test: {result.stdout.strip()}")
            else:
                print(f"❌ Python test failed: {result.stderr}")
                return False

        print("🎉 All tests passed! Daytona integration is working correctly.")
        return True

    except Exception as e:
        error_str = str(e).lower()
        if "ssl" in error_str and "certificate" in error_str:
            print("❌ SSL Certificate Error Detected")
            print(
                "   This is an issue with the Daytona API endpoint, not our implementation."
            )
            print(
                "   The grainchain integration is correct - the API endpoint has certificate issues."
            )
            print(f"   Error: {e}")
        else:
            print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_daytona_simplified())
    exit(0 if success else 1)
