#!/usr/bin/env python3
"""
Complete test of Morph.so sandbox provider with snapshot functionality.

This script demonstrates:
1. Creating a Morph sandbox
2. Creating state in the sandbox
3. Taking a snapshot
4. Modifying state after snapshot
5. Terminating the sandbox
6. Waking up from the snapshot
7. Verifying state was restored correctly

Usage:
    export MORPH_API_KEY="your_api_key"
    python test_morph_complete_cycle.py
"""

import asyncio
import os
import sys

from grainchain.core.interfaces import SandboxConfig
from grainchain.core.sandbox import Sandbox


async def test_complete_cycle():
    """Test the complete snapshot → terminate → wake up cycle."""

    # Check API key
    api_key = os.getenv("MORPH_API_KEY")
    if not api_key:
        print("❌ MORPH_API_KEY environment variable not set")
        sys.exit(1)

    print("🚀 Starting Morph.so complete cycle test...")

    config = SandboxConfig(
        timeout=60,
        provider_config={
            "image_id": "morphvm-minimal",
            "vcpus": 1,
            "memory": 1024,
            "disk_size": 8192,
        },
    )

    try:
        async with Sandbox(provider="morph", config=config) as sandbox:
            print(f"✅ Sandbox created: {sandbox.sandbox_id}")
            print(f"   Status: {sandbox.status}")

            # Step 1: Create initial state
            print("\n📝 Step 1: Creating initial state...")
            await sandbox.execute("mkdir -p /tmp/test")
            await sandbox.execute('echo "original data" > /tmp/test/data.txt')
            await sandbox.execute(
                'echo "$(date): Initial state created" >> /tmp/test/log.txt'
            )

            result = await sandbox.execute("cat /tmp/test/data.txt")
            print(f"   Initial data: {result.stdout.strip()}")

            # Step 2: Create snapshot
            print("\n📸 Step 2: Creating snapshot...")
            snapshot_id = await sandbox.create_snapshot()
            print(f"   Snapshot created: {snapshot_id}")

            # Step 3: Modify state after snapshot
            print("\n🔄 Step 3: Modifying state after snapshot...")
            await sandbox.execute('echo "modified data" > /tmp/test/data.txt')
            await sandbox.execute(
                'echo "$(date): State modified after snapshot" >> /tmp/test/log.txt'
            )

            result = await sandbox.execute("cat /tmp/test/data.txt")
            print(f"   Modified data: {result.stdout.strip()}")

            # Step 4: Terminate sandbox
            print("\n🛑 Step 4: Terminating sandbox...")
            original_id = sandbox.sandbox_id
            await sandbox.terminate()
            print(f"   Terminated: {original_id}")
            print(f"   Status: {sandbox.status}")

            # Step 5: Wake up from snapshot
            print("\n🌅 Step 5: Waking up from snapshot...")
            await sandbox.wake_up(snapshot_id)
            new_id = sandbox.sandbox_id
            print(f"   Woken up: {new_id}")
            print(f"   Status: {sandbox.status}")
            print(f"   ID changed: {original_id} → {new_id}")

            # Step 6: Verify state restoration
            print("\n🔍 Step 6: Verifying state restoration...")

            # Check if data was restored
            result = await sandbox.execute("cat /tmp/test/data.txt")
            restored_data = result.stdout.strip()
            print(f"   Restored data: {restored_data}")

            # Check log file
            result = await sandbox.execute("cat /tmp/test/log.txt")
            log_content = result.stdout.strip()
            print(f"   Log content: {log_content}")

            # Verify restoration
            if restored_data == "original data":
                print("\n🎉 SUCCESS: State was correctly restored from snapshot!")
                print("   ✅ Data matches pre-snapshot state")
                print("   ✅ Modified state after snapshot was discarded")
            else:
                print(f"\n❌ FAILURE: Expected 'original data', got '{restored_data}'")
                return False

            # Step 7: Test functionality after restoration
            print("\n🔧 Step 7: Testing functionality after restoration...")
            result = await sandbox.execute(
                'echo "Post-restoration test" > /tmp/test/new_file.txt'
            )
            result = await sandbox.execute("cat /tmp/test/new_file.txt")
            print(f"   New file content: {result.stdout.strip()}")

            if result.stdout.strip() == "Post-restoration test":
                print("   ✅ Sandbox is fully functional after restoration")
            else:
                print("   ❌ Sandbox functionality issue after restoration")
                return False

            print("\n🎊 ALL TESTS PASSED! Morph.so snapshot cycle working perfectly!")
            return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    success = await test_complete_cycle()
    if success:
        print("\n✨ Morph.so provider is ready for production use!")
        sys.exit(0)
    else:
        print("\n💥 Tests failed - please check the implementation")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
