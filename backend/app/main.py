from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Product
from app.schemas import ProductCreate, ProductResponse

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