from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import OrderItem
from app.schemas.order_items import OrderItemCreate, OrderItemUpdate


# Async CRUD operations
async def get_order_items_async(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[OrderItem]:
    """Get order items with pagination (async)"""
    result = await db.execute(
        select(OrderItem).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_order_item_async(db: AsyncSession, order_item_id: int) -> Optional[OrderItem]:
    """Get order item by ID (async)"""
    result = await db.execute(
        select(OrderItem).filter(OrderItem.order_item_id == order_item_id)
    )
    return result.scalar_one_or_none()


async def create_order_item_async(db: AsyncSession, order_item: OrderItemCreate) -> OrderItem:
    """Create a new order item (async)"""
    db_order_item = OrderItem(
        order_id=order_item.order_id,
        product_id=order_item.product_id,
        quantity=order_item.quantity,
        unit_price=order_item.unit_price
    )
    db.add(db_order_item)
    await db.commit()
    await db.refresh(db_order_item)
    return db_order_item


async def update_order_item_async(db: AsyncSession, order_item_id: int, order_item_update: OrderItemUpdate) -> Optional[OrderItem]:
    """Update order item (async)"""
    db_order_item = await get_order_item_async(db, order_item_id)
    if not db_order_item:
        return None
    
    update_data = order_item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_order_item, field, value)
    
    await db.commit()
    await db.refresh(db_order_item)
    return db_order_item


async def delete_order_item_async(db: AsyncSession, order_item_id: int) -> Optional[OrderItem]:
    """Delete order item (async)"""
    db_order_item = await get_order_item_async(db, order_item_id)
    if not db_order_item:
        return None
    
    await db.delete(db_order_item)
    await db.commit()
    return db_order_item


# Sync CRUD operations (for backward compatibility)
def get_order_items(db: Session, skip: int = 0, limit: int = 100) -> List[OrderItem]:
    """Get order items with pagination (sync)"""
    return db.query(OrderItem).offset(skip).limit(limit).all()


def get_order_item(db: Session, order_item_id: int) -> Optional[OrderItem]:
    """Get order item by ID (sync)"""
    return db.query(OrderItem).filter(OrderItem.order_item_id == order_item_id).first()


def create_order_item(db: Session, order_item: OrderItemCreate) -> OrderItem:
    """Create a new order item (sync)"""
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
    """Update order item (sync)"""
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
    """Delete order item (sync)"""
    db_order_item = get_order_item(db, order_item_id)
    if not db_order_item:
        return None
    
    db.delete(db_order_item)
    db.commit()
    return db_order_item
