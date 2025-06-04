# Grainchain Benchmark Analysis Guide

This guide covers the comprehensive benchmark analysis and comparison features available in Grainchain.

## Overview

The Grainchain benchmark analysis system provides powerful tools to:

- **Compare providers** across different metrics and time periods
- **Analyze trends** in performance over time
- **Detect regressions** automatically
- **Generate visualizations** and interactive dashboards
- **Create comprehensive reports** in multiple formats
- **Get provider recommendations** based on your use case

## Quick Start

### Basic Provider Comparison

Compare two providers to see which performs better:

```bash
grainchain analysis compare --provider1 local --provider2 e2b --days 30 --chart
```

This will:
- Compare the last 30 days of data between local and e2b providers
- Show improvements and regressions
- Generate a comparison chart

### Trend Analysis

Analyze performance trends over time:

```bash
grainchain analysis trends --provider local --days 30 --metric success_rate --interactive
```

This will:
- Analyze success rate trends for the local provider
- Show trend direction and strength
- Generate an interactive chart

### Generate Reports

Create comprehensive analysis reports:

```bash
grainchain analysis report --format html --days 30 --include-charts
```

This will:
- Generate an HTML report covering the last 30 days
- Include performance charts and detailed analysis
- Provide provider recommendations

## CLI Commands Reference

### `grainchain analysis compare`

Compare performance between two providers.

**Options:**
- `--provider1` (required): First provider to compare
- `--provider2` (required): Second provider to compare
- `--days`: Number of days to look back (default: 30)
- `--output`: Output file path for detailed report
- `--chart`: Generate comparison chart
- `--chart-type`: Chart type (bar, radar)

**Examples:**
```bash
# Basic comparison
grainchain analysis compare --provider1 local --provider2 e2b

# With chart generation
grainchain analysis compare --provider1 local --provider2 e2b --chart --chart-type radar

# Save detailed report
grainchain analysis compare --provider1 local --provider2 e2b --output comparison_report.html
```

### `grainchain analysis trends`

Analyze performance trends over time.

**Options:**
- `--provider`: Provider to analyze (optional, analyzes all if not specified)
- `--days`: Number of days to analyze (default: 30)
- `--metric`: Metric to analyze (success_rate, avg_execution_time, avg_creation_time)
- `--output`: Output file path for chart
- `--interactive`: Generate interactive HTML chart

**Examples:**
```bash
# Analyze success rate trends for local provider
grainchain analysis trends --provider local --metric success_rate

# Analyze execution time trends across all providers
grainchain analysis trends --metric avg_execution_time --days 60

# Generate interactive dashboard
grainchain analysis trends --interactive --output dashboard.html
```

### `grainchain analysis report`

Generate comprehensive benchmark analysis reports.

**Options:**
- `--format`: Report format (html, markdown, pdf)
- `--output`: Output file path
- `--days`: Number of days to include (default: 30)
- `--include-charts`: Include charts in report

**Examples:**
```bash
# Generate HTML report
grainchain analysis report --format html --include-charts

# Generate markdown report for last 60 days
grainchain analysis report --format markdown --days 60 --output report.md

# Generate PDF report (requires weasyprint)
grainchain analysis report --format pdf --output report.pdf
```

### `grainchain analysis regressions`

Detect performance regressions automatically.

**Options:**
- `--baseline-days`: Days for baseline period (default: 7)
- `--comparison-days`: Days for comparison period (default: 7)
- `--threshold`: Regression threshold as decimal (default: 0.1 = 10%)

**Examples:**
```bash
# Detect regressions with default settings
grainchain analysis regressions

# Use custom threshold and periods
grainchain analysis regressions --baseline-days 14 --comparison-days 7 --threshold 0.05
```

### `grainchain analysis recommend`

Get provider recommendations based on performance data.

**Options:**
- `--use-case`: Use case for recommendation (general, speed, reliability)
- `--days`: Number of days to analyze (default: 30)

**Examples:**
```bash
# General recommendation
grainchain analysis recommend

# Recommendation for speed-critical use case
grainchain analysis recommend --use-case speed

# Recommendation for reliability-critical use case
grainchain analysis recommend --use-case reliability
```

### `grainchain analysis dashboard`

Generate comprehensive performance dashboards.

**Options:**
- `--output-dir`: Output directory for charts (default: benchmarks/charts)
- `--days`: Number of days to include (default: 30)
- `--interactive`: Generate interactive charts

**Examples:**
```bash
# Generate static dashboard
grainchain analysis dashboard

# Generate interactive dashboard
grainchain analysis dashboard --interactive --output-dir ./charts
```

## Understanding the Output

### Comparison Results

When comparing providers, you'll see:

```
COMPARISON RESULTS
==========================================
Comparison between local vs e2b:

e2b improvements:
  • Success rate: +44.4%
  • Avg Creation Time: -2.31s faster

local improvements:
  • Avg Execution Time: -2.28s faster
```

This shows:
- **e2b** has better success rate and faster creation time
- **local** has faster execution time
- The magnitude of each difference

### Trend Analysis

Trend analysis shows:

```
TREND ANALYSIS RESULTS
==========================================
Metric: success_rate
Provider: local
Time Period: 30 days
Trend Direction: improving
Trend Strength: 0.85

Statistical Summary:
  • Mean: 77.50
  • Median: 80.00
  • Std Dev: 12.50
  • Min: 55.00
  • Max: 95.00
  • Data Points: 15
```

- **Trend Direction**: improving, declining, stable, or insufficient_data
- **Trend Strength**: 0-1 scale, higher means stronger trend
- **Statistical Summary**: Key statistics about the metric

### Provider Recommendations

Recommendations include:

```
PROVIDER RECOMMENDATION
==========================================
Recommended Provider: e2b
Confidence Score: 85.2%

Reasons:
  • Based on 25 recent benchmark runs
  • Excellent reliability with 94.5% success rate
  • Fast execution time (2.1s average)
  • Significantly outperforms other providers

Performance Summary:
  • Success Rate: 94.5%
  • Avg Execution Time: 2.10s
  • Avg Creation Time: 2.40s
  • Data Points: 25
```

## Configuration

### Analysis Configuration

The analysis system can be configured via `benchmarks/configs/analysis.json`:

```json
{
  "default_settings": {
    "time_range_days": 30,
    "comparison_threshold": 0.1,
    "preferred_chart_format": "png",
    "preferred_report_format": "html"
  },
  "visualization": {
    "chart_style": "seaborn-v0_8",
    "figure_size": [12, 8],
    "dpi": 300
  },
  "metrics": {
    "primary_metrics": ["success_rate", "avg_execution_time", "avg_creation_time"],
    "metric_weights": {
      "success_rate": 0.5,
      "avg_execution_time": 0.3,
      "avg_creation_time": 0.2
    }
  }
}
```

### Key Configuration Options

- **time_range_days**: Default time range for analysis
- **comparison_threshold**: Threshold for detecting significant differences
- **chart_style**: Matplotlib style for charts
- **metric_weights**: Weights used in provider scoring
- **provider_colors**: Custom colors for providers in charts

## Data Sources

The analysis system works with:

1. **JSON benchmark files** in `benchmarks/results/`
2. **Markdown benchmark reports** (as fallback)
3. **Historical data** from multiple benchmark runs

### Data Requirements

For meaningful analysis, you need:
- **Multiple benchmark runs** over time
- **Consistent provider testing** across runs
- **At least 3-5 data points** for trend analysis
- **Recent data** (within configured time range)

## Advanced Usage

### Custom Analysis Scripts

You can use the analysis modules directly in Python:

```python
from benchmarks.analysis import BenchmarkDataParser, BenchmarkComparator

# Load data
parser = BenchmarkDataParser("benchmarks/results")
results = parser.load_all_results()

# Compare providers
comparator = BenchmarkComparator(parser)
comparison = comparator.compare_providers("local", "e2b", days=30)

print(comparison.summary)
```

### Programmatic Report Generation

```python
from benchmarks.analysis import BenchmarkReporter

reporter = BenchmarkReporter("reports")
report_path = reporter.generate_comprehensive_report(
    results,
    format="html",
    include_charts=True
)
```

### Custom Visualizations

```python
from benchmarks.analysis import BenchmarkVisualizer

visualizer = BenchmarkVisualizer("charts")
chart_path = visualizer.create_performance_dashboard(results)
interactive_path = visualizer.create_interactive_dashboard(results)
```

## Troubleshooting

### Common Issues

**No data found:**
- Ensure benchmark results exist in `benchmarks/results/`
- Check that the time range includes your data
- Verify provider names match exactly

**Charts not generating:**
- Install matplotlib: `pip install matplotlib`
- For interactive charts: `pip install plotly`
- Check output directory permissions

**PDF reports failing:**
- Install weasyprint: `pip install weasyprint`
- Use HTML or markdown format as alternative

**Trend analysis shows "insufficient_data":**
- Need at least 3 data points for trend analysis
- Increase time range or run more benchmarks
- Check that the specified provider exists in the data

### Performance Tips

- **Large datasets**: Use smaller time ranges for faster analysis
- **Memory usage**: Interactive dashboards use more memory
- **Chart generation**: Static charts are faster than interactive ones
- **Report size**: Exclude charts for smaller report files

## Integration with CI/CD

### Automated Regression Detection

Add to your CI pipeline:

```bash
# Run benchmarks
grainchain benchmark --provider all

# Check for regressions
grainchain analysis regressions --threshold 0.05

# Generate report
grainchain analysis report --format html --output benchmark_report.html
```

### Performance Monitoring

Set up regular analysis:

```bash
#!/bin/bash
# Daily performance analysis
grainchain analysis trends --days 7 --interactive --output daily_trends.html
grainchain analysis recommend --use-case general > provider_recommendation.txt
```

## Best Practices

1. **Regular benchmarking**: Run benchmarks consistently to build historical data
2. **Multiple providers**: Test multiple providers to enable meaningful comparisons
3. **Consistent environments**: Use similar test conditions across runs
4. **Trend monitoring**: Set up automated trend analysis to catch issues early
5. **Threshold tuning**: Adjust regression thresholds based on your requirements
6. **Documentation**: Include analysis results in your project documentation

## API Reference

For detailed API documentation, see the module docstrings:

- `benchmarks.analysis.data_parser.BenchmarkDataParser`
- `benchmarks.analysis.comparator.BenchmarkComparator`
- `benchmarks.analysis.visualizer.BenchmarkVisualizer`
- `benchmarks.analysis.reporter.BenchmarkReporter`
- `benchmarks.analysis.config.AnalysisConfig`
