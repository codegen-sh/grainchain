# Grainchain Provider Benchmark Report

**Generated:** 2025-07-06T20:14:52.838818
**Duration:** 51.89 seconds
**Providers Tested:** local, e2b
**Test Scenarios:** 5

## Executive Summary

| Provider | Success Rate | Avg Time (s) | Creation Time (s) | Status |
|----------|--------------|--------------|-------------------|--------|
| local | 74.4% | 0.44 | 0.00 | ⚠️ |
| e2b | 93.3% | 2.85 | 0.38 | ✅ |

## 🏆 Best Performers

- **Most Reliable:** e2b
- **Fastest Execution:** local
- **Fastest Startup:** local

## Detailed Results

### LOCAL Provider

- **Overall Success Rate:** 74.4%
- **Average Scenario Time:** 0.44s
- **Average Creation Time:** 0.00s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 0.02s
- **Iterations:** 3/3

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 0.09s
- **Iterations:** 3/3

#### File Operations
- **Success Rate:** 0.0%
- **Average Time:** 0.00s
- **Iterations:** 3/3

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 0.08s
- **Iterations:** 3/3

#### Snapshot Lifecycle
- **Success Rate:** 72.2%
- **Average Time:** 2.00s
- **Iterations:** 3/3

### E2B Provider

- **Overall Success Rate:** 93.3%
- **Average Scenario Time:** 2.85s
- **Average Creation Time:** 0.38s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 1.32s
- **Iterations:** 3/3

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 1.46s
- **Iterations:** 3/3

#### File Operations
- **Success Rate:** 100.0%
- **Average Time:** 1.34s
- **Iterations:** 3/3

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 1.07s
- **Iterations:** 3/3

#### Snapshot Lifecycle
- **Success Rate:** 66.7%
- **Average Time:** 9.05s
- **Iterations:** 3/3

## Configuration

```json
{
  "providers": [
    "local",
    "e2b"
  ],
  "iterations": 3,
  "timeout": 30,
  "parallel_tests": false,
  "detailed_metrics": true,
  "export_formats": [
    "json",
    "markdown",
    "html"
  ]
}
```
