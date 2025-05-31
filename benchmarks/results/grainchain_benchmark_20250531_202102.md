# Grainchain Provider Benchmark Report

**Generated:** 2025-05-31T20:19:13.184892
**Duration:** 109.17 seconds
**Providers Tested:** local, e2b, daytona, modal
**Test Scenarios:** 5

## Executive Summary

| Provider | Success Rate | Avg Time (s) | Creation Time (s) | Status |
|----------|--------------|--------------|-------------------|--------|
| local | 73.3% | 0.03 | 0.00 | ⚠️ |
| e2b | 93.3% | 3.12 | 0.36 | ✅ |
| daytona | 96.7% | 3.87 | 0.23 | ✅ |

## 🏆 Best Performers

- **Most Reliable:** daytona
- **Fastest Execution:** local
- **Fastest Startup:** local

## Detailed Results

### LOCAL Provider

- **Overall Success Rate:** 73.3%
- **Average Scenario Time:** 0.03s
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
- **Success Rate:** 66.7%
- **Average Time:** 0.01s
- **Iterations:** 3/3

### E2B Provider

- **Overall Success Rate:** 93.3%
- **Average Scenario Time:** 3.12s
- **Average Creation Time:** 0.36s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 0.98s
- **Iterations:** 3/3

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 1.74s
- **Iterations:** 3/3

#### File Operations
- **Success Rate:** 100.0%
- **Average Time:** 1.49s
- **Iterations:** 3/3

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 1.62s
- **Iterations:** 3/3

#### Snapshot Lifecycle
- **Success Rate:** 66.7%
- **Average Time:** 9.78s
- **Iterations:** 3/3

### DAYTONA Provider

- **Overall Success Rate:** 96.7%
- **Average Scenario Time:** 3.87s
- **Average Creation Time:** 0.23s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 0.91s
- **Iterations:** 3/3

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 1.11s
- **Iterations:** 3/3

#### File Operations
- **Success Rate:** 100.0%
- **Average Time:** 0.69s
- **Iterations:** 3/3

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 0.78s
- **Iterations:** 3/3

#### Snapshot Lifecycle
- **Success Rate:** 83.3%
- **Average Time:** 15.88s
- **Iterations:** 3/3

### MODAL Provider

❌ **Status:** unavailable
**Error:** Modal provider requires the 'modal' package. Install it with: pip install grainchain[modal]

## Configuration

```json
{
  "providers": [
    "local",
    "e2b",
    "daytona",
    "modal"
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
