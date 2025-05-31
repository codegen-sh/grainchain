# Grainchain Benchmarking Infrastructure

.PHONY: help install benchmark publish clean

help: ## Show this help message
	@echo "Grainchain Benchmarking Infrastructure"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

benchmark: ## Run a single benchmark
	python benchmarks/scripts/benchmark_runner.py

benchmark-config: ## Run benchmark with custom config
	python benchmarks/scripts/benchmark_runner.py --config benchmarks/configs/default.json

publish: ## Run benchmark and publish results
	python benchmarks/scripts/auto_publish.py --run-benchmark

summary: ## Generate summary report only
	python benchmarks/scripts/auto_publish.py --generate-summary

clean: ## Clean up benchmark artifacts
	docker container prune -f
	docker image prune -f

test-docker: ## Test Docker connectivity
	docker --version
	docker ps

setup: install ## Setup the benchmarking environment
	@echo "✅ Benchmarking environment setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run 'make benchmark' to execute a benchmark"
	@echo "  2. Run 'make publish' to run and auto-commit results"
	@echo "  3. Check 'benchmarks/results/' for output files"

# Development targets
dev-benchmark: ## Run benchmark with development settings
	python benchmarks/scripts/benchmark_runner.py --config benchmarks/configs/default.json --output-dir benchmarks/results/dev

lint: ## Lint Python code
	python -m flake8 benchmarks/scripts/ --max-line-length=120 --ignore=E501,W503

format: ## Format Python code
	python -m black benchmarks/scripts/

