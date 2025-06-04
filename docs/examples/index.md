# Examples

This section provides practical examples of using GrainChain in real-world scenarios. From basic usage patterns to advanced integration examples, you'll find code samples and tutorials to help you get the most out of GrainChain.

## Quick Examples

### Basic Code Execution

```python
import asyncio
from grainchain import Sandbox

async def basic_example():
    async with Sandbox() as sandbox:
        # Execute a simple command
        result = await sandbox.execute("echo 'Hello, GrainChain!'")
        print(f"Output: {result.stdout}")
        print(f"Exit code: {result.exit_code}")

asyncio.run(basic_example())
```

### File Operations

```python
async def file_operations():
    async with Sandbox() as sandbox:
        # Upload a Python script
        script_content = '''
import json
import sys

data = {"message": "Hello from sandbox!", "args": sys.argv[1:]}
print(json.dumps(data, indent=2))
'''
        await sandbox.upload_file("hello.py", script_content)
        
        # Execute the script with arguments
        result = await sandbox.execute("python hello.py arg1 arg2")
        print(result.stdout)
        
        # Download the script back
        downloaded = await sandbox.download_file("hello.py")
        print(f"Downloaded {len(downloaded)} bytes")
```

### Error Handling

```python
from grainchain.exceptions import ExecutionError, TimeoutError

async def error_handling_example():
    async with Sandbox() as sandbox:
        try:
            # This will fail
            result = await sandbox.execute("python nonexistent_script.py")
        except ExecutionError as e:
            print(f"Execution failed: {e.stderr}")
        
        try:
            # This will timeout
            result = await sandbox.execute("sleep 60", timeout=5)
        except TimeoutError:
            print("Command timed out")
```

## Use Case Examples

### AI Code Generation and Testing

```python
async def ai_code_testing():
    """Example of testing AI-generated code safely"""
    
    # Simulated AI-generated code
    generated_code = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"fib({i}) = {fibonacci(i)}")
'''
    
    async with Sandbox() as sandbox:
        # Upload the generated code
        await sandbox.upload_file("generated.py", generated_code)
        
        # Test it safely
        result = await sandbox.execute("python generated.py")
        
        if result.exit_code == 0:
            print("Generated code executed successfully!")
            print(result.stdout)
        else:
            print("Generated code failed:")
            print(result.stderr)
```

### Educational Platform

```python
async def student_code_evaluation():
    """Example of evaluating student submissions"""
    
    student_submission = '''
def sort_numbers(numbers):
    return sorted(numbers)

# Test cases
test_cases = [
    [3, 1, 4, 1, 5],
    [10, 2, 8, 5],
    []
]

for test in test_cases:
    result = sort_numbers(test)
    print(f"Input: {test}, Output: {result}")
'''
    
    async with Sandbox() as sandbox:
        # Upload student code
        await sandbox.upload_file("submission.py", student_submission)
        
        # Upload test framework
        test_framework = '''
import sys
import json
sys.path.append('.')
from submission import sort_numbers

def run_tests():
    tests = [
        ([3, 1, 4, 1, 5], [1, 1, 3, 4, 5]),
        ([10, 2, 8, 5], [2, 5, 8, 10]),
        ([], [])
    ]
    
    results = []
    for input_data, expected in tests:
        try:
            actual = sort_numbers(input_data)
            passed = actual == expected
            results.append({
                "input": input_data,
                "expected": expected,
                "actual": actual,
                "passed": passed
            })
        except Exception as e:
            results.append({
                "input": input_data,
                "error": str(e),
                "passed": False
            })
    
    return results

if __name__ == "__main__":
    results = run_tests()
    print(json.dumps(results, indent=2))
'''
        
        await sandbox.upload_file("test_runner.py", test_framework)
        
        # Run tests
        result = await sandbox.execute("python test_runner.py")
        
        if result.exit_code == 0:
            import json
            test_results = json.loads(result.stdout)
            
            passed = sum(1 for r in test_results if r.get("passed", False))
            total = len(test_results)
            
            print(f"Tests passed: {passed}/{total}")
            for i, test in enumerate(test_results):
                status = "✅" if test.get("passed") else "❌"
                print(f"  Test {i+1}: {status}")
```

### Data Processing Pipeline

```python
async def data_processing_pipeline():
    """Example of running a data processing pipeline"""
    
    # Sample data processing script
    pipeline_script = '''
import json
import csv
from io import StringIO

# Sample data
data = [
    {"name": "Alice", "age": 30, "city": "New York"},
    {"name": "Bob", "age": 25, "city": "San Francisco"},
    {"name": "Charlie", "age": 35, "city": "Chicago"}
]

# Process data
processed = []
for person in data:
    processed.append({
        "name": person["name"].upper(),
        "age_group": "young" if person["age"] < 30 else "adult",
        "city": person["city"]
    })

# Output as CSV
output = StringIO()
writer = csv.DictWriter(output, fieldnames=["name", "age_group", "city"])
writer.writeheader()
writer.writerows(processed)

print("Processed data:")
print(output.getvalue())

# Save to file
with open("processed_data.csv", "w") as f:
    f.write(output.getvalue())

print("Data saved to processed_data.csv")
'''
    
    async with Sandbox() as sandbox:
        # Upload and run the pipeline
        await sandbox.upload_file("pipeline.py", pipeline_script)
        result = await sandbox.execute("python pipeline.py")
        
        print("Pipeline output:")
        print(result.stdout)
        
        # Download the processed data
        csv_data = await sandbox.download_file("processed_data.csv")
        print("\nProcessed CSV data:")
        print(csv_data)
```

## Integration Examples

### Web API Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

app = FastAPI()

class CodeExecutionRequest(BaseModel):
    code: str
    language: str = "python"
    timeout: int = 30

@app.post("/execute")
async def execute_code(request: CodeExecutionRequest):
    """API endpoint for code execution"""
    
    try:
        async with Sandbox() as sandbox:
            if request.language == "python":
                # Upload code to a file
                await sandbox.upload_file("user_code.py", request.code)
                result = await sandbox.execute(
                    "python user_code.py", 
                    timeout=request.timeout
                )
            else:
                raise HTTPException(400, "Unsupported language")
            
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.exit_code,
                "execution_time": result.execution_time
            }
    
    except Exception as e:
        raise HTTPException(500, f"Execution failed: {str(e)}")
```

### Jupyter Notebook Integration

```python
# In a Jupyter notebook cell
import asyncio
from grainchain import Sandbox

async def notebook_execution():
    """Execute code from notebook in sandbox"""
    
    # Code from notebook cell
    notebook_code = '''
import matplotlib.pyplot as plt
import numpy as np

# Generate data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create plot
plt.figure(figsize=(10, 6))
plt.plot(x, y)
plt.title("Sine Wave")
plt.xlabel("X")
plt.ylabel("Y")
plt.grid(True)
plt.savefig("sine_wave.png", dpi=150, bbox_inches="tight")
plt.show()

print("Plot saved as sine_wave.png")
'''
    
    async with Sandbox() as sandbox:
        # Install required packages
        await sandbox.execute("pip install matplotlib numpy")
        
        # Upload and run the code
        await sandbox.upload_file("plot_code.py", notebook_code)
        result = await sandbox.execute("python plot_code.py")
        
        print(result.stdout)
        
        # Download the generated plot
        plot_data = await sandbox.download_file("sine_wave.png")
        
        # Save locally
        with open("downloaded_plot.png", "wb") as f:
            f.write(plot_data)
        
        print("Plot downloaded successfully!")

# Run in notebook
await notebook_execution()
```

## Next Steps

- [Basic Usage](/examples/basic) - Simple examples to get started
- [Advanced Patterns](/examples/advanced) - Complex use cases and patterns
- [Integration Examples](/examples/integrations) - Real-world integration scenarios
- [API Reference](/api/) - Complete API documentation
- [CLI Reference](/cli/) - Command-line interface guide

