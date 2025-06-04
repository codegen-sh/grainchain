#!/usr/bin/env python3
"""Debug script to check what's available in Morph sandbox."""

import asyncio
import os

from grainchain import Sandbox
from grainchain.core.interfaces import SandboxConfig


async def debug_morph():
    """Debug what's available in Morph sandbox."""
    if not os.getenv("MORPH_API_KEY"):
        print("❌ MORPH_API_KEY not set")
        return

    print("🔍 Debugging Morph sandbox...")

    try:
        config = SandboxConfig(timeout=60, working_directory="~")

        async with Sandbox(provider="morph", config=config) as sandbox:
            print(f"✅ Connected to sandbox: {sandbox.sandbox_id}")

            # Check what Python interpreters are available
            commands_to_test = [
                "which python",
                "which python3",
                "which python3.9",
                "which python3.10",
                "which python3.11",
                "python --version",
                "python3 --version",
                "ls /usr/bin/python*",
                "ls /bin/python*",
                "cat /etc/os-release",
                "uname -a",
            ]

            for cmd in commands_to_test:
                print(f"\n🔧 Running: {cmd}")
                result = await sandbox.execute(cmd)
                print(f"   Return code: {result.return_code}")
                if result.stdout.strip():
                    print(f"   STDOUT: {result.stdout.strip()}")
                if result.stderr.strip():
                    print(f"   STDERR: {result.stderr.strip()}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_morph())
