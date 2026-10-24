"""Elexon BMRS API client service for retrieving UK national wind generation

actuals (FUELHH) and forecasts (WINDFOR).
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union
import httpx

from app.core.config import get_settings
from app.schemas.actual import ActualGenerationRecord
from app.schemas.forecast import ForecastRecord
from app.utils.datetime_utils import format_utc_iso, parse_timestamp


class ElexonError(Exception):
    """Base exception for Elexon API integration errors."""


class ElexonAPIError(ElexonError):
    """Exception raised when Elexon returns an HTTP error or malformed payload."""

    def __init__(self, status_code: int, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"Elexon API error {status_code}: {message}")
        self.status_code = status_code
        self.message = message
        self.details = details or {}


class ElexonTimeoutError(ElexonError):
    """Exception raised when an Elexon API request times out."""


class ElexonService:
    """Service for interacting with Elexon Insights Solution (BMRS) endpoints."""

    def __init__(
        self,
        client: Optional[httpx.AsyncClient] = None,
        base_url: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ):
        settings = get_settings()
        self.base_url = (base_url or settings.elexon_base_url).rstrip("/")
        self.timeout_seconds = timeout_seconds or settings.elexon_timeout_seconds
        self._external_client = client

    async def _request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Execute an asynchronous HTTP GET request to Elexon BMRS."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        query_params = {k: v for k, v in (params or {}).items() if v is not None}
        headers = {"Accept": "application/json"}

        client = self._external_client
        close_client = False
        if client is None:
            client = httpx.AsyncClient(timeout=self.timeout_seconds)
            close_client = True

        try:
            response = await client.get(url, params=query_params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as err:
            raise ElexonTimeoutError(
                f"Elexon API request timed out after {self.timeout_seconds} seconds."
            ) from err
        except httpx.HTTPStatusError as err:
            raise ElexonAPIError(
                status_code=err.response.status_code,
                message=f"Request to {endpoint} failed: {err.response.text}",
                details={"url": str(err.request.url)},
            ) from err
        except httpx.RequestError as err:
            raise ElexonError(f"Network error communicating with Elexon API: {err}") from err
        finally:
            if close_client:
                await client.aclose()

    @staticmethod
    def _extract_data_list(payload: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Extract records array from Elexon standard or stream JSON responses."""
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            data = payload.get("data")
            if isinstance(data, list):
                return data
        return []

    async def get_actual_wind_generation(
        self,
        settlement_date: str,
    ) -> List[ActualGenerationRecord]:
        """Fetch actual half-hourly wind generation (FUELHH dataset) for a settlement date.

        Args:
            settlement_date: UK settlement date formatted as YYYY-MM-DD.

        Returns:
            List of validated ActualGenerationRecord instances sorted by start_time.
        """
        params = {
            "settlementDate": settlement_date,
            "format": "json",
        }
        payload = await self._request("datasets/FUELHH", params=params)
        raw_items = self._extract_data_list(payload)

        records: List[ActualGenerationRecord] = []
        base_utc = datetime.strptime(settlement_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)

        for item in raw_items:
            fuel_type = str(item.get("fuelType", "")).strip().upper()
            if fuel_type != "WIND":
                continue

            period_raw = item.get("settlementPeriod")
            if period_raw is None:
                continue

            settlement_period = int(period_raw)
            gen_val = item.get("generation")
            generation_mw = max(0.0, float(gen_val)) if gen_val is not None else 0.0

            # Derive delivery startTime if absent in the FUELHH feed
            if item.get("startTime"):
                start_time = parse_timestamp(item["startTime"], default_tz=timezone.utc)
            else:
                start_time = base_utc + timedelta(minutes=(settlement_period - 1) * 30)

            rec = ActualGenerationRecord(
                start_time=start_time,
                settlement_date=settlement_date,
                settlement_period=settlement_period,
                generation_mw=generation_mw,
                fuel_type="WIND",
            )
            records.append(rec)

        # Sort chronologically by start_time
        records.sort(key=lambda r: r.start_time)
        return records

    async def get_wind_forecasts(
        self,
        settlement_date: Optional[str] = None,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
    ) -> List[ForecastRecord]:
        """Fetch wind generation forecasts (WINDFOR dataset) from Elexon BMRS.

        Args:
            settlement_date: Filter by UK settlement date (YYYY-MM-DD).
            from_time: Filter records published from this timestamp.
            to_time: Filter records published up to this timestamp.

        Returns:
            List of validated ForecastRecord instances sorted by start_time then publish_time.
        """
        params: Dict[str, Any] = {"format": "json"}
        if settlement_date:
            params["settlementDate"] = settlement_date
        if from_time:
            params["publishDateTimeFrom"] = format_utc_iso(from_time)
        if to_time:
            params["publishDateTimeTo"] = format_utc_iso(to_time)

        payload = await self._request("datasets/WINDFOR", params=params)
        raw_items = self._extract_data_list(payload)

        records: List[ForecastRecord] = []
        for item in raw_items:
            if not item.get("publishTime") or not item.get("startTime"):
                continue

            publish_time = parse_timestamp(item["publishTime"], default_tz=timezone.utc)
            start_time = parse_timestamp(item["startTime"], default_tz=timezone.utc)

            # Strictly reject invalid lookahead records from upstream feeds
            if publish_time > start_time:
                continue

            s_date = item.get("settlementDate") or start_time.strftime("%Y-%m-%d")
            s_period_raw = item.get("settlementPeriod")
            if s_period_raw is not None:
                settlement_period = int(s_period_raw)
            else:
                settlement_period = ((start_time.hour * 60 + start_time.minute) // 30) + 1

            if not (1 <= settlement_period <= 50):
                continue

            gen_val = item.get("generation")
            generation_mw = max(0.0, float(gen_val)) if gen_val is not None else 0.0

            rec = ForecastRecord(
                start_time=start_time,
                publish_time=publish_time,
                settlement_date=s_date,
                settlement_period=settlement_period,
                generation_mw=generation_mw,
                fuel_type="WIND",
            )
            records.append(rec)

        records.sort(key=lambda r: (r.start_time, r.publish_time))
        return records

    async def get_january_2026_wind_actuals(self, day: int = 1) -> List[ActualGenerationRecord]:
        """Convenience helper to retrieve national wind actuals for January 2026."""
        settlement_date = f"2026-01-{day:02d}"
        return await self.get_actual_wind_generation(settlement_date=settlement_date)

    async def get_january_2026_wind_forecasts(self, day: int = 1) -> List[ForecastRecord]:
        """Convenience helper to retrieve national wind forecasts for January 2026."""
        settlement_date = f"2026-01-{day:02d}"
        return await self.get_wind_forecasts(settlement_date=settlement_date)
