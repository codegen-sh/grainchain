# Grainchain Provider Benchmark Report

**Generated:** 2025-05-31T18:10:10.548207
**Duration:** 11.21 seconds
**Providers Tested:** local, e2b
**Test Scenarios:** 4

## Executive Summary

| Provider | Success Rate | Avg Time (s) | Creation Time (s) | Status |
|----------|--------------|--------------|-------------------|--------|
| local | 75.0% | 0.03 | 0.00 | ⚠️ |
| e2b | 100.0% | 1.28 | 0.26 | ✅ |

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
- **Average Time:** 0.02s
- **Iterations:** 2/2

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 0.06s
- **Iterations:** 2/2

#### File Operations
- **Success Rate:** 0.0%
- **Average Time:** 0.00s
- **Iterations:** 2/2

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 0.05s
- **Iterations:** 2/2

### E2B Provider

- **Overall Success Rate:** 100.0%
- **Average Scenario Time:** 1.28s
- **Average Creation Time:** 0.26s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 1.18s
- **Iterations:** 2/2

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 1.58s
- **Iterations:** 2/2

#### File Operations
- **Success Rate:** 100.0%
- **Average Time:** 1.22s
- **Iterations:** 2/2

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 1.13s
- **Iterations:** 2/2

## Configuration

```json
{
  "providers": [
    "local",
    "e2b"
  ],
  "iterations": 2,
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
