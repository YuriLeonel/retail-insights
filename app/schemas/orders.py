from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OrderBase(BaseModel):
    invoice_no: Optional[str] = None
    customer_id: Optional[int] = None
    invoice_date: Optional[datetime] = None
    country: Optional[str] = None


class OrderCreate(OrderBase):
    invoice_no: str
    customer_id: int
    invoice_date: datetime
    country: str


class OrderUpdate(OrderBase):
    pass


class OrderResponse(OrderBase):
    order_id: int
    invoice_no: str
    customer_id: int
    invoice_date: datetime
    country: str

    class Config:
        from_attributes = True
