"""
Benchmark comparison engine for analyzing performance differences
"""

import statistics
from datetime import datetime, timedelta
from typing import Any, Optional

from .data_parser import BenchmarkDataParser
from .models import (
    BenchmarkResult,
    ComparisonResult,
    ProviderMetrics,
    ProviderRecommendation,
    TrendAnalysis,
)


class BenchmarkComparator:
    """Engine for comparing benchmark results across different dimensions"""

    def __init__(self, data_parser: BenchmarkDataParser):
        self.data_parser = data_parser

    def compare_providers(
        self, provider1: str, provider2: str, time_range_days: str | Noneint] = None
    ) -> ComparisonResult:
        """Compare two providers across all available metrics"""

        # Get data for both providers
        if time_range_days:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=time_range_days)
            results1 = [
                r
                for r in self.data_parser.get_results_by_provider(provider1)
                if start_date <= r.timestamp <= end_date
            ]
            results2 = [
                r
                for r in self.data_parser.get_results_by_provider(provider2)
                if start_date <= r.timestamp <= end_date
            ]
        else:
            results1 = self.data_parser.get_results_by_provider(provider1)
            results2 = self.data_parser.get_results_by_provider(provider2)

        if not results1 or not results2:
            return ComparisonResult(
                comparison_type="provider",
                baseline=provider1,
                target=provider2,
                metrics_compared=[],
                summary=f"Insufficient data for comparison. {provider1}: {len(results1)} results, {provider2}: {len(results2)} results",
            )

        # Aggregate metrics for each provider
        metrics1 = self._aggregate_provider_metrics(results1, provider1)
        metrics2 = self._aggregate_provider_metrics(results2, provider2)

        # Compare metrics
        improvements = {}
        regressions = {}
        metrics_compared = ["success_rate", "avg_execution_time", "avg_creation_time"]

        # Success rate comparison (higher is better)
        if metrics2["success_rate"] > metrics1["success_rate"]:
            improvements["success_rate"] = (
                metrics2["success_rate"] - metrics1["success_rate"]
            )
        elif metrics2["success_rate"] < metrics1["success_rate"]:
            regressions["success_rate"] = (
                metrics1["success_rate"] - metrics2["success_rate"]
            )

        # Execution time comparison (lower is better)
        if metrics2["avg_execution_time"] < metrics1["avg_execution_time"]:
            improvements["avg_execution_time"] = (
                metrics1["avg_execution_time"] - metrics2["avg_execution_time"]
            )
        elif metrics2["avg_execution_time"] > metrics1["avg_execution_time"]:
            regressions["avg_execution_time"] = (
                metrics2["avg_execution_time"] - metrics1["avg_execution_time"]
            )

        # Creation time comparison (lower is better)
        if metrics2["avg_creation_time"] < metrics1["avg_creation_time"]:
            improvements["avg_creation_time"] = (
                metrics1["avg_creation_time"] - metrics2["avg_creation_time"]
            )
        elif metrics2["avg_creation_time"] > metrics1["avg_creation_time"]:
            regressions["avg_creation_time"] = (
                metrics2["avg_creation_time"] - metrics1["avg_creation_time"]
            )

        # Generate summary
        summary = self._generate_provider_comparison_summary(
            provider1, provider2, metrics1, metrics2, improvements, regressions
        )

        return ComparisonResult(
            comparison_type="provider",
            baseline=provider1,
            target=provider2,
            metrics_compared=metrics_compared,
            improvements=improvements,
            regressions=regressions,
            summary=summary,
            detailed_analysis={
                "provider1_metrics": metrics1,
                "provider2_metrics": metrics2,
                "data_points": {"provider1": len(results1), "provider2": len(results2)},
            },
        )

    def analyze_time_trends(
        self,
        provider: str | Nonestr] = None,
        days: int = 30,
        metric: str = "success_rate",
    ) -> TrendAnalysis:
        """Analyze trends over time for a specific metric"""

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        if provider:
            results = [
                r
                for r in self.data_parser.get_results_by_provider(provider)
                if start_date <= r.timestamp <= end_date
            ]
        else:
            results = self.data_parser.get_results_by_date_range(start_date, end_date)

        if len(results) < 2:
            return TrendAnalysis(
                metric_name=metric,
                provider=provider,
                time_period=f"{days} days",
                trend_direction="insufficient_data",
                trend_strength=0.0,
                data_points=[],
                statistical_summary={},
            )

        # Extract metric values over time
        data_points = []
        metric_values = []

        for result in results:
            if provider and provider in result.provider_results:
                provider_metrics = result.provider_results[provider]
                value = self._extract_metric_value(provider_metrics, metric)
                if value is not None:
                    data_points.append(
                        {
                            "timestamp": result.timestamp,
                            "value": value,
                            "provider": provider,
                        }
                    )
                    metric_values.append(value)
            elif not provider:
                # Aggregate across all providers
                all_values = []
                for prov_metrics in result.provider_results.values():
                    value = self._extract_metric_value(prov_metrics, metric)
                    if value is not None:
                        all_values.append(value)

                if all_values:
                    avg_value = statistics.mean(all_values)
                    data_points.append(
                        {
                            "timestamp": result.timestamp,
                            "value": avg_value,
                            "provider": "all",
                        }
                    )
                    metric_values.append(avg_value)

        if len(metric_values) < 2:
            return TrendAnalysis(
                metric_name=metric,
                provider=provider,
                time_period=f"{days} days",
                trend_direction="insufficient_data",
                trend_strength=0.0,
                data_points=data_points,
                statistical_summary={},
            )

        # Calculate trend
        trend_direction, trend_strength = self._calculate_trend(metric_values)

        # Statistical summary
        statistical_summary = {
            "mean": statistics.mean(metric_values),
            "median": statistics.median(metric_values),
            "std_dev": statistics.stdev(metric_values) if len(metric_values) > 1 else 0,
            "min": min(metric_values),
            "max": max(metric_values),
            "data_points": len(metric_values),
        }

        return TrendAnalysis(
            metric_name=metric,
            provider=provider,
            time_period=f"{days} days",
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            data_points=data_points,
            statistical_summary=statistical_summary,
        )

    def detect_performance_regressions(
        self, baseline_days: int = 7, comparison_days: int = 7, threshold: float = 0.1
    ) -> list[ComparisonResult]:
        """Detect performance regressions by comparing recent vs baseline performance"""

        end_date = datetime.now()
        recent_start = end_date - timedelta(days=comparison_days)
        baseline_end = recent_start
        baseline_start = baseline_end - timedelta(days=baseline_days)

        baseline_results = self.data_parser.get_results_by_date_range(
            baseline_start, baseline_end
        )
        recent_results = self.data_parser.get_results_by_date_range(
            recent_start, end_date
        )

        regressions = []

        # Get all providers that appear in both periods
        baseline_providers = set()
        recent_providers = set()

        for result in baseline_results:
            baseline_providers.update(result.provider_results.keys())

        for result in recent_results:
            recent_providers.update(result.provider_results.keys())

        common_providers = baseline_providers.intersection(recent_providers)

        for provider in common_providers:
            baseline_metrics = self._aggregate_provider_metrics(
                [r for r in baseline_results if provider in r.provider_results],
                provider,
            )
            recent_metrics = self._aggregate_provider_metrics(
                [r for r in recent_results if provider in r.provider_results], provider
            )

            # Check for regressions
            regression_detected = False
            regressions_found = {}

            # Success rate regression (decrease > threshold)
            if (
                baseline_metrics["success_rate"] - recent_metrics["success_rate"]
                > threshold
            ):
                regressions_found["success_rate"] = (
                    baseline_metrics["success_rate"] - recent_metrics["success_rate"]
                )
                regression_detected = True

            # Execution time regression (increase > threshold)
            if (
                recent_metrics["avg_execution_time"]
                - baseline_metrics["avg_execution_time"]
                > threshold
            ):
                regressions_found["avg_execution_time"] = (
                    recent_metrics["avg_execution_time"]
                    - baseline_metrics["avg_execution_time"]
                )
                regression_detected = True

            if regression_detected:
                regressions.append(
                    ComparisonResult(
                        comparison_type="regression",
                        baseline=baseline_start,
                        target=recent_start,
                        metrics_compared=list(regressions_found.keys()),
                        regressions=regressions_found,
                        summary=f"Performance regression detected for {provider}",
                        detailed_analysis={
                            "provider": provider,
                            "baseline_metrics": baseline_metrics,
                            "recent_metrics": recent_metrics,
                            "threshold": threshold,
                        },
                    )
                )

        return regressions

    def recommend_provider(
        self, use_case: str = "general", time_range_days: int = 30
    ) -> ProviderRecommendation:
        """Recommend the best provider based on recent performance data"""

        end_date = datetime.now()
        start_date = end_date - timedelta(days=time_range_days)
        results = self.data_parser.get_results_by_date_range(start_date, end_date)

        if not results:
            return ProviderRecommendation(
                recommended_provider="unknown",
                confidence_score=0.0,
                reasoning=["No recent benchmark data available"],
                use_case_specific={use_case: "No data available"},
            )

        # Aggregate metrics for all providers
        provider_metrics = {}
        for result in results:
            for provider, metrics in result.provider_results.items():
                if provider not in provider_metrics:
                    provider_metrics[provider] = []
                provider_metrics[provider].append(metrics)

        # Calculate scores for each provider
        provider_scores = {}
        for provider, metrics_list in provider_metrics.items():
            aggregated = self._aggregate_provider_metrics_list(metrics_list)
            score = self._calculate_provider_score(aggregated, use_case)
            provider_scores[provider] = {"score": score, "metrics": aggregated}

        if not provider_scores:
            return ProviderRecommendation(
                recommended_provider="unknown",
                confidence_score=0.0,
                reasoning=["No provider data available"],
            )

        # Find best provider
        best_provider = max(
            provider_scores.keys(), key=lambda p: provider_scores[p]["score"]
        )
        best_score = provider_scores[best_provider]["score"]
        best_metrics = provider_scores[best_provider]["metrics"]

        # Generate reasoning
        reasoning = self._generate_recommendation_reasoning(
            best_provider, best_metrics, provider_scores, use_case
        )

        # Calculate confidence based on score difference and data quality
        confidence = min(best_score / 100.0, 1.0)  # Normalize to 0-1

        return ProviderRecommendation(
            recommended_provider=best_provider,
            confidence_score=confidence,
            reasoning=reasoning,
            use_case_specific={use_case: f"Best choice for {use_case} workloads"},
            performance_summary=best_metrics,
        )

    def _aggregate_provider_metrics(
        self, results: list[BenchmarkResult], provider: str
    ) -> dict[str, float]:
        """Aggregate metrics for a provider across multiple results"""
        success_rates = []
        execution_times = []
        creation_times = []

        for result in results:
            if provider in result.provider_results:
                metrics = result.provider_results[provider]
                success_rates.append(metrics.overall_success_rate)
                execution_times.append(metrics.avg_execution_time)
                creation_times.append(metrics.avg_creation_time)

        return {
            "success_rate": statistics.mean(success_rates) if success_rates else 0.0,
            "avg_execution_time": statistics.mean(execution_times)
            if execution_times
            else 0.0,
            "avg_creation_time": statistics.mean(creation_times)
            if creation_times
            else 0.0,
            "data_points": len(success_rates),
        }

    def _aggregate_provider_metrics_list(
        self, metrics_list: list[ProviderMetrics]
    ) -> dict[str, float]:
        """Aggregate a list of ProviderMetrics"""
        success_rates = [m.overall_success_rate for m in metrics_list]
        execution_times = [m.avg_execution_time for m in metrics_list]
        creation_times = [m.avg_creation_time for m in metrics_list]

        return {
            "success_rate": statistics.mean(success_rates) if success_rates else 0.0,
            "avg_execution_time": statistics.mean(execution_times)
            if execution_times
            else 0.0,
            "avg_creation_time": statistics.mean(creation_times)
            if creation_times
            else 0.0,
            "data_points": len(success_rates),
        }

    def _extract_metric_value(
        self, provider_metrics: ProviderMetrics, metric: str
    ) -> str | Nonefloat]:
        """Extract a specific metric value from provider metrics"""
        if metric == "success_rate":
            return provider_metrics.overall_success_rate
        elif metric == "avg_execution_time":
            return provider_metrics.avg_execution_time
        elif metric == "avg_creation_time":
            return provider_metrics.avg_creation_time
        else:
            return None

    def _calculate_trend(self, values: list[float]) -> tuple[str, float]:
        """Calculate trend direction and strength from a series of values"""
        if len(values) < 2:
            return "insufficient_data", 0.0

        # Simple linear trend calculation
        n = len(values)
        x = list(range(n))

        # Calculate correlation coefficient as trend strength
        try:
            correlation = statistics.correlation(x, values)

            if correlation > 0.3:
                return "improving", abs(correlation)
            elif correlation < -0.3:
                return "declining", abs(correlation)
            else:
                return "stable", abs(correlation)
        except statistics.StatisticsError:
            return "stable", 0.0

    def _calculate_provider_score(
        self, metrics: dict[str, float], use_case: str
    ) -> float:
        """Calculate a composite score for a provider based on use case"""
        success_rate = metrics.get("success_rate", 0.0)
        execution_time = metrics.get("avg_execution_time", float("inf"))
        creation_time = metrics.get("avg_creation_time", float("inf"))

        # Base score from success rate (0-50 points)
        score = success_rate * 0.5

        # Execution time score (0-30 points, lower is better)
        if execution_time > 0:
            exec_score = max(0, 30 - (execution_time * 10))
            score += exec_score

        # Creation time score (0-20 points, lower is better)
        if creation_time > 0:
            creation_score = max(0, 20 - (creation_time * 5))
            score += creation_score

        # Use case specific adjustments
        if use_case == "speed":
            # Prioritize execution time
            score = score * 0.7 + (exec_score * 0.3)
        elif use_case == "reliability":
            # Prioritize success rate
            score = (success_rate * 0.7) + (score * 0.3)

        return score

    def _generate_provider_comparison_summary(
        self,
        provider1: str,
        provider2: str,
        metrics1: dict[str, float],
        metrics2: dict[str, float],
        improvements: dict[str, float],
        regressions: dict[str, float],
    ) -> str:
        """Generate a human-readable summary of provider comparison"""

        summary_parts = [f"Comparison between {provider1} and {provider2}:"]

        if improvements:
            summary_parts.append(f"\n{provider2} improvements:")
            for metric, value in improvements.items():
                if metric == "success_rate":
                    summary_parts.append(f"  • Success rate: +{value:.1f}%")
                elif "time" in metric:
                    summary_parts.append(
                        f"  • {metric.replace('_', ' ').title()}: -{value:.2f}s faster"
                    )

        if regressions:
            summary_parts.append(f"\n{provider2} regressions:")
            for metric, value in regressions.items():
                if metric == "success_rate":
                    summary_parts.append(f"  • Success rate: -{value:.1f}%")
                elif "time" in metric:
                    summary_parts.append(
                        f"  • {metric.replace('_', ' ').title()}: +{value:.2f}s slower"
                    )

        if not improvements and not regressions:
            summary_parts.append("\nPerformance is similar between both providers.")

        return "".join(summary_parts)

    def _generate_recommendation_reasoning(
        self,
        best_provider: str,
        best_metrics: dict[str, float],
        all_scores: dict[str, dict[str, Any]],
        use_case: str,
    ) -> list[str]:
        """Generate reasoning for provider recommendation"""
        reasoning = []

        reasoning.append(
            f"Based on {best_metrics.get('data_points', 0)} recent benchmark runs"
        )

        success_rate = best_metrics.get("success_rate", 0)
        if success_rate > 90:
            reasoning.append(
                f"Excellent reliability with {success_rate:.1f}% success rate"
            )
        elif success_rate > 75:
            reasoning.append(f"Good reliability with {success_rate:.1f}% success rate")
        else:
            reasoning.append(
                f"Moderate reliability with {success_rate:.1f}% success rate"
            )

        exec_time = best_metrics.get("avg_execution_time", 0)
        if exec_time < 1.0:
            reasoning.append(f"Fast execution time ({exec_time:.2f}s average)")
        elif exec_time < 5.0:
            reasoning.append(f"Reasonable execution time ({exec_time:.2f}s average)")

        # Compare with other providers
        other_providers = [p for p in all_scores.keys() if p != best_provider]
        if other_providers:
            best_score = all_scores[best_provider]["score"]
            other_scores = [all_scores[p]["score"] for p in other_providers]
            avg_other_score = statistics.mean(other_scores)

            if best_score > avg_other_score * 1.2:
                reasoning.append("Significantly outperforms other providers")
            elif best_score > avg_other_score * 1.1:
                reasoning.append("Performs better than other providers")

        return reasoning
