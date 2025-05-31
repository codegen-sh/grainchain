# Grainchain Provider Benchmark Report

**Generated:** 2025-05-31T20:09:02.305354
**Duration:** 58.68 seconds
**Providers Tested:** local, e2b, daytona
**Test Scenarios:** 5

## Executive Summary

| Provider | Success Rate | Avg Time (s) | Creation Time (s) | Status |
|----------|--------------|--------------|-------------------|--------|
| local | 73.3% | 0.08 | 0.00 | ⚠️ |
| e2b | 93.3% | 3.14 | 0.45 | ✅ |
| daytona | 96.7% | 7.39 | 0.46 | ✅ |

## 🏆 Best Performers

- **Most Reliable:** daytona
- **Fastest Execution:** local
- **Fastest Startup:** local

## Detailed Results

### LOCAL Provider

- **Overall Success Rate:** 73.3%
- **Average Scenario Time:** 0.08s
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
- **Average Time:** 0.15s
- **Iterations:** 1/1

#### Snapshot Lifecycle
- **Success Rate:** 66.7%
- **Average Time:** 0.02s
- **Iterations:** 1/1

### E2B Provider

- **Overall Success Rate:** 93.3%
- **Average Scenario Time:** 3.14s
- **Average Creation Time:** 0.45s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 1.36s
- **Iterations:** 1/1

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 1.11s
- **Iterations:** 1/1

#### File Operations
- **Success Rate:** 100.0%
- **Average Time:** 1.08s
- **Iterations:** 1/1

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 1.63s
- **Iterations:** 1/1

#### Snapshot Lifecycle
- **Success Rate:** 66.7%
- **Average Time:** 10.53s
- **Iterations:** 1/1

### DAYTONA Provider

- **Overall Success Rate:** 96.7%
- **Average Scenario Time:** 7.39s
- **Average Creation Time:** 0.46s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 2.96s
- **Iterations:** 1/1

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 1.22s
- **Iterations:** 1/1

#### File Operations
- **Success Rate:** 100.0%
- **Average Time:** 3.50s
- **Iterations:** 1/1

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 2.36s
- **Iterations:** 1/1

#### Snapshot Lifecycle
- **Success Rate:** 83.3%
- **Average Time:** 26.90s
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
