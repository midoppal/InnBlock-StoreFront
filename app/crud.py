from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Order, OrderItem, Product
from app.schemas import OrderCreate


def get_products(db: Session):
    return (
        db.query(Product)
        .filter(Product.is_active == True)
        .order_by(Product.id.asc())
        .all()
    )


def get_product_by_id(db: Session, product_id: int):
    return (
        db.query(Product)
        .filter(Product.id == product_id, Product.is_active == True)
        .first()
    )

def create_product(db: Session, product_data):
    product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
        image_url=product_data.image_url,
        is_active=product_data.is_active,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def update_product(db: Session, product_id: int, product_data):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        return None

    update_data = product_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


def deactivate_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        return None

    product.is_active = False
    db.commit()
    db.refresh(product)

    return product


def restock_product(db: Session, product_id: int, quantity: int):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        return None

    product.stock += quantity
    db.commit()
    db.refresh(product)

    return product

def get_all_products_admin(db: Session):
    return (
        db.query(Product)
        .order_by(Product.id.asc())
        .all()
    )


def activate_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        return None

    product.is_active = True
    db.commit()
    db.refresh(product)

    return product


def create_order(db: Session, order_data: OrderCreate):
    total_amount = Decimal("0.00")
    order_items_to_create = []

    for item in order_data.items:
        product = (
            db.query(Product)
            .filter(Product.id == item.product_id, Product.is_active == True)
            .first()
        )

        if product is None:
            raise ValueError(f"Product with id {item.product_id} not found")

        if item.quantity > product.stock:
            raise ValueError(
                f"Not enough stock for product '{product.name}'. Available: {product.stock}"
            )

        item_total = Decimal(product.price) * item.quantity
        total_amount += item_total

        order_items_to_create.append({
            "product": product,
            "quantity": item.quantity,
            "price_at_purchase": Decimal(product.price),
        })

    order = Order(
        customer_name=order_data.customer_name,
        customer_email=order_data.customer_email,
        total_amount=total_amount,
    )
    db.add(order)
    db.flush()

    for item_data in order_items_to_create:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data["product"].id,
            quantity=item_data["quantity"],
            price_at_purchase=item_data["price_at_purchase"],
        )
        db.add(order_item)

        item_data["product"].stock -= item_data["quantity"]

    db.commit()

    saved_order = db.query(Order).filter(Order.id == order.id).first()
    return saved_order