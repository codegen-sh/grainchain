#!/usr/bin/env python3
"""Debug file operations for local provider"""

import asyncio

from grainchain import Sandbox


async def test_file_operations():
    """Test file operations with local provider"""
    print("🔍 Testing file operations with local provider...")

    try:
        # Create sandbox using async context manager
        async with Sandbox(provider="local") as sandbox:
            print(f"✅ Created sandbox: {sandbox.sandbox_id}")

            # Test upload
            test_content = "Hello, Grainchain!"
            await sandbox.upload_file("test.txt", test_content)
            print("✅ File uploaded successfully")

            # Test download
            downloaded = await sandbox.download_file("test.txt")
            downloaded_str = downloaded.decode("utf-8")
            print(f"✅ File downloaded: '{downloaded_str}'")

            # Verify content
            if downloaded_str.strip() == test_content.strip():
                print("✅ Content verification passed")
                return True
            else:
                print(
                    f"❌ Content mismatch: expected '{test_content}', got '{downloaded_str}'"
                )
                return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_file_operations())
    print(f"🎯 Result: {'SUCCESS' if result else 'FAILED'}")
