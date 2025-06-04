"""
Benchmark report generation system
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from .models import BenchmarkResult, ComparisonResult
from .visualizer import BenchmarkVisualizer


class BenchmarkReporter:
    """Report generator for benchmark analysis"""

    def __init__(self, output_dir: str | Path = "benchmarks/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.visualizer = BenchmarkVisualizer()

    def generate_comparison_report(
        self,
        comparison_result: ComparisonResult,
        output_path: str | NonePath] = None,
        format: str = "markdown",
    ) -> Path:
        """Generate a detailed comparison report"""

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comparison_report_{timestamp}.{format}"
            output_path = self.output_dir / filename

        if format == "markdown":
            return self._generate_markdown_comparison_report(
                comparison_result, output_path
            )
        elif format == "html":
            return self._generate_html_comparison_report(comparison_result, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def generate_comprehensive_report(
        self,
        results: list[BenchmarkResult],
        format: str = "html",
        output_path: str | NonePath] = None,
        include_charts: bool = True,
    ) -> Path:
        """Generate a comprehensive benchmark analysis report"""

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_report_{timestamp}.{format}"
            output_path = self.output_dir / filename

        if format == "markdown":
            return self._generate_markdown_comprehensive_report(
                results, output_path, include_charts
            )
        elif format == "html":
            return self._generate_html_comprehensive_report(
                results, output_path, include_charts
            )
        elif format == "pdf":
            return self._generate_pdf_comprehensive_report(
                results, output_path, include_charts
            )
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_markdown_comparison_report(
        self, comparison_result: ComparisonResult, output_path: Path
    ) -> Path:
        """Generate markdown comparison report"""

        provider1 = comparison_result.baseline
        provider2 = comparison_result.target

        md_content = f"""# Provider Comparison Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Comparison:** {provider1} vs {provider2}
**Type:** {comparison_result.comparison_type}

## Executive Summary

{comparison_result.summary}

## Detailed Analysis

### Metrics Compared
{', '.join(comparison_result.metrics_compared)}

"""

        if comparison_result.improvements:
            md_content += f"### {provider2} Improvements\n\n"
            for metric, value in comparison_result.improvements.items():
                if metric == "success_rate":
                    md_content += f"- **Success Rate:** +{value:.1f}%\n"
                elif "time" in metric:
                    md_content += f"- **{metric.replace('_', ' ').title()}:** -{value:.2f}s faster\n"
            md_content += "\n"

        if comparison_result.regressions:
            md_content += f"### {provider2} Regressions\n\n"
            for metric, value in comparison_result.regressions.items():
                if metric == "success_rate":
                    md_content += f"- **Success Rate:** -{value:.1f}%\n"
                elif "time" in metric:
                    md_content += f"- **{metric.replace('_', ' ').title()}:** +{value:.2f}s slower\n"
            md_content += "\n"

        # Add detailed metrics if available
        if comparison_result.detailed_analysis:
            md_content += "### Detailed Metrics\n\n"

            metrics1 = comparison_result.detailed_analysis.get("provider1_metrics", {})
            metrics2 = comparison_result.detailed_analysis.get("provider2_metrics", {})

            md_content += f"| Metric | {provider1} | {provider2} | Difference |\n"
            md_content += "|--------|-------------|-------------|------------|\n"

            for metric in ["success_rate", "avg_execution_time", "avg_creation_time"]:
                val1 = metrics1.get(metric, 0)
                val2 = metrics2.get(metric, 0)
                diff = val2 - val1

                if metric == "success_rate":
                    md_content += f"| Success Rate (%) | {val1:.1f} | {val2:.1f} | {diff:+.1f} |\n"
                elif "time" in metric:
                    md_content += f"| {metric.replace('_', ' ').title()} (s) | {val1:.2f} | {val2:.2f} | {diff:+.2f} |\n"

        md_content += """
## Recommendations

Based on this comparison:

"""

        if comparison_result.improvements and not comparison_result.regressions:
            md_content += (
                f"- **{provider2}** shows clear improvements over **{provider1}**\n"
            )
            md_content += (
                f"- Consider migrating to **{provider2}** for better performance\n"
            )
        elif comparison_result.regressions and not comparison_result.improvements:
            md_content += f"- **{provider1}** performs better than **{provider2}**\n"
            md_content += f"- Stick with **{provider1}** for optimal performance\n"
        elif comparison_result.improvements and comparison_result.regressions:
            md_content += "- Both providers have trade-offs\n"
            md_content += (
                "- Choose based on which metrics are most important for your use case\n"
            )
        else:
            md_content += "- Performance is similar between both providers\n"
            md_content += (
                "- Choice can be based on other factors (cost, features, etc.)\n"
            )

        with open(output_path, "w") as f:
            f.write(md_content)

        return output_path

    def _generate_html_comparison_report(
        self, comparison_result: ComparisonResult, output_path: Path
    ) -> Path:
        """Generate HTML comparison report"""

        # Generate chart for the comparison
        chart_path = self.visualizer.create_provider_comparison_chart(comparison_result)

        provider1 = comparison_result.baseline
        provider2 = comparison_result.target

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Provider Comparison Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; margin-bottom: 30px; }}
        .metric-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .metric-table th, .metric-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        .metric-table th {{ background-color: #f2f2f2; }}
        .improvement {{ color: #28a745; font-weight: bold; }}
        .regression {{ color: #dc3545; font-weight: bold; }}
        .chart {{ text-align: center; margin: 30px 0; }}
        .recommendations {{ background: #e9ecef; padding: 20px; border-radius: 5px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Provider Comparison Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Comparison:</strong> {provider1} vs {provider2}</p>
        <p><strong>Type:</strong> {comparison_result.comparison_type}</p>
    </div>

    <h2>Executive Summary</h2>
    <p>{comparison_result.summary}</p>

    <h2>Performance Comparison Chart</h2>
    <div class="chart">
        <img src="{chart_path.name}" alt="Provider Comparison Chart" style="max-width: 100%; height: auto;">
    </div>

    <h2>Detailed Metrics</h2>
"""

        if comparison_result.detailed_analysis:
            metrics1 = comparison_result.detailed_analysis.get("provider1_metrics", {})
            metrics2 = comparison_result.detailed_analysis.get("provider2_metrics", {})

            html_content += f"""
    <table class="metric-table">
        <thead>
            <tr>
                <th>Metric</th>
                <th>{provider1}</th>
                <th>{provider2}</th>
                <th>Difference</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
"""

            for metric in ["success_rate", "avg_execution_time", "avg_creation_time"]:
                val1 = metrics1.get(metric, 0)
                val2 = metrics2.get(metric, 0)
                diff = val2 - val1

                # Determine status
                if metric == "success_rate":
                    status = (
                        "improvement"
                        if diff > 0
                        else "regression"
                        if diff < 0
                        else "same"
                    )
                    status_text = (
                        "Better" if diff > 0 else "Worse" if diff < 0 else "Same"
                    )
                    metric_name = "Success Rate (%)"
                    val1_str = f"{val1:.1f}"
                    val2_str = f"{val2:.1f}"
                    diff_str = f"{diff:+.1f}"
                else:
                    status = (
                        "improvement"
                        if diff < 0
                        else "regression"
                        if diff > 0
                        else "same"
                    )
                    status_text = (
                        "Better" if diff < 0 else "Worse" if diff > 0 else "Same"
                    )
                    metric_name = metric.replace("_", " ").title() + " (s)"
                    val1_str = f"{val1:.2f}"
                    val2_str = f"{val2:.2f}"
                    diff_str = f"{diff:+.2f}"

                status_class = status if status != "same" else ""

                html_content += f"""
            <tr>
                <td>{metric_name}</td>
                <td>{val1_str}</td>
                <td>{val2_str}</td>
                <td class="{status_class}">{diff_str}</td>
                <td class="{status_class}">{status_text}</td>
            </tr>
"""

            html_content += """
        </tbody>
    </table>
"""

        # Add recommendations
        html_content += """
    <div class="recommendations">
        <h2>Recommendations</h2>
"""

        if comparison_result.improvements and not comparison_result.regressions:
            html_content += f"<p><strong>{provider2}</strong> shows clear improvements over <strong>{provider1}</strong>. Consider migrating to <strong>{provider2}</strong> for better performance.</p>"
        elif comparison_result.regressions and not comparison_result.improvements:
            html_content += f"<p><strong>{provider1}</strong> performs better than <strong>{provider2}</strong>. Stick with <strong>{provider1}</strong> for optimal performance.</p>"
        elif comparison_result.improvements and comparison_result.regressions:
            html_content += "<p>Both providers have trade-offs. Choose based on which metrics are most important for your use case.</p>"
        else:
            html_content += "<p>Performance is similar between both providers. Choice can be based on other factors (cost, features, etc.).</p>"

        html_content += """
    </div>
</body>
</html>
"""

        with open(output_path, "w") as f:
            f.write(html_content)

        return output_path

    def _generate_markdown_comprehensive_report(
        self, results: list[BenchmarkResult], output_path: Path, include_charts: bool
    ) -> Path:
        """Generate comprehensive markdown report"""

        if not results:
            md_content = (
                "# Comprehensive Benchmark Report\n\nNo benchmark data available.\n"
            )
            with open(output_path, "w") as f:
                f.write(md_content)
            return output_path

        # Generate charts if requested
        chart_paths = []
        if include_charts:
            dashboard_path = self.visualizer.create_performance_dashboard(results)
            chart_paths.append(dashboard_path)

        # Analyze data
        providers = set()
        for result in results:
            providers.update(result.provider_results.keys())

        start_date = min(r.timestamp for r in results)
        end_date = max(r.timestamp for r in results)

        md_content = f"""# Comprehensive Benchmark Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
**Total Benchmark Runs:** {len(results)}
**Providers Analyzed:** {', '.join(sorted(providers))}

## Executive Summary

This report analyzes {len(results)} benchmark runs across {len(providers)} providers over a {(end_date - start_date).days} day period.

"""

        # Provider performance summary
        md_content += "## Provider Performance Summary\n\n"
        md_content += "| Provider | Avg Success Rate | Avg Execution Time | Avg Creation Time | Runs |\n"
        md_content += "|----------|------------------|-------------------|-------------------|------|\n"

        for provider in sorted(providers):
            provider_results = []
            for result in results:
                if provider in result.provider_results:
                    provider_results.append(result.provider_results[provider])

            if provider_results:
                avg_success = sum(
                    p.overall_success_rate for p in provider_results
                ) / len(provider_results)
                avg_exec = sum(p.avg_execution_time for p in provider_results) / len(
                    provider_results
                )
                avg_creation = sum(p.avg_creation_time for p in provider_results) / len(
                    provider_results
                )

                md_content += f"| {provider} | {avg_success:.1f}% | {avg_exec:.2f}s | {avg_creation:.2f}s | {len(provider_results)} |\n"

        # Charts section
        if include_charts and chart_paths:
            md_content += "\n## Performance Charts\n\n"
            for chart_path in chart_paths:
                md_content += f"![Performance Dashboard]({chart_path.name})\n\n"

        # Detailed analysis by provider
        md_content += "\n## Detailed Provider Analysis\n\n"

        for provider in sorted(providers):
            provider_results = [r for r in results if provider in r.provider_results]
            if not provider_results:
                continue

            md_content += f"### {provider.upper()}\n\n"

            # Calculate statistics
            success_rates = [
                r.provider_results[provider].overall_success_rate
                for r in provider_results
            ]
            exec_times = [
                r.provider_results[provider].avg_execution_time
                for r in provider_results
            ]

            md_content += f"- **Benchmark Runs:** {len(provider_results)}\n"
            md_content += f"- **Success Rate:** {sum(success_rates)/len(success_rates):.1f}% (min: {min(success_rates):.1f}%, max: {max(success_rates):.1f}%)\n"
            md_content += f"- **Execution Time:** {sum(exec_times)/len(exec_times):.2f}s (min: {min(exec_times):.2f}s, max: {max(exec_times):.2f}s)\n"

            # Latest performance
            latest_result = max(provider_results, key=lambda r: r.timestamp)
            latest_metrics = latest_result.provider_results[provider]

            md_content += f"\n**Latest Performance ({latest_result.timestamp.strftime('%Y-%m-%d')}):**\n"
            md_content += (
                f"- Success Rate: {latest_metrics.overall_success_rate:.1f}%\n"
            )
            md_content += (
                f"- Execution Time: {latest_metrics.avg_execution_time:.2f}s\n"
            )
            md_content += (
                f"- Creation Time: {latest_metrics.avg_creation_time:.2f}s\n\n"
            )

        # Recommendations
        md_content += "## Recommendations\n\n"

        # Find best performing provider
        provider_scores = {}
        for provider in providers:
            provider_results = [r for r in results if provider in r.provider_results]
            if provider_results:
                avg_success = sum(
                    r.provider_results[provider].overall_success_rate
                    for r in provider_results
                ) / len(provider_results)
                avg_exec = sum(
                    r.provider_results[provider].avg_execution_time
                    for r in provider_results
                ) / len(provider_results)

                # Simple scoring: success rate (0-100) + speed bonus (lower time = higher score)
                score = avg_success + max(0, 10 - avg_exec)
                provider_scores[provider] = score

        if provider_scores:
            best_provider = max(
                provider_scores.keys(), key=lambda p: provider_scores[p]
            )
            md_content += (
                f"- **Recommended Provider:** {best_provider} (highest overall score)\n"
            )
            md_content += (
                "- **For Reliability:** Choose the provider with highest success rate\n"
            )
            md_content += (
                "- **For Speed:** Choose the provider with lowest execution time\n"
            )

        md_content += f"\n---\n*Report generated by Grainchain Benchmark Analysis at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        with open(output_path, "w") as f:
            f.write(md_content)

        return output_path

    def _generate_html_comprehensive_report(
        self, results: list[BenchmarkResult], output_path: Path, include_charts: bool
    ) -> Path:
        """Generate comprehensive HTML report"""

        # Generate interactive dashboard if charts requested
        chart_html = ""
        if include_charts:
            interactive_path = self.visualizer.create_interactive_dashboard(results)
            if interactive_path:
                # Read the interactive dashboard HTML and embed it
                with open(interactive_path) as f:
                    chart_html = f.read()

        if not results:
            html_content = """<!DOCTYPE html>
<html><head><title>Benchmark Report</title></head>
<body><h1>Comprehensive Benchmark Report</h1><p>No benchmark data available.</p></body>
</html>"""
            with open(output_path, "w") as f:
                f.write(html_content)
            return output_path

        # Analyze data
        providers = set()
        for result in results:
            providers.update(result.provider_results.keys())

        start_date = min(r.timestamp for r in results)
        end_date = max(r.timestamp for r in results)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive Benchmark Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; margin-bottom: 30px; }}
        .summary-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .summary-table th, .summary-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        .summary-table th {{ background-color: #f2f2f2; }}
        .provider-section {{ margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
        .recommendations {{ background: #e9ecef; padding: 20px; border-radius: 5px; margin-top: 30px; }}
        .chart-container {{ margin: 30px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Comprehensive Benchmark Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Analysis Period:</strong> {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}</p>
        <p><strong>Total Benchmark Runs:</strong> {len(results)}</p>
        <p><strong>Providers Analyzed:</strong> {', '.join(sorted(providers))}</p>
    </div>

    <h2>Executive Summary</h2>
    <p>This report analyzes {len(results)} benchmark runs across {len(providers)} providers over a {(end_date - start_date).days} day period.</p>

    <h2>Provider Performance Summary</h2>
    <table class="summary-table">
        <thead>
            <tr>
                <th>Provider</th>
                <th>Avg Success Rate</th>
                <th>Avg Execution Time</th>
                <th>Avg Creation Time</th>
                <th>Runs</th>
            </tr>
        </thead>
        <tbody>
"""

        for provider in sorted(providers):
            provider_results = []
            for result in results:
                if provider in result.provider_results:
                    provider_results.append(result.provider_results[provider])

            if provider_results:
                avg_success = sum(
                    p.overall_success_rate for p in provider_results
                ) / len(provider_results)
                avg_exec = sum(p.avg_execution_time for p in provider_results) / len(
                    provider_results
                )
                avg_creation = sum(p.avg_creation_time for p in provider_results) / len(
                    provider_results
                )

                html_content += f"""
            <tr>
                <td>{provider}</td>
                <td>{avg_success:.1f}%</td>
                <td>{avg_exec:.2f}s</td>
                <td>{avg_creation:.2f}s</td>
                <td>{len(provider_results)}</td>
            </tr>
"""

        html_content += """
        </tbody>
    </table>
"""

        # Add interactive charts if available
        if include_charts and chart_html:
            html_content += """
    <h2>Interactive Performance Dashboard</h2>
    <div class="chart-container">
"""
            # Extract just the plotly div from the chart HTML
            import re

            plotly_div_match = re.search(
                r'<div[^>]*id="[^"]*"[^>]*>.*?</div>', chart_html, re.DOTALL
            )
            plotly_script_match = re.search(
                r"<script[^>]*>.*?</script>", chart_html, re.DOTALL
            )

            if plotly_div_match and plotly_script_match:
                html_content += plotly_div_match.group(0)
                html_content += plotly_script_match.group(0)

            html_content += """
    </div>
"""

        # Add detailed provider analysis
        html_content += """
    <h2>Detailed Provider Analysis</h2>
"""

        for provider in sorted(providers):
            provider_results = [r for r in results if provider in r.provider_results]
            if not provider_results:
                continue

            success_rates = [
                r.provider_results[provider].overall_success_rate
                for r in provider_results
            ]
            exec_times = [
                r.provider_results[provider].avg_execution_time
                for r in provider_results
            ]

            latest_result = max(provider_results, key=lambda r: r.timestamp)
            latest_metrics = latest_result.provider_results[provider]

            html_content += f"""
    <div class="provider-section">
        <h3>{provider.upper()}</h3>
        <ul>
            <li><strong>Benchmark Runs:</strong> {len(provider_results)}</li>
            <li><strong>Success Rate:</strong> {sum(success_rates)/len(success_rates):.1f}% (min: {min(success_rates):.1f}%, max: {max(success_rates):.1f}%)</li>
            <li><strong>Execution Time:</strong> {sum(exec_times)/len(exec_times):.2f}s (min: {min(exec_times):.2f}s, max: {max(exec_times):.2f}s)</li>
        </ul>
        <h4>Latest Performance ({latest_result.timestamp.strftime('%Y-%m-%d')})</h4>
        <ul>
            <li>Success Rate: {latest_metrics.overall_success_rate:.1f}%</li>
            <li>Execution Time: {latest_metrics.avg_execution_time:.2f}s</li>
            <li>Creation Time: {latest_metrics.avg_creation_time:.2f}s</li>
        </ul>
    </div>
"""

        # Add recommendations
        provider_scores = {}
        for provider in providers:
            provider_results = [r for r in results if provider in r.provider_results]
            if provider_results:
                avg_success = sum(
                    r.provider_results[provider].overall_success_rate
                    for r in provider_results
                ) / len(provider_results)
                avg_exec = sum(
                    r.provider_results[provider].avg_execution_time
                    for r in provider_results
                ) / len(provider_results)
                score = avg_success + max(0, 10 - avg_exec)
                provider_scores[provider] = score

        html_content += """
    <div class="recommendations">
        <h2>Recommendations</h2>
"""

        if provider_scores:
            best_provider = max(
                provider_scores.keys(), key=lambda p: provider_scores[p]
            )
            html_content += f"""
        <ul>
            <li><strong>Recommended Provider:</strong> {best_provider} (highest overall score)</li>
            <li><strong>For Reliability:</strong> Choose the provider with highest success rate</li>
            <li><strong>For Speed:</strong> Choose the provider with lowest execution time</li>
        </ul>
"""

        html_content += f"""
    </div>

    <hr>
    <p><em>Report generated by Grainchain Benchmark Analysis at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
</body>
</html>
"""

        with open(output_path, "w") as f:
            f.write(html_content)

        return output_path

    def _generate_pdf_comprehensive_report(
        self, results: list[BenchmarkResult], output_path: Path, include_charts: bool
    ) -> Path:
        """Generate comprehensive PDF report"""

        try:
            # Try to use weasyprint for HTML to PDF conversion
            import weasyprint

            # First generate HTML report
            html_path = output_path.with_suffix(".html")
            self._generate_html_comprehensive_report(results, html_path, include_charts)

            # Convert to PDF
            weasyprint.HTML(filename=str(html_path)).write_pdf(str(output_path))

            # Clean up temporary HTML file
            html_path.unlink()

        except ImportError:
            # Fallback: generate markdown and suggest manual conversion
            md_path = output_path.with_suffix(".md")
            self._generate_markdown_comprehensive_report(
                results, md_path, include_charts
            )

            # Create a simple text file with instructions
            with open(output_path, "w") as f:
                f.write(
                    f"""PDF generation requires weasyprint package.

Install with: pip install weasyprint

Alternatively, a markdown report has been generated at: {md_path}
You can convert it to PDF using tools like pandoc:
pandoc {md_path} -o {output_path}
"""
                )

        return output_path
