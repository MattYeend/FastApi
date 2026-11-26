from decimal import Decimal

from fastapi.testclient import TestClient

URL = "/api/v1/products/"


def create_product(
    client: TestClient,
    name: str = "Widget",
    price: str = "9.99",
    stock: int = 5,
) -> dict:
    response = client.post(
        URL, json={"name": name, "price": price, "stock": stock}
    )

    assert response.status_code == 201

    return response.json()


def test_create_product(client: TestClient) -> None:
    product = create_product(client)

    assert product["name"] == "Widget"
    assert Decimal(product["price"]) == Decimal("9.99")
    assert product["stock"] == 5
    assert product["description"] is None


def test_create_product_defaults_stock_to_zero(client: TestClient) -> None:
    response = client.post(URL, json={"name": "Widget", "price": "1.00"})

    assert response.status_code == 201
    assert response.json()["stock"] == 0


def test_create_product_rejects_invalid_values(client: TestClient) -> None:
    invalid_payloads = [
        {"name": "Widget", "price": "0"},
        {"name": "Widget", "price": "-1"},
        {"name": "Widget", "price": "1.005"},
        {"name": "Widget", "price": "123456789.00"},
        {"name": "Widget", "price": "1.00", "stock": -1},
        {"name": "W", "price": "1.00"},
        {"name": "Widget", "price": "1.00", "unknown": "value"},
    ]

    for payload in invalid_payloads:
        assert client.post(URL, json=payload).status_code == 422, payload


def test_index_is_ordered_and_paginated(client: TestClient) -> None:
    for number in range(3):
        create_product(client, name=f"Product {number}")

    response = client.get(URL, params={"skip": 1, "limit": 1})

    assert response.status_code == 200
    assert [product["name"] for product in response.json()] == ["Product 1"]


def test_index_rejects_an_invalid_limit(client: TestClient) -> None:
    assert client.get(URL, params={"limit": 0}).status_code == 422
    assert client.get(URL, params={"limit": 101}).status_code == 422


def test_show_returns_a_product(client: TestClient) -> None:
    product = create_product(client)

    response = client.get(f"{URL}{product['id']}")

    assert response.status_code == 200
    assert response.json() == product


def test_show_returns_404_for_a_missing_product(client: TestClient) -> None:
    assert client.get(f"{URL}999").status_code == 404


def test_update_changes_only_the_given_fields(client: TestClient) -> None:
    product = create_product(client)

    response = client.patch(f"{URL}{product['id']}", json={"stock": 20})

    assert response.status_code == 200
    assert response.json() == {**product, "stock": 20}


def test_put_also_updates_a_product(client: TestClient) -> None:
    product = create_product(client)

    response = client.put(f"{URL}{product['id']}", json={"name": "Gadget"})

    assert response.status_code == 200
    assert response.json()["name"] == "Gadget"


def test_update_can_clear_the_description(client: TestClient) -> None:
    product = create_product(client)
    client.patch(f"{URL}{product['id']}", json={"description": "Useful"})

    response = client.patch(f"{URL}{product['id']}", json={"description": None})

    assert response.status_code == 200
    assert response.json()["description"] is None


def test_update_rejects_explicit_nulls(client: TestClient) -> None:
    product = create_product(client)

    for field in ("name", "price", "stock"):
        response = client.patch(f"{URL}{product['id']}", json={field: None})

        assert response.status_code == 422, field


def test_update_returns_404_for_a_missing_product(
    client: TestClient,
) -> None:
    assert client.patch(f"{URL}999", json={"stock": 1}).status_code == 404


def test_destroy_deletes_a_product(client: TestClient) -> None:
    product = create_product(client)

    assert client.delete(f"{URL}{product['id']}").status_code == 204
    assert client.get(f"{URL}{product['id']}").status_code == 404


def test_destroy_returns_404_for_a_missing_product(
    client: TestClient,
) -> None:
    assert client.delete(f"{URL}999").status_code == 404