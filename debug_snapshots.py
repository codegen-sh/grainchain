#!/usr/bin/env python3
"""Debug snapshot persistence across sandbox instances."""

import asyncio

from grainchain import Sandbox


async def test_snapshot_persistence():
    print("🔍 Testing snapshot persistence across sandbox instances...")

    # Step 1: Create first sandbox and snapshot
    print("\n📦 Step 1: Creating first sandbox...")
    async with Sandbox(provider="local") as sandbox1:
        print(f"✅ Created sandbox: {sandbox1.sandbox_id}")

        # Create a test file
        await sandbox1.upload_file("test_snapshot.txt", "Hello from snapshot!")
        print("✅ Uploaded test file")

        # Create snapshot
        snapshot_id = await sandbox1.create_snapshot()
        print(f"✅ Created snapshot: {snapshot_id}")

        # Check provider instance
        print(f"📍 Provider instance: {id(sandbox1._session._provider)}")
        print(
            f"📍 Global snapshots: {list(sandbox1._session._provider._global_snapshots.keys())}"
        )

    print("✅ First sandbox closed")

    # Step 2: Create second sandbox and restore
    print("\n📦 Step 2: Creating second sandbox...")
    async with Sandbox(provider="local") as sandbox2:
        print(f"✅ Created sandbox: {sandbox2.sandbox_id}")

        # Check provider instance
        print(f"📍 Provider instance: {id(sandbox2._session._provider)}")
        print(
            f"📍 Global snapshots: {list(sandbox2._session._provider._global_snapshots.keys())}"
        )

        try:
            # Try to restore snapshot
            await sandbox2.restore_snapshot(snapshot_id)
            print("✅ Snapshot restored successfully")

            # Verify file exists
            content = await sandbox2.download_file("test_snapshot.txt")
            content_str = (
                content.decode("utf-8") if isinstance(content, bytes) else content
            )
            print(f"✅ File content: '{content_str}'")

            if content_str.strip() == "Hello from snapshot!":
                print("🎯 Result: SUCCESS - Snapshot persistence works!")
            else:
                print("❌ Result: FAILED - Content mismatch")

        except Exception as e:
            print(f"❌ Snapshot restore failed: {e}")
            print("🎯 Result: FAILED - Snapshot not found")


if __name__ == "__main__":
    asyncio.run(test_snapshot_persistence())
