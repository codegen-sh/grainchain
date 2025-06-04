# Grainchain Provider Benchmark Report

**Generated:** 2025-06-04T02:53:12.502516
**Duration:** 5.69 seconds
**Providers Tested:** local, morph
**Test Scenarios:** 5

## Executive Summary

| Provider | Success Rate | Avg Time (s) | Creation Time (s) | Status |
|----------|--------------|--------------|-------------------|--------|
| local | 76.7% | 1.07 | 0.00 | ⚠️ |

## 🏆 Best Performers

- **Most Reliable:** local
- **Fastest Execution:** local
- **Fastest Startup:** local

## Detailed Results

### LOCAL Provider

- **Overall Success Rate:** 76.7%
- **Average Scenario Time:** 1.07s
- **Average Creation Time:** 0.00s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 0.02s
- **Iterations:** 1/1

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 0.07s
- **Iterations:** 1/1

#### File Operations
- **Success Rate:** 0.0%
- **Average Time:** 0.00s
- **Iterations:** 1/1

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 0.06s
- **Iterations:** 1/1

#### Snapshot Lifecycle
- **Success Rate:** 83.3%
- **Average Time:** 5.22s
- **Iterations:** 1/1

### MORPH Provider

❌ **Status:** unavailable
**Error:** Failed to create sandbox: Failed to create sandbox: Morph authentication failed: HTTP Error 402 for url 'https://cloud.morph.so/api/snapshot'
Status Code: 402
Response Body: {
  "detail": "Payment required"
}

## Configuration

```json
{
  "providers": [
    "local",
    "morph"
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
