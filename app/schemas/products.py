from pydantic import BaseModel
from typing import Optional


class ProductBase(BaseModel):
    stock_code: Optional[str] = None
    description: Optional[str] = None


class ProductCreate(ProductBase):
    stock_code: str
    description: str


class ProductUpdate(ProductBase):
    pass


class ProductResponse(ProductBase):
    product_id: int
    stock_code: str
    description: str

    class Config:
        from_attributes = True
