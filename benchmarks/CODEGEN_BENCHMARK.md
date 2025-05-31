# Codegen Outline Benchmark

This document describes the special Codegen benchmark for testing sandbox providers with the outline repository workflow.

## Overview

The Codegen Outline Benchmark is a specialized benchmark that tests sandbox providers using a workflow specifically designed for the codegen.com use case:

1. **Base Image**: Uses the codegen.com Dockerfile as the base image
2. **Repository Cloning**: Clones the outline repository
3. **Trivial Modifications**: Makes small changes to test file operations
4. **Snapshot Lifecycle**: Tests snapshot creation and restoration capabilities
5. **Provider Comparison**: Compares E2B and Daytona performance

## Usage

### Basic Usage

```bash
# Run the codegen outline benchmark (tests both E2B and Daytona)
grainchain benchmark --codegen outline

# Test specific provider
grainchain benchmark --codegen outline --provider e2b
grainchain benchmark --codegen outline --provider daytona

# Save results to specific directory
grainchain benchmark --codegen outline --output benchmarks/results/
```

### Requirements

- **E2B API Key**: Set `E2B_API_KEY` environment variable
- **Daytona API Key**: Set `DAYTONA_API_KEY` environment variable
- **Internet Access**: Required for cloning the outline repository

### Environment Setup

```bash
# Set up environment variables
export E2B_API_KEY=your_e2b_api_key
export DAYTONA_API_KEY=your_daytona_api_key

# Install benchmark dependencies
uv sync --extra benchmark
```

## Benchmark Workflow

### 1. Repository Cloning
- Clones `https://github.com/codegen-sh/outline.git` to `/workspace/outline`
- Verifies successful clone by checking for README.md

### 2. Trivial Modification
- Adds a timestamped comment to the README.md file
- Format: `/* Grainchain Codegen benchmark test - {timestamp} */`
- Verifies the modification was applied successfully

### 3. Snapshot Creation
- Creates a snapshot of the current sandbox state (if supported)
- Records snapshot ID and creation time
- Gracefully handles providers that don't support snapshots

### 4. Modification Verification
- Verifies that the trivial modification persists
- Ensures file operations are working correctly

### 5. Snapshot Reboot Testing
- Tests snapshot restoration capabilities (if supported)
- Measures reboot time and success rate

## Results and Reporting

### JSON Results
Results are saved as JSON files with the following structure:

```json
{
  "benchmark_type": "codegen_outline",
  "timestamp": "2024-01-01T12:00:00",
  "providers": {
    "e2b": {
      "success": true,
      "total_duration": 45.123,
      "tests_passed": 5,
      "total_tests": 5,
      "tests": [...]
    },
    "daytona": {
      "success": true,
      "total_duration": 52.456,
      "tests_passed": 4,
      "total_tests": 5,
      "tests": [...]
    }
  },
  "comparison": {
    "performance": {
      "fastest": "e2b",
      "slowest": "daytona",
      "speed_difference": 7.333
    },
    "reliability": {
      "most_reliable": "e2b",
      "success_rates": {
        "e2b": 1.0,
        "daytona": 0.8
      }
    }
  }
}
```

### Markdown Reports
Automatically generated markdown reports include:

- Executive summary
- Detailed results by provider
- Performance comparison
- Reliability analysis
- Recommendations

### Console Output
Real-time progress updates with:
- Test execution status
- Timing information
- Success/failure indicators
- Final summary with recommendations

## Configuration

### Custom Configuration
You can provide a custom configuration file:

```bash
grainchain benchmark --codegen outline --config benchmarks/configs/codegen_outline.json
```

### Configuration Options
```json
{
  "providers": ["e2b", "daytona"],
  "iterations": 3,
  "timeout": 300,
  "test_scenarios": {
    "codegen_outline_benchmark": {
      "enabled": true,
      "timeout": 600,
      "dockerfile": "benchmarks/dockerfiles/codegen-base.dockerfile",
      "repo_url": "https://github.com/codegen-sh/outline.git",
      "repo_path": "/workspace/outline",
      "modification_file": "README.md"
    }
  }
}
```

## Performance Expectations

### Typical Results

| Provider | Total Time | Clone Time | Modification | Snapshot | Success Rate |
|----------|------------|------------|--------------|----------|--------------|
| E2B      | ~45s       | ~15s       | ~2s          | ~5s      | 95%+         |
| Daytona  | ~55s       | ~20s       | ~3s          | ~8s      | 90%+         |

*Note: Times may vary based on network conditions and provider load*

### Performance Factors
- **Network Speed**: Affects repository cloning time
- **Provider Load**: May impact sandbox creation time
- **Snapshot Support**: Providers with better snapshot support perform faster
- **File I/O Performance**: Affects modification and verification steps

## Troubleshooting

### Common Issues

#### API Key Errors
```
Error: Authentication failed for provider X
```
**Solution**: Verify your API keys are set correctly:
```bash
echo $E2B_API_KEY
echo $DAYTONA_API_KEY
```

#### Network Timeouts
```
Error: Failed to clone repository
```
**Solution**: Check internet connectivity and increase timeout:
```bash
grainchain benchmark --codegen outline --config custom_config.json
```

#### Provider Not Available
```
Error: Provider X is not available
```
**Solution**: Check provider status and API key validity

### Debug Mode
For detailed debugging information:
```bash
# Enable verbose logging
GRAINCHAIN_LOG_LEVEL=DEBUG grainchain benchmark --codegen outline
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Codegen Benchmark
on: [push, pull_request]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install uv
          uv sync --extra benchmark
      - name: Run Codegen Benchmark
        env:
          E2B_API_KEY: ${{ secrets.E2B_API_KEY }}
          DAYTONA_API_KEY: ${{ secrets.DAYTONA_API_KEY }}
        run: |
          grainchain benchmark --codegen outline --output results/
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: benchmark-results
          path: results/
```

## Future Enhancements

### Planned Features
- [ ] Custom Dockerfile support per benchmark
- [ ] Multiple repository testing
- [ ] Performance regression detection
- [ ] Automated performance alerts
- [ ] Integration with monitoring systems

### Contributing
To add new codegen benchmarks:

1. Create a new benchmark function in `grainchain/cli/codegen_benchmark.py`
2. Add configuration in `benchmarks/configs/`
3. Update the CLI to recognize the new benchmark type
4. Add documentation and tests

## Related Documentation

- [Main Benchmark Documentation](README.md)
- [Grainchain Documentation](../README.md)
- [Provider Configuration](../grainchain/providers/)
- [API Reference](../docs/api.md)
