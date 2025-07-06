"""
Configuration management for benchmark analysis
"""

import json
from pathlib import Path
from typing import Any, Optional, Union


class AnalysisConfig:
    """Configuration manager for benchmark analysis settings"""

    def __init__(self, config_path: str | Path | None = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "configs" / "analysis.json"

        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path) as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default configuration if file doesn't exist
            return self._get_default_config()
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file {self.config_path}: {e}")

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration"""
        return {
            "default_settings": {
                "time_range_days": 30,
                "comparison_threshold": 0.1,
                "chart_output_dir": "benchmarks/charts",
                "report_output_dir": "benchmarks/reports",
                "preferred_chart_format": "png",
                "preferred_report_format": "html",
                "include_charts_in_reports": True,
                "interactive_charts": False,
            },
            "visualization": {
                "chart_style": "seaborn-v0_8",
                "color_palette": [
                    "#1f77b4",
                    "#ff7f0e",
                    "#2ca02c",
                    "#d62728",
                    "#9467bd",
                ],
                "figure_size": [12, 8],
                "dpi": 300,
                "font_size": 12,
                "grid_alpha": 0.3,
            },
            "metrics": {
                "primary_metrics": [
                    "success_rate",
                    "avg_execution_time",
                    "avg_creation_time",
                ],
                "metric_weights": {
                    "success_rate": 0.5,
                    "avg_execution_time": 0.3,
                    "avg_creation_time": 0.2,
                },
            },
            "providers": {
                "display_names": {
                    "local": "Local",
                    "e2b": "E2B",
                    "modal": "Modal",
                    "daytona": "Daytona",
                    "morph": "Morph",
                }
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation (e.g., 'default_settings.time_range_days')"""
        keys = key.split(".")
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value using dot notation"""
        keys = key.split(".")
        config = self._config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

    def save(self, path: str | Path | None = None) -> None:
        """Save configuration to file"""
        save_path = Path(path) if path else self.config_path
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, "w") as f:
            json.dump(self._config, f, indent=2)

    def update(self, updates: dict[str, Any]) -> None:
        """Update configuration with a dictionary of changes"""

        def deep_update(base_dict: dict[str, Any], update_dict: dict[str, Any]) -> None:
            for key, value in update_dict.items():
                if (
                    key in base_dict
                    and isinstance(base_dict[key], dict)
                    and isinstance(value, dict)
                ):
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value

        deep_update(self._config, updates)

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self._config = self._get_default_config()

    # Convenience properties for commonly used settings

    @property
    def time_range_days(self) -> int:
        """Default time range for analysis in days"""
        return self.get("default_settings.time_range_days", 30)

    @property
    def comparison_threshold(self) -> float:
        """Threshold for detecting significant differences"""
        return self.get("default_settings.comparison_threshold", 0.1)

    @property
    def chart_output_dir(self) -> str:
        """Directory for chart outputs"""
        return self.get("default_settings.chart_output_dir", "benchmarks/charts")

    @property
    def report_output_dir(self) -> str:
        """Directory for report outputs"""
        return self.get("default_settings.report_output_dir", "benchmarks/reports")

    @property
    def preferred_chart_format(self) -> str:
        """Preferred format for charts"""
        return self.get("default_settings.preferred_chart_format", "png")

    @property
    def preferred_report_format(self) -> str:
        """Preferred format for reports"""
        return self.get("default_settings.preferred_report_format", "html")

    @property
    def include_charts_in_reports(self) -> bool:
        """Whether to include charts in reports by default"""
        return self.get("default_settings.include_charts_in_reports", True)

    @property
    def interactive_charts(self) -> bool:
        """Whether to generate interactive charts by default"""
        return self.get("default_settings.interactive_charts", False)

    @property
    def chart_style(self) -> str:
        """Matplotlib style for charts"""
        return self.get("visualization.chart_style", "seaborn-v0_8")

    @property
    def color_palette(self) -> list:
        """Color palette for charts"""
        return self.get(
            "visualization.color_palette",
            ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
        )

    @property
    def figure_size(self) -> list:
        """Default figure size for charts"""
        return self.get("visualization.figure_size", [12, 8])

    @property
    def dpi(self) -> int:
        """DPI for chart outputs"""
        return self.get("visualization.dpi", 300)

    @property
    def primary_metrics(self) -> list:
        """Primary metrics for analysis"""
        return self.get(
            "metrics.primary_metrics",
            ["success_rate", "avg_execution_time", "avg_creation_time"],
        )

    @property
    def metric_weights(self) -> dict:
        """Weights for different metrics in scoring"""
        return self.get(
            "metrics.metric_weights",
            {"success_rate": 0.5, "avg_execution_time": 0.3, "avg_creation_time": 0.2},
        )

    @property
    def provider_display_names(self) -> dict:
        """Display names for providers"""
        return self.get("providers.display_names", {})

    @property
    def provider_colors(self) -> dict:
        """Colors for different providers in charts"""
        return self.get("providers.provider_colors", {})

    def get_provider_display_name(self, provider: str) -> str:
        """Get display name for a provider"""
        return self.provider_display_names.get(provider, provider.title())

    def get_provider_color(self, provider: str) -> str:
        """Get color for a provider"""
        colors = self.provider_colors
        if provider in colors:
            return colors[provider]

        # Fallback to color palette
        palette = self.color_palette
        provider_list = sorted(colors.keys()) if colors else []
        if provider not in provider_list:
            provider_list.append(provider)

        index = provider_list.index(provider) % len(palette)
        return palette[index]

    def get_regression_threshold(self, metric: str) -> float:
        """Get regression threshold for a specific metric"""
        thresholds = self.get("metrics.regression_thresholds", {})
        return thresholds.get(metric, self.comparison_threshold)

    def get_use_case_weights(self, use_case: str) -> dict:
        """Get metric weights for a specific use case"""
        use_case_weights = self.get("analysis.recommendation.use_case_weights", {})
        return use_case_weights.get(use_case, self.metric_weights)

    def is_regression_alerts_enabled(self) -> bool:
        """Check if regression alerts are enabled"""
        return self.get("notifications.regression_alerts", True)

    def get_alert_threshold(self, alert_type: str) -> float:
        """Get threshold for a specific alert type"""
        thresholds = self.get("notifications.alert_thresholds", {})
        return thresholds.get(alert_type, 0.0)


# Global configuration instance
_global_config = None


def get_config() -> AnalysisConfig:
    """Get the global configuration instance"""
    global _global_config
    if _global_config is None:
        _global_config = AnalysisConfig()
    return _global_config


def set_config(config: AnalysisConfig) -> None:
    """Set the global configuration instance"""
    global _global_config
    _global_config = config


def load_config(config_path: str | Path) -> AnalysisConfig:
    """Load configuration from a specific path"""
    return AnalysisConfig(config_path)
