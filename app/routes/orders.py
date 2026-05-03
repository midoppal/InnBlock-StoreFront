from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=schemas.OrderResponse)
def create_new_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db)):
    try:
        order = crud.create_order(db, order_data)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[schemas.OrderResponse])
def read_orders(db: Session = Depends(get_db)):
    return crud.get_orders(db)


@router.get("/{order_id}", response_model=schemas.OrderResponse)
def read_order(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order_by_id(db, order_id)

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order

@router.post("/from-cart", response_model=schemas.OrderResponse)
def create_new_order_from_cart(
    order_data: schemas.OrderCreateFromCart,
    db: Session = Depends(get_db),
):
    try:
        order = crud.create_order_from_cart(db, order_data)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))