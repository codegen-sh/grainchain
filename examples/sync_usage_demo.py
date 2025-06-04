#!/usr/bin/env python3
"""
Synchronous Usage Demo

This example demonstrates the synchronous API that doesn't require
async/await knowledge, making grainchain accessible to all Python developers.
"""

from grainchain.convenience import (
    QuickSandbox,
    quick_execute,
    quick_python,
    quick_script,
)


def synchronous_api_demo():
    """Demonstrate the synchronous API."""
    print("🔄 Synchronous API Demo")
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


def data_processing_demo():
    """Demonstrate data processing with sync API."""
    print("\n📊 Data Processing Demo")
    print("=" * 40)

    # Create a data processing script
    data_script = """
import json

# Sample data
data = [
    {"name": "Alice", "age": 25, "city": "New York"},
    {"name": "Bob", "age": 30, "city": "San Francisco"},
    {"name": "Charlie", "age": 35, "city": "Chicago"}
]

# Process data
total_age = sum(person["age"] for person in data)
avg_age = total_age / len(data)

print(f"Total people: {len(data)}")
print(f"Average age: {avg_age:.1f}")

# Save results
results = {"count": len(data), "avg_age": avg_age}
with open("results.json", "w") as f:
    json.dump(results, f)

print("Results saved to results.json")
"""

    with QuickSandbox() as sandbox:
        print("1. Processing data...")
        sandbox.upload_file("process.py", data_script)
        result = sandbox.execute("python3 process.py")
        print("   Output:")
        for line in result.stdout.strip().split("\n"):
            print(f"      {line}")

        print("\n2. Downloading results...")
        try:
            results_content = sandbox.download_file("results.json")
            print(f"   Results: {results_content.decode().strip()}")
        except Exception as e:
            print(f"   Note: {e}")
            print("   (This is expected in some sandbox configurations)")


def testing_pattern_demo():
    """Demonstrate testing patterns with sync API."""
    print("\n🧪 Testing Pattern Demo")
    print("=" * 40)

    def test_script_execution():
        """Test that a script executes correctly."""
        script = "print('Test passed!')"
        result = quick_script(script, "test.py")
        assert result.success, "Script should execute successfully"
        assert "Test passed!" in result.stdout, "Should contain expected output"
        return True

    def test_error_handling():
        """Test error handling."""
        result = quick_python("raise ValueError('test error')")
        assert not result.success, "Should fail with error"
        assert "ValueError" in result.stderr, "Should contain error message"
        return True

    def test_file_operations():
        """Test file operations."""
        with QuickSandbox() as sandbox:
            test_content = "Hello, testing!"
            sandbox.upload_file("test.txt", test_content)
            downloaded = sandbox.download_file("test.txt")
            assert downloaded.decode() == test_content, "File content should match"
            return True

    # Run tests
    tests = [
        ("Script execution", test_script_execution),
        ("Error handling", test_error_handling),
        ("File operations", test_file_operations),
    ]

    for test_name, test_func in tests:
        try:
            test_func()
            print(f"   ✅ {test_name}: PASSED")
        except Exception as e:
            print(f"   ❌ {test_name}: FAILED - {e}")


def comparison_demo():
    """Show the difference between async and sync APIs."""
    print("\n📊 API Comparison Demo")
    print("=" * 40)

    print("ASYNC API (traditional):")
    print("```python")
    print("import asyncio")
    print("from grainchain import create_local_sandbox")
    print("")
    print("async def main():")
    print("    async with create_local_sandbox() as sandbox:")
    print("        result = await sandbox.execute('echo Hello')")
    print("        print(result.stdout)")
    print("")
    print("asyncio.run(main())")
    print("```")

    print("\nSYNC API (simplified):")
    print("```python")
    print("from grainchain.convenience import quick_execute")
    print("")
    print("result = quick_execute('echo Hello')")
    print("print(result.stdout)")
    print("```")

    print("\nBoth produce the same result:")
    result = quick_execute("echo 'Hello from sync API!'")
    print(f"Output: {result.stdout.strip()}")


def main():
    """Run all synchronous API demos."""
    try:
        synchronous_api_demo()
        data_processing_demo()
        testing_pattern_demo()
        comparison_demo()

        print("\n🎉 All synchronous API demos completed!")
        print("\n💡 Key Benefits of Sync API:")
        print("   • No async/await knowledge required")
        print("   • Perfect for simple scripts and testing")
        print("   • Easy integration with existing sync code")
        print("   • Handles async complexity internally")
        print("   • Same functionality as async API")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
