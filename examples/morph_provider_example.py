#!/usr/bin/env python3
"""
Example demonstrating Morph.so provider usage with custom base images and snapshotting.

This example shows:
1. Creating a sandbox with a custom base image
2. Setting up a development environment
3. Creating snapshots for state management
4. Restoring from snapshots
"""

import asyncio
import os

from grainchain.core.interfaces import SandboxConfig
from grainchain.core.sandbox import Sandbox


async def morph_example():
    """Demonstrate Morph provider capabilities."""

    # Configuration for Morph provider
    # You can customize the base image, resources, etc.
    sandbox_config = SandboxConfig(
        timeout=300,  # 5 minutes
        working_directory="~",
        provider_config={
            "image_id": "morphvm-minimal",  # Use minimal base image
            "vcpus": 2,  # 2 CPU cores
            "memory": 2048,  # 2GB RAM
            "disk_size": 10240,  # 10GB disk
        },
    )

    print("🚀 Starting Morph.so sandbox example...")

    # Create sandbox using Morph provider
    async with Sandbox(provider="morph", config=sandbox_config) as sandbox:
        print(f"✅ Created Morph sandbox: {sandbox.sandbox_id}")

        # 1. Basic setup and testing
        print("\n📦 Setting up development environment...")

        # Install some development tools
        result = await sandbox.execute("apt update && apt install -y curl git")
        if result.success:
            print("✅ Installed basic tools")
        else:
            print(f"❌ Failed to install tools: {result.stderr}")
            return

        # Install Python packages
        result = await sandbox.execute("pip install requests numpy")
        if result.success:
            print("✅ Installed Python packages")

        # 2. Create a simple Python application
        print("\n🐍 Creating a sample application...")

        app_code = '''
import requests
import numpy as np
import json

def fetch_data():
    """Fetch some sample data."""
    try:
        response = requests.get("https://httpbin.org/json")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def process_data(data):
    """Process data with numpy."""
    if "error" in data:
        return data

    # Create some sample numerical data
    arr = np.random.rand(10)
    return {
        "original": data,
        "processed": {
            "random_array": arr.tolist(),
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr))
        }
    }

if __name__ == "__main__":
    print("Fetching and processing data...")
    data = fetch_data()
    result = process_data(data)
    print(json.dumps(result, indent=2))
'''

        await sandbox.upload_file("/home/app.py", app_code)
        print("✅ Created sample application")

        # Test the application
        result = await sandbox.execute("cd /home && python app.py")
        if result.success:
            print("✅ Application runs successfully")
            print(f"📊 Output preview: {result.stdout[:200]}...")

        # 3. Create a snapshot of the configured environment
        print("\n📸 Creating snapshot of configured environment...")

        snapshot_id = await sandbox.create_snapshot()
        print(f"✅ Created snapshot: {snapshot_id}")

        # 4. Make some changes to demonstrate snapshot restoration
        print("\n🔧 Making changes to the environment...")

        # Create some temporary files
        await sandbox.execute("echo 'temporary file 1' > /tmp/temp1.txt")
        await sandbox.execute("echo 'temporary file 2' > /tmp/temp2.txt")
        await sandbox.execute("mkdir -p /tmp/workspace")

        # Verify changes exist
        result = await sandbox.execute("ls -la /tmp/temp*.txt")
        print(f"📁 Created temporary files: {result.stdout.strip()}")

        # 5. Restore from snapshot
        print("\n🔄 Restoring from snapshot...")

        try:
            await sandbox.restore_snapshot(snapshot_id)
            print("✅ Restored from snapshot")

            # Verify that temporary files are gone but our app remains
            result = await sandbox.execute("ls -la /tmp/temp*.txt")
            if result.return_code != 0:
                print("✅ Temporary files were removed (as expected)")

            result = await sandbox.execute("ls -la /home/app.py")
            if result.success:
                print("✅ Application file still exists")

        except NotImplementedError:
            print("ℹ️  Snapshot restoration not yet implemented for this provider")

        # 6. Demonstrate file operations
        print("\n📂 Testing file operations...")

        # List files in home directory
        files = await sandbox.list_files("/home")
        print(f"📋 Files in /home: {[f.name for f in files]}")

        # Download our application file
        content = await sandbox.download_file("/home/app.py")
        print(f"📥 Downloaded app.py ({len(content)} bytes)")

        # 7. Performance test
        print("\n⚡ Running performance test...")

        perf_script = """
import time
import numpy as np

start = time.time()
# Simulate some computational work
for i in range(100):
    arr = np.random.rand(1000)
    result = np.fft.fft(arr)

end = time.time()
print(f"Completed 100 FFT operations in {end - start:.2f} seconds")
"""

        await sandbox.upload_file("/home/perf_test.py", perf_script)
        result = await sandbox.execute("cd /home && python perf_test.py")
        if result.success:
            print(f"⚡ Performance result: {result.stdout.strip()}")

        print("\n🎉 Morph.so example completed successfully!")
        print(f"📊 Sandbox ID: {sandbox.sandbox_id}")
        print(f"🏷️  Provider: {sandbox.provider_name}")
        print(f"📸 Snapshot ID: {snapshot_id}")


async def main():
    """Main function to run the example."""
    try:
        await morph_example()
    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Make sure you have set your Morph API key
    if not os.getenv("MORPH_API_KEY"):
        print("⚠️  Please set MORPH_API_KEY environment variable")
        print("   export MORPH_API_KEY='your-api-key-here'")
        exit(1)

    asyncio.run(main())
