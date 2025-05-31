# Grainchain Provider Benchmark Report

**Generated:** 2025-05-31T20:07:57.490468
**Duration:** 60.40 seconds
**Providers Tested:** local, e2b, daytona
**Test Scenarios:** 5

## Executive Summary

| Provider | Success Rate | Avg Time (s) | Creation Time (s) | Status |
|----------|--------------|--------------|-------------------|--------|
| local | 73.3% | 0.07 | 0.00 | ⚠️ |
| e2b | 93.3% | 2.72 | 0.29 | ✅ |
| daytona | 96.7% | 8.29 | 0.45 | ✅ |

## 🏆 Best Performers

- **Most Reliable:** daytona
- **Fastest Execution:** local
- **Fastest Startup:** local

## Detailed Results

### LOCAL Provider

- **Overall Success Rate:** 73.3%
- **Average Scenario Time:** 0.07s
- **Average Creation Time:** 0.00s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 0.07s
- **Iterations:** 1/1

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 0.14s
- **Iterations:** 1/1

#### File Operations
- **Success Rate:** 0.0%
- **Average Time:** 0.00s
- **Iterations:** 1/1

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 0.14s
- **Iterations:** 1/1

#### Snapshot Lifecycle
- **Success Rate:** 66.7%
- **Average Time:** 0.02s
- **Iterations:** 1/1

### E2B Provider

- **Overall Success Rate:** 93.3%
- **Average Scenario Time:** 2.72s
- **Average Creation Time:** 0.29s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 0.95s
- **Iterations:** 1/1

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 1.06s
- **Iterations:** 1/1

#### File Operations
- **Success Rate:** 100.0%
- **Average Time:** 1.08s
- **Iterations:** 1/1

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 1.39s
- **Iterations:** 1/1

#### Snapshot Lifecycle
- **Success Rate:** 66.7%
- **Average Time:** 9.10s
- **Iterations:** 1/1

### DAYTONA Provider

- **Overall Success Rate:** 96.7%
- **Average Scenario Time:** 8.29s
- **Average Creation Time:** 0.45s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 2.71s
- **Iterations:** 1/1

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 2.44s
- **Iterations:** 1/1

#### File Operations
- **Success Rate:** 100.0%
- **Average Time:** 1.88s
- **Iterations:** 1/1

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 3.24s
- **Iterations:** 1/1

#### Snapshot Lifecycle
- **Success Rate:** 83.3%
- **Average Time:** 31.16s
- **Iterations:** 1/1

## Configuration

```json
{
  "providers": [
    "local",
    "e2b",
    "daytona"
  ],
  "iterations": 1,
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
