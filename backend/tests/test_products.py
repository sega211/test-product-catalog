import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.models import Product

test_database_url = os.environ.get("TEST_DATABASE_URL")
if not test_database_url:
    raise RuntimeError("Не задана переменная TEST_DATABASE_URL")


parsed_test_url = make_url(test_database_url)

if parsed_test_url.database != "catalog_test":
    raise RuntimeError("Тесты разрешено запускать только с БД catalog_test")

test_engine = create_engine(test_database_url, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False
)

@pytest.fixture(autouse=True)
def clean_test_product():
    with TestingSessionLocal() as db:
        db.execute(delete(Product))
        db.commit()
    yield

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)

def test_list_products(client):
    response = client.get("/products")

    assert response.status_code ==200
    assert isinstance(response.json(), list)

def test_create_product(client):
    response = client.post(
        "/products",
        json={"title": "Тест продукта"}
    )

    assert response.status_code ==201
    data = response.json()
    assert data["title"]== "Тест продукта"
    assert isinstance(data["id"], int)

def test_create_product_rejects_blank_title(client):
    response = client.post(
        "/products",
        json={"title": "  "}
    )

    assert response.status_code == 422

def test_get_missing_product(client):
    response = client.get("/products/99999999")

    assert response.status_code == 404

@pytest.fixture(scope="module", autouse=True)
def dispose_test_engine():
    yield
    test_engine.dispose()

