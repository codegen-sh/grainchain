"""
Example demonstrating how to check provider status programmatically.

This example shows how to use the provider information utilities to check
which sandbox providers are available and properly configured.
"""

import asyncio

from grainchain import (
    Sandbox,
    check_provider,
    get_available_providers,
    get_providers_info,
)


def basic_provider_check():
    """Basic example of checking provider status."""
    print("🔧 Checking Provider Status\n")

    # Get information about all providers
    providers = get_providers_info()

    for name, info in providers.items():
        status = "✅ Ready" if info.available else "❌ Not ready"
        print(f"{name.upper()}: {status}")

        if not info.available:
            if not info.dependencies_installed:
                print(f"  - Install: {info.install_command}")
            if info.missing_config:
                print(f"  - Missing config: {', '.join(info.missing_config)}")
        print()


def check_specific_provider():
    """Example of checking a specific provider."""
    print("🔍 Checking E2B Provider\n")

    info = check_provider("e2b")

    print(f"Provider: {info.name}")
    print(f"Available: {'✅' if info.available else '❌'}")
    print(f"Dependencies installed: {'✅' if info.dependencies_installed else '❌'}")
    print(f"Configured: {'✅' if info.configured else '❌'}")

    if info.missing_config:
        print(f"Missing configuration: {', '.join(info.missing_config)}")
        print("\nSetup instructions:")
        for instruction in info.config_instructions or []:
            print(f"  {instruction}")


def list_available_providers():
    """Example of getting only available providers."""
    print("📋 Available Providers\n")

    available = get_available_providers()

    if available:
        print(f"Ready to use: {', '.join(available)}")
    else:
        print("No providers are currently available.")
        print("Run the setup instructions above to configure providers.")


async def test_available_providers():
    """Example of testing available providers."""
    print("🧪 Testing Available Providers\n")

    available = get_available_providers()

    if not available:
        print("No providers available for testing.")
        return

    for provider_name in available:
        print(f"Testing {provider_name}...")
        try:
            async with Sandbox(provider=provider_name) as sandbox:
                result = await sandbox.execute(
                    "echo 'Hello from " + provider_name + "'"
                )
                if result.success:
                    print(f"  ✅ {provider_name} working: {result.stdout.strip()}")
                else:
                    print(f"  ❌ {provider_name} failed: {result.stderr}")
        except Exception as e:
            print(f"  ❌ {provider_name} error: {e}")
        print()


def main():
    """Run all examples."""
    print("=" * 50)
    print("Grainchain Provider Status Examples")
    print("=" * 50)
    print()

    # Basic provider check
    basic_provider_check()

    print("-" * 30)

    # Check specific provider
    check_specific_provider()

    print("-" * 30)

    # List available providers
    list_available_providers()

    print("-" * 30)

    # Test available providers
    asyncio.run(test_available_providers())


if __name__ == "__main__":
    main()
