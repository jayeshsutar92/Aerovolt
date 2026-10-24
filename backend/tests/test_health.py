from fastapi.testclient import TestClient


def test_health_check_endpoint(client: TestClient):
    """GET /api/health should return 200 with structured health metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "Aerovolt"
    assert "environment" in data
    assert "version" in data


def test_root_endpoint(client: TestClient):
    """GET / should return 200 with service message and endpoint links."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "Aerovolt" in data["message"]
    assert data["health_check"] == "/api/health"


def test_cors_headers_allowed_origin(client: TestClient):
    """CORS requests from configured local development origin should be permitted."""
    origin = "http://localhost:5173"
    response = client.get("/api/health", headers={"Origin": origin})

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin


def test_cors_headers_disallowed_origin(client: TestClient):
    """CORS requests from unauthorized origins should not receive access-control-allow-origin."""
    origin = "http://malicious-site.example.com"
    response = client.get("/api/health", headers={"Origin": origin})

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") != origin
