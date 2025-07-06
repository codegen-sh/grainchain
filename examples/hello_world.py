#!/usr/bin/env python3
"""
Hello World Example - The Simplest Grainchain Usage

This example demonstrates the absolute simplest way to use grainchain.
Perfect for getting started in just a few lines of code!
"""

import asyncio

from grainchain import create_local_sandbox


async def hello_world():
    """The simplest possible grainchain example."""
    print("⏳ Grainchain Hello World")
    print("=" * 30)

    # Create and use a sandbox in just 3 lines!
    sandbox = create_local_sandbox()
    async with sandbox:
        result = await sandbox.execute("echo 'Hello, Grainchain!'")
        print(f"Output: {result.stdout.strip()}")


async def hello_python():
    """Simple Python execution example."""
    print("\n🐍 Python Hello World")
    print("=" * 30)

    sandbox = create_local_sandbox()
    async with sandbox:
        result = await sandbox.execute("python3 -c 'print(\"Hello from Python!\")'")
        print(f"Output: {result.stdout.strip()}")


async def hello_file():
    """Simple file operations example."""
    print("\n📁 File Operations Hello World")
    print("=" * 30)

    sandbox = create_local_sandbox()
    async with sandbox:
        # Create a simple Python script
        script = """
print("Hello from a file!")
print(f"2 + 2 = {2 + 2}")
"""

        # Upload and execute
        await sandbox.upload_file("hello.py", script)
        result = await sandbox.execute("python3 hello.py")
        print("Output:")
        print(result.stdout.strip())


if __name__ == "__main__":

    async def main():
        await hello_world()
        await hello_python()
        await hello_file()
        print("\n✅ All hello world examples completed!")

    asyncio.run(main())
