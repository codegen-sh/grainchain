#!/usr/bin/env python3
"""
Simplified Usage Examples

This example demonstrates the new simplified API patterns that make
grainchain easier to use while maintaining full functionality.
"""

import asyncio

from grainchain import (
    Providers,
    create_e2b_sandbox,
    create_local_sandbox,
    create_sandbox,
)
from grainchain.convenience import (
    QuickSandbox,
    create_dev_sandbox,
    create_test_sandbox,
    quick_execute,
    quick_python,
    quick_script,
)


async def provider_constants_example():
    """Using provider constants instead of strings."""
    print("🔧 Provider Constants Example")
    print("=" * 40)

    # Before: using strings (still works)
    # sandbox1 = create_sandbox("local")

    # After: using constants (more reliable)
    sandbox2 = create_sandbox(Providers.LOCAL)

    async with sandbox2:
        result = await sandbox2.execute("echo 'Using provider constants!'")
        print(f"Output: {result.stdout.strip()}")


async def factory_functions_example():
    """Using convenience factory functions."""
    print("\n🏭 Factory Functions Example")
    print("=" * 40)

    # Simple local sandbox with defaults
    print("1. Local sandbox with defaults:")
    sandbox = create_local_sandbox()
    async with sandbox:
        result = await sandbox.execute("pwd")
        print(f"   Working directory: {result.stdout.strip()}")

    # Local sandbox with custom timeout
    print("\n2. Local sandbox with custom timeout:")
    sandbox = create_local_sandbox(timeout=30)
    async with sandbox:
        result = await sandbox.execute("echo 'Custom timeout sandbox'")
        print(f"   Output: {result.stdout.strip()}")

    # E2B sandbox (if available)
    print("\n3. E2B sandbox example:")
    try:
        sandbox = create_e2b_sandbox(template="python")
        print("   E2B sandbox created successfully!")
        # Note: Would need E2B credentials to actually use
    except Exception as e:
        print(f"   E2B not available: {e}")


async def preset_configurations_example():
    """Using preset configurations for common scenarios."""
    print("\n⚙️ Preset Configurations Example")
    print("=" * 40)

    # Development sandbox
    print("1. Development sandbox:")
    dev_sandbox = create_dev_sandbox()
    async with dev_sandbox:
        result = await dev_sandbox.execute("echo $ENV")
        print(f"   Environment: {result.stdout.strip()}")

    # Testing sandbox
    print("\n2. Testing sandbox:")
    test_sandbox = create_test_sandbox()
    async with test_sandbox:
        result = await test_sandbox.execute("echo $ENV")
        print(f"   Environment: {result.stdout.strip()}")


def synchronous_api_example():
    """Using the synchronous API for simple scripts."""
    print("\n🔄 Synchronous API Example")
    print("=" * 40)

    # Quick execution without async/await
    print("1. Quick command execution:")
    result = quick_execute("echo 'No async needed!'")
    print(f"   Output: {result.stdout.strip()}")

    # Quick Python execution
    print("\n2. Quick Python execution:")
    result = quick_python("print(f'2 + 2 = {2 + 2}')")
    print(f"   Output: {result.stdout.strip()}")

    # Quick script execution
    print("\n3. Quick script execution:")
    script = """
import os
print(f"Current directory: {os.getcwd()}")
print("Hello from quick script!")
"""
    result = quick_script(script, "hello.py")
    print("   Output:")
    for line in result.stdout.strip().split("\n"):
        print(f"      {line}")

    # Using QuickSandbox context manager
    print("\n4. QuickSandbox context manager:")
    with QuickSandbox() as sandbox:
        result = sandbox.execute("echo 'Synchronous context manager!'")
        print(f"   Output: {result.stdout.strip()}")

        # Upload and download files
        sandbox.upload_file("test.txt", "Hello from sync API!")
        content = sandbox.download_file("test.txt")
        print(f"   File content: {content.decode().strip()}")


async def comparison_example():
    """Show before/after comparison of API usage."""
    print("\n📊 Before/After Comparison")
    print("=" * 40)

    print("BEFORE (still works, but more verbose):")
    print("```python")
    print("from grainchain import Sandbox, SandboxConfig")
    print("config = SandboxConfig(timeout=60, working_directory='.')")
    print("async with Sandbox(provider='local', config=config) as sandbox:")
    print("    result = await sandbox.execute('echo Hello')")
    print("```")

    print("\nAFTER (simplified):")
    print("```python")
    print("from grainchain import create_local_sandbox")
    print("async with create_local_sandbox() as sandbox:")
    print("    result = await sandbox.execute('echo Hello')")
    print("```")

    print("\nEVEN SIMPLER (for simple scripts):")
    print("```python")
    print("from grainchain.convenience import quick_execute")
    print("result = quick_execute('echo Hello')")
    print("```")

    # Demonstrate the actual simplified usage
    print("\nActual simplified execution:")
    sandbox = create_local_sandbox()
    async with sandbox:
        result = await sandbox.execute("echo 'Simplified API in action!'")
        print(f"Output: {result.stdout.strip()}")


async def multi_provider_example():
    """Show how to easily switch between providers."""
    print("\n🔀 Multi-Provider Example")
    print("=" * 40)

    providers_to_try = [
        (Providers.LOCAL, "Local provider"),
    ]

    # Add other providers if they're available
    # Note: In a real scenario, you'd check for credentials/availability

    for provider, description in providers_to_try:
        print(f"\nTrying {description}:")
        try:
            sandbox = create_sandbox(provider, timeout=30)
            async with sandbox:
                result = await sandbox.execute(
                    "echo 'Hello from ' + $HOSTNAME || echo 'Hello from sandbox'"
                )
                print(f"   ✅ {description}: {result.stdout.strip()}")
        except Exception as e:
            print(f"   ❌ {description}: {e}")


async def main():
    """Run all simplified usage examples."""
    try:
        await provider_constants_example()
        await factory_functions_example()
        await preset_configurations_example()

        # Synchronous examples (no await needed)
        synchronous_api_example()

        await comparison_example()
        await multi_provider_example()

        print("\n🎉 All simplified usage examples completed!")
        print("\n💡 Key Benefits:")
        print("   • Less boilerplate code")
        print("   • Sensible defaults")
        print("   • Provider constants prevent typos")
        print("   • Synchronous API for simple scripts")
        print("   • Preset configurations for common scenarios")
        print("   • Easy provider switching")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
