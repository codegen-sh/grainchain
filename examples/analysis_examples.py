#!/usr/bin/env python3
"""
Examples of using the Grainchain benchmark analysis system
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the parent directory to Python path to import grainchain
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.analysis import (
    AnalysisConfig,
    BenchmarkComparator,
    BenchmarkDataParser,
    BenchmarkReporter,
    BenchmarkVisualizer,
)


def example_basic_comparison():
    """Example: Basic provider comparison"""
    print("=" * 60)
    print("EXAMPLE: Basic Provider Comparison")
    print("=" * 60)

    # Initialize the data parser
    parser = BenchmarkDataParser("benchmarks/results")

    # Load all available results
    results = parser.load_all_results()
    print(f"Loaded {len(results)} benchmark results")

    if len(results) == 0:
        print("No benchmark data found. Run some benchmarks first!")
        return

    # Get available providers
    providers = set()
    for result in results:
        providers.update(result.provider_results.keys())

    print(f"Available providers: {', '.join(sorted(providers))}")

    if len(providers) < 2:
        print("Need at least 2 providers for comparison")
        return

    # Compare the first two providers
    provider_list = sorted(list(providers))
    provider1, provider2 = provider_list[0], provider_list[1]

    # Initialize comparator and perform comparison
    comparator = BenchmarkComparator(parser)
    comparison = comparator.compare_providers(provider1, provider2, days=30)

    print("\nComparison Results:")
    print(f"Baseline: {comparison.baseline}")
    print(f"Target: {comparison.target}")
    print(f"Summary: {comparison.summary}")

    if comparison.improvements:
        print(f"\n{provider2} improvements:")
        for metric, value in comparison.improvements.items():
            print(f"  • {metric}: {value:.2f}")

    if comparison.regressions:
        print(f"\n{provider2} regressions:")
        for metric, value in comparison.regressions.items():
            print(f"  • {metric}: {value:.2f}")


def example_trend_analysis():
    """Example: Trend analysis over time"""
    print("\n" + "=" * 60)
    print("EXAMPLE: Trend Analysis")
    print("=" * 60)

    parser = BenchmarkDataParser("benchmarks/results")
    comparator = BenchmarkComparator(parser)

    # Get available providers
    results = parser.load_all_results()
    if not results:
        print("No benchmark data found for trend analysis")
        return

    providers = set()
    for result in results:
        providers.update(result.provider_results.keys())

    if not providers:
        print("No providers found in benchmark data")
        return

    provider = sorted(list(providers))[0]
    print(f"Analyzing trends for provider: {provider}")

    # Analyze success rate trends
    trend = comparator.analyze_time_trends(provider, days=30, metric="success_rate")

    print("\nTrend Analysis Results:")
    print(f"Metric: {trend.metric_name}")
    print(f"Provider: {trend.provider}")
    print(f"Time Period: {trend.time_period}")
    print(f"Trend Direction: {trend.trend_direction}")
    print(f"Trend Strength: {trend.trend_strength:.2f}")
    print(f"Data Points: {len(trend.data_points)}")

    if trend.statistical_summary:
        stats = trend.statistical_summary
        print("\nStatistical Summary:")
        print(f"  Mean: {stats.get('mean', 0):.2f}")
        print(f"  Std Dev: {stats.get('std_dev', 0):.2f}")
        print(f"  Min: {stats.get('min', 0):.2f}")
        print(f"  Max: {stats.get('max', 0):.2f}")


def example_regression_detection():
    """Example: Automatic regression detection"""
    print("\n" + "=" * 60)
    print("EXAMPLE: Regression Detection")
    print("=" * 60)

    parser = BenchmarkDataParser("benchmarks/results")
    comparator = BenchmarkComparator(parser)

    # Detect regressions
    regressions = comparator.detect_performance_regressions(
        baseline_days=7, comparison_days=7, threshold=0.1
    )

    if not regressions:
        print("✅ No performance regressions detected!")
        return

    print(f"❌ Found {len(regressions)} performance regression(s):")

    for i, regression in enumerate(regressions, 1):
        provider = regression.detailed_analysis["provider"]
        print(f"\n{i}. Provider: {provider}")

        for metric, value in regression.regressions.items():
            if metric == "success_rate":
                print(f"   • Success rate decreased by {value:.1f}%")
            elif "time" in metric:
                print(
                    f"   • {metric.replace('_', ' ').title()} increased by {value:.2f}s"
                )


def example_provider_recommendation():
    """Example: Provider recommendation"""
    print("\n" + "=" * 60)
    print("EXAMPLE: Provider Recommendation")
    print("=" * 60)

    parser = BenchmarkDataParser("benchmarks/results")
    comparator = BenchmarkComparator(parser)

    # Get recommendations for different use cases
    use_cases = ["general", "speed", "reliability"]

    for use_case in use_cases:
        print(f"\n--- Recommendation for {use_case.upper()} use case ---")

        recommendation = comparator.recommend_provider(use_case, days=30)

        print(f"Recommended Provider: {recommendation.recommended_provider}")
        print(f"Confidence Score: {recommendation.confidence_score:.1%}")

        if recommendation.reasoning:
            print("Reasons:")
            for reason in recommendation.reasoning:
                print(f"  • {reason}")

        if recommendation.performance_summary:
            summary = recommendation.performance_summary
            print("Performance Summary:")
            print(f"  • Success Rate: {summary.get('success_rate', 0):.1f}%")
            print(
                f"  • Avg Execution Time: {summary.get('avg_execution_time', 0):.2f}s"
            )
            print(f"  • Avg Creation Time: {summary.get('avg_creation_time', 0):.2f}s")


def example_visualization():
    """Example: Creating visualizations"""
    print("\n" + "=" * 60)
    print("EXAMPLE: Visualization Generation")
    print("=" * 60)

    parser = BenchmarkDataParser("benchmarks/results")
    results = parser.load_all_results()

    if not results:
        print("No benchmark data found for visualization")
        return

    # Initialize visualizer
    visualizer = BenchmarkVisualizer("examples/charts")

    print("Generating visualizations...")

    # Create performance dashboard
    dashboard_path = visualizer.create_performance_dashboard(results)
    print(f"✅ Performance dashboard saved to: {dashboard_path}")

    # Create interactive dashboard (if plotly is available)
    try:
        interactive_path = visualizer.create_interactive_dashboard(results)
        if interactive_path:
            print(f"✅ Interactive dashboard saved to: {interactive_path}")
    except Exception as e:
        print(f"⚠️  Interactive dashboard not available: {e}")

    # Export chart data
    data_path = visualizer.export_chart_data(results)
    print(f"✅ Chart data exported to: {data_path}")

    # If we have multiple providers, create a comparison chart
    providers = set()
    for result in results:
        providers.update(result.provider_results.keys())

    if len(providers) >= 2:
        provider_list = sorted(list(providers))
        comparator = BenchmarkComparator(parser)
        comparison = comparator.compare_providers(provider_list[0], provider_list[1])

        chart_path = visualizer.create_provider_comparison_chart(comparison)
        print(f"✅ Provider comparison chart saved to: {chart_path}")


def example_report_generation():
    """Example: Generating comprehensive reports"""
    print("\n" + "=" * 60)
    print("EXAMPLE: Report Generation")
    print("=" * 60)

    parser = BenchmarkDataParser("benchmarks/results")
    results = parser.load_all_results()

    if not results:
        print("No benchmark data found for report generation")
        return

    # Initialize reporter
    reporter = BenchmarkReporter("examples/reports")

    print("Generating reports...")

    # Generate markdown report
    md_report = reporter.generate_comprehensive_report(
        results, format="markdown", include_charts=False
    )
    print(f"✅ Markdown report saved to: {md_report}")

    # Generate HTML report with charts
    html_report = reporter.generate_comprehensive_report(
        results, format="html", include_charts=True
    )
    print(f"✅ HTML report saved to: {html_report}")

    # Generate comparison report if we have multiple providers
    providers = set()
    for result in results:
        providers.update(result.provider_results.keys())

    if len(providers) >= 2:
        provider_list = sorted(list(providers))
        comparator = BenchmarkComparator(parser)
        comparison = comparator.compare_providers(provider_list[0], provider_list[1])

        comparison_report = reporter.generate_comparison_report(
            comparison, format="html"
        )
        print(f"✅ Comparison report saved to: {comparison_report}")


def example_configuration():
    """Example: Working with configuration"""
    print("\n" + "=" * 60)
    print("EXAMPLE: Configuration Management")
    print("=" * 60)

    # Load default configuration
    config = AnalysisConfig()

    print("Current Configuration:")
    print(f"  Time Range Days: {config.time_range_days}")
    print(f"  Comparison Threshold: {config.comparison_threshold}")
    print(f"  Chart Format: {config.preferred_chart_format}")
    print(f"  Report Format: {config.preferred_report_format}")

    # Modify configuration
    print("\nModifying configuration...")
    config.set("default_settings.time_range_days", 60)
    config.set("default_settings.comparison_threshold", 0.05)

    print(f"  New Time Range Days: {config.time_range_days}")
    print(f"  New Comparison Threshold: {config.comparison_threshold}")

    # Get provider display names
    print("\nProvider Display Names:")
    for provider in ["local", "e2b", "modal", "daytona", "morph"]:
        display_name = config.get_provider_display_name(provider)
        color = config.get_provider_color(provider)
        print(f"  {provider} -> {display_name} (color: {color})")

    # Save configuration to a custom file
    custom_config_path = Path("examples/custom_analysis_config.json")
    config.save(custom_config_path)
    print(f"\n✅ Custom configuration saved to: {custom_config_path}")


def example_data_filtering():
    """Example: Advanced data filtering and analysis"""
    print("\n" + "=" * 60)
    print("EXAMPLE: Advanced Data Filtering")
    print("=" * 60)

    parser = BenchmarkDataParser("benchmarks/results")

    # Get all results
    all_results = parser.load_all_results()
    print(f"Total benchmark results: {len(all_results)}")

    if not all_results:
        print("No benchmark data found")
        return

    # Filter by date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    recent_results = parser.get_results_by_date_range(start_date, end_date)
    print(f"Results from last 7 days: {len(recent_results)}")

    # Filter by provider
    providers = set()
    for result in all_results:
        providers.update(result.provider_results.keys())

    for provider in sorted(providers):
        provider_results = parser.get_results_by_provider(provider)
        print(f"Results for {provider}: {len(provider_results)}")

    # Get latest result
    latest_result = parser.get_latest_result()
    if latest_result:
        print("\nLatest benchmark:")
        print(f"  Timestamp: {latest_result.timestamp}")
        print(f"  Duration: {latest_result.duration_seconds:.1f}s")
        print(f"  Providers: {', '.join(latest_result.providers_tested)}")
        print(f"  Test Scenarios: {latest_result.test_scenarios}")


def main():
    """Run all examples"""
    print("Grainchain Benchmark Analysis Examples")
    print("=" * 60)

    # Create output directories
    Path("examples/charts").mkdir(parents=True, exist_ok=True)
    Path("examples/reports").mkdir(parents=True, exist_ok=True)

    try:
        # Run all examples
        example_basic_comparison()
        example_trend_analysis()
        example_regression_detection()
        example_provider_recommendation()
        example_visualization()
        example_report_generation()
        example_configuration()
        example_data_filtering()

        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print(
            "Check the examples/charts and examples/reports directories for generated files."
        )

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Make sure you have benchmark data in benchmarks/results/")
        print("Run 'grainchain benchmark' to generate some test data first.")


if __name__ == "__main__":
    main()
