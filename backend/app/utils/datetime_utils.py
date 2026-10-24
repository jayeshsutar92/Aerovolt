"""Narrowly scoped datetime utilities for timestamp parsing, UTC normalization,

and delivery-window validation in Aerovolt.
"""

from datetime import datetime, timezone
from typing import Optional, Union


def ensure_utc(dt: datetime, assume_utc: bool = False) -> datetime:
    """Ensure a datetime is timezone-aware and normalized to UTC.

    Args:
        dt: The datetime to normalize.
        assume_utc: If True, naive datetimes are assumed to be UTC.
            If False (default), naive datetimes raise ValueError to avoid
            silently misinterpreting timezone context.

    Returns:
        Timezone-aware datetime normalized to UTC.

    Raises:
        ValueError: If a naive datetime is encountered and assume_utc is False.
    """
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        if assume_utc:
            return dt.replace(tzinfo=timezone.utc)
        raise ValueError(
            f"Naive datetime encountered: '{dt}'. Timezone information is required "
            "to prevent ambiguous timestamp interpretation."
        )
    return dt.astimezone(timezone.utc)


def parse_timestamp(
    value: Union[str, datetime],
    default_tz: Optional[timezone] = None,
) -> datetime:
    """Parse and normalize an external timestamp into a UTC-aware datetime.

    Accepts ISO 8601 strings (e.g. '2026-10-24T12:00:00Z', '2026-10-24 12:00:00+01:00')
    or datetime objects.

    Args:
        value: Input timestamp as string or datetime.
        default_tz: Optional fallback timezone applied only when the parsed
            input is naive. If None and the parsed input is naive, raises ValueError.

    Returns:
        A timezone-aware datetime in UTC.

    Raises:
        TypeError: If value is not a str or datetime.
        ValueError: If value is empty, malformed, or naive without default_tz.
    """
    if isinstance(value, datetime):
        if value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None:
            return value.astimezone(timezone.utc)
        if default_tz is not None:
            return value.replace(tzinfo=default_tz).astimezone(timezone.utc)
        raise ValueError(
            f"Naive datetime object '{value}' lacks timezone information. "
            "An explicit timezone is required."
        )

    if isinstance(value, str):
        clean_str = value.strip()
        if not clean_str:
            raise ValueError("Timestamp string cannot be empty or whitespace.")

        try:
            parsed = datetime.fromisoformat(clean_str)
        except ValueError as err:
            raise ValueError(
                f"Invalid timestamp format '{value}'. Expected ISO 8601 string."
            ) from err

        if parsed.tzinfo is not None and parsed.tzinfo.utcoffset(parsed) is not None:
            return parsed.astimezone(timezone.utc)

        if default_tz is not None:
            return parsed.replace(tzinfo=default_tz).astimezone(timezone.utc)

        raise ValueError(
            f"Parsed timestamp '{value}' lacks timezone offset. "
            "An explicit timezone is required to prevent ambiguous timestamp interpretation."
        )

    raise TypeError(
        f"Unsupported timestamp type: {type(value).__name__}. Expected str or datetime."
    )


def format_utc_iso(dt: datetime) -> str:
    """Format a datetime as an ISO 8601 UTC string with trailing 'Z'.

    Args:
        dt: The datetime to format (naive or aware).

    Returns:
        ISO 8601 formatted string, e.g. '2026-10-24T12:00:00Z'.
    """
    utc_dt = ensure_utc(dt, assume_utc=True) if dt.tzinfo is None else ensure_utc(dt)
    iso = utc_dt.isoformat()
    if iso.endswith("+00:00"):
        return iso[:-6] + "Z"
    return iso


def validate_delivery_window(start_time: datetime, publish_time: datetime) -> None:
    """Validate that forecast publication time does not violate anti-leakage rules.

    In electricity markets, a forecast is only valid if published prior to or at
    the start of the target delivery window (publish_time <= start_time).

    Args:
        start_time: Target delivery start timestamp in UTC.
        publish_time: Forecast publication timestamp in UTC.

    Raises:
        ValueError: If publish_time > start_time.
    """
    utc_start = ensure_utc(start_time, assume_utc=False)
    utc_pub = ensure_utc(publish_time, assume_utc=False)

    if utc_pub > utc_start:
        raise ValueError(
            f"Forecast publication time ({utc_pub.isoformat()}) cannot be after "
            f"the delivery start time ({utc_start.isoformat()}). Lookahead violation."
        )
