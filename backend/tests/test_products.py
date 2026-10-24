import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy import create_engine, delete
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.models import Product
from io import BytesIO
from PIL import Image
from botocore.exceptions import BotoCoreError

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

def test_get_image_for_missing_products_returns_404(client):
    response = client.get("/products/999999999/image")

    assert response.status_code == 404
    assert response.json()["detail"] == "Товар не найден"

def test_get_image_without_image_key_returns_404(client):
    response = client.post(
        "/products",
        json={"title": "Товар без изображения"}
    )

    assert response.status_code == 201

    product_id = response.json()["id"]
    response = client.get(f"/products/{product_id}/image")

    assert response.status_code == 404
    assert response.json()["detail"] == "У товара нет изображения"

def test_get_product_image_returns_image(client):
    image_content = b"fake-image-content"

    response = client.post(
        "/products",
        json={"title": "товар с изображением"}
    )

    assert response.status_code == 201

    product_id = response.json()["id"]

    with TestingSessionLocal() as db:
        product = db.get(Product, product_id)
        assert product is not None
        product.image_key = "test/image.png"
        db.commit()

    with patch(
        "app.main.read_image",
        return_value = (image_content, "image/png")
    ) as mocked_read_image:
        response = client.get(f"/products/{product_id}/image")
    assert response.status_code ==200
    assert response.content == image_content
    assert response.headers["content-type"] == "image/png"
    assert response.headers["cache-control"] == "private, max-age=300"
    mocked_read_image.assert_called_once_with("test/image.png")

def test_create_product_with_image(client):
    image_buffer = BytesIO()
    Image.new("RGB", (2, 2), color="red").save(
        image_buffer,
        format="PNG",
    )
    image_content = image_buffer.getvalue()

    with patch("app.main.upload_image") as mock_upload:
        response = client.post(
            "/products/with-image",
            data={"title": "Товар с фото"},
            files={
                "image": (
                    "test.png",
                    image_content,
                    "image/png",
                )
            },
        )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Товар с фото"

    with TestingSessionLocal() as db:
        product = db.get(Product, data["id"])
        assert product is not None
        assert product.image_key.startswith("products/")
        assert product.image_key.endswith(".png")

    mock_upload.assert_called_once()
    args = mock_upload.call_args.args
    assert args[0] == product.image_key
    assert args[1] == image_content
    assert args[2] == "image/png"

def test_create_product_with_invalid_image_returns_422(client):
    with patch("app.main.upload_image") as mock_upload:
        response = client.post(
            "/products/with-image",
            data={"title": "Товар с неверным файлом"},
            files={
                "image": (
                    "invalid.png",
                    b"this is not an image",
                    "image/png",
                )
            },
        )

    assert response.status_code == 422
    mock_upload.assert_not_called()

def test_create_product_with_image_storage_error_returns_502(client):
    image_buffer = BytesIO()
    Image.new("RGB", (2, 2), color="red").save(
        image_buffer,
        format="PNG",
    )
    image_content = image_buffer.getvalue()

    with patch(
        "app.main.upload_image",
        side_effect=BotoCoreError(),
    ) as mock_upload:
        response = client.post(
            "/products/with-image",
            data={"title": "Товар при ошибке хранилища"},
            files={
                "image": (
                    "test.png",
                    image_content,
                    "image/png",
                )
            },
        )

    assert response.status_code == 502
    mock_upload.assert_called_once()

    with TestingSessionLocal() as db:
        product = db.query(Product).filter_by(
            title="Товар при ошибке хранилища"
        ).first()
        assert product is None


@pytest.fixture(scope="module", autouse=True)
def dispose_test_engine():
    yield
    test_engine.dispose()

