from fastapi.testclient import TestClient

URL = "/api/v1/users/"


def create_user(
    client: TestClient,
    name: str = "Ada Lovelace",
    email: str = "ada@example.com",
) -> dict:
    response = client.post(URL, json={"name": name, "email": email})

    assert response.status_code == 201

    return response.json()


def test_create_user_normalises_the_email(client: TestClient) -> None:
    user = create_user(client, email="Ada@Example.COM")

    assert user["email"] == "ada@example.com"
    assert user["is_active"] is True


def test_create_user_rejects_a_duplicate_email(client: TestClient) -> None:
    create_user(client)

    response = client.post(
        URL, json={"name": "Someone Else", "email": "ada@example.com"}
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Email already registered"}


def test_create_user_duplicate_check_ignores_case(client: TestClient) -> None:
    create_user(client)

    response = client.post(
        URL, json={"name": "Someone Else", "email": "ADA@example.com"}
    )

    assert response.status_code == 409


def test_create_user_rejects_an_invalid_email(client: TestClient) -> None:
    response = client.post(URL, json={"name": "Ada", "email": "not-an-email"})

    assert response.status_code == 422


def test_create_user_rejects_an_overlong_email(client: TestClient) -> None:
    email = f"{'a' * 250}@example.com"

    response = client.post(URL, json={"name": "Ada", "email": email})

    assert response.status_code == 422


def test_create_user_rejects_unknown_fields(client: TestClient) -> None:
    response = client.post(
        URL,
        json={"name": "Ada", "email": "ada@example.com", "is_admin": True},
    )

    assert response.status_code == 422


def test_index_is_ordered_and_paginated(client: TestClient) -> None:
    for number in range(3):
        create_user(client, email=f"user{number}@example.com")

    response = client.get(URL, params={"skip": 1, "limit": 1})

    assert response.status_code == 200
    assert [user["email"] for user in response.json()] == ["user1@example.com"]


def test_index_rejects_an_invalid_limit(client: TestClient) -> None:
    assert client.get(URL, params={"limit": 0}).status_code == 422
    assert client.get(URL, params={"limit": 101}).status_code == 422


def test_show_returns_a_user(client: TestClient) -> None:
    user = create_user(client)

    response = client.get(f"{URL}{user['id']}")

    assert response.status_code == 200
    assert response.json() == user


def test_show_returns_404_for_a_missing_user(client: TestClient) -> None:
    assert client.get(f"{URL}999").status_code == 404


def test_update_changes_only_the_given_fields(client: TestClient) -> None:
    user = create_user(client)

    response = client.patch(f"{URL}{user['id']}", json={"is_active": False})

    assert response.status_code == 200
    assert response.json() == {**user, "is_active": False}


def test_put_also_updates_a_user(client: TestClient) -> None:
    user = create_user(client)

    response = client.put(f"{URL}{user['id']}", json={"name": "Grace Hopper"})

    assert response.status_code == 200
    assert response.json()["name"] == "Grace Hopper"


def test_update_allows_keeping_the_same_email(client: TestClient) -> None:
    user = create_user(client)

    response = client.patch(
        f"{URL}{user['id']}", json={"email": "Ada@example.com"}
    )

    assert response.status_code == 200


def test_update_rejects_an_email_owned_by_another_user(
    client: TestClient,
) -> None:
    create_user(client, email="first@example.com")
    second = create_user(client, email="second@example.com")

    response = client.patch(
        f"{URL}{second['id']}", json={"email": "first@example.com"}
    )

    assert response.status_code == 409


def test_update_rejects_explicit_nulls(client: TestClient) -> None:
    user = create_user(client)

    for field in ("name", "email", "is_active"):
        response = client.patch(f"{URL}{user['id']}", json={field: None})

        assert response.status_code == 422, field


def test_update_returns_404_for_a_missing_user(client: TestClient) -> None:
    response = client.patch(f"{URL}999", json={"name": "Nobody"})

    assert response.status_code == 404


def test_destroy_deletes_a_user(client: TestClient) -> None:
    user = create_user(client)

    assert client.delete(f"{URL}{user['id']}").status_code == 204
    assert client.get(f"{URL}{user['id']}").status_code == 404


def test_destroy_returns_404_for_a_missing_user(client: TestClient) -> None:
    assert client.delete(f"{URL}999").status_code == 404