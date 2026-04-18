from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine

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
        