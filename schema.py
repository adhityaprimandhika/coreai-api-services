from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Category(BaseModel):
    id: int
    name: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class Merchant(BaseModel):
    id: int
    name: str
    sub_name: str
    merchant_code: str
    category_id: int
    logo: str
    website: str
    latitude: float
    longitude: float
    address: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class MerchantGarage(BaseModel):
    id: int
    name: str
    category: str
    address: str
    logo: str
    latitude: float
    longitude: float
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True