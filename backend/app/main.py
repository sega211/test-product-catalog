from fastapi import Depends, FastAPI, HTTPException, File, Form, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database import SessionLocal
from app.models import Product
from app.schemas import ProductCreate, ProductResponse
from uuid import uuid4
from botocore.exceptions import ClientError, BotoCoreError
from app.storage import read_image, upload_image, delete_image
from app.image_validation import (
    MAX_IMAGE_SIZE,
    ImageValidationError,
    validate_image,
)

app = FastAPI(title="Test Catalog API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "good"}

@app.get("/products", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)) -> list[Product]:
    return list(db.scalars(select(Product).order_by(Product.id)).all())

@app.get("/products/{product_id}" , response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Товар не найден"
        )

    return product


@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db)
) -> Product:
    product = Product(title=payload.title)
    db.add(product)
    db.commit();
    db.refresh(product)

    return product

@app.get("/products/{product_id}/image")
def get_product_image(
    product_id: int,
    db: Session = Depends(get_db)
) -> Response:
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Товар не найден"
        )

    if not product.image_key:
        raise HTTPException(
            status_code=404,
            detail="У товара нет изображения"
        )

    try:
        content, content_type = read_image(product.image_key)
    except ClientError as exc:
        error_code = exc.response.get("Error",{}).get("Code")
        if error_code in {"NoSuchKey", "NoSuchObject", "NotFound"}:
            raise HTTPException(\
                status_code=404,
                detail="Изображение не найдено"
            ) from exc
        raise HTTPException(
            status_code=502,
            detail="Ошибка хранилища изображений"
        ) from exc

    return Response(
        content=content,
        media_type=content_type,
        headers={"Cache-Control": "private, max-age=300"}
    )

@app.post("/products/with-image", response_model=ProductResponse, status_code=201)
async def create_product_with_image(
    title: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Product:
    title = title.strip()

    if not title or len(title) > 255:
        raise HTTPException(
            status_code=422,
            detail="Название должно содержать от 1 до 255 символов",
        )

    content = await image.read(MAX_IMAGE_SIZE + 1)

    try:
        content_type = validate_image(content)
    except ImageValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    finally:
        await image.close()

    extensions = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
    }
    image_key = f"products/{uuid4().hex}.{extensions[content_type]}"
    try:
        upload_image(image_key, content, content_type)
    except BotoCoreError as exc:
        raise HTTPException(
            status_code=502,
            detail="Не удалось загрузить изображение в хранилище",
        ) from exc

    product = Product(title=title, image_key=image_key)

    try:
        db.add(product)
        db.commit()
        db.refresh(product)
    except SQLAlchemyError as exc:
        db.rollback()

        try:
            delete_image(image_key)
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail="Не удалось сохранить товар",
        ) from exc
    return product
