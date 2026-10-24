"""Service for processing, normalizing, and selecting wind generation forecast records

based on purchasing decision times and delivery horizons.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union

from app.schemas.forecast import ForecastRecord
from app.utils.datetime_utils import ensure_utc, parse_timestamp


class ForecastService:
    """Service for normalizing and selecting wind generation forecasts."""

    @staticmethod
    def normalize_record(raw: Union[Dict[str, Any], ForecastRecord]) -> ForecastRecord:
        """Validate and convert raw dictionary or instance into a ForecastRecord."""
        if isinstance(raw, ForecastRecord):
            return raw

        start_time = parse_timestamp(raw["start_time"], default_tz=timezone.utc)
        publish_time = parse_timestamp(raw["publish_time"], default_tz=timezone.utc)

        return ForecastRecord(
            start_time=start_time,
            publish_time=publish_time,
            settlement_date=str(raw["settlement_date"]),
            settlement_period=int(raw["settlement_period"]),
            generation_mw=float(raw["generation_mw"]),
            fuel_type=str(raw.get("fuel_type", "WIND")),
        )

    def normalize_records(
        self,
        raw_list: List[Union[Dict[str, Any], ForecastRecord]],
    ) -> List[ForecastRecord]:
        """Normalize a list of raw forecast items into validated ForecastRecord models."""
        normalized: List[ForecastRecord] = []
        for item in raw_list:
            try:
                rec = self.normalize_record(item)
                normalized.append(rec)
            except (ValueError, KeyError, TypeError):
                # Omit unparseable or invalid records
                continue
        normalized.sort(key=lambda r: (r.start_time, r.publish_time))
        return normalized

    @staticmethod
    def select_forecasts_for_decision_time(
        records: List[ForecastRecord],
        decision_time: datetime,
    ) -> List[ForecastRecord]:
        """Select the most recent forecast available at a specified purchasing decision time.

        Strictly enforces anti-leakage rules:
        - Only forecasts with publish_time <= decision_time are considered.
        - Only forecasts with publish_time <= start_time are considered.
        - For each distinct delivery start_time, the record with the latest publish_time
          prior to or at decision_time is selected.

        Args:
            records: List of available forecast records.
            decision_time: Cutoff timestamp representing when the purchasing decision occurred.

        Returns:
            List of selected ForecastRecord items, one per delivery start_time,
            ordered chronologically by delivery start_time.
        """
        utc_decision = ensure_utc(decision_time, assume_utc=False)

        # Group valid candidates by delivery start_time
        candidates_by_start: Dict[datetime, List[ForecastRecord]] = {}
        for rec in records:
            # Reconstruct what was available at decision time: never select publish_time > decision_time
            if rec.publish_time <= utc_decision and rec.publish_time <= rec.start_time:
                candidates_by_start.setdefault(rec.start_time, []).append(rec)

        # For each start_time, pick the record that maximizes publish_time
        selected: List[ForecastRecord] = []
        for start_dt, cands in candidates_by_start.items():
            # In case of tie on publish_time, choose highest generation or stable tie-break
            best = max(cands, key=lambda r: (r.publish_time, r.generation_mw))
            selected.append(best)

        selected.sort(key=lambda r: r.start_time)
        return selected

    @classmethod
    def select_day_ahead_forecasts(
        cls,
        records: List[ForecastRecord],
        settlement_date: str,
        gate_closure_hour_utc: int = 17,
    ) -> List[ForecastRecord]:
        """Select the day-ahead forecast view for a given settlement date.

        Day-ahead decision time is defined as (settlement_date - 1 day) at gate_closure_hour_utc (default: 17:00 UTC).

        Args:
            records: Candidate forecast records.
            settlement_date: Target settlement date (YYYY-MM-DD).
            gate_closure_hour_utc: Day-ahead market gate closure hour in UTC (default: 17).

        Returns:
            List of selected day-ahead forecasts for the settlement date.
        """
        target_date = datetime.strptime(settlement_date, "%Y-%m-%d").date()
        day_before = target_date - timedelta(days=1)
        decision_time = datetime(
            day_before.year,
            day_before.month,
            day_before.day,
            gate_closure_hour_utc,
            0,
            0,
            tzinfo=timezone.utc,
        )

        # Filter candidates matching the target settlement_date
        date_records = [r for r in records if r.settlement_date == settlement_date]
        return cls.select_forecasts_for_decision_time(date_records, decision_time=decision_time)

    @staticmethod
    def select_gate_closure_forecasts(
        records: List[ForecastRecord],
        lead_hours: float = 1.0,
    ) -> List[ForecastRecord]:
        """Select forecasts available at intraday gate closure (e.g., 1 hour before delivery).

        For each delivery start_time, cutoff = start_time - lead_hours.
        The latest forecast published on or before that cutoff is chosen.

        Args:
            records: Candidate forecast records.
            lead_hours: Hours prior to delivery start_time for gate closure (default 1.0h).

        Returns:
            List of selected gate closure forecasts.
        """
        lead_delta = timedelta(hours=lead_hours)
        candidates_by_start: Dict[datetime, List[ForecastRecord]] = {}

        for rec in records:
            cutoff = rec.start_time - lead_delta
            if rec.publish_time <= cutoff and rec.publish_time <= rec.start_time:
                candidates_by_start.setdefault(rec.start_time, []).append(rec)

        selected: List[ForecastRecord] = []
        for start_dt, cands in candidates_by_start.items():
            best = max(cands, key=lambda r: (r.publish_time, r.generation_mw))
            selected.append(best)

        selected.sort(key=lambda r: r.start_time)
        return selected
