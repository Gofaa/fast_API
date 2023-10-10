from concurrent.futures._base import PENDING

from pydantic import BaseModel
from typing import Optional


class SignUpModel(BaseModel):
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        org_mode = True
        json_schema_extra = {
            'example': {
                'username': 'gofa',
                'email': 'gofa@gail.com',
                'password': 'gofa123',
                'is_staff': False,
                'is_active': True
            }
        }


class Settings(BaseModel):
    authjwt_secret_key: str = 'aa580cb79f490f914f22621d3ee99ffbf7f15fb0cee91908c9e896520257bd38'  # get secret key
    # from python console import secrets and secrets.python_hex()


class LoginModel(BaseModel):
    username_or_email: str
    password: str


class OrderModel(BaseModel):
    id: Optional[int]
    quantity: int
    order_statuses: Optional[str] = 'PENDING'
    user_id: Optional[int]
    product_id: int

    class Config:
        orm_model = True
        json_schema_extra = {
            'example': {
                'quantity': 2
            }
        }


class OrderStatusModel(BaseModel):
    order_statuses: Optional[str] = "PENDING"

    class Config:
        orm_model = True
        json_schema_extra = {
            "example": {
                "order_statuses": "PENDING"
            }
        }


class ProductModel(BaseModel):
    id: Optional[int]
    name: str
    price: int

    class Config:
        orm_model = True
        schema_extra = {
            'example': {
                'name': "to'y osh",
                'price': 30000
            }
        }
