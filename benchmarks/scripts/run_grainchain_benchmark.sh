#!/bin/bash
# Grainchain Provider Benchmark Runner
# This script runs benchmarks for Grainchain sandbox providers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Grainchain Provider Benchmark Suite${NC}"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "grainchain" ]; then
    echo -e "${RED}❌ Error: Please run this script from the grainchain repository root${NC}"
    exit 1
fi

# Check if grainchain is installed
if ! python -c "import grainchain" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installing grainchain in development mode...${NC}"
    pip install -e .
fi

# Load environment variables
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Loading environment variables from .env${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}⚠️  No .env file found. E2B tests may fail without API key.${NC}"
fi

# Set default providers if not specified
PROVIDERS=${1:-"local e2b"}
ITERATIONS=${2:-3}

echo -e "${BLUE}📊 Configuration:${NC}"
echo "  Providers: $PROVIDERS"
echo "  Iterations: $ITERATIONS"
echo "  Timeout: 30s"
echo ""

# Run the benchmark
echo -e "${GREEN}🧪 Starting benchmark...${NC}"
python benchmarks/scripts/grainchain_benchmark.py \
    --providers $PROVIDERS \
    --iterations $ITERATIONS \
    --config benchmarks/configs/grainchain.json

# Check if benchmark completed successfully
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 Benchmark completed successfully!${NC}"
    echo -e "${BLUE}📁 Results saved to: benchmarks/results/${NC}"
    echo ""
    
    # Show latest results if available
    if [ -f "benchmarks/results/latest_grainchain.md" ]; then
        echo -e "${BLUE}📈 Latest Results Summary:${NC}"
        echo "----------------------------------------"
        head -20 benchmarks/results/latest_grainchain.md
        echo ""
        echo -e "${BLUE}📄 Full report: benchmarks/results/latest_grainchain.md${NC}"
    fi
else
    echo -e "${RED}❌ Benchmark failed!${NC}"
    exit 1
fi

