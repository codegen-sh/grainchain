#!/bin/bash
# Show latest benchmark status

set -e

OUTPUT_DIR="benchmarks/results"
LATEST_REPORT=$(find "$OUTPUT_DIR" -name "benchmark_report_*.md" | sort | tail -1)

if [ -z "$LATEST_REPORT" ]; then
    echo "❌ No benchmark reports found. Run './scripts/benchmark_all.sh' first."
    exit 1
fi

echo "📊 Latest Grainchain Benchmark Results"
echo "======================================"
echo ""
echo "📁 Report: $(basename "$LATEST_REPORT")"
echo "📅 Generated: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$LATEST_REPORT" 2>/dev/null || stat -c "%y" "$LATEST_REPORT" 2>/dev/null | cut -d' ' -f1-2)"
echo ""

# Extract and display the performance table
echo "⚡ Performance Summary:"
echo ""
awk '/## Performance Results/,/## Summary/' "$LATEST_REPORT" | grep -E "^\|" | head -5

echo ""

# Show performance analysis
echo "📈 Performance Analysis:"
awk '/## Performance Analysis/,/## Recommendations/' "$LATEST_REPORT" | grep -E "^-"

echo ""
echo "🔍 Full report: $LATEST_REPORT"
echo "🚀 Rerun benchmarks: ./scripts/benchmark_all.sh"
