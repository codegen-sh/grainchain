#!/usr/bin/env python3
"""Debug snapshot creation in detail."""

import asyncio
import os

from grainchain import Sandbox


async def test_snapshot_creation():
    print("🔍 Testing detailed snapshot creation...")

    async with Sandbox(provider="local") as sandbox:
        print(f"✅ Created sandbox: {sandbox.sandbox_id}")
        print(f"📍 Sandbox dir: {sandbox._session.sandbox_dir}")

        # Create a test file
        await sandbox.upload_file("test_snapshot.txt", "Hello from snapshot!")
        print("✅ Uploaded test file")

        # Check if file exists in sandbox
        result = await sandbox.execute("ls -la test_snapshot.txt")
        print(f"📁 File check: {result.stdout}")

        try:
            # Create snapshot with detailed error handling
            print("🔄 Creating snapshot...")
            snapshot_id = await sandbox.create_snapshot()
            print(f"✅ Created snapshot: {snapshot_id}")

            # Check if snapshot directory was created
            snapshot_dir = f"/tmp/grainchain_snapshots/{snapshot_id}"
            print(f"📍 Expected snapshot dir: {snapshot_dir}")

            if os.path.exists(snapshot_dir):
                print("✅ Snapshot directory exists")
                # List contents
                result = await sandbox.execute(f"ls -la {snapshot_dir}")
                print(f"📁 Snapshot contents: {result.stdout}")
            else:
                print("❌ Snapshot directory does not exist")

        except Exception as e:
            print(f"❌ Snapshot creation failed: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_snapshot_creation())
