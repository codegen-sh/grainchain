# Grainchain Integration Guide

This guide shows how to integrate Grainchain into your Python projects and applications.

## Table of Contents

- [Basic Integration](#basic-integration)
- [Framework Integration](#framework-integration)
- [Production Best Practices](#production-best-practices)
- [Error Handling](#error-handling)
- [Configuration Management](#configuration-management)
- [Performance Optimization](#performance-optimization)
- [Real-World Examples](#real-world-examples)

## Basic Integration

### Simple Integration

```python
from grainchain import Sandbox, SandboxConfig

class CodeExecutor:
    def __init__(self, provider="local"):
        self.provider = provider

    async def execute_code(self, code: str, language: str = "python"):
        """Execute code in a sandbox and return results."""
        async with Sandbox(provider=self.provider) as sandbox:
            if language == "python":
                await sandbox.upload_file("script.py", code)
                result = await sandbox.execute("python script.py")
            elif language == "bash":
                result = await sandbox.execute(code)
            else:
                raise ValueError(f"Unsupported language: {language}")

            return {
                "success": result.success,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.return_code
            }

# Usage
executor = CodeExecutor()
result = await executor.execute_code("print('Hello, World!')")
print(result["output"])  # "Hello, World!"
```

### Data Processing Pipeline

```python
from grainchain import Sandbox, SandboxConfig
from typing import List, Dict, Any
import json

class DataProcessor:
    def __init__(self, provider="local", timeout=300):
        self.provider = provider
        self.config = SandboxConfig(timeout=timeout)

    async def process_data(self, data: List[Dict], script: str) -> Dict[str, Any]:
        """Process data using a custom script in a sandbox."""
        async with Sandbox(provider=self.provider, config=self.config) as sandbox:
            # Upload data
            data_json = json.dumps(data, indent=2)
            await sandbox.upload_file("data.json", data_json)

            # Upload processing script
            await sandbox.upload_file("process.py", script)

            # Execute processing
            result = await sandbox.execute("python process.py")

            if not result.success:
                raise RuntimeError(f"Processing failed: {result.stderr}")

            # Download results
            try:
                results_content = await sandbox.download_file("results.json")
                return json.loads(results_content.decode())
            except Exception:
                # Return raw output if JSON parsing fails
                return {"raw_output": result.stdout}

# Usage
processor = DataProcessor()
data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
script = """
import json

with open('data.json', 'r') as f:
    data = json.load(f)

# Process data
average_age = sum(person['age'] for person in data) / len(data)
results = {
    'total_people': len(data),
    'average_age': average_age,
    'names': [person['name'] for person in data]
}

with open('results.json', 'w') as f:
    json.dump(results, f)
"""

results = await processor.process_data(data, script)
print(results)  # {'total_people': 2, 'average_age': 27.5, 'names': ['Alice', 'Bob']}
```

## Framework Integration

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from grainchain import Sandbox, SandboxConfig
import asyncio

app = FastAPI()

class CodeRequest(BaseModel):
    code: str
    language: str = "python"
    timeout: int = 60

class CodeResponse(BaseModel):
    success: bool
    output: str
    error: str
    execution_time: float

@app.post("/execute", response_model=CodeResponse)
async def execute_code(request: CodeRequest):
    """Execute code in a sandbox via REST API."""
    import time
    start_time = time.time()

    try:
        config = SandboxConfig(timeout=request.timeout)
        async with Sandbox(provider="local", config=config) as sandbox:
            if request.language == "python":
                await sandbox.upload_file("script.py", request.code)
                result = await sandbox.execute("python script.py")
            elif request.language == "bash":
                result = await sandbox.execute(request.code)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported language: {request.language}")

            execution_time = time.time() - start_time

            return CodeResponse(
                success=result.success,
                output=result.stdout,
                error=result.stderr,
                execution_time=execution_time
            )

    except Exception as e:
        execution_time = time.time() - start_time
        return CodeResponse(
            success=False,
            output="",
            error=str(e),
            execution_time=execution_time
        )

# Run with: uvicorn main:app --reload
```

### Django Integration

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from grainchain import Sandbox, SandboxConfig
import json
import asyncio

@csrf_exempt
@require_http_methods(["POST"])
def execute_code(request):
    """Django view for code execution."""
    try:
        data = json.loads(request.body)
        code = data.get('code', '')
        language = data.get('language', 'python')

        # Run async code in sync Django view
        result = asyncio.run(_execute_code_async(code, language))

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

async def _execute_code_async(code: str, language: str):
    """Async helper for code execution."""
    config = SandboxConfig(timeout=60)
    async with Sandbox(provider="local", config=config) as sandbox:
        if language == "python":
            await sandbox.upload_file("script.py", code)
            result = await sandbox.execute("python script.py")
        else:
            result = await sandbox.execute(code)

        return {
            'success': result.success,
            'output': result.stdout,
            'error': result.stderr
        }

# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('execute/', views.execute_code, name='execute_code'),
]
```

### Flask Integration

```python
from flask import Flask, request, jsonify
from grainchain import Sandbox, SandboxConfig
import asyncio

app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def execute_code():
    """Flask endpoint for code execution."""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language = data.get('language', 'python')

        # Run async code in sync Flask route
        result = asyncio.run(_execute_code_async(code, language))

        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

async def _execute_code_async(code: str, language: str):
    """Async helper for code execution."""
    config = SandboxConfig(timeout=60)
    async with Sandbox(provider="local", config=config) as sandbox:
        if language == "python":
            await sandbox.upload_file("script.py", code)
            result = await sandbox.execute("python script.py")
        else:
            result = await sandbox.execute(code)

        return {
            'success': result.success,
            'output': result.stdout,
            'error': result.stderr
        }

if __name__ == '__main__':
    app.run(debug=True)
```

## Production Best Practices

### Configuration Management

```python
import os
from dataclasses import dataclass
from grainchain import Sandbox, SandboxConfig

@dataclass
class AppConfig:
    """Application configuration."""
    default_provider: str = "local"
    default_timeout: int = 300
    max_concurrent_sandboxes: int = 10
    e2b_api_key: str = ""
    morph_api_key: str = ""
    daytona_api_key: str = ""

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables."""
        return cls(
            default_provider=os.getenv("GRAINCHAIN_DEFAULT_PROVIDER", "local"),
            default_timeout=int(os.getenv("GRAINCHAIN_DEFAULT_TIMEOUT", "300")),
            max_concurrent_sandboxes=int(os.getenv("GRAINCHAIN_MAX_CONCURRENT", "10")),
            e2b_api_key=os.getenv("E2B_API_KEY", ""),
            morph_api_key=os.getenv("MORPH_API_KEY", ""),
            daytona_api_key=os.getenv("DAYTONA_API_KEY", ""),
        )

class SandboxManager:
    """Production-ready sandbox manager."""

    def __init__(self, config: AppConfig):
        self.config = config
        self._semaphore = asyncio.Semaphore(config.max_concurrent_sandboxes)

    async def execute_with_limits(self, code: str, provider: str = None):
        """Execute code with concurrency limits."""
        async with self._semaphore:
            provider = provider or self.config.default_provider
            sandbox_config = SandboxConfig(timeout=self.config.default_timeout)

            async with Sandbox(provider=provider, config=sandbox_config) as sandbox:
                await sandbox.upload_file("script.py", code)
                return await sandbox.execute("python script.py")

# Usage
config = AppConfig.from_env()
manager = SandboxManager(config)
result = await manager.execute_with_limits("print('Hello')")
```

### Error Handling and Retry Logic

```python
import asyncio
from typing import Optional
from grainchain import Sandbox, SandboxConfig
from grainchain.core.exceptions import SandboxError, ProviderError

class RobustExecutor:
    """Executor with retry logic and comprehensive error handling."""

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def execute_with_retry(
        self,
        code: str,
        provider: str = "local",
        timeout: int = 300
    ) -> dict:
        """Execute code with automatic retry on failures."""
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                config = SandboxConfig(timeout=timeout)
                async with Sandbox(provider=provider, config=config) as sandbox:
                    await sandbox.upload_file("script.py", code)
                    result = await sandbox.execute("python script.py")

                    return {
                        "success": True,
                        "output": result.stdout,
                        "error": result.stderr,
                        "attempt": attempt + 1
                    }

            except ProviderError as e:
                last_error = e
                if "API key" in str(e) or "authentication" in str(e).lower():
                    # Don't retry authentication errors
                    break

                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff

            except SandboxError as e:
                last_error = e
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay)

            except Exception as e:
                last_error = e
                break  # Don't retry unexpected errors

        return {
            "success": False,
            "output": "",
            "error": str(last_error),
            "attempt": attempt + 1
        }

# Usage
executor = RobustExecutor(max_retries=3)
result = await executor.execute_with_retry("print('Hello')", provider="e2b")
```

### Monitoring and Logging

```python
import logging
import time
from contextlib import asynccontextmanager
from grainchain import Sandbox, SandboxConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoredSandbox:
    """Sandbox wrapper with monitoring and logging."""

    def __init__(self, provider: str = "local", config: SandboxConfig = None):
        self.provider = provider
        self.config = config or SandboxConfig()

    @asynccontextmanager
    async def create_sandbox(self):
        """Create a sandbox with monitoring."""
        start_time = time.time()
        sandbox_id = None

        try:
            logger.info(f"Creating sandbox with provider: {self.provider}")

            async with Sandbox(provider=self.provider, config=self.config) as sandbox:
                sandbox_id = sandbox.sandbox_id
                creation_time = time.time() - start_time

                logger.info(f"Sandbox created: {sandbox_id} in {creation_time:.2f}s")

                yield sandbox

        except Exception as e:
            logger.error(f"Sandbox error: {e}", exc_info=True)
            raise

        finally:
            total_time = time.time() - start_time
            logger.info(f"Sandbox {sandbox_id} lifecycle completed in {total_time:.2f}s")

    async def execute_monitored(self, command: str):
        """Execute command with performance monitoring."""
        async with self.create_sandbox() as sandbox:
            start_time = time.time()

            logger.info(f"Executing command: {command[:50]}...")

            result = await sandbox.execute(command)

            execution_time = time.time() - start_time

            logger.info(
                f"Command executed in {execution_time:.2f}s, "
                f"success: {result.success}, "
                f"return_code: {result.return_code}"
            )

            if not result.success:
                logger.warning(f"Command failed: {result.stderr}")

            return result

# Usage
monitored = MonitoredSandbox(provider="local")
result = await monitored.execute_monitored("python -c 'print(\"Hello\")'")
```

## Performance Optimization

### Connection Pooling

```python
import asyncio
from typing import Dict, List
from grainchain import Sandbox, SandboxConfig

class SandboxPool:
    """Pool of reusable sandbox connections."""

    def __init__(self, provider: str, pool_size: int = 5):
        self.provider = provider
        self.pool_size = pool_size
        self._pool: List[Sandbox] = []
        self._in_use: Dict[str, Sandbox] = {}
        self._lock = asyncio.Lock()

    async def initialize(self):
        """Initialize the sandbox pool."""
        config = SandboxConfig(timeout=300)

        for _ in range(self.pool_size):
            sandbox = Sandbox(provider=self.provider, config=config)
            await sandbox.__aenter__()
            self._pool.append(sandbox)

    async def acquire(self) -> Sandbox:
        """Acquire a sandbox from the pool."""
        async with self._lock:
            if self._pool:
                sandbox = self._pool.pop()
                self._in_use[sandbox.sandbox_id] = sandbox
                return sandbox
            else:
                # Pool exhausted, create new sandbox
                config = SandboxConfig(timeout=300)
                sandbox = Sandbox(provider=self.provider, config=config)
                await sandbox.__aenter__()
                self._in_use[sandbox.sandbox_id] = sandbox
                return sandbox

    async def release(self, sandbox: Sandbox):
        """Release a sandbox back to the pool."""
        async with self._lock:
            if sandbox.sandbox_id in self._in_use:
                del self._in_use[sandbox.sandbox_id]

                if len(self._pool) < self.pool_size:
                    self._pool.append(sandbox)
                else:
                    await sandbox.__aexit__(None, None, None)

    async def cleanup(self):
        """Clean up all sandboxes in the pool."""
        async with self._lock:
            for sandbox in self._pool + list(self._in_use.values()):
                await sandbox.__aexit__(None, None, None)

            self._pool.clear()
            self._in_use.clear()

# Usage
pool = SandboxPool(provider="local", pool_size=3)
await pool.initialize()

try:
    sandbox = await pool.acquire()
    result = await sandbox.execute("echo 'Hello from pool'")
    await pool.release(sandbox)
finally:
    await pool.cleanup()
```

### Batch Processing

```python
import asyncio
from typing import List, Dict, Any
from grainchain import Sandbox, SandboxConfig

class BatchProcessor:
    """Process multiple tasks in parallel using sandboxes."""

    def __init__(self, provider: str = "local", max_concurrent: int = 5):
        self.provider = provider
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single task."""
        async with self._semaphore:
            config = SandboxConfig(timeout=task.get("timeout", 300))

            async with Sandbox(provider=self.provider, config=config) as sandbox:
                # Upload task data
                if "files" in task:
                    for filename, content in task["files"].items():
                        await sandbox.upload_file(filename, content)

                # Execute task command
                result = await sandbox.execute(task["command"])

                # Download results if specified
                outputs = {}
                if "output_files" in task:
                    for filename in task["output_files"]:
                        try:
                            content = await sandbox.download_file(filename)
                            outputs[filename] = content.decode()
                        except Exception as e:
                            outputs[filename] = f"Error: {e}"

                return {
                    "task_id": task.get("id", "unknown"),
                    "success": result.success,
                    "output": result.stdout,
                    "error": result.stderr,
                    "files": outputs
                }

    async def process_batch(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple tasks in parallel."""
        # Create tasks for asyncio
        async_tasks = [self.process_task(task) for task in tasks]

        # Execute all tasks concurrently
        results = await asyncio.gather(*async_tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "task_id": tasks[i].get("id", f"task_{i}"),
                    "success": False,
                    "output": "",
                    "error": str(result),
                    "files": {}
                })
            else:
                processed_results.append(result)

        return processed_results

# Usage
processor = BatchProcessor(provider="local", max_concurrent=3)

tasks = [
    {
        "id": "task_1",
        "command": "python script.py",
        "files": {"script.py": "print('Task 1')"},
        "timeout": 60
    },
    {
        "id": "task_2",
        "command": "python script.py",
        "files": {"script.py": "print('Task 2')"},
        "timeout": 60
    }
]

results = await processor.process_batch(tasks)
for result in results:
    print(f"Task {result['task_id']}: {result['output']}")
```

## Real-World Examples

### Code Playground Backend

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from grainchain import Sandbox, SandboxConfig
import json
import asyncio

app = FastAPI()

class CodePlayground:
    """Real-time code execution playground."""

    def __init__(self):
        self.active_sessions = {}

    async def handle_websocket(self, websocket: WebSocket, session_id: str):
        """Handle WebSocket connection for real-time code execution."""
        await websocket.accept()

        try:
            config = SandboxConfig(timeout=30)
            async with Sandbox(provider="local", config=config) as sandbox:
                self.active_sessions[session_id] = {
                    "websocket": websocket,
                    "sandbox": sandbox
                }

                await websocket.send_json({
                    "type": "connected",
                    "sandbox_id": sandbox.sandbox_id
                })

                while True:
                    data = await websocket.receive_json()

                    if data["type"] == "execute":
                        await self._execute_code(websocket, sandbox, data["code"])
                    elif data["type"] == "upload":
                        await self._upload_file(websocket, sandbox, data["filename"], data["content"])
                    elif data["type"] == "list_files":
                        await self._list_files(websocket, sandbox)

        except WebSocketDisconnect:
            pass
        finally:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

    async def _execute_code(self, websocket: WebSocket, sandbox: Sandbox, code: str):
        """Execute code and send results via WebSocket."""
        try:
            await websocket.send_json({"type": "executing"})

            result = await sandbox.execute(code)

            await websocket.send_json({
                "type": "result",
                "success": result.success,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.return_code
            })

        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })

    async def _upload_file(self, websocket: WebSocket, sandbox: Sandbox, filename: str, content: str):
        """Upload file to sandbox."""
        try:
            await sandbox.upload_file(filename, content)
            await websocket.send_json({
                "type": "file_uploaded",
                "filename": filename
            })
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": f"Failed to upload {filename}: {e}"
            })

    async def _list_files(self, websocket: WebSocket, sandbox: Sandbox):
        """List files in sandbox."""
        try:
            files = await sandbox.list_files(".")
            file_list = [{"name": f.name, "size": f.size, "is_directory": f.is_directory} for f in files]

            await websocket.send_json({
                "type": "file_list",
                "files": file_list
            })
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "message": f"Failed to list files: {e}"
            })

playground = CodePlayground()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await playground.handle_websocket(websocket, session_id)
```

### AI Code Assistant

```python
from grainchain import Sandbox, SandboxConfig
from typing import List, Dict, Any
import re

class AICodeAssistant:
    """AI-powered code assistant using Grainchain for safe execution."""

    def __init__(self, provider: str = "local"):
        self.provider = provider

    async def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze code for potential issues and suggestions."""
        config = SandboxConfig(timeout=60)

        async with Sandbox(provider=self.provider, config=config) as sandbox:
            # Create analysis script
            analysis_script = f'''
import ast
import sys

code = """{code}"""

try:
    tree = ast.parse(code)

    # Basic analysis
    analysis = {{
        "syntax_valid": True,
        "functions": [],
        "classes": [],
        "imports": [],
        "variables": []
    }}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            analysis["functions"].append(node.name)
        elif isinstance(node, ast.ClassDef):
            analysis["classes"].append(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                analysis["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                analysis["imports"].append(f"{{module}}.{{alias.name}}")
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            analysis["variables"].append(node.id)

    print("ANALYSIS_RESULT:", analysis)

except SyntaxError as e:
    print("SYNTAX_ERROR:", str(e))
except Exception as e:
    print("ERROR:", str(e))
'''

            await sandbox.upload_file("analyze.py", analysis_script)
            result = await sandbox.execute("python analyze.py")

            # Parse results
            if "ANALYSIS_RESULT:" in result.stdout:
                import ast
                analysis_str = result.stdout.split("ANALYSIS_RESULT:")[1].strip()
                return ast.literal_eval(analysis_str)
            elif "SYNTAX_ERROR:" in result.stdout:
                error = result.stdout.split("SYNTAX_ERROR:")[1].strip()
                return {"syntax_valid": False, "error": error}
            else:
                return {"syntax_valid": False, "error": "Analysis failed"}

    async def test_code(self, code: str, test_cases: List[Dict]) -> Dict[str, Any]:
        """Test code against provided test cases."""
        config = SandboxConfig(timeout=120)

        async with Sandbox(provider=self.provider, config=config) as sandbox:
            # Upload the code to test
            await sandbox.upload_file("user_code.py", code)

            # Create test runner
            test_script = f'''
import sys
import json
from user_code import *

test_cases = {json.dumps(test_cases)}
results = []

for i, test_case in enumerate(test_cases):
    try:
        # Execute the test
        if "function" in test_case:
            func = globals()[test_case["function"]]
            args = test_case.get("args", [])
            kwargs = test_case.get("kwargs", {{}})
            result = func(*args, **kwargs)

            expected = test_case.get("expected")
            passed = result == expected if expected is not None else True

            results.append({{
                "test_id": i,
                "passed": passed,
                "result": str(result),
                "expected": str(expected),
                "error": None
            }})

    except Exception as e:
        results.append({{
            "test_id": i,
            "passed": False,
            "result": None,
            "expected": test_case.get("expected"),
            "error": str(e)
        }})

print("TEST_RESULTS:", json.dumps(results))
'''

            await sandbox.upload_file("test_runner.py", test_script)
            result = await sandbox.execute("python test_runner.py")

            # Parse test results
            if "TEST_RESULTS:" in result.stdout:
                import json
                results_str = result.stdout.split("TEST_RESULTS:")[1].strip()
                return json.loads(results_str)
            else:
                return {"error": "Test execution failed", "output": result.stdout, "stderr": result.stderr}

# Usage
assistant = AICodeAssistant()

# Analyze code
code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

analysis = await assistant.analyze_code(code)
print("Analysis:", analysis)

# Test code
test_cases = [
    {"function": "fibonacci", "args": [0], "expected": 0},
    {"function": "fibonacci", "args": [1], "expected": 1},
    {"function": "fibonacci", "args": [5], "expected": 5}
]

test_results = await assistant.test_code(code, test_cases)
print("Test results:", test_results)
```

This integration guide provides comprehensive examples for using Grainchain in real-world applications, from simple integrations to complex production systems. The examples demonstrate best practices for error handling, performance optimization, and scalability.
