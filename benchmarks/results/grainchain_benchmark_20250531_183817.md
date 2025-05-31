# Grainchain Provider Benchmark Report

**Generated:** 2025-05-31T18:38:00.913188  
**Duration:** 16.33 seconds  
**Providers Tested:** local, e2b, daytona  
**Test Scenarios:** 4  

## Executive Summary

| Provider | Success Rate | Avg Time (s) | Creation Time (s) | Status |
|----------|--------------|--------------|-------------------|--------|
| local | 75.0% | 0.04 | 0.00 | ⚠️ |
| e2b | 100.0% | 0.98 | 0.27 | ✅ |

## 🏆 Best Performers

- **Most Reliable:** e2b
- **Fastest Execution:** local
- **Fastest Startup:** local

## Detailed Results

### LOCAL Provider

- **Overall Success Rate:** 75.0%
- **Average Scenario Time:** 0.04s
- **Average Creation Time:** 0.00s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 0.02s
- **Iterations:** 3/3

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 0.08s
- **Iterations:** 3/3

#### File Operations
- **Success Rate:** 0.0%
- **Average Time:** 0.00s
- **Iterations:** 3/3

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 0.07s
- **Iterations:** 3/3

### E2B Provider

- **Overall Success Rate:** 100.0%
- **Average Scenario Time:** 0.98s
- **Average Creation Time:** 0.27s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 1.02s
- **Iterations:** 3/3

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 1.10s
- **Iterations:** 3/3

#### File Operations
- **Success Rate:** 100.0%
- **Average Time:** 1.08s
- **Iterations:** 3/3

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 0.74s
- **Iterations:** 3/3

### DAYTONA Provider

❌ **Status:** unavailable
**Error:** Required configuration 'api_key' not found for provider daytona

## Configuration

```json
{
  "providers": [
    "local",
    "e2b",
    "daytona"
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
