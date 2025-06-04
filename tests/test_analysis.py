"""
Tests for benchmark analysis functionality
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from benchmarks.analysis import (
    AnalysisConfig,
    BenchmarkComparator,
    BenchmarkDataParser,
    BenchmarkReporter,
    BenchmarkVisualizer,
)
from benchmarks.analysis.models import BenchmarkResult, ProviderMetrics, ScenarioMetrics


class TestBenchmarkDataParser:
    """Test cases for BenchmarkDataParser"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.results_dir = Path(self.temp_dir) / "results"
        self.results_dir.mkdir()

        # Load sample data
        fixtures_dir = Path(__file__).parent / "fixtures"
        with open(fixtures_dir / "sample_benchmark_data.json") as f:
            self.sample_data = json.load(f)

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_load_json_result(self):
        """Test loading benchmark result from JSON file"""
        # Create a sample JSON file
        json_file = self.results_dir / "grainchain_benchmark_20250601_100000.json"
        with open(json_file, "w") as f:
            json.dump(self.sample_data, f)

        parser = BenchmarkDataParser(self.results_dir)
        result = parser.load_json_result(json_file)

        assert result is not None
        assert isinstance(result, BenchmarkResult)
        assert len(result.providers_tested) == 2
        assert "local" in result.providers_tested
        assert "e2b" in result.providers_tested
        assert result.test_scenarios == 5
        assert result.duration_seconds == 330.0

    def test_load_all_results(self):
        """Test loading all benchmark results"""
        # Create multiple JSON files
        for i in range(3):
            json_file = (
                self.results_dir / f"grainchain_benchmark_2025060{i+1}_100000.json"
            )
            with open(json_file, "w") as f:
                json.dump(self.sample_data, f)

        parser = BenchmarkDataParser(self.results_dir)
        results = parser.load_all_results()

        assert len(results) == 3
        assert all(isinstance(r, BenchmarkResult) for r in results)

    def test_get_results_by_provider(self):
        """Test filtering results by provider"""
        json_file = self.results_dir / "grainchain_benchmark_20250601_100000.json"
        with open(json_file, "w") as f:
            json.dump(self.sample_data, f)

        parser = BenchmarkDataParser(self.results_dir)
        local_results = parser.get_results_by_provider("local")
        e2b_results = parser.get_results_by_provider("e2b")
        nonexistent_results = parser.get_results_by_provider("nonexistent")

        assert len(local_results) == 1
        assert len(e2b_results) == 1
        assert len(nonexistent_results) == 0

    def test_get_results_by_date_range(self):
        """Test filtering results by date range"""
        json_file = self.results_dir / "grainchain_benchmark_20250601_100000.json"
        with open(json_file, "w") as f:
            json.dump(self.sample_data, f)

        parser = BenchmarkDataParser(self.results_dir)

        start_date = datetime(2025, 5, 31)
        end_date = datetime(2025, 6, 2)
        results = parser.get_results_by_date_range(start_date, end_date)

        assert len(results) == 1

        # Test with date range that excludes the result
        start_date = datetime(2025, 6, 2)
        end_date = datetime(2025, 6, 3)
        results = parser.get_results_by_date_range(start_date, end_date)

        assert len(results) == 0

    def test_parse_provider_data(self):
        """Test parsing provider data from JSON"""
        parser = BenchmarkDataParser(self.results_dir)
        provider_data = self.sample_data["provider_results"]["local"]

        metrics = parser._parse_provider_data("local", provider_data)

        assert isinstance(metrics, ProviderMetrics)
        assert metrics.provider_name == "local"
        assert metrics.overall_success_rate == 55.6
        assert metrics.avg_creation_time == 0.09
        assert metrics.avg_execution_time == 5.08
        assert len(metrics.scenarios) == 3

        # Test scenario parsing
        basic_commands = metrics.scenarios["basic_commands"]
        assert isinstance(basic_commands, ScenarioMetrics)
        assert basic_commands.success_rate == 100.0
        assert basic_commands.total_iterations == 3
        assert basic_commands.successful_iterations == 3


class TestBenchmarkComparator:
    """Test cases for BenchmarkComparator"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.results_dir = Path(self.temp_dir) / "results"
        self.results_dir.mkdir()

        # Create sample data
        fixtures_dir = Path(__file__).parent / "fixtures"
        with open(fixtures_dir / "sample_benchmark_data.json") as f:
            sample_data = json.load(f)

        json_file = self.results_dir / "grainchain_benchmark_20250601_100000.json"
        with open(json_file, "w") as f:
            json.dump(sample_data, f)

        self.parser = BenchmarkDataParser(self.results_dir)
        self.comparator = BenchmarkComparator(self.parser)

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_compare_providers(self):
        """Test provider comparison"""
        comparison = self.comparator.compare_providers("local", "e2b")

        assert comparison.comparison_type == "provider"
        assert comparison.baseline == "local"
        assert comparison.target == "e2b"
        assert len(comparison.metrics_compared) > 0

        # E2B should show improvements in success rate
        assert "success_rate" in comparison.improvements
        assert comparison.improvements["success_rate"] > 0

        # Local should be faster in creation time
        assert "avg_creation_time" in comparison.improvements

    def test_analyze_time_trends_insufficient_data(self):
        """Test trend analysis with insufficient data"""
        trend = self.comparator.analyze_time_trends(
            "local", days=30, metric="success_rate"
        )

        assert trend.trend_direction == "insufficient_data"
        assert trend.trend_strength == 0.0

    def test_detect_performance_regressions(self):
        """Test regression detection"""
        regressions = self.comparator.detect_performance_regressions(
            baseline_days=7, comparison_days=7, threshold=0.1
        )

        # With only one data point, no regressions should be detected
        assert len(regressions) == 0

    def test_recommend_provider(self):
        """Test provider recommendation"""
        recommendation = self.comparator.recommend_provider("general", days=30)

        assert recommendation.recommended_provider in ["local", "e2b"]
        assert 0 <= recommendation.confidence_score <= 1
        assert len(recommendation.reasoning) > 0

    def test_aggregate_provider_metrics(self):
        """Test metric aggregation"""
        results = self.parser.load_all_results()
        metrics = self.comparator._aggregate_provider_metrics(results, "local")

        assert "success_rate" in metrics
        assert "avg_execution_time" in metrics
        assert "avg_creation_time" in metrics
        assert metrics["data_points"] == 1


class TestBenchmarkVisualizer:
    """Test cases for BenchmarkVisualizer"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.charts_dir = Path(self.temp_dir) / "charts"
        self.charts_dir.mkdir()

        self.visualizer = BenchmarkVisualizer(self.charts_dir)

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_create_performance_dashboard_empty(self):
        """Test creating dashboard with no data"""
        chart_path = self.visualizer.create_performance_dashboard([])

        assert chart_path.exists()
        assert chart_path.suffix == ".png"

    def test_export_chart_data_empty(self):
        """Test exporting chart data with no results"""
        data_path = self.visualizer.export_chart_data([])

        assert data_path.exists()
        assert data_path.suffix == ".json"

        with open(data_path) as f:
            data = json.load(f)

        assert "metadata" in data
        assert data["metadata"]["total_results"] == 0


class TestBenchmarkReporter:
    """Test cases for BenchmarkReporter"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.reports_dir = Path(self.temp_dir) / "reports"
        self.reports_dir.mkdir()

        self.reporter = BenchmarkReporter(self.reports_dir)

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_generate_comprehensive_report_markdown(self):
        """Test generating comprehensive markdown report"""
        report_path = self.reporter.generate_comprehensive_report(
            [], format="markdown", include_charts=False
        )

        assert report_path.exists()
        assert report_path.suffix == ".md"

        with open(report_path) as f:
            content = f.read()

        assert "Comprehensive Benchmark Report" in content
        assert "No benchmark data available" in content

    def test_generate_comprehensive_report_html(self):
        """Test generating comprehensive HTML report"""
        report_path = self.reporter.generate_comprehensive_report(
            [], format="html", include_charts=False
        )

        assert report_path.exists()
        assert report_path.suffix == ".html"

        with open(report_path) as f:
            content = f.read()

        assert "<html" in content
        assert "Comprehensive Benchmark Report" in content


class TestAnalysisConfig:
    """Test cases for AnalysisConfig"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.json"

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_default_config(self):
        """Test default configuration values"""
        config = AnalysisConfig(self.config_file)  # Non-existent file

        assert config.time_range_days == 30
        assert config.comparison_threshold == 0.1
        assert config.preferred_chart_format == "png"
        assert config.preferred_report_format == "html"

    def test_load_custom_config(self):
        """Test loading custom configuration"""
        custom_config = {
            "default_settings": {"time_range_days": 60, "comparison_threshold": 0.2}
        }

        with open(self.config_file, "w") as f:
            json.dump(custom_config, f)

        config = AnalysisConfig(self.config_file)

        assert config.time_range_days == 60
        assert config.comparison_threshold == 0.2

    def test_get_set_config_values(self):
        """Test getting and setting configuration values"""
        config = AnalysisConfig(self.config_file)

        # Test getting with dot notation
        assert config.get("default_settings.time_range_days") == 30
        assert config.get("nonexistent.key", "default") == "default"

        # Test setting with dot notation
        config.set("default_settings.time_range_days", 45)
        assert config.get("default_settings.time_range_days") == 45

    def test_save_config(self):
        """Test saving configuration to file"""
        config = AnalysisConfig(self.config_file)
        config.set("default_settings.time_range_days", 90)
        config.save()

        # Load the saved config
        new_config = AnalysisConfig(self.config_file)
        assert new_config.time_range_days == 90

    def test_provider_display_names(self):
        """Test provider display name functionality"""
        config = AnalysisConfig(self.config_file)

        # Test default behavior
        assert config.get_provider_display_name("local") == "Local"
        assert config.get_provider_display_name("unknown") == "Unknown"

    def test_provider_colors(self):
        """Test provider color functionality"""
        config = AnalysisConfig(self.config_file)

        # Should return a color from the palette
        color = config.get_provider_color("local")
        assert color.startswith("#")
        assert len(color) == 7  # Hex color format


class TestIntegration:
    """Integration tests for the analysis system"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.results_dir = Path(self.temp_dir) / "results"
        self.results_dir.mkdir()

        # Create sample data files
        fixtures_dir = Path(__file__).parent / "fixtures"
        with open(fixtures_dir / "sample_benchmark_data.json") as f:
            sample_data = json.load(f)

        # Create multiple benchmark files with different timestamps
        for i in range(3):
            data = sample_data.copy()
            timestamp = datetime(2025, 6, 1 + i, 10, 0, 0)
            data["benchmark_info"]["start_time"] = timestamp.isoformat()

            json_file = (
                self.results_dir
                / f"grainchain_benchmark_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(json_file, "w") as f:
                json.dump(data, f)

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_full_analysis_workflow(self):
        """Test complete analysis workflow"""
        # Initialize components
        parser = BenchmarkDataParser(self.results_dir)
        comparator = BenchmarkComparator(parser)
        visualizer = BenchmarkVisualizer(Path(self.temp_dir) / "charts")
        reporter = BenchmarkReporter(Path(self.temp_dir) / "reports")

        # Load data
        results = parser.load_all_results()
        assert len(results) == 3

        # Perform comparison
        comparison = comparator.compare_providers("local", "e2b")
        assert comparison is not None

        # Generate visualization
        chart_path = visualizer.create_performance_dashboard(results)
        assert chart_path.exists()

        # Generate report
        report_path = reporter.generate_comprehensive_report(
            results, format="markdown", include_charts=False
        )
        assert report_path.exists()

        # Verify report content
        with open(report_path) as f:
            content = f.read()

        assert "local" in content
        assert "e2b" in content
        assert "3" in content  # Number of benchmark runs


if __name__ == "__main__":
    pytest.main([__file__])
