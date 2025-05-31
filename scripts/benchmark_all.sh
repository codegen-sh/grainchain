#!/bin/bash
# Generate comprehensive benchmark report for all providers

set -e

# Configuration
PROVIDERS="local e2b daytona"
OUTPUT_DIR="benchmarks/results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="$OUTPUT_DIR/benchmark_report_$TIMESTAMP.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Running comprehensive Grainchain benchmarks..."
echo "📊 Results will be saved to: $REPORT_FILE"

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Initialize report
cat > "$REPORT_FILE" << EOF
# Grainchain Benchmark Report

**Generated:** $(date)
**Commit:** $(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
**Environment:** $(uname -s) $(uname -r)

## Performance Results

| Provider | Total Time | Basic Echo | Python Test | File Ops | Status |
|----------|------------|------------|-------------|----------|--------|
EOF

# Track results for summary
total_tests=0
passed_tests=0
local_time=""
e2b_time=""
daytona_time=""

# Run benchmarks for each provider
for provider in $PROVIDERS; do
    echo -e "\n${YELLOW}🧪 Testing $provider provider...${NC}"

    # Check if provider dependencies are available
    case $provider in
        "e2b")
            if [ -z "$E2B_API_KEY" ]; then
                echo -e "${RED}⚠️ Skipping E2B: E2B_API_KEY not set${NC}"
                echo "| $provider | N/A | N/A | N/A | N/A | ⚠️ Skipped |" >> "$REPORT_FILE"
                continue
            fi
            ;;
        "daytona")
            if [ -z "$DAYTONA_API_KEY" ]; then
                echo -e "${RED}⚠️ Skipping Daytona: DAYTONA_API_KEY not set${NC}"
                echo "| $provider | N/A | N/A | N/A | N/A | ⚠️ Skipped |" >> "$REPORT_FILE"
                continue
            fi
            ;;
    esac

    # Run benchmark and capture results
    if output=$(grainchain benchmark --provider "$provider" --output "$OUTPUT_DIR" 2>&1); then
        echo -e "${GREEN}✅ $provider benchmark completed${NC}"

        # Extract timing information from output
        basic_time=$(echo "$output" | grep "Basic echo test:" | sed 's/.*: \([0-9.]*\)s/\1/')
        python_time=$(echo "$output" | grep "Python test:" | sed 's/.*: \([0-9.]*\)s/\1/')
        file_time=$(echo "$output" | grep "File operations test:" | sed 's/.*: \([0-9.]*\)s/\1/')
        total_time=$(echo "$output" | grep "Total time:" | sed 's/.*: \([0-9.]*\)s/\1/')

        # Add to report
        echo "| **$provider** | ${total_time}s | ${basic_time}s | ${python_time}s | ${file_time}s | ✅ Pass |" >> "$REPORT_FILE"

        # Store results for comparison
        case $provider in
            "local") local_time="$total_time" ;;
            "e2b") e2b_time="$total_time" ;;
            "daytona") daytona_time="$total_time" ;;
        esac

        ((passed_tests++))
    else
        echo -e "${RED}❌ $provider benchmark failed${NC}"
        echo "$output"
        echo "| **$provider** | N/A | N/A | N/A | N/A | ❌ Failed |" >> "$REPORT_FILE"
    fi

    ((total_tests++))
done

# Add summary to report
cat >> "$REPORT_FILE" << EOF

## Summary

- **Total Providers Tested:** $total_tests
- **Passed:** $passed_tests
- **Failed:** $((total_tests - passed_tests))

## Performance Analysis

EOF

# Performance analysis
if [ -n "$local_time" ] && [ -n "$e2b_time" ]; then
    speedup=$(echo "scale=1; $e2b_time / $local_time" | bc 2>/dev/null || echo "N/A")
    echo "- **E2B vs Local:** ${speedup}x slower" >> "$REPORT_FILE"
fi

if [ -n "$local_time" ] && [ -n "$daytona_time" ]; then
    speedup=$(echo "scale=1; $daytona_time / $local_time" | bc 2>/dev/null || echo "N/A")
    echo "- **Daytona vs Local:** ${speedup}x slower" >> "$REPORT_FILE"
fi

# Add recommendations
cat >> "$REPORT_FILE" << EOF

## Recommendations

- **Development/Testing:** Use \`local\` provider for fastest iteration
- **Production (Speed):** Use \`e2b\` for best balance of speed and reliability
- **Production (Features):** Use \`daytona\` for comprehensive workspace environments

## Raw Results

Latest benchmark files saved to:
EOF

# List recent benchmark files
find "$OUTPUT_DIR" -name "benchmark_*_$TIMESTAMP.json" -o -name "*$TIMESTAMP*" 2>/dev/null | head -5 | while read file; do
    echo "- \`$(basename "$file")\`" >> "$REPORT_FILE"
done

echo ""
echo -e "${GREEN}📊 Benchmark report generated: $REPORT_FILE${NC}"
echo -e "${YELLOW}💡 Commit this file to track performance over time${NC}"

# Show quick summary
echo ""
echo "📈 Quick Summary:"
[ -n "$local_time" ] && echo "  local: ${local_time}s"
[ -n "$e2b_time" ] && echo "  e2b: ${e2b_time}s"
[ -n "$daytona_time" ] && echo "  daytona: ${daytona_time}s"

echo ""
echo "🎯 To commit results:"
echo "  git add $REPORT_FILE"
echo "  git commit -m \"benchmark: update performance baseline $(date +%Y-%m-%d)\""
