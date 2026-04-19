from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Store backend is running"}


@app.get("/health/db")
def db_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"database": "connected"}
    except Exception as e:
        return {
            "database": "failed",
            "error": str(e)
        }


@app.get("/health/models")
def model_health_check():
    return {
        "tables_expected": ["products", "orders", "order_items"]
    }


@app.get("/debug/products-count")
def debug_products_count():
    db: Session = SessionLocal()
    try:
        count = db.query(models.Product).count()
        return {"products_count": count}
    finally:
        db.close()