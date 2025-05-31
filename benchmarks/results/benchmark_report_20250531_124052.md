# Grainchain Benchmark Report

**Generated:** Sat May 31 12:40:52 PDT 2025
**Commit:** bf9b109
**Environment:** Darwin 24.5.0

## Performance Results

| Provider | Total Time | Basic Echo | Python Test | File Ops | Status |
|----------|------------|------------|-------------|----------|--------|
| **local** | 0.036s | 0.007s | 0.021s | 0.008s | ✅ Pass |
| **e2b** | 0.599s | 0.331s | 0.111s | 0.156s | ✅ Pass |
| **daytona** | 1.012s | 0.305s | 0.156s | 0.551s | ✅ Pass |

## Summary

- **Total Providers Tested:** 3
- **Passed:** 3
- **Failed:** 0

## Performance Analysis

- **E2B vs Local:** 16.6x slower
- **Daytona vs Local:** 28.1x slower

## Recommendations

- **Development/Testing:** Use `local` provider for fastest iteration
- **Production (Speed):** Use `e2b` for best balance of speed and reliability
- **Production (Features):** Use `daytona` for comprehensive workspace environments

## Raw Results

Latest benchmark files saved to:
- `benchmark_report_20250531_124052.md`
