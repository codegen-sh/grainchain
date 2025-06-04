# Grainchain Benchmarks

This directory contains benchmarking infrastructure for testing and comparing different sandbox providers in the Grainchain project.

## 📊 New: Benchmark Analysis & Comparison

Grainchain now includes powerful analysis tools to compare providers, analyze trends, and generate comprehensive reports.

### Quick Analysis Commands

```bash
# Compare two providers
grainchain analysis compare --provider1 local --provider2 e2b --chart

# Analyze performance trends
grainchain analysis trends --provider local --days 30 --interactive

# Generate comprehensive report
grainchain analysis report --format html --include-charts

# Detect performance regressions
grainchain analysis regressions --threshold 0.1

# Get provider recommendations
grainchain analysis recommend --use-case reliability

# Create performance dashboard
grainchain analysis dashboard --interactive
```

### Analysis Features

- **Provider Comparison**: Compare performance between different providers
- **Trend Analysis**: Analyze performance trends over time with statistical insights
- **Regression Detection**: Automatically detect performance regressions
- **Visualization**: Generate charts, graphs, and interactive dashboards
- **Comprehensive Reports**: Create detailed reports in HTML, Markdown, or PDF
- **Provider Recommendations**: Get data-driven provider recommendations
- **Configuration Management**: Customize analysis settings and preferences

For detailed analysis documentation, see [Analysis Guide](../docs/analysis_guide.md).

## Overview

The benchmark suite evaluates sandbox providers across multiple scenarios:
- **Basic Commands**: Simple shell commands and system information
- **Python Execution**: Python script execution and package management
- **File Operations**: File creation, reading, writing, and manipulation
- **Computational Tasks**: CPU-intensive operations and mathematical computations

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
