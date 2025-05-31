# Grainchain Benchmarks

This directory contains benchmarking infrastructure for testing and comparing different sandbox providers in the Grainchain project, with support for multiple repositories and programming languages.

## Overview

The benchmark suite evaluates sandbox providers across multiple scenarios and repositories:
- **Multi-Repository Support**: Test TypeScript, Python, and other language repositories
- **Basic Commands**: Simple shell commands and system information
- **Python Execution**: Python script execution and package management
- **File Operations**: File creation, reading, writing, and manipulation
- **Computational Tasks**: CPU-intensive operations and mathematical computations
- **Per-Repository Output**: Generate separate results for each tested repository

## Supported Repositories

### TypeScript Repositories
- **outline**: Knowledge base application (default)

### Python Repositories
- **requests**: Popular HTTP library
- **fastapi**: Modern web framework

## Multi-Repository Benchmarking

### Quick Start

Run benchmarks for all configured repositories:
```bash
# Using grainchain (recommended)
source .venv/bin/activate
python benchmarks/scripts/grainchain_multi_repo_benchmark.py

# Using Docker (requires docker installation)
python benchmarks/scripts/multi_repo_benchmark_runner.py
```

Run benchmark for a specific repository:
```bash
# Using grainchain
source .venv/bin/activate
python benchmarks/scripts/grainchain_multi_repo_benchmark.py --repo requests

# Using Docker
python benchmarks/scripts/multi_repo_benchmark_runner.py --repo requests
```

Test multi-repo setup with E2B:
```bash
source .venv/bin/activate
python test_multi_repo_dockerfile.py
```

Test specific repository setup:
```bash
source .venv/bin/activate
python test_multi_repo_dockerfile.py --repo fastapi
```

### Configuration

Repository configurations are stored in `benchmarks/configs/`:
- `outline.json` - TypeScript/Node.js repository
- `requests.json` - Python HTTP library
- `fastapi.json` - Python web framework

Each configuration includes:
- Repository URL and branch
- Language and package manager
- Install and test commands
- Trivial changes for snapshot testing
- Metrics collection settings

### Results

Results are generated per repository in `benchmarks/results/`:
- `multi_benchmark_results_TIMESTAMP.json` - Overall results
- `{repo_name}_benchmark_TIMESTAMP.json` - Per-repository results

## Supported Providers

### ✅ Working Providers

#### Local Provider
- **Status**: ✅ Fully functional
- **Setup**: No additional configuration required
- **Performance**: Fastest execution (~0.04s avg)
- **Use case**: Development and testing

#### E2B Provider
- **Status**: ✅ Fully functional
- **Setup**: Requires `E2B_API_KEY` environment variable
- **Performance**: Good performance (~1.17s avg)
- **Use case**: Production sandboxing

### ⚠️ Modal Provider
- **Status**: ⚠️ Limited support (Python 3.13 compatibility issues)
- **Setup**: Requires `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET` environment variables
- **Known Issues**:
  - Modal currently supports Python 3.9-3.12 only
  - Image building may fail in Python 3.13 environments
  - Requires compatible Python version for proper functionality
- **Workaround**: Use in environments with Python 3.12 or earlier

## Environment Setup

### Required Environment Variables

Create a `.env` file or set these environment variables:

```bash
# E2B Provider
E2B_API_KEY=your_e2b_api_key_here

# Modal Provider (optional, has compatibility limitations)
MODAL_TOKEN_ID=your_modal_token_id_here
MODAL_TOKEN_SECRET=your_modal_token_secret_here
```

### Installation

```bash
# Install dependencies
pip install -e ".[e2b,modal]"

# Or install specific providers
pip install -e ".[e2b]"  # For E2B only
pip install -e ".[modal]"  # For Modal only (requires Python ≤3.12)
```

## Running Benchmarks

### Basic Usage

```bash
# Run benchmarks for all available providers
python benchmarks/scripts/grainchain_benchmark.py

# Run benchmarks for specific providers
python benchmarks/scripts/grainchain_benchmark.py --providers local e2b

# Run with custom iterations
python benchmarks/scripts/grainchain_benchmark.py --providers local --iterations 5

# Run with custom output directory
python benchmarks/scripts/grainchain_benchmark.py --output-dir custom_results
```

### Command Line Options

- `--providers`: Specify which providers to benchmark (default: all available)
- `--iterations`: Number of iterations per scenario (default: 3)
- `--output-dir`: Output directory for results (default: benchmarks/results)
- `--verbose`: Enable verbose logging

### Example Commands

```bash
# Quick test with local provider
python benchmarks/scripts/grainchain_benchmark.py --providers local --iterations 1

# Comprehensive benchmark with working providers
python benchmarks/scripts/grainchain_benchmark.py --providers local e2b --iterations 5

# Test Modal provider (if compatible Python version)
python benchmarks/scripts/grainchain_benchmark.py --providers modal --iterations 1
```

## Results

Benchmark results are saved as JSON files in the `benchmarks/results/` directory with timestamps.

### Sample Results

```
🎉 Grainchain benchmark completed successfully!
📊 Results saved to: benchmarks/results

📈 Quick Summary:
  local: 75.0% success, 0.04s avg
  e2b: 100.0% success, 1.17s avg
```

### Performance Comparison

| Provider | Success Rate | Avg Time | Use Case |
|----------|-------------|----------|----------|
| Local    | 75-100%     | ~0.04s   | Development |
| E2B      | 100%        | ~1.17s   | Production |
| Modal    | N/A*        | N/A*     | Limited** |

*Results may vary based on environment compatibility
**Requires Python ≤3.12

## Troubleshooting

### Modal Provider Issues

If you encounter Modal provider errors:

1. **Python Version Check**: Ensure you're using Python 3.12 or earlier
   ```bash
   python --version  # Should show 3.12.x or earlier
   ```

2. **Environment Variables**: Verify Modal credentials are set
   ```bash
   echo $MODAL_TOKEN_ID
   echo $MODAL_TOKEN_SECRET
   ```

3. **Alternative**: Use other providers (local, E2B) for testing

### E2B Provider Issues

1. **API Key**: Ensure `E2B_API_KEY` is set correctly
2. **Network**: Check internet connectivity for API access
3. **Quota**: Verify your E2B account has available quota

### General Issues

1. **Dependencies**: Ensure all optional dependencies are installed
2. **Permissions**: Check file system permissions for result output
3. **Logs**: Use `--verbose` flag for detailed error information

## Contributing

When adding new providers or scenarios:

1. Follow the existing provider interface in `grainchain/providers/`
2. Add corresponding test scenarios in the benchmark script
3. Update this README with setup instructions and known limitations
4. Test with multiple iterations to ensure reliability

## Provider Implementation Status

- ✅ **Local**: Complete implementation
- ✅ **E2B**: Complete implementation with file operations
- ⚠️ **Modal**: Basic implementation with compatibility limitations
- 🔄 **Future**: Additional providers can be added following the base interface
