from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import Order
from app.schemas.orders import OrderCreate, OrderUpdate


# Async CRUD operations
async def get_orders_async(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get orders with pagination (async)"""
    result = await db.execute(
        select(Order).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_order_async(db: AsyncSession, order_id: int) -> Optional[Order]:
    """Get order by ID (async)"""
    result = await db.execute(
        select(Order).filter(Order.order_id == order_id)
    )
    return result.scalar_one_or_none()


async def create_order_async(db: AsyncSession, order: OrderCreate) -> Order:
    """Create a new order (async)"""
    db_order = Order(
        invoice_no=order.invoice_no,
        customer_id=order.customer_id,
        invoice_date=order.invoice_date,
        country=order.country
    )
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order


async def update_order_async(db: AsyncSession, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
    """Update order (async)"""
    db_order = await get_order_async(db, order_id)
    if not db_order:
        return None
    
    update_data = order_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_order, field, value)
    
    await db.commit()
    await db.refresh(db_order)
    return db_order


async def delete_order_async(db: AsyncSession, order_id: int) -> Optional[Order]:
    """Delete order (async)"""
    db_order = await get_order_async(db, order_id)
    if not db_order:
        return None
    
    await db.delete(db_order)
    await db.commit()
    return db_order


# Sync CRUD operations (for backward compatibility)
def get_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get orders with pagination (sync)"""
    return db.query(Order).offset(skip).limit(limit).all()


def get_order(db: Session, order_id: int) -> Optional[Order]:
    """Get order by ID (sync)"""
    return db.query(Order).filter(Order.order_id == order_id).first()


def create_order(db: Session, order: OrderCreate) -> Order:
    """Create a new order (sync)"""
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
    """Update order (sync)"""
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
    """Delete order (sync)"""
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    
    db.delete(db_order)
    db.commit()
    return db_order
