from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("", response_model=schemas.CartResponse)
def create_cart(db: Session = Depends(get_db)):
    cart = crud.create_cart(db)
    return crud.build_cart_response(cart)


@router.get("/{cart_id}", response_model=schemas.CartResponse)
def read_cart(cart_id: int, db: Session = Depends(get_db)):
    cart = crud.get_cart(db, cart_id)

    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")

    return crud.build_cart_response(cart)


@router.post("/{cart_id}/items", response_model=schemas.CartResponse)
def add_item_to_cart(
    cart_id: int,
    item_data: schemas.CartItemAdd,
    db: Session = Depends(get_db),
):
    try:
        return crud.add_item_to_cart(
            db,
            cart_id=cart_id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{cart_id}/items/{product_id}", response_model=schemas.CartResponse)
def update_cart_item(
    cart_id: int,
    product_id: int,
    item_data: schemas.CartItemUpdate,
    db: Session = Depends(get_db),
):
    try:
        return crud.update_cart_item(
            db,
            cart_id=cart_id,
            product_id=product_id,
            quantity=item_data.quantity,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{cart_id}/items/{product_id}", response_model=schemas.CartResponse)
def remove_cart_item(
    cart_id: int,
    product_id: int,
    db: Session = Depends(get_db),
):
    try:
        return crud.remove_cart_item(db, cart_id, product_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{cart_id}", response_model=schemas.CartResponse)
def clear_cart(cart_id: int, db: Session = Depends(get_db)):
    try:
        return crud.clear_cart(db, cart_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))