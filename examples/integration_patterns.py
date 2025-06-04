#!/usr/bin/env python3
"""
Integration Patterns Examples

This example demonstrates how to integrate grainchain with other tools
and frameworks, showing common patterns for real-world usage.
"""

import asyncio
import json

from grainchain import create_local_sandbox
from grainchain.convenience import QuickSandbox, create_dev_sandbox


async def jupyter_notebook_pattern():
    """Pattern for using grainchain in Jupyter notebooks."""
    print("📓 Jupyter Notebook Integration Pattern")
    print("=" * 45)

    print("# In a Jupyter cell, you can use grainchain like this:")
    print("```python")
    print("from grainchain import create_local_sandbox")
    print("")
    print("# Create a sandbox for the notebook session")
    print("sandbox = create_local_sandbox()")
    print("await sandbox.__aenter__()  # Start the sandbox")
    print("")
    print("# Use throughout the notebook")
    print("result = await sandbox.execute('pip install pandas')")
    print(
        "result = await sandbox.execute('python -c \"import pandas; print(pandas.__version__)\"')"
    )
    print("")
    print("# Clean up when done")
    print("await sandbox.__aexit__(None, None, None)")
    print("```")

    # Demonstrate the actual pattern
    print("\nActual demonstration:")
    sandbox = create_local_sandbox()
    await sandbox.__aenter__()

    try:
        # Simulate notebook cells
        print("Cell 1: Setting up environment")
        result = await sandbox.execute(
            "python3 -c 'import sys; print(f\"Python {sys.version}\")'"
        )
        print(f"   {result.stdout.strip()}")

        print("Cell 2: Creating data")
        await sandbox.upload_file(
            "data.py",
            """
import json
data = {"name": "grainchain", "version": "0.1.0", "type": "sandbox"}
with open("data.json", "w") as f:
    json.dump(data, f)
print("Data created!")
""",
        )
        result = await sandbox.execute("python3 data.py")
        print(f"   {result.stdout.strip()}")

        print("Cell 3: Processing data")
        result = await sandbox.execute(
            'python3 -c \'import json; data=json.load(open("data.json")); print(f"Loaded: {data["name"]} v{data["version"]}")\''
        )
        print(f"   {result.stdout.strip()}")

    finally:
        await sandbox.__aexit__(None, None, None)


def testing_framework_pattern():
    """Pattern for using grainchain in testing frameworks."""
    print("\n🧪 Testing Framework Integration Pattern")
    print("=" * 45)

    print("# Example pytest integration:")
    print("```python")
    print("import pytest")
    print("from grainchain import create_test_sandbox")
    print("")
    print("@pytest.fixture")
    print("async def sandbox():")
    print("    sandbox = create_test_sandbox()")
    print("    async with sandbox:")
    print("        yield sandbox")
    print("")
    print("async def test_my_script(sandbox):")
    print("    await sandbox.upload_file('script.py', 'print(\"test\")')")
    print("    result = await sandbox.execute('python3 script.py')")
    print("    assert result.success")
    print("    assert 'test' in result.stdout")
    print("```")

    # Demonstrate the pattern
    print("\nActual test simulation:")

    async def simulate_test():
        sandbox = create_dev_sandbox()
        async with sandbox:
            # Test 1: Script execution
            await sandbox.upload_file("test_script.py", "print('Test passed!')")
            result = await sandbox.execute("python3 test_script.py")
            assert result.success, "Script should execute successfully"
            assert "Test passed!" in result.stdout, "Should contain expected output"
            print("   ✅ Test 1: Script execution - PASSED")

            # Test 2: Error handling
            result = await sandbox.execute(
                "python3 -c 'raise ValueError(\"test error\")'"
            )
            assert not result.success, "Should fail with error"
            assert "ValueError" in result.stderr, "Should contain error message"
            print("   ✅ Test 2: Error handling - PASSED")

            # Test 3: File operations
            test_content = "Hello, testing!"
            await sandbox.upload_file("test.txt", test_content)
            downloaded = await sandbox.download_file("test.txt")
            assert downloaded.decode() == test_content, "File content should match"
            print("   ✅ Test 3: File operations - PASSED")

    await simulate_test()


def ci_cd_pattern():
    """Pattern for using grainchain in CI/CD pipelines."""
    print("\n🔄 CI/CD Pipeline Integration Pattern")
    print("=" * 45)

    print("# Example GitHub Actions workflow:")
    print("```yaml")
    print("name: Test with Grainchain")
    print("on: [push, pull_request]")
    print("jobs:")
    print("  test:")
    print("    runs-on: ubuntu-latest")
    print("    steps:")
    print("    - uses: actions/checkout@v3")
    print("    - uses: actions/setup-python@v4")
    print("      with:")
    print("        python-version: '3.12'")
    print("    - run: pip install grainchain")
    print("    - run: python test_with_grainchain.py")
    print("```")

    # Simulate CI/CD testing
    print("\nSimulating CI/CD test run:")

    async def simulate_ci_test():
        # Use QuickSandbox for CI environments where async might be complex
        with QuickSandbox(timeout=30) as sandbox:
            # Test environment setup
            result = sandbox.execute("python3 --version")
            print(f"   Python version: {result.stdout.strip()}")

            # Run tests
            test_script = """
import sys
import json

# Simulate test results
results = {
    "tests_run": 5,
    "passed": 5,
    "failed": 0,
    "status": "success"
}

print(f"Tests run: {results['tests_run']}")
print(f"Passed: {results['passed']}")
print(f"Failed: {results['failed']}")
print(f"Status: {results['status']}")

# Exit with appropriate code
sys.exit(0 if results['failed'] == 0 else 1)
"""
            sandbox.upload_file("ci_test.py", test_script)
            result = sandbox.execute("python3 ci_test.py")

            if result.success:
                print("   ✅ CI tests passed!")
                print(f"   Output: {result.stdout.strip()}")
            else:
                print("   ❌ CI tests failed!")
                print(f"   Error: {result.stderr.strip()}")

    await simulate_ci_test()


async def data_pipeline_pattern():
    """Pattern for using grainchain in data processing pipelines."""
    print("\n📊 Data Pipeline Integration Pattern")
    print("=" * 45)

    print("# Example data processing pipeline:")
    print("```python")
    print("from grainchain import create_data_sandbox")
    print("")
    print("async def process_data(input_file, output_file):")
    print("    async with create_data_sandbox() as sandbox:")
    print("        # Upload data")
    print("        await sandbox.upload_file('input.csv', input_file)")
    print("        ")
    print("        # Process with pandas")
    print("        await sandbox.execute('pip install pandas')")
    print("        await sandbox.execute('python3 process.py')")
    print("        ")
    print("        # Download results")
    print("        return await sandbox.download_file('output.csv')")
    print("```")

    # Demonstrate data processing
    print("\nActual data processing demonstration:")

    sandbox = create_dev_sandbox()
    async with sandbox:
        # Create sample data
        sample_data = """name,age,city
Alice,25,New York
Bob,30,San Francisco
Charlie,35,Chicago
Diana,28,Boston"""

        await sandbox.upload_file("data.csv", sample_data)
        print("   📁 Sample data uploaded")

        # Create processing script
        processing_script = """
import csv
import json

# Read CSV data
data = []
with open('data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

# Process data (calculate average age)
total_age = sum(int(person['age']) for person in data)
avg_age = total_age / len(data)

# Create summary
summary = {
    "total_people": len(data),
    "average_age": avg_age,
    "cities": list(set(person['city'] for person in data))
}

# Save results
with open('summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print(f"Processed {len(data)} records")
print(f"Average age: {avg_age:.1f}")
print(f"Cities: {', '.join(summary['cities'])}")
"""

        await sandbox.upload_file("process.py", processing_script)
        result = await sandbox.execute("python3 process.py")
        print(f"   🔄 Processing output: {result.stdout.strip()}")

        # Download results
        summary_data = await sandbox.download_file("summary.json")
        summary = json.loads(summary_data.decode())
        print(f"   📈 Results: {summary}")


async def microservice_pattern():
    """Pattern for using grainchain in microservice architectures."""
    print("\n🏗️ Microservice Integration Pattern")
    print("=" * 45)

    print("# Example FastAPI microservice:")
    print("```python")
    print("from fastapi import FastAPI")
    print("from grainchain import create_local_sandbox")
    print("")
    print("app = FastAPI()")
    print("")
    print("@app.post('/execute')")
    print("async def execute_code(code: str):")
    print("    async with create_local_sandbox(timeout=30) as sandbox:")
    print("        result = await sandbox.execute(f'python3 -c \"{code}\"')")
    print("        return {'success': result.success, 'output': result.stdout}")
    print("```")

    # Simulate microservice behavior
    print("\nSimulating microservice requests:")

    async def simulate_microservice_request(code: str, request_id: int):
        print(f"   Request {request_id}: Executing code")
        async with create_local_sandbox(timeout=30) as sandbox:
            result = await sandbox.execute(f"python3 -c '{code}'")
            response = {
                "request_id": request_id,
                "success": result.success,
                "output": result.stdout.strip(),
                "error": result.stderr.strip() if not result.success else None,
            }
            print(f"   Response {request_id}: {response}")
            return response

    # Simulate multiple requests
    requests = [
        "print('Hello from request 1')",
        "print(f'2 + 2 = {2 + 2}')",
        "import datetime; print(f'Current time: {datetime.datetime.now()}')",
    ]

    for i, code in enumerate(requests, 1):
        await simulate_microservice_request(code, i)


async def main():
    """Run all integration pattern examples."""
    try:
        await jupyter_notebook_pattern()
        testing_framework_pattern()
        await ci_cd_pattern()
        await data_pipeline_pattern()
        await microservice_pattern()

        print("\n🎯 Integration Patterns Summary")
        print("=" * 45)
        print("✅ Jupyter Notebook: Use async context managers")
        print("✅ Testing: Create fixtures with test sandboxes")
        print("✅ CI/CD: Use QuickSandbox for simpler integration")
        print("✅ Data Pipelines: Use data-specific configurations")
        print("✅ Microservices: Async context managers for requests")

        print("\n💡 Best Practices:")
        print("   • Use appropriate sandbox configurations for each use case")
        print("   • Handle timeouts appropriately for your environment")
        print("   • Clean up resources properly (context managers help)")
        print("   • Use synchronous API when async is not needed")
        print("   • Consider provider capabilities for your use case")

    except Exception as e:
        print(f"\n❌ Integration pattern example failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
