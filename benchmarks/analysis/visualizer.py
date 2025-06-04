"""
Benchmark visualization components for creating charts and graphs
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

try:
    import plotly.express as px
    import plotly.graph_objects as go
    import plotly.offline as pyo
    from plotly.subplots import make_subplots

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from .models import BenchmarkResult, ComparisonResult, TrendAnalysis


class BenchmarkVisualizer:
    """Visualization engine for benchmark data"""

    def __init__(self, output_dir: str | Path = "benchmarks/charts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Set matplotlib style
        plt.style.use(
            "seaborn-v0_8" if "seaborn-v0_8" in plt.style.available else "default"
        )

    def create_provider_comparison_chart(
        self,
        comparison_result: ComparisonResult,
        chart_type: str = "bar",
        save_path: str | NonePath] = None,
    ) -> Path:
        """Create a chart comparing two providers"""

        if not save_path:
            save_path = (
                self.output_dir
                / f"provider_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )

        provider1 = comparison_result.baseline
        provider2 = comparison_result.target

        # Extract metrics from detailed analysis
        metrics1 = comparison_result.detailed_analysis.get("provider1_metrics", {})
        metrics2 = comparison_result.detailed_analysis.get("provider2_metrics", {})

        if chart_type == "bar":
            self._create_bar_comparison(
                metrics1, metrics2, provider1, provider2, save_path
            )
        elif chart_type == "radar":
            self._create_radar_comparison(
                metrics1, metrics2, provider1, provider2, save_path
            )
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

        return save_path

    def create_trend_chart(
        self, trend_analysis: TrendAnalysis, save_path: str | NonePath] = None
    ) -> Path:
        """Create a trend analysis chart"""

        if not save_path:
            provider_suffix = (
                f"_{trend_analysis.provider}" if trend_analysis.provider else "_all"
            )
            save_path = (
                self.output_dir
                / f"trend_{trend_analysis.metric_name}{provider_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )

        # Extract data points
        timestamps = [dp["timestamp"] for dp in trend_analysis.data_points]
        values = [dp["value"] for dp in trend_analysis.data_points]

        if not timestamps or not values:
            # Create empty chart with message
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(
                0.5,
                0.5,
                "No data available for trend analysis",
                ha="center",
                va="center",
                transform=ax.transAxes,
                fontsize=14,
            )
            ax.set_title(f"Trend Analysis: {trend_analysis.metric_name}")
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            plt.close()
            return save_path

        # Create the trend chart
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot the data
        ax.plot(timestamps, values, marker="o", linewidth=2, markersize=6)

        # Add trend line if enough data points
        if len(values) > 2:
            import numpy as np

            x_numeric = mdates.date2num(timestamps)
            z = np.polyfit(x_numeric, values, 1)
            p = np.poly1d(z)
            ax.plot(
                timestamps,
                p(x_numeric),
                "--",
                alpha=0.7,
                color="red",
                label=f"Trend: {trend_analysis.trend_direction}",
            )

        # Formatting
        ax.set_title(
            f"Trend Analysis: {trend_analysis.metric_name.replace('_', ' ').title()}"
        )
        ax.set_xlabel("Time")

        # Y-axis label based on metric
        if "rate" in trend_analysis.metric_name:
            ax.set_ylabel("Success Rate (%)")
        elif "time" in trend_analysis.metric_name:
            ax.set_ylabel("Time (seconds)")
        else:
            ax.set_ylabel("Value")

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        ax.xaxis.set_major_locator(
            mdates.DayLocator(interval=max(1, len(timestamps) // 10))
        )
        plt.xticks(rotation=45)

        # Add grid and legend
        ax.grid(True, alpha=0.3)
        if len(values) > 2:
            ax.legend()

        # Add statistics text box
        stats = trend_analysis.statistical_summary
        stats_text = f"Mean: {stats.get('mean', 0):.2f}\n"
        stats_text += f"Std Dev: {stats.get('std_dev', 0):.2f}\n"
        stats_text += f"Data Points: {stats.get('data_points', 0)}"

        ax.text(
            0.02,
            0.98,
            stats_text,
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()

        return save_path

    def create_performance_dashboard(
        self, results: list[BenchmarkResult], save_path: str | NonePath] = None
    ) -> Path:
        """Create a comprehensive performance dashboard"""

        if not save_path:
            save_path = (
                self.output_dir
                / f"performance_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )

        if not results:
            # Create empty dashboard
            fig, ax = plt.subplots(figsize=(15, 10))
            ax.text(
                0.5,
                0.5,
                "No benchmark data available",
                ha="center",
                va="center",
                transform=ax.transAxes,
                fontsize=16,
            )
            ax.set_title("Performance Dashboard")
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            plt.close()
            return save_path

        # Create subplot layout
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle("Benchmark Performance Dashboard", fontsize=16)

        # 1. Success Rate Over Time
        self._plot_success_rate_over_time(results, ax1)

        # 2. Execution Time Comparison
        self._plot_execution_time_comparison(results, ax2)

        # 3. Provider Performance Summary
        self._plot_provider_performance_summary(results, ax3)

        # 4. Scenario Success Rates
        self._plot_scenario_success_rates(results, ax4)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()

        return save_path

    def create_interactive_dashboard(
        self, results: list[BenchmarkResult], save_path: str | NonePath] = None
    ) -> str | NonePath]:
        """Create an interactive HTML dashboard using Plotly"""

        if not PLOTLY_AVAILABLE:
            print(
                "Warning: Plotly not available. Install with 'pip install plotly' for interactive charts."
            )
            return None

        if not save_path:
            save_path = (
                self.output_dir
                / f"interactive_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            )

        if not results:
            # Create simple HTML with message
            html_content = """
            <html>
            <head><title>Benchmark Dashboard</title></head>
            <body>
                <h1>Benchmark Performance Dashboard</h1>
                <p>No benchmark data available.</p>
            </body>
            </html>
            """
            with open(save_path, "w") as f:
                f.write(html_content)
            return save_path

        # Create subplots
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Success Rate Over Time",
                "Execution Time Comparison",
                "Provider Performance",
                "Scenario Analysis",
            ),
            specs=[
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}],
            ],
        )

        # Extract data for plotting
        providers = set()
        for result in results:
            providers.update(result.provider_results.keys())

        colors = px.colors.qualitative.Set1[: len(providers)]
        provider_colors = dict(zip(providers, colors))

        # 1. Success Rate Over Time
        for i, provider in enumerate(providers):
            timestamps = []
            success_rates = []

            for result in results:
                if provider in result.provider_results:
                    timestamps.append(result.timestamp)
                    success_rates.append(
                        result.provider_results[provider].overall_success_rate
                    )

            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=success_rates,
                    mode="lines+markers",
                    name=f"{provider} Success Rate",
                    line=dict(color=provider_colors[provider]),
                    showlegend=True,
                ),
                row=1,
                col=1,
            )

        # 2. Execution Time Comparison (latest data)
        if results:
            latest_result = results[-1]
            providers_list = list(latest_result.provider_results.keys())
            exec_times = [
                latest_result.provider_results[p].avg_execution_time
                for p in providers_list
            ]

            fig.add_trace(
                go.Bar(
                    x=providers_list,
                    y=exec_times,
                    name="Execution Time",
                    marker_color=[provider_colors[p] for p in providers_list],
                    showlegend=False,
                ),
                row=1,
                col=2,
            )

        # 3. Provider Performance (Success Rate vs Execution Time)
        for provider in providers:
            success_rates = []
            exec_times = []

            for result in results:
                if provider in result.provider_results:
                    success_rates.append(
                        result.provider_results[provider].overall_success_rate
                    )
                    exec_times.append(
                        result.provider_results[provider].avg_execution_time
                    )

            if success_rates and exec_times:
                avg_success = sum(success_rates) / len(success_rates)
                avg_exec_time = sum(exec_times) / len(exec_times)

                fig.add_trace(
                    go.Scatter(
                        x=[avg_exec_time],
                        y=[avg_success],
                        mode="markers",
                        name=provider,
                        marker=dict(size=15, color=provider_colors[provider]),
                        showlegend=False,
                    ),
                    row=2,
                    col=1,
                )

        # 4. Scenario Analysis (latest data)
        if results:
            latest_result = results[-1]
            scenario_data = {}

            for provider, metrics in latest_result.provider_results.items():
                for scenario_name, scenario_metrics in metrics.scenarios.items():
                    if scenario_name not in scenario_data:
                        scenario_data[scenario_name] = []
                    scenario_data[scenario_name].append(
                        {
                            "provider": provider,
                            "success_rate": scenario_metrics.success_rate,
                        }
                    )

            for scenario_name, data in scenario_data.items():
                providers_list = [d["provider"] for d in data]
                success_rates = [d["success_rate"] for d in data]

                fig.add_trace(
                    go.Bar(
                        x=providers_list,
                        y=success_rates,
                        name=scenario_name,
                        showlegend=False,
                    ),
                    row=2,
                    col=2,
                )

        # Update layout
        fig.update_layout(
            title_text="Interactive Benchmark Dashboard", height=800, showlegend=True
        )

        # Update axes labels
        fig.update_xaxes(title_text="Time", row=1, col=1)
        fig.update_yaxes(title_text="Success Rate (%)", row=1, col=1)

        fig.update_xaxes(title_text="Provider", row=1, col=2)
        fig.update_yaxes(title_text="Execution Time (s)", row=1, col=2)

        fig.update_xaxes(title_text="Execution Time (s)", row=2, col=1)
        fig.update_yaxes(title_text="Success Rate (%)", row=2, col=1)

        fig.update_xaxes(title_text="Provider", row=2, col=2)
        fig.update_yaxes(title_text="Success Rate (%)", row=2, col=2)

        # Save as HTML
        pyo.plot(fig, filename=str(save_path), auto_open=False)

        return save_path

    def _create_bar_comparison(
        self,
        metrics1: dict[str, float],
        metrics2: dict[str, float],
        provider1: str,
        provider2: str,
        save_path: Path,
    ):
        """Create a bar chart comparing two providers"""

        metrics = ["success_rate", "avg_execution_time", "avg_creation_time"]
        labels = ["Success Rate (%)", "Execution Time (s)", "Creation Time (s)"]

        values1 = [metrics1.get(m, 0) for m in metrics]
        values2 = [metrics2.get(m, 0) for m in metrics]

        x = range(len(metrics))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))

        bars1 = ax.bar(
            [i - width / 2 for i in x], values1, width, label=provider1, alpha=0.8
        )
        bars2 = ax.bar(
            [i + width / 2 for i in x], values2, width, label=provider2, alpha=0.8
        )

        ax.set_xlabel("Metrics")
        ax.set_ylabel("Values")
        ax.set_title(f"Provider Comparison: {provider1} vs {provider2}")
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(
                    f"{height:.2f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                )

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()

    def _create_radar_comparison(
        self,
        metrics1: dict[str, float],
        metrics2: dict[str, float],
        provider1: str,
        provider2: str,
        save_path: Path,
    ):
        """Create a radar chart comparing two providers"""

        import numpy as np

        # Normalize metrics for radar chart (0-100 scale)
        categories = ["Success Rate", "Speed (inv)", "Startup Speed (inv)"]

        # Invert time metrics (lower is better)
        values1 = [
            metrics1.get("success_rate", 0),
            100
            - min(100, metrics1.get("avg_execution_time", 0) * 20),  # Scale and invert
            100
            - min(100, metrics1.get("avg_creation_time", 0) * 50),  # Scale and invert
        ]

        values2 = [
            metrics2.get("success_rate", 0),
            100 - min(100, metrics2.get("avg_execution_time", 0) * 20),
            100 - min(100, metrics2.get("avg_creation_time", 0) * 50),
        ]

        # Number of variables
        N = len(categories)

        # Compute angle for each axis
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Complete the circle

        # Add first value at the end to close the radar chart
        values1 += values1[:1]
        values2 += values2[:1]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection="polar"))

        # Plot data
        ax.plot(angles, values1, "o-", linewidth=2, label=provider1, alpha=0.8)
        ax.fill(angles, values1, alpha=0.25)

        ax.plot(angles, values2, "o-", linewidth=2, label=provider2, alpha=0.8)
        ax.fill(angles, values2, alpha=0.25)

        # Add category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)

        # Set y-axis limits
        ax.set_ylim(0, 100)

        # Add legend and title
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.0))
        ax.set_title(
            f"Provider Comparison Radar: {provider1} vs {provider2}",
            size=14,
            weight="bold",
            pad=20,
        )

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()

    def _plot_success_rate_over_time(self, results: list[BenchmarkResult], ax):
        """Plot success rate over time for all providers"""
        providers = set()
        for result in results:
            providers.update(result.provider_results.keys())

        for provider in providers:
            timestamps = []
            success_rates = []

            for result in results:
                if provider in result.provider_results:
                    timestamps.append(result.timestamp)
                    success_rates.append(
                        result.provider_results[provider].overall_success_rate
                    )

            if timestamps:
                ax.plot(
                    timestamps, success_rates, marker="o", label=provider, linewidth=2
                )

        ax.set_title("Success Rate Over Time")
        ax.set_xlabel("Time")
        ax.set_ylabel("Success Rate (%)")
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Format x-axis
        if results:
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    def _plot_execution_time_comparison(self, results: list[BenchmarkResult], ax):
        """Plot execution time comparison for latest results"""
        if not results:
            return

        latest_result = results[-1]
        providers = list(latest_result.provider_results.keys())
        exec_times = [
            latest_result.provider_results[p].avg_execution_time for p in providers
        ]

        bars = ax.bar(providers, exec_times, alpha=0.7)
        ax.set_title("Latest Execution Time Comparison")
        ax.set_xlabel("Provider")
        ax.set_ylabel("Execution Time (s)")
        ax.grid(True, alpha=0.3)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.2f}s",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
            )

    def _plot_provider_performance_summary(self, results: list[BenchmarkResult], ax):
        """Plot provider performance summary (success rate vs execution time)"""
        providers = set()
        for result in results:
            providers.update(result.provider_results.keys())

        for provider in providers:
            success_rates = []
            exec_times = []

            for result in results:
                if provider in result.provider_results:
                    success_rates.append(
                        result.provider_results[provider].overall_success_rate
                    )
                    exec_times.append(
                        result.provider_results[provider].avg_execution_time
                    )

            if success_rates and exec_times:
                avg_success = sum(success_rates) / len(success_rates)
                avg_exec_time = sum(exec_times) / len(exec_times)

                ax.scatter(avg_exec_time, avg_success, s=100, label=provider, alpha=0.7)

        ax.set_title("Provider Performance Summary")
        ax.set_xlabel("Average Execution Time (s)")
        ax.set_ylabel("Average Success Rate (%)")
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _plot_scenario_success_rates(self, results: list[BenchmarkResult], ax):
        """Plot scenario success rates for latest results"""
        if not results:
            return

        latest_result = results[-1]
        scenario_data = {}

        # Aggregate scenario data across providers
        for provider, metrics in latest_result.provider_results.items():
            for scenario_name, scenario_metrics in metrics.scenarios.items():
                if scenario_name not in scenario_data:
                    scenario_data[scenario_name] = []
                scenario_data[scenario_name].append(scenario_metrics.success_rate)

        # Calculate average success rate per scenario
        scenarios = list(scenario_data.keys())
        avg_success_rates = [
            sum(rates) / len(rates) for rates in scenario_data.values()
        ]

        bars = ax.bar(scenarios, avg_success_rates, alpha=0.7)
        ax.set_title("Scenario Success Rates (Latest)")
        ax.set_xlabel("Scenario")
        ax.set_ylabel("Average Success Rate (%)")
        ax.grid(True, alpha=0.3)

        # Rotate x-axis labels for better readability
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.1f}%",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
            )

    def export_chart_data(
        self, results: list[BenchmarkResult], save_path: str | NonePath] = None
    ) -> Path:
        """Export chart data as JSON for external visualization tools"""

        if not save_path:
            save_path = (
                self.output_dir
                / f"chart_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

        chart_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_results": len(results),
                "date_range": {
                    "start": min(r.timestamp for r in results).isoformat()
                    if results
                    else None,
                    "end": max(r.timestamp for r in results).isoformat()
                    if results
                    else None,
                },
            },
            "time_series": {},
            "latest_comparison": {},
            "scenario_analysis": {},
        }

        if not results:
            with open(save_path, "w") as f:
                json.dump(chart_data, f, indent=2)
            return save_path

        # Time series data
        providers = set()
        for result in results:
            providers.update(result.provider_results.keys())

        for provider in providers:
            chart_data["time_series"][provider] = {
                "timestamps": [],
                "success_rates": [],
                "execution_times": [],
                "creation_times": [],
            }

            for result in results:
                if provider in result.provider_results:
                    metrics = result.provider_results[provider]
                    chart_data["time_series"][provider]["timestamps"].append(
                        result.timestamp.isoformat()
                    )
                    chart_data["time_series"][provider]["success_rates"].append(
                        metrics.overall_success_rate
                    )
                    chart_data["time_series"][provider]["execution_times"].append(
                        metrics.avg_execution_time
                    )
                    chart_data["time_series"][provider]["creation_times"].append(
                        metrics.avg_creation_time
                    )

        # Latest comparison data
        latest_result = results[-1]
        for provider, metrics in latest_result.provider_results.items():
            chart_data["latest_comparison"][provider] = {
                "success_rate": metrics.overall_success_rate,
                "execution_time": metrics.avg_execution_time,
                "creation_time": metrics.avg_creation_time,
                "total_scenarios": metrics.total_scenarios,
            }

        # Scenario analysis
        for provider, metrics in latest_result.provider_results.items():
            chart_data["scenario_analysis"][provider] = {}
            for scenario_name, scenario_metrics in metrics.scenarios.items():
                chart_data["scenario_analysis"][provider][scenario_name] = {
                    "success_rate": scenario_metrics.success_rate,
                    "avg_execution_time": scenario_metrics.avg_execution_time,
                    "total_iterations": scenario_metrics.total_iterations,
                }

        with open(save_path, "w") as f:
            json.dump(chart_data, f, indent=2)

        return save_path
