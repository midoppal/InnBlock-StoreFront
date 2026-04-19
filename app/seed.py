from decimal import Decimal

from app.database import SessionLocal, engine
from app.models import Base, Product


sample_products = [
    {
        "name": "Basic Black T-Shirt",
        "description": "Soft cotton t-shirt for everyday wear.",
        "price": Decimal("19.99"),
        "stock": 25,
        "image_url": "https://via.placeholder.com/300x200?text=Black+T-Shirt",
        "is_active": True,
    },
    {
        "name": "Classic Gray Hoodie",
        "description": "Warm hoodie with a relaxed fit.",
        "price": Decimal("49.99"),
        "stock": 12,
        "image_url": "https://via.placeholder.com/300x200?text=Gray+Hoodie",
        "is_active": True,
    },
    {
        "name": "Navy Baseball Cap",
        "description": "Adjustable cap with a simple embroidered logo.",
        "price": Decimal("24.99"),
        "stock": 30,
        "image_url": "https://via.placeholder.com/300x200?text=Baseball+Cap",
        "is_active": True,
    },
    {
        "name": "White Sneakers",
        "description": "Minimal sneakers designed for casual daily wear.",
        "price": Decimal("79.99"),
        "stock": 8,
        "image_url": "https://via.placeholder.com/300x200?text=White+Sneakers",
        "is_active": True,
    },
]


def seed_products():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing_count = db.query(Product).count()

        if existing_count > 0:
            print(f"Products already exist ({existing_count} found). Skipping seed.")
            return

        for product_data in sample_products:
            product = Product(**product_data)
            db.add(product)

        db.commit()
        print("Sample products inserted successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_products()