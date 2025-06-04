"""
Tests specifically for comparison functionality
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from benchmarks.analysis.comparator import BenchmarkComparator
from benchmarks.analysis.models import (
    BenchmarkResult,
    ProviderMetrics,
    ScenarioMetrics,
)


class TestProviderComparison:
    """Test cases for provider comparison functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_parser = Mock()
        self.comparator = BenchmarkComparator(self.mock_parser)

    def create_mock_result(self, timestamp, provider_data):
        """Create a mock BenchmarkResult"""
        return BenchmarkResult(
            timestamp=timestamp,
            duration_seconds=300.0,
            providers_tested=list(provider_data.keys()),
            test_scenarios=3,
            provider_results=provider_data,
        )

    def create_mock_provider_metrics(self, success_rate, exec_time, creation_time):
        """Create mock ProviderMetrics"""
        return ProviderMetrics(
            provider_name="test",
            overall_success_rate=success_rate,
            avg_execution_time=exec_time,
            avg_creation_time=creation_time,
            total_scenarios=3,
            scenarios={
                "basic_commands": ScenarioMetrics(
                    name="basic_commands",
                    description="Basic commands",
                    success_rate=success_rate,
                    avg_execution_time=exec_time,
                    min_execution_time=exec_time * 0.8,
                    max_execution_time=exec_time * 1.2,
                    total_iterations=3,
                    successful_iterations=int(3 * success_rate / 100),
                    failed_iterations=3 - int(3 * success_rate / 100),
                )
            },
        )

    def test_compare_providers_clear_winner(self):
        """Test comparison where one provider clearly outperforms"""
        # Provider 1: Lower success rate, slower execution
        provider1_metrics = self.create_mock_provider_metrics(70.0, 5.0, 1.0)

        # Provider 2: Higher success rate, faster execution
        provider2_metrics = self.create_mock_provider_metrics(95.0, 2.0, 0.5)

        result1 = self.create_mock_result(
            datetime.now() - timedelta(days=1), {"provider1": provider1_metrics}
        )
        result2 = self.create_mock_result(
            datetime.now() - timedelta(days=1), {"provider2": provider2_metrics}
        )

        self.mock_parser.get_results_by_provider.side_effect = [[result1], [result2]]

        comparison = self.comparator.compare_providers("provider1", "provider2")

        assert comparison.comparison_type == "provider"
        assert comparison.baseline == "provider1"
        assert comparison.target == "provider2"

        # Provider 2 should show improvements
        assert "success_rate" in comparison.improvements
        assert "avg_execution_time" in comparison.improvements
        assert "avg_creation_time" in comparison.improvements

        assert comparison.improvements["success_rate"] == 25.0  # 95 - 70
        assert comparison.improvements["avg_execution_time"] == 3.0  # 5 - 2
        assert comparison.improvements["avg_creation_time"] == 0.5  # 1 - 0.5

        assert len(comparison.regressions) == 0

    def test_compare_providers_mixed_results(self):
        """Test comparison with mixed results (some improvements, some regressions)"""
        # Provider 1: High success rate, slow execution, fast creation
        provider1_metrics = self.create_mock_provider_metrics(95.0, 5.0, 0.1)

        # Provider 2: Lower success rate, fast execution, slow creation
        provider2_metrics = self.create_mock_provider_metrics(80.0, 1.0, 2.0)

        result1 = self.create_mock_result(
            datetime.now() - timedelta(days=1), {"provider1": provider1_metrics}
        )
        result2 = self.create_mock_result(
            datetime.now() - timedelta(days=1), {"provider2": provider2_metrics}
        )

        self.mock_parser.get_results_by_provider.side_effect = [[result1], [result2]]

        comparison = self.comparator.compare_providers("provider1", "provider2")

        # Should have both improvements and regressions
        assert len(comparison.improvements) > 0
        assert len(comparison.regressions) > 0

        # Provider 2 should be faster in execution
        assert "avg_execution_time" in comparison.improvements
        assert comparison.improvements["avg_execution_time"] == 4.0  # 5 - 1

        # But worse in success rate and creation time
        assert "success_rate" in comparison.regressions
        assert "avg_creation_time" in comparison.regressions
        assert comparison.regressions["success_rate"] == 15.0  # 95 - 80
        assert comparison.regressions["avg_creation_time"] == 1.9  # 2 - 0.1

    def test_compare_providers_no_data(self):
        """Test comparison when no data is available"""
        self.mock_parser.get_results_by_provider.side_effect = [[], []]

        comparison = self.comparator.compare_providers("provider1", "provider2")

        assert comparison.comparison_type == "provider"
        assert "Insufficient data" in comparison.summary
        assert len(comparison.improvements) == 0
        assert len(comparison.regressions) == 0

    def test_compare_providers_single_provider_no_data(self):
        """Test comparison when only one provider has data"""
        provider1_metrics = self.create_mock_provider_metrics(80.0, 3.0, 1.0)
        result1 = self.create_mock_result(
            datetime.now() - timedelta(days=1), {"provider1": provider1_metrics}
        )

        self.mock_parser.get_results_by_provider.side_effect = [
            [result1],
            [],  # Second provider has no data
        ]

        comparison = self.comparator.compare_providers("provider1", "provider2")

        assert "Insufficient data" in comparison.summary
        assert len(comparison.improvements) == 0
        assert len(comparison.regressions) == 0


class TestTrendAnalysis:
    """Test cases for trend analysis functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_parser = Mock()
        self.comparator = BenchmarkComparator(self.mock_parser)

    def create_trend_data(self, values, start_date=None):
        """Create mock data for trend analysis"""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=len(values))

        results = []
        for i, value in enumerate(values):
            timestamp = start_date + timedelta(days=i)
            provider_metrics = ProviderMetrics(
                provider_name="test_provider",
                overall_success_rate=value,
                avg_execution_time=2.0,
                avg_creation_time=1.0,
                total_scenarios=3,
            )

            result = BenchmarkResult(
                timestamp=timestamp,
                duration_seconds=300.0,
                providers_tested=["test_provider"],
                test_scenarios=3,
                provider_results={"test_provider": provider_metrics},
            )
            results.append(result)

        return results

    def test_analyze_improving_trend(self):
        """Test trend analysis with improving performance"""
        # Success rates improving over time
        success_rates = [60.0, 70.0, 80.0, 85.0, 90.0]
        results = self.create_trend_data(success_rates)

        self.mock_parser.get_results_by_provider.return_value = results

        trend = self.comparator.analyze_time_trends(
            "test_provider", days=5, metric="success_rate"
        )

        assert trend.metric_name == "success_rate"
        assert trend.provider == "test_provider"
        assert trend.trend_direction == "improving"
        assert trend.trend_strength > 0.5  # Strong positive correlation
        assert len(trend.data_points) == 5

        stats = trend.statistical_summary
        assert stats["mean"] == 77.0  # Average of success rates
        assert stats["min"] == 60.0
        assert stats["max"] == 90.0

    def test_analyze_declining_trend(self):
        """Test trend analysis with declining performance"""
        # Success rates declining over time
        success_rates = [90.0, 85.0, 75.0, 65.0, 55.0]
        results = self.create_trend_data(success_rates)

        self.mock_parser.get_results_by_provider.return_value = results

        trend = self.comparator.analyze_time_trends(
            "test_provider", days=5, metric="success_rate"
        )

        assert trend.trend_direction == "declining"
        assert trend.trend_strength > 0.5  # Strong negative correlation

    def test_analyze_stable_trend(self):
        """Test trend analysis with stable performance"""
        # Success rates staying relatively stable
        success_rates = [80.0, 82.0, 78.0, 81.0, 79.0]
        results = self.create_trend_data(success_rates)

        self.mock_parser.get_results_by_provider.return_value = results

        trend = self.comparator.analyze_time_trends(
            "test_provider", days=5, metric="success_rate"
        )

        assert trend.trend_direction == "stable"
        assert trend.trend_strength < 0.3  # Low correlation

    def test_analyze_trend_insufficient_data(self):
        """Test trend analysis with insufficient data"""
        # Only one data point
        results = self.create_trend_data([80.0])

        self.mock_parser.get_results_by_provider.return_value = results

        trend = self.comparator.analyze_time_trends(
            "test_provider", days=5, metric="success_rate"
        )

        assert trend.trend_direction == "insufficient_data"
        assert trend.trend_strength == 0.0

    def test_analyze_trend_all_providers(self):
        """Test trend analysis across all providers"""
        # Create data for multiple providers
        provider1_metrics = ProviderMetrics(
            provider_name="provider1",
            overall_success_rate=80.0,
            avg_execution_time=2.0,
            avg_creation_time=1.0,
            total_scenarios=3,
        )

        provider2_metrics = ProviderMetrics(
            provider_name="provider2",
            overall_success_rate=90.0,
            avg_execution_time=3.0,
            avg_creation_time=1.5,
            total_scenarios=3,
        )

        result = BenchmarkResult(
            timestamp=datetime.now(),
            duration_seconds=300.0,
            providers_tested=["provider1", "provider2"],
            test_scenarios=3,
            provider_results={
                "provider1": provider1_metrics,
                "provider2": provider2_metrics,
            },
        )

        self.mock_parser.get_results_by_date_range.return_value = [result]

        trend = self.comparator.analyze_time_trends(None, days=5, metric="success_rate")

        assert trend.provider is None
        assert len(trend.data_points) == 1
        assert trend.data_points[0]["value"] == 85.0  # Average of 80 and 90


class TestRegressionDetection:
    """Test cases for performance regression detection"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_parser = Mock()
        self.comparator = BenchmarkComparator(self.mock_parser)

    def create_regression_test_data(
        self, baseline_success, recent_success, provider="test_provider"
    ):
        """Create test data for regression detection"""
        baseline_metrics = ProviderMetrics(
            provider_name=provider,
            overall_success_rate=baseline_success,
            avg_execution_time=2.0,
            avg_creation_time=1.0,
            total_scenarios=3,
        )

        recent_metrics = ProviderMetrics(
            provider_name=provider,
            overall_success_rate=recent_success,
            avg_execution_time=2.0,
            avg_creation_time=1.0,
            total_scenarios=3,
        )

        baseline_result = BenchmarkResult(
            timestamp=datetime.now() - timedelta(days=10),
            duration_seconds=300.0,
            providers_tested=[provider],
            test_scenarios=3,
            provider_results={provider: baseline_metrics},
        )

        recent_result = BenchmarkResult(
            timestamp=datetime.now() - timedelta(days=1),
            duration_seconds=300.0,
            providers_tested=[provider],
            test_scenarios=3,
            provider_results={provider: recent_metrics},
        )

        return [baseline_result], [recent_result]

    def test_detect_success_rate_regression(self):
        """Test detection of success rate regression"""
        baseline_results, recent_results = self.create_regression_test_data(90.0, 70.0)

        self.mock_parser.get_results_by_date_range.side_effect = [
            baseline_results,
            recent_results,
        ]

        regressions = self.comparator.detect_performance_regressions(
            baseline_days=7, comparison_days=7, threshold=0.1
        )

        assert len(regressions) == 1
        regression = regressions[0]

        assert regression.comparison_type == "regression"
        assert "success_rate" in regression.regressions
        assert regression.regressions["success_rate"] == 20.0  # 90 - 70

        provider = regression.detailed_analysis["provider"]
        assert provider == "test_provider"

    def test_detect_no_regression(self):
        """Test when no regression is detected"""
        baseline_results, recent_results = self.create_regression_test_data(80.0, 82.0)

        self.mock_parser.get_results_by_date_range.side_effect = [
            baseline_results,
            recent_results,
        ]

        regressions = self.comparator.detect_performance_regressions(
            baseline_days=7, comparison_days=7, threshold=0.1
        )

        assert len(regressions) == 0

    def test_detect_regression_below_threshold(self):
        """Test regression below threshold is not detected"""
        baseline_results, recent_results = self.create_regression_test_data(80.0, 75.0)

        self.mock_parser.get_results_by_date_range.side_effect = [
            baseline_results,
            recent_results,
        ]

        regressions = self.comparator.detect_performance_regressions(
            baseline_days=7,
            comparison_days=7,
            threshold=0.1,  # 10% threshold
        )

        # 5% regression should not be detected with 10% threshold
        assert len(regressions) == 0


class TestProviderRecommendation:
    """Test cases for provider recommendation functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_parser = Mock()
        self.comparator = BenchmarkComparator(self.mock_parser)

    def create_provider_comparison_data(self):
        """Create data for provider comparison"""
        # Provider 1: High reliability, slow execution
        provider1_metrics = ProviderMetrics(
            provider_name="provider1",
            overall_success_rate=95.0,
            avg_execution_time=5.0,
            avg_creation_time=2.0,
            total_scenarios=3,
        )

        # Provider 2: Medium reliability, fast execution
        provider2_metrics = ProviderMetrics(
            provider_name="provider2",
            overall_success_rate=80.0,
            avg_execution_time=1.0,
            avg_creation_time=0.5,
            total_scenarios=3,
        )

        # Provider 3: Low reliability, medium execution
        provider3_metrics = ProviderMetrics(
            provider_name="provider3",
            overall_success_rate=60.0,
            avg_execution_time=3.0,
            avg_creation_time=1.0,
            total_scenarios=3,
        )

        result = BenchmarkResult(
            timestamp=datetime.now(),
            duration_seconds=300.0,
            providers_tested=["provider1", "provider2", "provider3"],
            test_scenarios=3,
            provider_results={
                "provider1": provider1_metrics,
                "provider2": provider2_metrics,
                "provider3": provider3_metrics,
            },
        )

        return [result]

    def test_recommend_provider_general(self):
        """Test general provider recommendation"""
        results = self.create_provider_comparison_data()
        self.mock_parser.get_results_by_date_range.return_value = results

        recommendation = self.comparator.recommend_provider("general", days=30)

        assert recommendation.recommended_provider in [
            "provider1",
            "provider2",
            "provider3",
        ]
        assert 0 <= recommendation.confidence_score <= 1
        assert len(recommendation.reasoning) > 0
        assert "performance_summary" in recommendation.__dict__

    def test_recommend_provider_reliability(self):
        """Test provider recommendation for reliability use case"""
        results = self.create_provider_comparison_data()
        self.mock_parser.get_results_by_date_range.return_value = results

        recommendation = self.comparator.recommend_provider("reliability", days=30)

        # Should prefer provider1 due to highest success rate
        assert recommendation.recommended_provider == "provider1"
        assert (
            "reliability" in recommendation.reasoning[0].lower()
            or "success" in recommendation.reasoning[0].lower()
        )

    def test_recommend_provider_speed(self):
        """Test provider recommendation for speed use case"""
        results = self.create_provider_comparison_data()
        self.mock_parser.get_results_by_date_range.return_value = results

        recommendation = self.comparator.recommend_provider("speed", days=30)

        # Should prefer provider2 due to fastest execution
        assert recommendation.recommended_provider == "provider2"

    def test_recommend_provider_no_data(self):
        """Test provider recommendation with no data"""
        self.mock_parser.get_results_by_date_range.return_value = []

        recommendation = self.comparator.recommend_provider("general", days=30)

        assert recommendation.recommended_provider == "unknown"
        assert recommendation.confidence_score == 0.0
        assert "No recent benchmark data available" in recommendation.reasoning


if __name__ == "__main__":
    pytest.main([__file__])
