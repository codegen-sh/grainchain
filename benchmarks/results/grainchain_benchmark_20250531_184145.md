# Grainchain Provider Benchmark Report

**Generated:** 2025-05-31T18:41:33.391541  
**Duration:** 12.55 seconds  
**Providers Tested:** local, e2b, daytona  
**Test Scenarios:** 4  

## Executive Summary

| Provider | Success Rate | Avg Time (s) | Creation Time (s) | Status |
|----------|--------------|--------------|-------------------|--------|
| local | 75.0% | 0.04 | 0.00 | ⚠️ |
| e2b | 100.0% | 1.06 | 0.33 | ✅ |

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
- **Iterations:** 2/2

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 0.08s
- **Iterations:** 2/2

#### File Operations
- **Success Rate:** 0.0%
- **Average Time:** 0.00s
- **Iterations:** 2/2

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 0.06s
- **Iterations:** 2/2

### E2B Provider

- **Overall Success Rate:** 100.0%
- **Average Scenario Time:** 1.06s
- **Average Creation Time:** 0.33s

#### Basic Commands
- **Success Rate:** 100.0%
- **Average Time:** 0.89s
- **Iterations:** 2/2

#### Python Execution
- **Success Rate:** 100.0%
- **Average Time:** 1.36s
- **Iterations:** 2/2

#### File Operations
- **Success Rate:** 100.0%
- **Average Time:** 1.18s
- **Iterations:** 2/2

#### Computational Tasks
- **Success Rate:** 100.0%
- **Average Time:** 0.81s
- **Iterations:** 2/2

### DAYTONA Provider

❌ **Status:** unavailable
**Error:** Failed to create sandbox: Failed to create sandbox: Daytona sandbox creation failed: Failed to create sandbox: HTTPSConnectionPool(host='api.daytona.io', port=443): Max retries exceeded with url: /workspace (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate (_ssl.c:1028)')))

## Configuration

```json
{
  "providers": [
    "local",
    "e2b",
    "daytona"
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
