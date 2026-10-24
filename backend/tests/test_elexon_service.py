import httpx
import pytest

from app.services.elexon_service import (
    ElexonAPIError,
    ElexonError,
    ElexonService,
    ElexonTimeoutError,
)


@pytest.mark.anyio
async def test_get_actual_wind_generation_success():
    """Verify parsing and filtering of FUELHH wind actuals."""
    sample_fuelhh_response = {
        "data": [
            {
                "dataset": "FUELHH",
                "publishTime": "2026-01-01T00:35:00Z",
                "settlementDate": "2026-01-01",
                "settlementPeriod": 1,
                "fuelType": "WIND",
                "generation": 1250.0,
            },
            {
                "dataset": "FUELHH",
                "publishTime": "2026-01-01T00:35:00Z",
                "settlementDate": "2026-01-01",
                "settlementPeriod": 1,
                "fuelType": "CCGT",
                "generation": 4500.0,
            },
            {
                "dataset": "FUELHH",
                "publishTime": "2026-01-01T01:05:00Z",
                "settlementDate": "2026-01-01",
                "settlementPeriod": 2,
                "fuelType": "WIND",
                "generation": 1300.5,
            },
        ]
    }

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        assert "datasets/FUELHH" in str(request.url)
        assert request.url.params.get("settlementDate") == "2026-01-01"
        return httpx.Response(200, json=sample_fuelhh_response)

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        service = ElexonService(client=client, base_url="https://mock.elexon.test")
        records = await service.get_actual_wind_generation("2026-01-01")

    # Only WIND records should be returned (2 out of 3)
    assert len(records) == 2
    assert records[0].settlement_period == 1
    assert records[0].generation_mw == 1250.0
    assert records[0].fuel_type == "WIND"
    assert records[1].settlement_period == 2
    assert records[1].generation_mw == 1300.5


@pytest.mark.anyio
async def test_get_wind_forecasts_success():
    """Verify parsing and anti-leakage handling of WINDFOR forecasts."""
    sample_windfor_response = {
        "data": [
            {
                "publishTime": "2025-12-31T17:00:00Z",
                "startTime": "2026-01-01T00:00:00Z",
                "settlementDate": "2026-01-01",
                "settlementPeriod": 1,
                "generation": 1200.0,
            },
            # Invalid lookahead entry (publishTime > startTime) should be skipped
            {
                "publishTime": "2026-01-01T01:00:00Z",
                "startTime": "2026-01-01T00:00:00Z",
                "settlementDate": "2026-01-01",
                "settlementPeriod": 1,
                "generation": 1500.0,
            },
            {
                "publishTime": "2025-12-31T23:00:00Z",
                "startTime": "2026-01-01T00:00:00Z",
                "settlementDate": "2026-01-01",
                "settlementPeriod": 1,
                "generation": 1280.0,
            },
        ]
    }

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        assert "datasets/WINDFOR" in str(request.url)
        return httpx.Response(200, json=sample_windfor_response)

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        service = ElexonService(client=client, base_url="https://mock.elexon.test")
        records = await service.get_wind_forecasts(settlement_date="2026-01-01")

    # The lookahead violation record is filtered out, leaving 2 valid records
    assert len(records) == 2
    assert records[0].publish_time.hour == 17
    assert records[1].publish_time.hour == 23


@pytest.mark.anyio
async def test_elexon_api_http_error():
    """Non-200 responses should raise ElexonAPIError."""

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(502, text="Upstream gateway error")

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        service = ElexonService(client=client, base_url="https://mock.elexon.test")
        with pytest.raises(ElexonAPIError) as exc:
            await service.get_actual_wind_generation("2026-01-01")

    assert exc.value.status_code == 502


@pytest.mark.anyio
async def test_elexon_timeout_error():
    """Timeouts should raise ElexonTimeoutError."""

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("Read timed out")

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        service = ElexonService(client=client, base_url="https://mock.elexon.test")
        with pytest.raises(ElexonTimeoutError):
            await service.get_actual_wind_generation("2026-01-01")


@pytest.mark.anyio
async def test_january_2026_convenience_methods():
    """Verify January 2026 convenience helpers format settlement dates properly."""
    requested_dates = []

    async def mock_handler(request: httpx.Request) -> httpx.Response:
        date = request.url.params.get("settlementDate")
        requested_dates.append(date)
        return httpx.Response(200, json={"data": []})

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        service = ElexonService(client=client, base_url="https://mock.elexon.test")
        await service.get_january_2026_wind_actuals(day=5)
        await service.get_january_2026_wind_forecasts(day=15)

    assert requested_dates == ["2026-01-05", "2026-01-15"]
