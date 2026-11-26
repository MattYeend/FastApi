import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app

PROTECTED_ENDPOINTS = ["/api/v1/users/", "/api/v1/products/"]


@pytest.mark.parametrize("url", PROTECTED_ENDPOINTS)
def test_missing_api_key_is_rejected(
    anonymous_client: TestClient, url: str
) -> None:
    response = anonymous_client.get(url)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "ApiKey"


@pytest.mark.parametrize("url", PROTECTED_ENDPOINTS)
def test_wrong_api_key_is_rejected(
    anonymous_client: TestClient, url: str
) -> None:
    response = anonymous_client.get(url, headers={"X-API-Key": "wrong"})

    assert response.status_code == 401


@pytest.mark.parametrize("url", PROTECTED_ENDPOINTS)
def test_valid_api_key_is_accepted(client: TestClient, url: str) -> None:
    response = client.get(url)

    assert response.status_code == 200


def test_unconfigured_api_key_fails_closed(
    anonymous_client: TestClient,
) -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        _env_file=None,
        api_key=None,
    )

    response = anonymous_client.get(
        "/api/v1/users/", headers={"X-API-Key": "anything"}
    )

    assert response.status_code == 503