from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProductRead(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    image_url: str
    stock: int

    class Config:
        from_attributes = True


class CartItemRead(BaseModel):
    id: int
    product: ProductRead
    quantity: int

    class Config:
        from_attributes = True


class ReviewRead(BaseModel):
    id: int
    user_name: str
    rating: int
    comment: str
    created_at: datetime

    class Config:
        from_attributes = True
