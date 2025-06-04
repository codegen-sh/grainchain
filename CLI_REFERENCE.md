# Grainchain CLI Reference

This document provides a comprehensive reference for all Grainchain CLI commands.

## Installation and Setup

```bash
# Install grainchain
pip install grainchain
# or
uv add grainchain

# Verify installation
grainchain --version
```

## Command Overview

```bash
grainchain --help
```

**Available Commands:**
- `benchmark` - Run performance benchmarks
- `check` - Run all quality checks (lint, format, test)
- `format` - Format code using ruff
- `install-hooks` - Install pre-commit hooks
- `lint` - Run linting checks with ruff
- `test` - Run tests using pytest
- `typecheck` - Run type checking with mypy

## Benchmark Commands

### Basic Benchmarking

```bash
# Test local provider (fastest, no API keys needed)
grainchain benchmark --provider local

# Test specific providers (requires API keys)
grainchain benchmark --provider e2b
grainchain benchmark --provider daytona
grainchain benchmark --provider morph
```

### Advanced Benchmarking

```bash
# Save results to specific directory
grainchain benchmark --provider local --output ./my_results/

# Use custom benchmark configuration
grainchain benchmark --provider local --config ./my_benchmark_config.yaml

# Get help for benchmark command
grainchain benchmark --help
```

### Expected Output

```
🚀 Running benchmarks with local provider...
🏃 Starting benchmark with local provider...
✅ Basic echo test: 0.002s
✅ Python test: 0.018s
✅ File operations test: 0.004s

📈 Benchmark Summary:
   Provider: local
   Total time: 0.024s
   Tests passed: 3
✅ Benchmarks completed successfully!
```

## Development Commands

### Code Quality

```bash
# Run all quality checks
grainchain check

# Format code
grainchain format

# Run linting
grainchain lint

# Run linting with auto-fix
grainchain lint --fix

# Type checking (currently disabled)
grainchain typecheck
```

### Testing

```bash
# Run all tests
grainchain test

# Run tests with coverage
grainchain test --cov

# Run specific test file
grainchain test tests/test_specific.py

# Run tests with verbose output
grainchain test -v
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
grainchain install-hooks

# This will automatically run quality checks before each commit
```

## Environment Variables

Set these environment variables for provider access:

```bash
# E2B Provider
export E2B_API_KEY="your-e2b-api-key"

# Morph Provider
export MORPH_API_KEY="your-morph-api-key"

# Daytona Provider
export DAYTONA_API_KEY="your-daytona-api-key"
```

Or create a `.env` file:

```bash
# .env file
E2B_API_KEY=your-e2b-api-key
MORPH_API_KEY=your-morph-api-key
DAYTONA_API_KEY=your-daytona-api-key
```

## Common Usage Patterns

### Quick Development Workflow

```bash
# 1. Test your setup
grainchain benchmark --provider local

# 2. Run quality checks
grainchain check

# 3. Format code if needed
grainchain format

# 4. Run tests
grainchain test
```

### Performance Testing Workflow

```bash
# 1. Test local provider first
grainchain benchmark --provider local

# 2. Test remote providers (with API keys)
grainchain benchmark --provider e2b
grainchain benchmark --provider daytona
grainchain benchmark --provider morph

# 3. Save results for comparison
grainchain benchmark --provider local --output ./results/local/
grainchain benchmark --provider e2b --output ./results/e2b/
```

### CI/CD Integration

```bash
# In your CI pipeline
grainchain check          # Run all quality checks
grainchain test --cov     # Run tests with coverage
grainchain benchmark --provider local  # Basic performance test
```

## Troubleshooting CLI Issues

### Command Not Found

```bash
# If 'grainchain' command is not found
pip install grainchain
# or
uv add grainchain

# Verify installation
which grainchain
grainchain --version
```

### Permission Issues

```bash
# If you get permission errors
pip install --user grainchain
# or use virtual environment
python -m venv venv
source venv/bin/activate
pip install grainchain
```

### API Key Issues

```bash
# Verify environment variables are set
echo $E2B_API_KEY
echo $MORPH_API_KEY
echo $DAYTONA_API_KEY

# Test with local provider first (no API key needed)
grainchain benchmark --provider local
```

## Advanced Configuration

### Custom Benchmark Configuration

Create a `benchmark_config.yaml` file:

```yaml
# benchmark_config.yaml
timeout: 300
iterations: 5
providers:
  - local
  - e2b
tests:
  - basic_echo
  - python_execution
  - file_operations
  - snapshot_lifecycle
```

Use it:

```bash
grainchain benchmark --config benchmark_config.yaml
```

### Output Formats

```bash
# Default output (human-readable)
grainchain benchmark --provider local

# Save to specific directory with timestamp
grainchain benchmark --provider local --output ./results/$(date +%Y%m%d_%H%M%S)/
```

## Getting Help

```bash
# General help
grainchain --help

# Command-specific help
grainchain benchmark --help
grainchain test --help
grainchain lint --help

# Version information
grainchain --version
```

For more help:
- Check the [examples/](examples/) directory for working code
- Visit our [GitHub repository](https://github.com/codegen-sh/grainchain)
- Join our [Discord community](https://discord.gg/codegen)
