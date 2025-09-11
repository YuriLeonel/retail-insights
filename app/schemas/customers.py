from pydantic import BaseModel
from typing import Optional, List


class CustomerBase(BaseModel):
    customer_name: Optional[str] = None
    country: Optional[str] = None


class CustomerCreate(CustomerBase):
    customer_name: str
    country: str


class CustomerUpdate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    customer_id: int
    customer_name: str
    country: str

    class Config:
        from_attributes = True
