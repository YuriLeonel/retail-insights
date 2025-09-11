from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import Order
from app.schemas.orders import OrderCreate, OrderUpdate


def get_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    return db.query(Order).offset(skip).limit(limit).all()


def get_order(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.order_id == order_id).first()


def create_order(db: Session, order: OrderCreate) -> Order:
    db_order = Order(
        invoice_no=order.invoice_no,
        customer_id=order.customer_id,
        invoice_date=order.invoice_date,
        country=order.country
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def update_order(db: Session, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    
    update_data = order_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_order, field, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int) -> Optional[Order]:
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    
    db.delete(db_order)
    db.commit()
    return db_order
