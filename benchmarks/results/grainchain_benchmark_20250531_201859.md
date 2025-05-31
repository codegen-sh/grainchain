# Grainchain Provider Benchmark Report

**Generated:** 2025-05-31T20:18:08.291323
**Duration:** 51.69 seconds
**Providers Tested:** local, e2b
**Test Scenarios:** 5

## Executive Summary

| Provider | Success Rate | Avg Time (s) | Creation Time (s) | Status |
|----------|--------------|--------------|-------------------|--------|
| local | 74.4% | 0.39 | 0.00 | ⚠️ |
| e2b | 93.3% | 2.97 | 0.33 | ✅ |

## 🏆 Best Performers

- **Most Reliable:** e2b
- **Fastest Execution:** local
- **Fastest Startup:** local

## Detailed Results

### LOCAL Provider

- **Overall Success Rate:** 74.4%
- **Average Scenario Time:** 0.39s
- **Average Creation Time:** 0.00s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 0.01s
- **Iterations:** 3/3

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 0.07s
- **Iterations:** 3/3

#### File Operations
- **Success Rate:** 0.0%
- **Average Time:** 0.00s
- **Iterations:** 3/3

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 0.06s
- **Iterations:** 3/3

#### Snapshot Lifecycle
- **Success Rate:** 72.2%
- **Average Time:** 1.81s
- **Iterations:** 3/3

### E2B Provider

- **Overall Success Rate:** 93.3%
- **Average Scenario Time:** 2.97s
- **Average Creation Time:** 0.33s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 1.48s
- **Iterations:** 3/3

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 1.39s
- **Iterations:** 3/3

#### File Operations
- **Success Rate:** 100.0%
- **Average Time:** 1.44s
- **Iterations:** 3/3

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 1.01s
- **Iterations:** 3/3

#### Snapshot Lifecycle
- **Success Rate:** 66.7%
- **Average Time:** 9.52s
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
