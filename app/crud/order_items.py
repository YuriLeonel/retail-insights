from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import OrderItem
from app.schemas.order_items import OrderItemCreate, OrderItemUpdate


def get_order_items(db: Session, skip: int = 0, limit: int = 100) -> List[OrderItem]:
    return db.query(OrderItem).offset(skip).limit(limit).all()


def get_order_item(db: Session, order_item_id: int) -> Optional[OrderItem]:
    return db.query(OrderItem).filter(OrderItem.order_item_id == order_item_id).first()


def create_order_item(db: Session, order_item: OrderItemCreate) -> OrderItem:
    db_order_item = OrderItem(
        order_id=order_item.order_id,
        product_id=order_item.product_id,
        quantity=order_item.quantity,
        unit_price=order_item.unit_price
    )
    db.add(db_order_item)
    db.commit()
    db.refresh(db_order_item)
    return db_order_item


def update_order_item(db: Session, order_item_id: int, order_item_update: OrderItemUpdate) -> Optional[OrderItem]:
    db_order_item = get_order_item(db, order_item_id)
    if not db_order_item:
        return None
    
    update_data = order_item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_order_item, field, value)
    
    db.commit()
    db.refresh(db_order_item)
    return db_order_item


def delete_order_item(db: Session, order_item_id: int) -> Optional[OrderItem]:
    db_order_item = get_order_item(db, order_item_id)
    if not db_order_item:
        return None
    
    db.delete(db_order_item)
    db.commit()
    return db_order_item
