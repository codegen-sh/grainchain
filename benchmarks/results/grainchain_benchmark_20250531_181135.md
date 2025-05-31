# Grainchain Provider Benchmark Report

**Generated:** 2025-05-31T18:11:18.340973
**Duration:** 17.42 seconds
**Providers Tested:** local, e2b
**Test Scenarios:** 4

## Executive Summary

| Provider | Success Rate | Avg Time (s) | Creation Time (s) | Status |
|----------|--------------|--------------|-------------------|--------|
| local | 75.0% | 0.03 | 0.00 | ⚠️ |
| e2b | 100.0% | 1.31 | 0.35 | ✅ |

## 🏆 Best Performers

- **Most Reliable:** e2b
- **Fastest Execution:** local
- **Fastest Startup:** local

## Detailed Results

### LOCAL Provider

- **Overall Success Rate:** 75.0%
- **Average Scenario Time:** 0.03s
- **Average Creation Time:** 0.00s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 0.01s
- **Iterations:** 3/3

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 0.06s
- **Iterations:** 3/3

#### File Operations
- **Success Rate:** 0.0%
- **Average Time:** 0.00s
- **Iterations:** 3/3

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 0.05s
- **Iterations:** 3/3

### E2B Provider

- **Overall Success Rate:** 100.0%
- **Average Scenario Time:** 1.31s
- **Average Creation Time:** 0.35s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 1.12s
- **Iterations:** 3/3

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 1.24s
- **Iterations:** 3/3

#### File Operations
- **Success Rate:** 100.0%
- **Average Time:** 1.49s
- **Iterations:** 3/3

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 1.40s
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
