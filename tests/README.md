# Grainchain Test Suite

This directory contains the comprehensive test suite for Grainchain, providing thorough coverage of all components and functionality.

## 📁 Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── unit/                          # Unit tests (fast, isolated)
│   ├── test_sandbox.py           # Core Sandbox class tests
│   ├── test_providers.py         # Provider implementation tests
│   ├── test_config.py            # Configuration system tests
│   └── test_exceptions.py        # Exception handling tests
├── integration/                   # Integration tests (real providers)
│   ├── test_e2b_provider.py      # E2B provider integration tests
│   ├── test_modal_provider.py    # Modal provider integration tests
│   └── test_local_provider.py    # Local provider integration tests
└── README.md                     # This file
```

## 🚀 Quick Start

### Install Test Dependencies

```bash
# Install test dependencies
pip install -e ".[test]"

# Or install all development dependencies
pip install -e ".[dev]"
```

### Run All Tests

```bash
# Using pytest directly
pytest

# Using the test runner script
python run_tests.py all
```

### Run Specific Test Types

```bash
# Unit tests only (fast)
python run_tests.py unit

# Integration tests only
python run_tests.py integration

# Specific provider tests
python run_tests.py e2b      # Requires E2B_API_KEY
python run_tests.py modal    # Requires MODAL_TOKEN_ID and MODAL_TOKEN_SECRET
python run_tests.py local    # No credentials required
```

## 🧪 Test Categories

### Unit Tests

**Location**: `tests/unit/`  
**Speed**: Fast (< 30 seconds total)  
**Dependencies**: None (uses mocks)

Unit tests verify individual components in isolation:

- **Sandbox Core**: Main interface, context management, error handling
- **Providers**: All provider implementations with mocked dependencies
- **Configuration**: Config loading, validation, environment variable handling
- **Exceptions**: Custom exception types and error scenarios

```bash
# Run unit tests
pytest tests/unit/ -v

# Run specific unit test file
pytest tests/unit/test_sandbox.py -v
```

### Integration Tests

**Location**: `tests/integration/`  
**Speed**: Slower (may take several minutes)  
**Dependencies**: Real provider credentials (optional)

Integration tests verify end-to-end functionality with real providers:

- **E2B Integration**: Real E2B sandbox operations
- **Modal Integration**: Real Modal serverless execution
- **Local Integration**: Real local filesystem and subprocess operations

```bash
# Run integration tests
pytest tests/integration/ -v

# Run with specific markers
pytest -m "integration and not slow" -v
```

## 🔧 Configuration

### Environment Variables

Set these environment variables to enable provider-specific integration tests:

```bash
# E2B Provider
export E2B_API_KEY="your-e2b-api-key"

# Modal Provider
export MODAL_TOKEN_ID="your-modal-token-id"
export MODAL_TOKEN_SECRET="your-modal-token-secret"

# Optional: Default provider for tests
export GRAINCHAIN_DEFAULT_PROVIDER="local"
```

### Test Markers

Tests are organized using pytest markers:

- `unit`: Unit tests (fast, no external dependencies)
- `integration`: Integration tests (may require external services)
- `e2b`: Tests requiring E2B credentials
- `modal`: Tests requiring Modal credentials
- `slow`: Slow running tests (> 10 seconds)

```bash
# Run only fast tests
pytest -m "not slow" -v

# Run only E2B tests
pytest -m "e2b" -v

# Run integration tests except slow ones
pytest -m "integration and not slow" -v
```

## 📊 Coverage

The test suite aims for >90% code coverage across all components.

### Generate Coverage Report

```bash
# Run tests with coverage
python run_tests.py coverage

# Or using pytest directly
pytest --cov=grainchain --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html
```

### Coverage Targets

- **Overall**: >90%
- **Core modules**: >95%
- **Provider implementations**: >90%
- **Configuration system**: >95%

## 🏃‍♂️ Running Tests

### Using the Test Runner

The `run_tests.py` script provides convenient commands:

```bash
# Basic usage
python run_tests.py <test_type> [options]

# Examples
python run_tests.py unit --verbose
python run_tests.py integration --parallel
python run_tests.py all --html-cov
python run_tests.py e2b --fail-fast
```

**Options:**
- `--verbose, -v`: Verbose output
- `--parallel, -p`: Run tests in parallel
- `--no-cov`: Disable coverage reporting
- `--html-cov`: Generate HTML coverage report
- `--fail-fast, -x`: Stop on first failure

### Using Pytest Directly

```bash
# Basic test run
pytest

# Verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_sandbox.py

# Run specific test function
pytest tests/unit/test_sandbox.py::TestSandbox::test_sandbox_creation

# Run with coverage
pytest --cov=grainchain --cov-report=term-missing

# Run in parallel
pytest -n auto

# Stop on first failure
pytest -x
```

## 🔍 Test Development

### Writing New Tests

1. **Unit Tests**: Add to appropriate file in `tests/unit/`
2. **Integration Tests**: Add to appropriate file in `tests/integration/`
3. **Use Fixtures**: Leverage shared fixtures from `conftest.py`
4. **Add Markers**: Use appropriate pytest markers
5. **Mock External Dependencies**: Use mocks for unit tests

### Test Naming Convention

```python
class TestComponentName:
    """Test cases for ComponentName."""
    
    def test_component_basic_functionality(self):
        """Test basic functionality of component."""
        pass
    
    async def test_component_async_operation(self):
        """Test async operations of component."""
        pass
    
    def test_component_error_handling(self):
        """Test error handling in component."""
        pass
```

### Using Fixtures

```python
async def test_sandbox_operation(mock_sandbox, sample_python_code):
    """Test using shared fixtures."""
    await mock_sandbox.upload_file("script.py", sample_python_code)
    result = await mock_sandbox.execute("python script.py")
    assert result.success
```

### Adding New Fixtures

Add shared fixtures to `tests/conftest.py`:

```python
@pytest.fixture
def my_test_fixture():
    """Provide test data for multiple tests."""
    return {"key": "value"}
```

## 🐛 Debugging Tests

### Running Individual Tests

```bash
# Run single test with verbose output
pytest tests/unit/test_sandbox.py::TestSandbox::test_sandbox_creation -v -s

# Run with debugger
pytest tests/unit/test_sandbox.py::TestSandbox::test_sandbox_creation --pdb
```

### Common Issues

1. **Missing Credentials**: Set environment variables for integration tests
2. **Async Issues**: Ensure `pytest-asyncio` is installed and configured
3. **Import Errors**: Install package in development mode: `pip install -e .`
4. **Timeout Issues**: Increase timeout for slow tests or use `@pytest.mark.slow`

### Test Output

```bash
# Show print statements
pytest -s

# Show local variables on failure
pytest --tb=long

# Show only failures
pytest --tb=short
```

## 📈 Performance

### Test Execution Times

- **Unit Tests**: ~30 seconds
- **Integration Tests (Local)**: ~2 minutes
- **Integration Tests (E2B)**: ~5 minutes (with credentials)
- **Integration Tests (Modal)**: ~5 minutes (with credentials)
- **Full Suite**: ~10 minutes (with all credentials)

### Optimization Tips

1. **Run Unit Tests First**: Fast feedback loop
2. **Use Parallel Execution**: `pytest -n auto`
3. **Skip Slow Tests**: `pytest -m "not slow"`
4. **Use Specific Markers**: Target specific functionality

## 🔄 Continuous Integration

### GitHub Actions

The test suite is designed to work with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Unit Tests
  run: python run_tests.py unit

- name: Run Integration Tests
  run: python run_tests.py integration
  env:
    E2B_API_KEY: ${{ secrets.E2B_API_KEY }}
    MODAL_TOKEN_ID: ${{ secrets.MODAL_TOKEN_ID }}
    MODAL_TOKEN_SECRET: ${{ secrets.MODAL_TOKEN_SECRET }}
```

### Coverage Reporting

Upload coverage reports to services like Codecov:

```bash
# Generate XML coverage report
pytest --cov=grainchain --cov-report=xml

# Upload to Codecov
codecov -f coverage.xml
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Grainchain Documentation](../README.md)

## 🤝 Contributing

When contributing tests:

1. **Maintain Coverage**: Ensure new code is covered by tests
2. **Follow Conventions**: Use established naming and structure patterns
3. **Add Documentation**: Document complex test scenarios
4. **Test Edge Cases**: Include error conditions and boundary cases
5. **Keep Tests Fast**: Prefer unit tests over integration tests when possible

---

**Happy Testing! 🧪✨**

