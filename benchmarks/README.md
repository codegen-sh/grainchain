# Outline Benchmarking Infrastructure

This directory contains a comprehensive benchmarking infrastructure for the [Outline](https://github.com/outline/outline) application. The system automatically boots up VMs using the codex-universal base image, installs Outline, and measures performance impacts of trivial changes.

## 🏗️ Architecture

The benchmarking system consists of several components:

- **`benchmark_runner.py`**: Core benchmarking engine that orchestrates the entire process
- **`auto_publish.py`**: Automation script for periodic execution and result publishing
- **Configuration files**: JSON-based configuration for customizing benchmark parameters
- **GitHub Actions**: Automated CI/CD pipeline for scheduled benchmarks
- **Results storage**: Structured storage of benchmark data in multiple formats

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker
- Git

### Installation

```bash
# Install dependencies
make install

# Or manually:
pip install -r requirements.txt
```

### Running Benchmarks

```bash
# Run a single benchmark with default settings
make benchmark

# Run with custom configuration
make benchmark-config

# Run and automatically publish results
make publish

# Generate summary report
make summary
```

## 📊 What Gets Measured

The benchmarking system captures comprehensive metrics:

### Performance Metrics
- **Build Time**: Time to execute `yarn build`
- **Test Time**: Time to run the test suite
- **Memory Usage**: Container memory consumption during operations
- **CPU Usage**: Container CPU utilization

### File System Metrics
- **Project Size**: Total size of the Outline directory
- **Node Modules Size**: Size of installed dependencies
- **Package Count**: Number of installed npm packages

### Change Impact Analysis
- **Before/After Comparisons**: Performance impact of trivial changes
- **Percentage Changes**: Relative performance differences
- **Trend Analysis**: Historical performance tracking

## 🔧 Configuration

### Default Configuration

The system uses `benchmarks/configs/default.json` for default settings:

```json
{
  "base_image": "ghcr.io/openai/codex-universal:latest",
  "outline_repo": "https://github.com/outline/outline.git",
  "outline_branch": "main",
  "node_version": "20",
  "benchmark_iterations": 3,
  "trivial_changes": [
    {
      "type": "comment",
      "file": "README.md",
      "content": "# Benchmark test comment"
    },
    {
      "type": "whitespace",
      "file": "package.json",
      "content": "\\n"
    },
    {
      "type": "log",
      "file": "app/index.js",
      "content": "console.log('benchmark test');"
    }
  ]
}
```

### Custom Configuration

Create your own configuration file and use it:

```bash
python benchmarks/scripts/benchmark_runner.py --config my_config.json
```

## 📈 Results and Reports

### Output Formats

The system generates results in multiple formats:

1. **JSON**: Machine-readable data (`benchmark_YYYYMMDD_HHMMSS.json`)
2. **HTML**: Interactive web report (`benchmark_YYYYMMDD_HHMMSS.html`)
3. **Markdown**: GitHub-compatible report (`benchmark_YYYYMMDD_HHMMSS.md`)

### Latest Results

The most recent results are always available as:
- `benchmarks/results/latest.json`
- `benchmarks/results/latest.html`
- `benchmarks/results/latest.md`

### Summary Report

A comprehensive summary of all historical benchmarks is maintained in:
- `benchmarks/results/SUMMARY.md`

## 🤖 Automation

### GitHub Actions

The system includes a GitHub Actions workflow (`.github/workflows/benchmark.yml`) that:

- Runs benchmarks daily at 2 AM UTC
- Can be triggered manually
- Automatically commits results to the repository
- Uploads artifacts for download

### Scheduled Execution

To set up local scheduled execution:

```bash
# Add to crontab for daily execution at 2 AM
0 2 * * * cd /path/to/grainchain && make publish
```

## 🐳 Docker Integration

The system uses the [codex-universal](https://github.com/openai/codex-universal) base image, which provides:

- Pre-configured development environment
- Multiple language runtime support
- Consistent execution environment
- Isolated benchmark execution

### Container Lifecycle

1. **Pull**: Downloads the latest codex-universal image
2. **Start**: Launches container with configured environment variables
3. **Clone**: Downloads Outline repository
4. **Install**: Runs `yarn install` to set up dependencies
5. **Benchmark**: Executes performance measurements
6. **Cleanup**: Stops and removes container

## 📋 Benchmark Process

### Step-by-Step Execution

1. **Environment Setup**
   - Pull codex-universal Docker image
   - Start container with Node.js 20 and Python 3.12
   - Configure workspace directory

2. **Application Installation**
   - Clone Outline repository
   - Install dependencies with `yarn install --frozen-lockfile`
   - Verify successful installation

3. **Baseline Measurement**
   - Take initial performance snapshot
   - Measure build time, memory usage, file sizes
   - Record container resource utilization

4. **Change Impact Testing**
   - Apply trivial changes (comments, whitespace, logs)
   - Take performance snapshots after each change
   - Compare against baseline measurements
   - Revert changes between iterations

5. **Results Generation**
   - Calculate performance differences
   - Generate HTML, JSON, and Markdown reports
   - Update summary statistics

## 🔍 Troubleshooting

### Common Issues

**Docker Permission Errors**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Restart shell or logout/login
```

**Container Startup Failures**
```bash
# Check Docker daemon status
sudo systemctl status docker

# Test Docker connectivity
make test-docker
```

**Build Failures**
- Check Node.js version compatibility
- Verify network connectivity for package downloads
- Review container logs for specific error messages

### Debug Mode

Run with verbose logging:

```bash
python benchmarks/scripts/benchmark_runner.py --config benchmarks/configs/default.json 2>&1 | tee debug.log
```

## 🤝 Contributing

### Adding New Metrics

To add new performance metrics:

1. Extend the `take_snapshot()` method in `BenchmarkRunner`
2. Update the comparison logic in `_compare_snapshots()`
3. Modify report generation to include new metrics
4. Update configuration schema if needed

### Custom Change Types

To add new types of trivial changes:

1. Extend the `apply_trivial_change()` method
2. Add new change type to configuration
3. Update documentation

### Report Customization

The HTML and Markdown report templates can be customized by modifying:
- `generate_report()` for HTML output
- `generate_markdown_report()` for Markdown output

## 📚 References

- [Outline Repository](https://github.com/outline/outline)
- [Codex Universal Image](https://github.com/openai/codex-universal)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## 📄 License

This benchmarking infrastructure is part of the grainchain project and follows the same licensing terms.

