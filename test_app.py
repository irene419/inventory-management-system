import pytest
from unittest.mock import Mock
import app as app_module
from app import app, inventory


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_inventory():
    inventory.clear()
    inventory.extend([
        {
            "id": 1,
            "name": "Organic Almond Milk",
            "brand": "Brookside Dairy",
            "price": 3.99,
            "stock": 25,
            "barcode": "0025293001165"
        },
        {
            "id": 2,
            "name": "Green Tea",
            "brand": "Ketepa",
            "price": 1.49,
            "stock": 40,
            "barcode": "0051500255511"
        }
    ])
    app_module.next_id = 3
    yield


def test_get_inventory(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
    assert len(response.get_json()) == 2


def test_get_single_item(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == 1


def test_get_single_item_not_found(client):
    response = client.get("/inventory/9999")
    assert response.status_code == 404


def test_add_item(client):
    new_item = {"name": "Test Cereal", "brand": "TestBrand", "price": 5.99, "stock": 10}
    response = client.post("/inventory", json=new_item)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Test Cereal"
    assert "id" in data


def test_add_item_missing_name(client):
    response = client.post("/inventory", json={"brand": "NoName"})
    assert response.status_code == 400


def test_update_item(client):
    response = client.patch("/inventory/1", json={"stock": 100})
    assert response.status_code == 200
    data = response.get_json()
    assert data["stock"] == 100
    assert data["name"] == "Organic Almond Milk"


def test_update_item_not_found(client):
    response = client.patch("/inventory/9999", json={"stock": 5})
    assert response.status_code == 404


def test_delete_item(client):
    response = client.delete("/inventory/2")
    assert response.status_code == 200

    check = client.get("/inventory/2")
    assert check.status_code == 404


def test_delete_item_not_found(client):
    response = client.delete("/inventory/9999")
    assert response.status_code == 404


def test_lookup_product_found(client, mocker):
    fake_response = Mock()
    fake_response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Nutella",
            "brands": "Ferrero",
            "ingredients_text": "Sugar, palm oil, hazelnuts"
        }
    }
    mocker.patch("app.requests.get", return_value=fake_response)

    response = client.get("/inventory/lookup/3017620422003")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Nutella"
    assert data["brand"] == "Ferrero"


def test_lookup_product_not_found(client, mocker):
    fake_response = Mock()
    fake_response.json.return_value = {"status": 0}
    mocker.patch("app.requests.get", return_value=fake_response)

    response = client.get("/inventory/lookup/0000000000000")
    assert response.status_code == 404


def test_lookup_and_add(client, mocker):
    fake_response = Mock()
    fake_response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Coca-Cola",
            "brands": "Coca-Cola Company"
        }
    }
    mocker.patch("app.requests.get", return_value=fake_response)

    response = client.post("/inventory/lookup/5449000000996")
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Coca-Cola"

    check = client.get("/inventory")
    names = [item["name"] for item in check.get_json()]
    assert "Coca-Cola" in names