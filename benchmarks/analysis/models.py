"""
Data models for benchmark analysis
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union


@dataclass
class ScenarioMetrics:
    """Metrics for a single test scenario"""

    name: str
    description: str
    success_rate: float
    avg_execution_time: float
    min_execution_time: float
    max_execution_time: float
    total_iterations: int
    successful_iterations: int
    failed_iterations: int
    errors: list[str] = field(default_factory=list)


@dataclass
class ProviderMetrics:
    """Comprehensive metrics for a provider"""

    provider_name: str
    overall_success_rate: float
    avg_creation_time: float
    avg_execution_time: float
    total_scenarios: int
    scenarios: dict[str, ScenarioMetrics] = field(default_factory=dict)
    benchmark_timestamp: datetime | None = None
    benchmark_duration: float | None = None
    status: str = "unknown"


@dataclass
class BenchmarkResult:
    """Complete benchmark result for analysis"""

    timestamp: datetime
    duration_seconds: float
    providers_tested: list[str]
    test_scenarios: int
    provider_results: dict[str, ProviderMetrics] = field(default_factory=dict)
    file_path: Path | None = None
    raw_data: dict[str, Any] | None = None


@dataclass
class ComparisonResult:
    """Result of comparing benchmark data"""

    comparison_type: str  # "provider", "time_series", "regression"
    baseline: str | datetime  # Provider name or timestamp
    target: str | datetime
    metrics_compared: list[str]
    improvements: dict[str, float] = field(default_factory=dict)
    regressions: dict[str, float] = field(default_factory=dict)
    summary: str = ""
    detailed_analysis: dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """Time-series trend analysis result"""

    metric_name: str
    provider: str | None
    time_period: str
    trend_direction: str  # "improving", "declining", "stable"
    trend_strength: float  # 0-1 scale
    data_points: list[dict[str, Any]] = field(default_factory=list)
    statistical_summary: dict[str, float] = field(default_factory=dict)


@dataclass
class ProviderRecommendation:
    """Provider recommendation based on analysis"""

    recommended_provider: str
    confidence_score: float
    reasoning: list[str] = field(default_factory=list)
    use_case_specific: dict[str, str] = field(default_factory=dict)
    performance_summary: dict[str, Any] = field(default_factory=dict)
