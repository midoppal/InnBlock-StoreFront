from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.security import create_access_token

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=schemas.UserResponse)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_user(db, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/login", response_model=schemas.TokenResponse)
def login_user(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        user = crud.authenticate_user(db, user_data.email, user_data.password)

        if user is None:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "is_admin": user.is_admin,
        })

        return {
            "access_token": token,
            "token_type": "bearer",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))