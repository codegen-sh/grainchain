"""
CLI commands for benchmark analysis and comparison
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import click

from benchmarks.analysis import (
    BenchmarkComparator,
    BenchmarkDataParser,
    BenchmarkReporter,
    BenchmarkVisualizer,
)


@click.group()
def analysis():
    """Benchmark analysis and comparison tools"""
    pass


@analysis.command()
@click.option('--provider1', required=True, help='First provider to compare')
@click.option('--provider2', required=True, help='Second provider to compare')
@click.option('--days', default=30, help='Number of days to look back for data')
@click.option('--output', help='Output file path for comparison report')
@click.option('--chart', is_flag=True, help='Generate comparison chart')
@click.option('--chart-type', default='bar', type=click.Choice(['bar', 'radar']), 
              help='Type of chart to generate')
def compare(provider1: str, provider2: str, days: int, output: str | None, 
           chart: bool, chart_type: str):
    """Compare performance between two providers"""
    
    click.echo(f"🔍 Comparing {provider1} vs {provider2} (last {days} days)")
    
    try:
        # Initialize components
        parser = BenchmarkDataParser()
        comparator = BenchmarkComparator(parser)
        
        # Perform comparison
        comparison_result = comparator.compare_providers(provider1, provider2, days)
        
        # Display results
        click.echo("\n" + "=" * 60)
        click.echo("COMPARISON RESULTS")
        click.echo("=" * 60)
        click.echo(comparison_result.summary)
        
        if comparison_result.improvements:
            click.echo(f"\n✅ {provider2} improvements:")
            for metric, value in comparison_result.improvements.items():
                if metric == "success_rate":
                    click.echo(f"  • Success rate: +{value:.1f}%")
                elif "time" in metric:
                    click.echo(
                        f"  • {metric.replace('_', ' ').title()}: -{value:.2f}s faster"
                    )
        
        if comparison_result.regressions:
            click.echo(f"\n❌ {provider2} regressions:")
            for metric, value in comparison_result.regressions.items():
                if metric == "success_rate":
                    click.echo(f"  • Success rate: -{value:.1f}%")
                elif "time" in metric:
                    click.echo(
                        f"  • {metric.replace('_', ' ').title()}: +{value:.2f}s slower"
                    )
        
        # Generate chart if requested
        if chart:
            visualizer = BenchmarkVisualizer()
            chart_path = visualizer.create_provider_comparison_chart(
                comparison_result, chart_type
            )
            click.echo(f"\n📊 Chart saved to: {chart_path}")
        
        # Save detailed report if output specified
        if output:
            reporter = BenchmarkReporter()
            report_path = reporter.generate_comparison_report(
                comparison_result, Path(output)
            )
            click.echo(f"📄 Detailed report saved to: {report_path}")
    
    except Exception as e:
        click.echo(f"❌ Error during comparison: {e}", err=True)
        raise click.Abort() from e


@analysis.command()
@click.option("--provider", help="Provider to analyze (all providers if not specified)")
@click.option("--days", default=30, help="Number of days to analyze")
@click.option(
    "--metric",
    default="success_rate",
    type=click.Choice(["success_rate", "avg_execution_time", "avg_creation_time"]),
    help="Metric to analyze for trends",
)
@click.option("--output", help="Output file path for trend chart")
@click.option("--interactive", is_flag=True, help="Generate interactive HTML chart")
def trends(
    provider: Optional[str],
    days: int,
    metric: str,
    output: Optional[str],
    interactive: bool,
):
    """Analyze performance trends over time"""
    
    provider_text = provider if provider else "all providers"
    click.echo(f"📈 Analyzing {metric} trends for {provider_text} (last {days} days)")
    
    try:
        # Initialize components
        parser = BenchmarkDataParser()
        comparator = BenchmarkComparator(parser)
        
        # Perform trend analysis
        trend_analysis = comparator.analyze_time_trends(provider, days, metric)
        
        # Display results
        click.echo("\n" + "=" * 60)
        click.echo("TREND ANALYSIS RESULTS")
        click.echo("=" * 60)
        
        click.echo(f"Metric: {trend_analysis.metric_name}")
        click.echo(f"Provider: {trend_analysis.provider or 'All'}")
        click.echo(f"Time Period: {trend_analysis.time_period}")
        click.echo(f"Trend Direction: {trend_analysis.trend_direction}")
        click.echo(f"Trend Strength: {trend_analysis.trend_strength:.2f}")
        
        if trend_analysis.statistical_summary:
            stats = trend_analysis.statistical_summary
            click.echo("\nStatistical Summary:")
            click.echo(f"  • Mean: {stats.get('mean', 0):.2f}")
            click.echo(f"  • Median: {stats.get('median', 0):.2f}")
            click.echo(f"  • Std Dev: {stats.get('std_dev', 0):.2f}")
            click.echo(f"  • Min: {stats.get('min', 0):.2f}")
            click.echo(f"  • Max: {stats.get('max', 0):.2f}")
            click.echo(f"  • Data Points: {stats.get('data_points', 0)}")
        
        # Generate chart
        visualizer = BenchmarkVisualizer()
        
        if interactive:
            # Get all results for interactive dashboard
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            results = parser.get_results_by_date_range(start_date, end_date)
            
            chart_path = visualizer.create_interactive_dashboard(
                results, Path(output) if output else None
            )
            if chart_path:
                click.echo(f"📊 Interactive dashboard saved to: {chart_path}")
        else:
            chart_path = visualizer.create_trend_chart(
                trend_analysis, Path(output) if output else None
            )
            click.echo(f"📊 Trend chart saved to: {chart_path}")
    
    except Exception as e:
        click.echo(f"❌ Error during trend analysis: {e}", err=True)
        raise click.Abort() from e


@analysis.command()
@click.option(
    "--format",
    "output_format",
    default="html",
    type=click.Choice(["html", "markdown", "pdf"]),
    help="Report format",
)
@click.option("--output", help="Output file path")
@click.option("--days", default=30, help="Number of days to include in report")
@click.option("--include-charts", is_flag=True, help="Include charts in report")
def report(output_format: str, output: Optional[str], days: int, include_charts: bool):
    """Generate comprehensive benchmark analysis report"""
    
    click.echo(f"📋 Generating {output_format.upper()} report (last {days} days)")
    
    try:
        # Initialize components
        parser = BenchmarkDataParser()
        reporter = BenchmarkReporter()
        
        # Get recent results
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        results = parser.get_results_by_date_range(start_date, end_date)
        
        if not results:
            click.echo("❌ No benchmark data found for the specified time period")
            raise click.Abort() from e
        
        # Generate report
        output_path = Path(output) if output else None
        report_path = reporter.generate_comprehensive_report(
            results, output_format, output_path, include_charts
        )
        
        click.echo("✅ Report generated successfully!")
        click.echo(f"📄 Report saved to: {report_path}")
        
        # Display summary
        click.echo("\nReport Summary:")
        click.echo(
            f"  • Time period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        )
        click.echo(f"  • Benchmark runs: {len(results)}")
        
        providers = set()
        for result in results:
            providers.update(result.provider_results.keys())
        click.echo(f"  • Providers analyzed: {', '.join(sorted(providers))}")
    
    except Exception as e:
        click.echo(f"❌ Error generating report: {e}", err=True)
        raise click.Abort() from e


@analysis.command()
@click.option(
    "--baseline-days",
    default=7,
    help="Days to use for baseline period",
)
@click.option(
    "--comparison-days",
    default=7,
    help="Days to use for comparison period",
)
@click.option(
    "--threshold",
    default=0.1,
    help="Regression threshold (0.1 = 10%)",
)
def regressions(baseline_days: int, comparison_days: int, threshold: float):
    """Detect performance regressions"""
    
    click.echo(
        f"🔍 Detecting regressions (baseline: {baseline_days}d, comparison: {comparison_days}d, threshold: {threshold*100:.1f}%)"
    )
    
    try:
        # Initialize components
        parser = BenchmarkDataParser()
        comparator = BenchmarkComparator(parser)
        
        # Detect regressions
        regressions = comparator.detect_performance_regressions(
            baseline_days, comparison_days, threshold
        )
        
        if not regressions:
            click.echo("✅ No performance regressions detected!")
            return
        
        # Display results
        click.echo(f"\n❌ Found {len(regressions)} performance regression(s):")
        click.echo("=" * 60)
        
        for i, regression in enumerate(regressions, 1):
            provider = regression.detailed_analysis["provider"]
            click.echo(f"\n{i}. Provider: {provider}")
            
            for metric, value in regression.regressions.items():
                if metric == "success_rate":
                    click.echo(f"   • Success rate decreased by {value:.1f}%")
                elif "time" in metric:
                    click.echo(
                        f"   • {metric.replace('_', ' ').title()} increased by {value:.2f}s"
                    )
            
            baseline_metrics = regression.detailed_analysis["baseline_metrics"]
            recent_metrics = regression.detailed_analysis["recent_metrics"]
            
            click.echo(
                f"   • Baseline success rate: {baseline_metrics['success_rate']:.1f}%"
            )
            click.echo(
                f"   • Recent success rate: {recent_metrics['success_rate']:.1f}%"
            )
    
    except Exception as e:
        click.echo(f"❌ Error detecting regressions: {e}", err=True)
        raise click.Abort() from e


@analysis.command()
@click.option(
    "--use-case",
    default="general",
    type=click.Choice(["general", "speed", "reliability"]),
    help="Use case for recommendation",
)
@click.option("--days", default=30, help="Number of days to analyze")
def recommend(use_case: str, days: int):
    """Get provider recommendation based on performance data"""
    
    click.echo(f"🎯 Analyzing providers for {use_case} use case (last {days} days)")
    
    try:
        # Initialize components
        parser = BenchmarkDataParser()
        comparator = BenchmarkComparator(parser)
        
        # Get recommendation
        recommendation = comparator.recommend_provider(use_case, days)
        
        # Display results
        click.echo("\n" + "=" * 60)
        click.echo("PROVIDER RECOMMENDATION")
        click.echo("=" * 60)
        
        click.echo(f"Recommended Provider: {recommendation.recommended_provider}")
        click.echo(f"Confidence Score: {recommendation.confidence_score:.1%}")
        
        if recommendation.reasoning:
            click.echo("\nReasons:")
            for reason in recommendation.reasoning:
                click.echo(f"  • {reason}")
        
        if recommendation.performance_summary:
            click.echo("\nPerformance Summary:")
            summary = recommendation.performance_summary
            click.echo(f"  • Success Rate: {summary.get('success_rate', 0):.1f}%")
            click.echo(
                f"  • Avg Execution Time: {summary.get('avg_execution_time', 0):.2f}s"
            )
            click.echo(
                f"  • Avg Creation Time: {summary.get('avg_creation_time', 0):.2f}s"
            )
            click.echo(f"  • Data Points: {summary.get('data_points', 0)}")
    
    except Exception as e:
        click.echo(f"❌ Error generating recommendation: {e}", err=True)
        raise click.Abort() from e


@analysis.command()
@click.option(
    "--output-dir", default="benchmarks/charts", help="Output directory for charts"
)
@click.option("--days", default=30, help="Number of days to include")
@click.option("--interactive", is_flag=True, help="Generate interactive charts")
def dashboard(output_dir: str, days: int, interactive: bool):
    """Generate comprehensive performance dashboard"""
    
    click.echo(f"📊 Generating performance dashboard (last {days} days)")
    
    try:
        # Initialize components
        parser = BenchmarkDataParser()
        visualizer = BenchmarkVisualizer(output_dir)
        
        # Get recent results
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        results = parser.get_results_by_date_range(start_date, end_date)
        
        if not results:
            click.echo("❌ No benchmark data found for the specified time period")
            raise click.Abort() from e
        
        # Generate dashboard
        if interactive:
            dashboard_path = visualizer.create_interactive_dashboard(results)
            if dashboard_path:
                click.echo("✅ Interactive dashboard generated!")
                click.echo(f"📊 Dashboard saved to: {dashboard_path}")
            else:
                click.echo(
                    "❌ Could not generate interactive dashboard (plotly not available)"
                )
        else:
            dashboard_path = visualizer.create_performance_dashboard(results)
            click.echo("✅ Performance dashboard generated!")
            click.echo(f"📊 Dashboard saved to: {dashboard_path}")
        
        # Also export chart data
        data_path = visualizer.export_chart_data(results)
        click.echo(f"📄 Chart data exported to: {data_path}")
    
    except Exception as e:
        click.echo(f"❌ Error generating dashboard: {e}", err=True)
        raise click.Abort() from e


# Add the analysis group to the main CLI
def register_analysis_commands(main_cli):
    """Register analysis commands with the main CLI"""
    main_cli.add_command(analysis)
