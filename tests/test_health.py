from fastapi.testclient import TestClient


def test_health_returns_healthy(anonymous_client: TestClient) -> None:
    response = anonymous_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ready_checks_the_database(anonymous_client: TestClient) -> None:
    response = anonymous_client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_security_headers_are_added(anonymous_client: TestClient) -> None:
    response = anonymous_client.get("/health")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"