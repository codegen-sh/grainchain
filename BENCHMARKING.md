# Grainchain Benchmarking Guide

This document provides comprehensive instructions for running and understanding Grainchain sandbox provider benchmarks.

## 🚀 Quick Start

### 5-Minute Benchmark Walkthrough

Get your first benchmark results in under 5 minutes:

```bash
# 1. Verify installation
grainchain --version

# 2. Run your first benchmark (local provider, no API keys needed)
grainchain benchmark --provider local
```

**Expected output:**
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

🎉 **Congratulations!** You've successfully run your first Grainchain benchmark.

### Understanding Your Results

- **Basic echo test**: Tests simple command execution speed
- **Python test**: Tests Python code execution performance
- **File operations test**: Tests file upload/download speed
- **Total time**: Overall benchmark execution time

### Next Steps

1. **Try other providers** (requires API keys):
   ```bash
   grainchain benchmark --provider e2b
   grainchain benchmark --provider daytona
   grainchain benchmark --provider morph
   ```

2. **Save results for comparison**:
   ```bash
   grainchain benchmark --provider local --output ./results/
   ```

3. **Run comprehensive benchmarks**: See [Full Benchmark Suite](#full-benchmark-suite) below

## 📊 Understanding Results

### Result Files

Benchmark results are saved in `benchmarks/results/` in multiple formats:

- **`latest_grainchain.json`** - Latest results in JSON format
- **`latest_grainchain.md`** - Latest results in Markdown format
- **`grainchain_benchmark_YYYYMMDD_HHMMSS.json`** - Timestamped JSON results
- **`grainchain_benchmark_YYYYMMDD_HHMMSS.md`** - Timestamped Markdown reports

### Key Metrics

#### Provider Comparison Table

```
| Provider | Success Rate | Avg Time (s) | Creation Time (s) | Status |
|----------|--------------|--------------|-------------------|--------|
| local    | 75.0%        | 0.03         | 0.00              | ⚠️     |
| e2b      | 100.0%       | 1.28         | 0.26              | ✅     |
```

#### Performance Indicators

- **Success Rate**: Percentage of operations that completed successfully
- **Avg Time**: Average time per test scenario
- **Creation Time**: Time to create a new sandbox instance
- **Status**: ✅ (>80% success), ⚠️ (50-80% success), ❌ (<50% success)

### Test Scenarios

The benchmark suite includes 4 test scenarios:

1. **Basic Commands** - Simple shell commands (echo, pwd, ls, whoami, date)
2. **Python Execution** - Python version check and script execution
3. **File Operations** - Upload, download, and verify file content
4. **Computational Tasks** - CPU-intensive Python operations

## 🔧 Configuration

### Default Configuration

The benchmark uses `benchmarks/configs/grainchain.json`:

```json
{
  "providers": ["local", "e2b"],
  "iterations": 3,
  "timeout": 30,
  "parallel_tests": false,
  "detailed_metrics": true,
  "export_formats": ["json", "markdown", "html"]
}
```

### Custom Configuration

Create your own config file and use it:

```bash
python benchmarks/scripts/grainchain_benchmark.py --config my_config.json
```

### Environment Variables

Set up your provider credentials:

```bash
# E2B Provider
E2B_API_KEY=your_e2b_api_key_here
E2B_TEMPLATE=base

# Modal Provider
MODAL_TOKEN_ID=your_modal_token_id_here
MODAL_TOKEN_SECRET=your_modal_token_secret_here

# Daytona Provider
DAYTONA_API_KEY=your_daytona_api_key_here
```

## 📈 Interpreting Results

### Example Results Analysis

Based on recent benchmark results:

#### E2B Provider

- ✅ **Reliability**: 100% success rate across all scenarios
- ⏱️ **Performance**: ~1.3s average execution time
- 🚀 **Startup**: ~0.26s sandbox creation time
- 💡 **Best for**: Production workloads requiring high reliability

#### Local Provider

- ⚠️ **Reliability**: 75% success rate (file operations failing)
- ⚡ **Performance**: ~0.03s average execution time (43x faster)
- 🚀 **Startup**: ~0.00s sandbox creation time (instant)
- 💡 **Best for**: Development and testing with fast iteration

### Common Issues

#### Local Provider File Operations Failing

- **Cause**: Local provider may have limitations with file upload/download
- **Impact**: Reduces overall success rate to 75%
- **Recommendation**: Use E2B for file-heavy operations

#### E2B Provider Slower Performance

- **Cause**: Network latency and remote sandbox creation
- **Impact**: ~40x slower than local provider
- **Recommendation**: Acceptable trade-off for reliability in production

## 🛠️ Troubleshooting

### Common Problems

#### "Module not found" errors

```bash
# Install missing dependencies
pip install psutil
pip install -e .
```

#### E2B authentication errors

```bash
# Check your API key
echo $E2B_API_KEY

# Verify .env file
cat .env | grep E2B_API_KEY
```

#### Permission errors on scripts

```bash
# Make scripts executable
chmod +x benchmarks/scripts/run_grainchain_benchmark.sh
```

### Debug Mode

Run with verbose logging:

```bash
python benchmarks/scripts/grainchain_benchmark.py \
    --providers local e2b \
    --iterations 1 2>&1 | tee debug.log
```

## 🔄 Continuous Integration

### GitHub Actions (Future)

The benchmarking system is designed to integrate with CI/CD:

```yaml
# .github/workflows/grainchain-benchmark.yml
name: Grainchain Benchmarks
on:
  schedule:
    - cron: "0 2 * * *" # Daily at 2 AM
  workflow_dispatch:

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Grainchain Benchmarks
        run: make grainchain-benchmark
        env:
          E2B_API_KEY: ${{ secrets.E2B_API_KEY }}
```

### Local Automation

Set up cron job for regular benchmarking:

```bash
# Add to crontab for daily execution
0 2 * * * cd /path/to/grainchain && make grainchain-benchmark
```

## 📚 For Future Agents

### Adding New Providers

1. **Implement the provider** in `grainchain/providers/`
2. **Add to configuration** in `benchmarks/configs/grainchain.json`
3. **Update documentation** in this file
4. **Test thoroughly** with `make grainchain-benchmark`

### Adding New Test Scenarios

1. **Edit the benchmark script** `benchmarks/scripts/grainchain_benchmark.py`
2. **Add to `test_scenarios`** list in the `__init__` method
3. **Update configuration** if needed
4. **Document the new scenario** in this file

### Modifying Metrics

1. **Update `_run_scenario`** method for new metrics collection
2. **Modify `_aggregate_scenario_results`** for new aggregations
3. **Update report generation** in `_generate_markdown_report`
4. **Test with sample runs** to verify output

## 🎯 Best Practices

### For Development

- Use `make grainchain-local` for fast iteration
- Run `make grainchain-compare` before major releases
- Check file operations work across all providers

### For Production

- Prefer E2B for reliability-critical workloads
- Monitor success rates over time
- Set up automated benchmarking for regression detection

### For Debugging

- Use single iterations first: `./run_grainchain_benchmark.sh "local" 1`
- Check individual scenario results in JSON output
- Enable verbose logging for detailed error information

---

**Last Updated**: 2025-05-31
**Benchmark Version**: 1.0
**Supported Providers**: Local, E2B
**Future Providers**: Modal, Docker (coming soon - not currently supported)
