"""Service for aligning forecast and actual generation timeseries and calculating

quantitative forecasting accuracy metrics (MAE, RMSE, Bias, WAPE).
"""

from datetime import datetime
import math
from typing import Dict, List, Optional

from app.schemas.actual import ActualGenerationRecord
from app.schemas.analytics import (
    AccuracyMetrics,
    ComparisonResponse,
    ForecastActualComparisonPoint,
)
from app.schemas.forecast import ForecastRecord


class AnalyticsService:
    """Service for timeseries alignment and forecast accuracy analytics."""

    @staticmethod
    def align_records(
        forecasts: List[ForecastRecord],
        actuals: List[ActualGenerationRecord],
    ) -> List[ForecastActualComparisonPoint]:
        """Align selected forecasts and actual generation records using delivery start timestamps.

        Handles missing data gracefully:
        - If an actual is missing for a delivery window, forecast_mw is populated with actual_mw as None.
        - If a forecast is missing for a delivery window, actual_mw is populated with forecast_mw as None.
        - Error metrics are only calculated for complete pairs.

        Args:
            forecasts: List of selected forecast records.
            actuals: List of actual generation records.

        Returns:
            Chronologically sorted list of ForecastActualComparisonPoint objects.
        """
        forecast_by_start: Dict[datetime, ForecastRecord] = {f.start_time: f for f in forecasts}
        actual_by_start: Dict[datetime, ActualGenerationRecord] = {a.start_time: a for a in actuals}

        all_start_times = sorted(set(forecast_by_start.keys()) | set(actual_by_start.keys()))
        points: List[ForecastActualComparisonPoint] = []

        for start_dt in all_start_times:
            fc = forecast_by_start.get(start_dt)
            act = actual_by_start.get(start_dt)

            reference_obj = fc if fc is not None else act
            assert reference_obj is not None

            settlement_date = reference_obj.settlement_date
            settlement_period = reference_obj.settlement_period

            actual_val = act.generation_mw if act is not None else None
            forecast_val = fc.generation_mw if fc is not None else None

            if actual_val is not None and forecast_val is not None:
                error = round(forecast_val - actual_val, 3)
                abs_error = round(abs(forecast_val - actual_val), 3)
            else:
                error = None
                abs_error = None

            point = ForecastActualComparisonPoint(
                start_time=start_dt,
                settlement_date=settlement_date,
                settlement_period=settlement_period,
                actual_mw=actual_val,
                forecast_mw=forecast_val,
                error_mw=error,
                abs_error_mw=abs_error,
            )
            points.append(point)

        return points

    @staticmethod
    def calculate_accuracy_metrics(
        points: List[ForecastActualComparisonPoint],
        min_actual_sum_mw: float = 1.0,
    ) -> AccuracyMetrics:
        """Calculate quantitative accuracy metrics over aligned comparison points.

        Calculates:
        - MAE (Mean Absolute Error) in MW
        - RMSE (Root Mean Squared Error) in MW
        - Bias (Mean Error = Forecast - Actual) in MW
        - WAPE (Weighted Absolute Percentage Error = sum(|error|) / sum(actual) * 100%)

        To avoid misleading percentage metrics, WAPE is returned as None when
        total actual generation is zero or near-zero (< min_actual_sum_mw).

        Args:
            points: Aligned comparison points.
            min_actual_sum_mw: Minimum cumulative actual generation threshold
                below which percentage metrics are suppressed.

        Returns:
            AccuracyMetrics schema instance.
        """
        # Filter for intervals where both forecast and actual exist
        complete_pairs = [
            p
            for p in points
            if p.actual_mw is not None
            and p.forecast_mw is not None
            and p.error_mw is not None
            and p.abs_error_mw is not None
        ]

        n = len(complete_pairs)
        if n == 0:
            return AccuracyMetrics(
                mae=None,
                rmse=None,
                bias=None,
                wape_percent=None,
                sample_count=0,
            )

        abs_errors = [p.abs_error_mw for p in complete_pairs]
        signed_errors = [p.error_mw for p in complete_pairs]
        squared_errors = [p.error_mw**2 for p in complete_pairs]

        mae = round(sum(abs_errors) / n, 3)
        rmse = round(math.sqrt(sum(squared_errors) / n), 3)
        bias = round(sum(signed_errors) / n, 3)

        # Avoid misleading percentage metrics if actuals are near-zero or zero
        total_actual = sum(p.actual_mw for p in complete_pairs)
        if total_actual < min_actual_sum_mw:
            wape_percent = None
        else:
            wape_percent = round((sum(abs_errors) / total_actual) * 100.0, 2)

        return AccuracyMetrics(
            mae=mae,
            rmse=rmse,
            bias=bias,
            wape_percent=wape_percent,
            sample_count=n,
        )

    def compare(
        self,
        forecasts: List[ForecastRecord],
        actuals: List[ActualGenerationRecord],
        settlement_date: Optional[str] = None,
    ) -> ComparisonResponse:
        """Align series, calculate accuracy metrics, and assemble ComparisonResponse."""
        points = self.align_records(forecasts=forecasts, actuals=actuals)
        metrics = self.calculate_accuracy_metrics(points)
        return ComparisonResponse(
            points=points,
            metrics=metrics,
            settlement_date=settlement_date,
            sample_count=len(points),
        )
