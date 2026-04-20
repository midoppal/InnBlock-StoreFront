from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app import models
from app.routes import products

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(products.router)


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