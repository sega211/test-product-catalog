from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_pr0ducts():
    response = client.get("/products")

    assert response.status_code ==200
    assert isinstance(response.json(), list)

def test_create_product():
    response = client.post(
        "products",
        json={"title": "Тест продукта"}
    )

    assert response.status_code ==201
    data = response.json()
    assert data["title"]== "Тест продукта"
    assert isinstance(data["id"], int)

def test_create_product_rejects_blank_title():
    response = client.post(
        "/products",
        json={"title": "  "}
    )

    assert response.status_code == 422

def test_get_missing_product():
    response = client.get("/products/99999999")

    assert response.status_code == 404

