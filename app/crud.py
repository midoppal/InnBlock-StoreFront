from decimal import Decimal

from sqlalchemy.orm import Session
from app.models import Cart, CartItem, Order, OrderItem, Product
from app.schemas import OrderCreate
from app.models import User
from app.security import hash_password, verify_password

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

def create_cart(db: Session):
    cart = Cart()
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart


def get_cart(db: Session, cart_id: int):
    return db.query(Cart).filter(Cart.id == cart_id).first()


def build_cart_response(cart: Cart):
    items = []
    total_amount = Decimal("0.00")

    for item in cart.items:
        product = item.product
        item_total = Decimal(product.price) * item.quantity
        total_amount += item_total

        items.append({
            "id": item.id,
            "product_id": product.id,
            "name": product.name,
            "price": Decimal(product.price),
            "image_url": product.image_url,
            "stock": product.stock,
            "quantity": item.quantity,
            "item_total": item_total,
        })

    return {
        "id": cart.id,
        "items": items,
        "total_amount": total_amount,
    }


def add_item_to_cart(db: Session, cart_id: int, product_id: int, quantity: int):
    cart = get_cart(db, cart_id)

    if cart is None:
        raise ValueError("Cart not found")

    product = get_product_by_id(db, product_id)

    if product is None:
        raise ValueError("Product not found")

    existing_item = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
        .first()
    )

    current_quantity = existing_item.quantity if existing_item else 0
    new_quantity = current_quantity + quantity

    if new_quantity > product.stock:
        raise ValueError(f"Only {product.stock} available in stock")

    if existing_item:
        existing_item.quantity = new_quantity
    else:
        cart_item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart)

    return build_cart_response(cart)


def update_cart_item(db: Session, cart_id: int, product_id: int, quantity: int):
    cart = get_cart(db, cart_id)

    if cart is None:
        raise ValueError("Cart not found")

    item = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
        .first()
    )

    if item is None:
        raise ValueError("Cart item not found")

    if quantity == 0:
        db.delete(item)
        db.commit()
        db.refresh(cart)
        return build_cart_response(cart)

    product = get_product_by_id(db, product_id)

    if product is None:
        raise ValueError("Product not found")

    if quantity > product.stock:
        raise ValueError(f"Only {product.stock} available in stock")

    item.quantity = quantity
    db.commit()
    db.refresh(cart)

    return build_cart_response(cart)


def remove_cart_item(db: Session, cart_id: int, product_id: int):
    cart = get_cart(db, cart_id)

    if cart is None:
        raise ValueError("Cart not found")

    item = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
        .first()
    )

    if item is None:
        raise ValueError("Cart item not found")

    db.delete(item)
    db.commit()
    db.refresh(cart)

    return build_cart_response(cart)


def clear_cart(db: Session, cart_id: int):
    cart = get_cart(db, cart_id)

    if cart is None:
        raise ValueError("Cart not found")

    for item in list(cart.items):
        db.delete(item)

    db.commit()
    db.refresh(cart)

    return build_cart_response(cart)

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
        customer_phone=order_data.customer_phone,
        shipping_address_line1=order_data.shipping_address_line1,
        shipping_address_line2=order_data.shipping_address_line2,
        shipping_city=order_data.shipping_city,
        shipping_state=order_data.shipping_state,
        shipping_zip=order_data.shipping_zip,
        shipping_country=order_data.shipping_country,
        total_amount=total_amount,
        status="pending",
        payment_status="unpaid",
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

def create_order_from_cart(db: Session, order_data):
    cart = get_cart(db, order_data.cart_id)

    if cart is None:
        raise ValueError("Cart not found")

    if len(cart.items) == 0:
        raise ValueError("Cart is empty")

    total_amount = Decimal("0.00")
    order_items_to_create = []

    for cart_item in cart.items:
        product = get_product_by_id(db, cart_item.product_id)

        if product is None:
            raise ValueError(f"Product with id {cart_item.product_id} not found")

        if cart_item.quantity > product.stock:
            raise ValueError(
                f"Not enough stock for product '{product.name}'. Available: {product.stock}"
            )

        item_total = Decimal(product.price) * cart_item.quantity
        total_amount += item_total

        order_items_to_create.append({
            "product": product,
            "quantity": cart_item.quantity,
            "price_at_purchase": Decimal(product.price),
        })

    order = Order(
        customer_name=order_data.customer_name,
        customer_email=order_data.customer_email,
        customer_phone=order_data.customer_phone,
        shipping_address_line1=order_data.shipping_address_line1,
        shipping_address_line2=order_data.shipping_address_line2,
        shipping_city=order_data.shipping_city,
        shipping_state=order_data.shipping_state,
        shipping_zip=order_data.shipping_zip,
        shipping_country=order_data.shipping_country,
        total_amount=total_amount,
        status="pending",
        payment_status="unpaid",
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

    for cart_item in list(cart.items):
        db.delete(cart_item)

    db.commit()

    saved_order = db.query(Order).filter(Order.id == order.id).first()
    return saved_order

def get_orders(db: Session):
    return (
        db.query(Order)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_order_by_id(db: Session, order_id: int):
    return (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )
    
ALLOWED_ORDER_STATUSES = {"pending", "paid", "shipped", "cancelled", "completed"}


def update_order_status(db: Session, order_id: int, status: str):
    if status not in ALLOWED_ORDER_STATUSES:
        raise ValueError(
            f"Invalid status. Allowed statuses: {', '.join(sorted(ALLOWED_ORDER_STATUSES))}"
        )

    order = db.query(Order).filter(Order.id == order_id).first()

    if order is None:
        return None

    previous_status = order.status
    if previous_status == "cancelled" and status == "shipped":
        raise ValueError("Cannot ship a cancelled order")
    
    if status == "shipped" and order.payment_status != "paid":
        raise ValueError("Cannot ship an unpaid order")

    if previous_status == "cancelled" and status == "cancelled":
        return order

    if previous_status != "cancelled" and status == "cancelled":
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()

            if product:
                product.stock += item.quantity

    if previous_status == "cancelled" and status != "cancelled":
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()

            if product is None:
                raise ValueError(f"Product with id {item.product_id} not found")

            if item.quantity > product.stock:
                raise ValueError(
                    f"Cannot restore order because product '{product.name}' only has {product.stock} in stock"
                )

            product.stock -= item.quantity

    order.status = status
    db.commit()
    db.refresh(order)

    return order

ALLOWED_PAYMENT_STATUSES = {"unpaid", "paid", "refunded"}


def update_order_payment_status(db: Session, order_id: int, payment_status: str):
    if payment_status not in ALLOWED_PAYMENT_STATUSES:
        raise ValueError(
            f"Invalid payment status. Allowed statuses: {', '.join(sorted(ALLOWED_PAYMENT_STATUSES))}"
        )

    order = db.query(Order).filter(Order.id == order_id).first()

    if order is None:
        return None

    order.payment_status = payment_status
    db.commit()
    db.refresh(order)

    return order

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_data):
    existing_user = get_user_by_email(db, user_data.email)

    if existing_user:
        raise ValueError("A user with this email already exists")

    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if not user.is_active:
        raise ValueError("User account is inactive")

    return user