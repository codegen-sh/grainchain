#!/usr/bin/env python3
"""
Quick Start Example for Grainchain

This example demonstrates the core functionality of Grainchain in a simple,
easy-to-understand format. Perfect for getting started!

Run this example:
    python examples/quick_start_example.py
"""

import asyncio

from grainchain import Sandbox


async def hello_world_example():
    """Basic 'Hello World' example."""
    print("⏳ Grainchain Quick Start Example")
    print("=" * 40)

    print("\n1. Creating a sandbox...")
    async with Sandbox() as sandbox:
        print(f"   ✅ Sandbox created: {sandbox.sandbox_id}")
        print(f"   📍 Provider: {sandbox.provider_name}")

        print("\n2. Executing a simple command...")
        result = await sandbox.execute("echo 'Hello, Grainchain!'")
        print("   📤 Command: echo 'Hello, Grainchain!'")
        print(f"   📥 Output: {result.stdout.strip()}")

        print("\n3. Running Python code...")
        result = await sandbox.execute("python3 -c 'print(2 + 2)'")
        print("   📤 Command: python3 -c 'print(2 + 2)'")
        print(f"   📥 Output: {result.stdout.strip()}")

        print("\n4. Creating and running a Python file...")
        python_code = """
print("Hello from a Python file!")
print(f"The answer to everything is: {6 * 7}")

# Simple calculation
numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
print(f"Sum of {numbers} = {total}")
"""

        await sandbox.upload_file("hello.py", python_code)
        print("   ✅ Uploaded hello.py")

        result = await sandbox.execute("python3 hello.py")
        print("   📤 Command: python3 hello.py")
        print("   📥 Output:")
        for line in result.stdout.strip().split("\n"):
            print(f"      {line}")

        print("\n5. Working with files...")
        # List files in the sandbox
        files = await sandbox.list_files(".")
        print(
            f"   📁 Files in sandbox: {[f.name for f in files if not f.is_directory]}"
        )

        # Download the file we created
        content = await sandbox.download_file("hello.py")
        print(f"   📥 Downloaded hello.py ({len(content)} bytes)")

        print("\n✅ Quick start example completed successfully!")


async def data_processing_example():
    """Simple data processing example."""
    print("\n" + "=" * 40)
    print("📊 Data Processing Example")
    print("=" * 40)

    # Create a simple data processing script
    data_script = """
import json
import csv
from datetime import datetime

# Sample data
sales_data = [
    {"date": "2024-01-01", "product": "Widget A", "sales": 100, "price": 10.99},
    {"date": "2024-01-01", "product": "Widget B", "sales": 75, "price": 15.50},
    {"date": "2024-01-02", "product": "Widget A", "sales": 120, "price": 10.99},
    {"date": "2024-01-02", "product": "Widget B", "sales": 90, "price": 15.50},
    {"date": "2024-01-03", "product": "Widget A", "sales": 80, "price": 10.99},
    {"date": "2024-01-03", "product": "Widget B", "sales": 110, "price": 15.50},
]

print("Processing sales data...")

# Calculate totals
total_sales = sum(item["sales"] for item in sales_data)
total_revenue = sum(item["sales"] * item["price"] for item in sales_data)

print(f"Total units sold: {total_sales}")
print(f"Total revenue: ${total_revenue:.2f}")

# Group by product
product_totals = {}
for item in sales_data:
    product = item["product"]
    if product not in product_totals:
        product_totals[product] = {"sales": 0, "revenue": 0}

    product_totals[product]["sales"] += item["sales"]
    product_totals[product]["revenue"] += item["sales"] * item["price"]

print("\\nSales by product:")
for product, totals in product_totals.items():
    print(f"  {product}: {totals['sales']} units, ${totals['revenue']:.2f}")

# Save results to JSON
results = {
    "summary": {
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "processed_at": datetime.now().isoformat()
    },
    "by_product": product_totals
}

with open("sales_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\\n✅ Results saved to sales_results.json")
"""

    async with Sandbox() as sandbox:
        print("\n1. Uploading data processing script...")
        await sandbox.upload_file("process_data.py", data_script)
        print("   ✅ Script uploaded")

        print("\n2. Running data processing...")
        result = await sandbox.execute("python3 process_data.py")

        if result.success:
            print("   ✅ Processing completed successfully!")
            print("   📥 Output:")
            for line in result.stdout.strip().split("\n"):
                print(f"      {line}")

            print("\n3. Downloading results...")
            try:
                results_content = await sandbox.download_file("sales_results.json")
                print("   ✅ Results downloaded:")
                print("   📄 Content:")
                # Pretty print the JSON
                import json

                results = json.loads(results_content.decode())
                print(json.dumps(results, indent=4))
            except Exception as e:
                print(f"   ❌ Could not download results: {e}")
        else:
            print(f"   ❌ Processing failed: {result.stderr}")


async def benchmark_example():
    """Simple benchmark example."""
    print("\n" + "=" * 40)
    print("⚡ Performance Benchmark Example")
    print("=" * 40)

    import time

    print("\n1. Testing basic command execution speed...")

    start_time = time.time()
    async with Sandbox() as sandbox:
        # Test multiple commands
        commands = [
            "echo 'test'",
            "python3 -c 'print(\"hello\")'",
            "ls -la",
            "pwd",
            "date",
        ]

        for i, command in enumerate(commands, 1):
            cmd_start = time.time()
            result = await sandbox.execute(command)
            cmd_time = time.time() - cmd_start

            status = "✅" if result.success else "❌"
            print(f"   {status} Command {i}: {command} ({cmd_time:.3f}s)")

    total_time = time.time() - start_time
    print(f"\n📊 Total benchmark time: {total_time:.3f}s")
    print(f"📈 Average time per command: {total_time/len(commands):.3f}s")


async def error_handling_example():
    """Demonstrate error handling."""
    print("\n" + "=" * 40)
    print("🛡️ Error Handling Example")
    print("=" * 40)

    async with Sandbox() as sandbox:
        print("\n1. Testing successful command...")
        result = await sandbox.execute("echo 'This works!'")
        if result.success:
            print(f"   ✅ Success: {result.stdout.strip()}")

        print("\n2. Testing command that fails...")
        result = await sandbox.execute("nonexistent_command")
        if not result.success:
            print(f"   ❌ Failed as expected (return code: {result.return_code})")
            print(f"   📝 Error message: {result.stderr.strip()}")

        print("\n3. Testing file operations...")
        try:
            # Try to download a file that doesn't exist
            await sandbox.download_file("nonexistent_file.txt")
            print("   ❌ This shouldn't happen!")
        except Exception as e:
            print(f"   ✅ Caught expected error: {type(e).__name__}")
            print(f"   📝 Error message: {str(e)}")

        print("\n4. Testing Python error handling...")
        python_error_code = """
try:
    result = 10 / 0  # This will cause a ZeroDivisionError
except ZeroDivisionError as e:
    print(f"Caught error: {e}")
    print("Handled gracefully!")
"""

        await sandbox.upload_file("error_test.py", python_error_code)
        result = await sandbox.execute("python3 error_test.py")

        if result.success:
            print("   ✅ Python error handling:")
            for line in result.stdout.strip().split("\n"):
                print(f"      {line}")


async def main():
    """Run all quick start examples."""
    try:
        await hello_world_example()
        await data_processing_example()
        await benchmark_example()
        await error_handling_example()

        print("\n" + "🎉" * 20)
        print("🎉 All Quick Start Examples Completed Successfully! 🎉")
        print("🎉" * 20)

        print("\n📚 Next Steps:")
        print("   • Explore more examples in the examples/ directory")
        print("   • Try different providers (e2b, daytona, morph)")
        print("   • Read the full documentation in README.md")
        print("   • Run benchmarks: grainchain benchmark --provider local")
        print("   • Check out the integration guide: INTEGRATION.md")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback

        traceback.print_exc()

        print("\n🔧 Troubleshooting:")
        print("   • Make sure grainchain is installed: pip install grainchain")
        print("   • Check Python version: python --version (requires 3.12+)")
        print("   • Try running: grainchain benchmark --provider local")
        print("   • See TROUBLESHOOTING.md for more help")


if __name__ == "__main__":
    asyncio.run(main())
