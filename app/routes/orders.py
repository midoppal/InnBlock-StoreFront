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