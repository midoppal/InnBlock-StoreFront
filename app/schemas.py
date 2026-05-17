from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

################################################################################################################################################
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    stock: int
    image_url: Optional[str] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ProductRestock(BaseModel):
    quantity: int = Field(..., gt=0)

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True
################################################################################################################################################
class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=0)


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    name: str
    price: Decimal
    image_url: Optional[str] = None
    stock: int
    quantity: int
    item_total: Decimal


class CartResponse(BaseModel):
    id: int
    items: List[CartItemResponse]
    total_amount: Decimal

################################################################################################################################################
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_phone: Optional[str] = None

    shipping_address_line1: str
    shipping_address_line2: Optional[str] = None
    shipping_city: str
    shipping_state: str
    shipping_zip: str
    shipping_country: str = "United States"

    items: List[OrderItemCreate] = Field(..., min_length=1)
 
class OrderCreateFromCart(BaseModel):
    cart_id: int

    customer_name: str
    customer_email: EmailStr
    customer_phone: Optional[str] = None

    shipping_address_line1: str
    shipping_address_line2: Optional[str] = None
    shipping_city: str
    shipping_state: str
    shipping_zip: str
    shipping_country: str = "United States"
    
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: Decimal

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    customer_email: EmailStr
    customer_phone: Optional[str] = None

    shipping_address_line1: Optional[str] = None
    shipping_address_line2: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_zip: Optional[str] = None
    shipping_country: Optional[str] = None

    total_amount: Decimal
    status: str
    payment_status: str
    created_at: datetime
    items: List[OrderItemResponse]
    

    class Config:
        from_attributes = True
        
class OrderStatusUpdate(BaseModel):
    status: str

class OrderPaymentStatusUpdate(BaseModel):
    payment_status: str
    
################################################################################################################################################
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True
        
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"