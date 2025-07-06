# Grainchain Benchmark Summary

**Last Updated:** 2025-07-06 20:49:29
**Total Benchmark Runs:** 1

## Recent Results

| Date | Status | Success Rate | Avg Time (s) | Providers | Notes |
|------|--------|--------------|--------------|-----------|-------|
| 2025-07-06 | ✅ | 76.7% | 1.09 | local | OK |

## Configuration

The benchmarks use the following configuration:
- **Providers:** Local, E2B, Modal, Daytona, Morph (when available)
- **Test Scenarios:** Basic commands, Python execution, File operations, Computational tasks, Snapshot lifecycle
- **Default Iterations:** 3
- **Timeout:** 30 seconds per scenario

## Metrics Collected

- **Sandbox Creation Time:** Time to create a new sandbox
- **Command Execution Time:** Time to execute individual commands
- **Success Rate:** Percentage of successful operations
- **File Operations:** Upload/download performance
- **Snapshot Lifecycle:** Git clone, snapshot creation, and restoration

## Test Scenarios

1. **Basic Commands:** Shell commands (echo, pwd, ls, whoami, date)
2. **Python Execution:** Python script execution and version checks
3. **File Operations:** File upload/download with various sizes
4. **Computational Tasks:** CPU-intensive Python operations
5. **Snapshot Lifecycle:** Git clone, file creation, snapshot, kill, and restore

## Automation

This summary is automatically updated when new benchmark results are available.
Results are committed to the repository for historical tracking.
