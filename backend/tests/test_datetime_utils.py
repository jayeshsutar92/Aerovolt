from datetime import datetime, timezone, timedelta
import pytest

from app.utils.datetime_utils import (
    ensure_utc,
    format_utc_iso,
    parse_timestamp,
    validate_delivery_window,
)


def test_ensure_utc_aware():
    """Timezone-aware datetime should be converted to UTC."""
    offset = timezone(timedelta(hours=2))
    dt = datetime(2026, 10, 24, 14, 0, 0, tzinfo=offset)
    utc_dt = ensure_utc(dt)

    assert utc_dt.tzinfo == timezone.utc
    assert utc_dt.hour == 12


def test_ensure_utc_naive_raises():
    """Naive datetime should raise ValueError when assume_utc is False."""
    dt = datetime(2026, 10, 24, 12, 0, 0)
    with pytest.raises(ValueError) as exc:
        ensure_utc(dt, assume_utc=False)
    assert "Naive datetime encountered" in str(exc.value)


def test_ensure_utc_naive_assume_utc():
    """Naive datetime should be assigned UTC when assume_utc is True."""
    dt = datetime(2026, 10, 24, 12, 0, 0)
    utc_dt = ensure_utc(dt, assume_utc=True)

    assert utc_dt.tzinfo == timezone.utc
    assert utc_dt.hour == 12


def test_parse_timestamp_iso_z():
    """Parse ISO timestamp ending with 'Z' as UTC."""
    res = parse_timestamp("2026-10-24T15:30:00Z")
    assert res.tzinfo == timezone.utc
    assert res.year == 2026
    assert res.month == 10
    assert res.day == 24
    assert res.hour == 15
    assert res.minute == 30


def test_parse_timestamp_iso_offset():
    """Parse ISO timestamp with positive offset and convert to UTC."""
    res = parse_timestamp("2026-10-24T17:00:00+02:00")
    assert res.tzinfo == timezone.utc
    assert res.hour == 15


def test_parse_timestamp_naive_string_raises():
    """Parsing naive timestamp string without default_tz must raise ValueError."""
    with pytest.raises(ValueError) as exc:
        parse_timestamp("2026-10-24 15:00:00")
    assert "lacks timezone offset" in str(exc.value)


def test_parse_timestamp_naive_string_with_default_tz():
    """Parsing naive timestamp with default_tz assigns timezone and converts to UTC."""
    tz = timezone(timedelta(hours=1))
    res = parse_timestamp("2026-10-24 15:00:00", default_tz=tz)
    assert res.tzinfo == timezone.utc
    assert res.hour == 14


def test_parse_timestamp_datetime_object():
    """Passing a timezone-aware datetime object returns UTC."""
    dt = datetime(2026, 10, 24, 12, 0, tzinfo=timezone.utc)
    res = parse_timestamp(dt)
    assert res == dt


def test_parse_timestamp_invalid_string():
    """Malformed timestamp strings should raise ValueError."""
    with pytest.raises(ValueError) as exc:
        parse_timestamp("not-a-timestamp")
    assert "Invalid timestamp format" in str(exc.value)


def test_parse_timestamp_invalid_type():
    """Passing invalid types should raise TypeError."""
    with pytest.raises(TypeError) as exc:
        parse_timestamp(123456789)  # type: ignore[arg-type]
    assert "Unsupported timestamp type" in str(exc.value)


def test_format_utc_iso():
    """UTC datetimes should be formatted as ISO 8601 strings ending with 'Z'."""
    dt = datetime(2026, 10, 24, 12, 30, 0, tzinfo=timezone.utc)
    formatted = format_utc_iso(dt)
    assert formatted == "2026-10-24T12:30:00Z"


def test_validate_delivery_window_valid():
    """publish_time on or before start_time should succeed without error."""
    start = datetime(2026, 10, 24, 12, 0, tzinfo=timezone.utc)
    pub = datetime(2026, 10, 24, 8, 0, tzinfo=timezone.utc)
    validate_delivery_window(start, pub)

    # Identical timestamps are also valid
    validate_delivery_window(start, start)


def test_validate_delivery_window_lookahead_violation():
    """publish_time after start_time must raise ValueError."""
    start = datetime(2026, 10, 24, 12, 0, tzinfo=timezone.utc)
    pub = datetime(2026, 10, 24, 13, 0, tzinfo=timezone.utc)
    with pytest.raises(ValueError) as exc:
        validate_delivery_window(start, pub)
    assert "Lookahead violation" in str(exc.value)
