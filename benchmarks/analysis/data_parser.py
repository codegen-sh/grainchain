"""
Benchmark data parser for loading and processing benchmark results
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

from .models import BenchmarkResult, ProviderMetrics, ScenarioMetrics


class BenchmarkDataParser:
    """Parser for benchmark data files (JSON and Markdown)"""

    def __init__(self, results_dir: str | Path = "benchmarks/results"):
        self.results_dir = Path(results_dir)
        if not self.results_dir.exists():
            raise FileNotFoundError(f"Results directory not found: {self.results_dir}")

    def load_all_results(self) -> list[BenchmarkResult]:
        """Load all benchmark results from the results directory"""
        results = []

        # Load JSON files first (preferred format)
        json_files = list(self.results_dir.glob("grainchain_benchmark_*.json"))
        for json_file in json_files:
            try:
                result = self.load_json_result(json_file)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Warning: Failed to load {json_file}: {e}")

        # If no JSON files, try to parse markdown files
        if not results:
            md_files = list(self.results_dir.glob("grainchain_benchmark_*.md"))
            for md_file in md_files:
                try:
                    result = self.load_markdown_result(md_file)
                    if result:
                        results.append(result)
                except Exception as e:
                    print(f"Warning: Failed to load {md_file}: {e}")

        # Sort by timestamp
        results.sort(key=lambda x: x.timestamp)
        return results

    def load_json_result(self, file_path: Path) -> str | NoneBenchmarkResult]:
        """Load a benchmark result from a JSON file"""
        try:
            with open(file_path) as f:
                data = json.load(f)

            return self._parse_json_data(data, file_path)
        except Exception as e:
            print(f"Error loading JSON file {file_path}: {e}")
            return None

    def load_markdown_result(self, file_path: Path) -> str | NoneBenchmarkResult]:
        """Load a benchmark result from a Markdown file"""
        try:
            with open(file_path) as f:
                content = f.read()

            return self._parse_markdown_content(content, file_path)
        except Exception as e:
            print(f"Error loading Markdown file {file_path}: {e}")
            return None

    def _parse_json_data(
        self, data: dict[str, Any], file_path: Path
    ) -> BenchmarkResult:
        """Parse JSON benchmark data into BenchmarkResult"""
        benchmark_info = data.get("benchmark_info", {})
        provider_results = data.get("provider_results", {})

        # Extract timestamp
        start_time_str = benchmark_info.get("start_time", "")
        timestamp = self._parse_timestamp(start_time_str)

        # Extract basic info
        duration = benchmark_info.get("duration_seconds", 0.0)
        providers_tested = benchmark_info.get("providers", [])
        test_scenarios = benchmark_info.get("test_scenarios", 0)

        # Parse provider results
        parsed_providers = {}
        for provider_name, provider_data in provider_results.items():
            provider_metrics = self._parse_provider_data(provider_name, provider_data)
            parsed_providers[provider_name] = provider_metrics

        return BenchmarkResult(
            timestamp=timestamp,
            duration_seconds=duration,
            providers_tested=providers_tested,
            test_scenarios=test_scenarios,
            provider_results=parsed_providers,
            file_path=file_path,
            raw_data=data,
        )

    def _parse_markdown_content(self, content: str, file_path: Path) -> BenchmarkResult:
        """Parse Markdown benchmark content into BenchmarkResult"""
        # Extract timestamp from filename or content
        timestamp_match = re.search(r"(\d{8}_\d{6})", file_path.name)
        if timestamp_match:
            timestamp_str = timestamp_match.group(1)
            timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        else:
            # Try to extract from content
            generated_match = re.search(r"\*\*Generated:\*\* (.+)", content)
            if generated_match:
                timestamp = self._parse_timestamp(generated_match.group(1))
            else:
                timestamp = datetime.now()

        # Extract duration
        duration_match = re.search(r"\*\*Duration:\*\* ([\d.]+) seconds", content)
        duration = float(duration_match.group(1)) if duration_match else 0.0

        # Extract providers tested
        providers_match = re.search(r"\*\*Providers Tested:\*\* (.+)", content)
        providers_tested = []
        if providers_match:
            providers_tested = [p.strip() for p in providers_match.group(1).split(",")]

        # Extract test scenarios count
        scenarios_match = re.search(r"\*\*Test Scenarios:\*\* (\d+)", content)
        test_scenarios = int(scenarios_match.group(1)) if scenarios_match else 0

        # Parse provider results from markdown
        parsed_providers = self._parse_markdown_providers(content)

        return BenchmarkResult(
            timestamp=timestamp,
            duration_seconds=duration,
            providers_tested=providers_tested,
            test_scenarios=test_scenarios,
            provider_results=parsed_providers,
            file_path=file_path,
        )

    def _parse_provider_data(
        self, provider_name: str, provider_data: dict[str, Any]
    ) -> ProviderMetrics:
        """Parse provider data from JSON into ProviderMetrics"""
        overall_metrics = provider_data.get("overall_metrics", {})
        scenarios_data = provider_data.get("scenarios", {})

        # Parse scenario metrics
        scenarios = {}
        for scenario_name, scenario_data in scenarios_data.items():
            aggregated = scenario_data.get("aggregated", {})
            scenarios[scenario_name] = ScenarioMetrics(
                name=scenario_name,
                description=scenario_data.get("description", ""),
                success_rate=aggregated.get("success_rate", 0.0),
                avg_execution_time=aggregated.get("avg_execution_time", 0.0),
                min_execution_time=aggregated.get("min_execution_time", 0.0),
                max_execution_time=aggregated.get("max_execution_time", 0.0),
                total_iterations=aggregated.get("total_iterations", 0),
                successful_iterations=aggregated.get("successful_iterations", 0),
                failed_iterations=aggregated.get("failed_iterations", 0),
                errors=aggregated.get("errors", []),
            )

        return ProviderMetrics(
            provider_name=provider_name,
            overall_success_rate=overall_metrics.get("overall_success_rate", 0.0),
            avg_creation_time=overall_metrics.get("avg_creation_time", 0.0),
            avg_execution_time=overall_metrics.get("avg_execution_time", 0.0),
            total_scenarios=len(scenarios),
            scenarios=scenarios,
            status=provider_data.get("status", "unknown"),
        )

    def _parse_markdown_providers(self, content: str) -> dict[str, ProviderMetrics]:
        """Parse provider information from markdown content"""
        providers = {}

        # Find provider sections
        provider_sections = re.findall(
            r"### (.+?) Provider\n\n(.+?)(?=###|\Z)", content, re.DOTALL
        )

        for provider_name, section_content in provider_sections:
            provider_name = provider_name.upper()

            # Extract overall metrics
            success_rate_match = re.search(
                r"Overall Success Rate:\*\* ([\d.]+)%", section_content
            )
            success_rate = (
                float(success_rate_match.group(1)) if success_rate_match else 0.0
            )

            avg_time_match = re.search(
                r"Average Scenario Time:\*\* ([\d.]+)s", section_content
            )
            avg_time = float(avg_time_match.group(1)) if avg_time_match else 0.0

            creation_time_match = re.search(
                r"Average Creation Time:\*\* ([\d.]+)s", section_content
            )
            creation_time = (
                float(creation_time_match.group(1)) if creation_time_match else 0.0
            )

            # Parse scenarios
            scenarios = {}
            scenario_matches = re.findall(
                r"#### (.+?)\n- \*\*Success Rate:\*\* ([\d.]+)%\n- \*\*Average Time:\*\* ([\d.]+)s",
                section_content,
            )

            for scenario_name, scenario_success, scenario_time in scenario_matches:
                scenarios[scenario_name.lower().replace(" ", "_")] = ScenarioMetrics(
                    name=scenario_name.lower().replace(" ", "_"),
                    description=scenario_name,
                    success_rate=float(scenario_success),
                    avg_execution_time=float(scenario_time),
                    min_execution_time=float(scenario_time),
                    max_execution_time=float(scenario_time),
                    total_iterations=1,
                    successful_iterations=1 if float(scenario_success) > 0 else 0,
                    failed_iterations=0 if float(scenario_success) > 0 else 1,
                )

            providers[provider_name.lower()] = ProviderMetrics(
                provider_name=provider_name.lower(),
                overall_success_rate=success_rate,
                avg_creation_time=creation_time,
                avg_execution_time=avg_time,
                total_scenarios=len(scenarios),
                scenarios=scenarios,
                status="completed",
            )

        return providers

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string into datetime object"""
        # Try different timestamp formats
        formats = [
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y%m%d_%H%M%S",
            "%Y-%m-%d %H:%M:%S",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        # If all formats fail, return current time
        print(
            f"Warning: Could not parse timestamp '{timestamp_str}', using current time"
        )
        return datetime.now()

    def get_results_by_provider(self, provider: str) -> list[BenchmarkResult]:
        """Get all results for a specific provider"""
        all_results = self.load_all_results()
        return [result for result in all_results if provider in result.providers_tested]

    def get_results_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[BenchmarkResult]:
        """Get results within a specific date range"""
        all_results = self.load_all_results()
        return [
            result
            for result in all_results
            if start_date <= result.timestamp <= end_date
        ]

    def get_latest_result(self) -> str | NoneBenchmarkResult]:
        """Get the most recent benchmark result"""
        all_results = self.load_all_results()
        return all_results[-1] if all_results else None
