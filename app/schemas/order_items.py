from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class OrderItemBase(BaseModel):
    order_id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None


class OrderItemCreate(OrderItemBase):
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal


class OrderItemUpdate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    order_item_id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal

    class Config:
        from_attributes = True
