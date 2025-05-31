#!/usr/bin/env python3
"""Test script for Morph provider snapshot → terminate → wake up cycle."""

import asyncio
import os

from grainchain.core.interfaces import SandboxConfig
from grainchain.core.sandbox import Sandbox


async def test_snapshot_cycle():
    """Test the complete snapshot → terminate → wake up cycle."""

    # Make sure API key is set
    if not os.getenv("MORPH_API_KEY"):
        print("❌ MORPH_API_KEY environment variable not set")
        return False

    print("🚀 Testing Morph snapshot → terminate → wake up cycle...")

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

        # Create sandbox using the factory
        async with Sandbox(provider="morph", config=config) as sandbox:
            print(f"✅ Created Morph sandbox: {sandbox.sandbox_id}")

            # 1. Set up initial state
            print("\n📝 Setting up initial state...")
            await sandbox.upload_file("/tmp/initial_state.txt", "Initial state data")
            result = await sandbox.execute(
                "echo 'Initial setup complete' > /tmp/setup_log.txt"
            )
            print("✅ Initial state created")

            # Verify initial state
            result = await sandbox.execute("ls -la /tmp/*.txt")
            print(f"📁 Initial files: {result.stdout.strip()}")

            # 2. Create snapshot
            print("\n📸 Creating snapshot...")
            snapshot_id = await sandbox.create_snapshot()
            print(f"✅ Created snapshot: {snapshot_id}")

            # 3. Make changes after snapshot
            print("\n🔧 Making changes after snapshot...")
            await sandbox.upload_file(
                "/tmp/after_snapshot.txt", "Data added after snapshot"
            )
            await sandbox.execute("echo 'Post-snapshot change' >> /tmp/setup_log.txt")

            # Verify changes exist
            result = await sandbox.execute("ls -la /tmp/*.txt")
            print(f"📁 Files after changes: {result.stdout.strip()}")

            result = await sandbox.execute("cat /tmp/setup_log.txt")
            print(f"📄 Log content: {result.stdout.strip()}")

            # 4. Terminate sandbox
            print("\n🛑 Terminating sandbox...")
            await sandbox.terminate()
            print("✅ Sandbox terminated")

            # 5. Wake up from snapshot (should restore to pre-change state)
            print("\n🌅 Waking up from snapshot...")
            await sandbox.wake_up(snapshot_id)
            print("✅ Sandbox woken up from snapshot")

            # 6. Verify state was restored
            print("\n🔍 Verifying restored state...")

            # Check that post-snapshot file is gone
            result = await sandbox.execute("ls -la /tmp/after_snapshot.txt")
            if result.return_code != 0:
                print("✅ Post-snapshot file correctly removed")
            else:
                print("❌ Post-snapshot file still exists (unexpected)")
                return False

            # Check that initial files are still there
            result = await sandbox.execute("ls -la /tmp/initial_state.txt")
            if result.return_code == 0:
                print("✅ Initial state file preserved")
            else:
                print("❌ Initial state file missing (unexpected)")
                return False

            # Check log content (should only have initial entry)
            result = await sandbox.execute("cat /tmp/setup_log.txt")
            log_content = result.stdout.strip()
            print(f"📄 Restored log content: {log_content}")

            if "Post-snapshot change" not in log_content:
                print("✅ Post-snapshot changes correctly reverted")
            else:
                print("❌ Post-snapshot changes still present (unexpected)")
                return False

            # 7. Test wake up without snapshot (should just restart)
            print("\n🛑 Terminating again...")
            await sandbox.terminate()

            print("🌅 Waking up without snapshot...")
            await sandbox.wake_up()  # No snapshot_id
            print("✅ Sandbox woken up without snapshot")

            # 8. Verify sandbox is functional after wake up
            print("\n🔧 Testing functionality after wake up...")
            result = await sandbox.execute("echo 'Wake up test successful'")
            if result.success:
                print(f"✅ Command execution works: {result.stdout.strip()}")
            else:
                print("❌ Command execution failed after wake up")
                return False

            print(
                "\n🎉 All snapshot cycle tests passed! Morph provider snapshot → terminate → wake up works correctly."
            )
            return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Main function to run the test."""
    success = await test_snapshot_cycle()
    if success:
        print("\n✅ Test completed successfully!")
        exit(0)
    else:
        print("\n❌ Test failed!")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
