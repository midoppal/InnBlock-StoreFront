from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=List[schemas.ProductResponse])
def read_products(db: Session = Depends(get_db)):
    products = crud.get_products(db)
    return products


@router.get("/admin/all", response_model=List[schemas.ProductResponse])
def read_all_products_admin(db: Session = Depends(get_db)):
    products = crud.get_all_products_admin(db)
    return products

@router.get("/{product_id}", response_model=schemas.ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product_by_id(db, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.post("", response_model=schemas.ProductResponse)
def create_product(product_data: schemas.ProductCreate, db: Session = Depends(get_db)):
    product = crud.create_product(db, product_data)
    return product

@router.patch("/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: int,
    product_data: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):
    product = crud.update_product(db, product_id, product_data)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

@router.patch("/{product_id}/activate", response_model=schemas.ProductResponse)
def activate_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.activate_product(db, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

@router.patch("/{product_id}/deactivate", response_model=schemas.ProductResponse)
def deactivate_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.deactivate_product(db, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.patch("/{product_id}/restock", response_model=schemas.ProductResponse)
def restock_product(
    product_id: int,
    restock_data: schemas.ProductRestock,
    db: Session = Depends(get_db)
):
    product = crud.restock_product(db, product_id, restock_data.quantity)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product