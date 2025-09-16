from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import Customer
from app.schemas.customers import CustomerCreate, CustomerUpdate


# Async CRUD operations
async def get_customers_async(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Customer]:
    """Get customers with pagination (async)"""
    result = await db.execute(
        select(Customer).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_customer_async(db: AsyncSession, customer_id: int) -> Optional[Customer]:
    """Get customer by ID (async)"""
    result = await db.execute(
        select(Customer).filter(Customer.customer_id == customer_id)
    )
    return result.scalar_one_or_none()


async def create_customer_async(db: AsyncSession, customer: CustomerCreate) -> Customer:
    """Create a new customer (async)"""
    db_customer = Customer(
        customer_name=customer.customer_name,
        country=customer.country
    )
    db.add(db_customer)
    await db.commit()
    await db.refresh(db_customer)
    return db_customer


async def update_customer_async(db: AsyncSession, customer_id: int, customer_update: CustomerUpdate) -> Optional[Customer]:
    """Update customer (async)"""
    db_customer = await get_customer_async(db, customer_id)
    if not db_customer:
        return None
    
    update_data = customer_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_customer, field, value)
    
    await db.commit()
    await db.refresh(db_customer)
    return db_customer


async def delete_customer_async(db: AsyncSession, customer_id: int) -> Optional[Customer]:
    """Delete customer (async)"""
    db_customer = await get_customer_async(db, customer_id)
    if not db_customer:
        return None
    
    await db.delete(db_customer)
    await db.commit()
    return db_customer


# Sync CRUD operations (for backward compatibility)
def get_customers(db: Session, skip: int = 0, limit: int = 100) -> List[Customer]:
    """Get customers with pagination (sync)"""
    return db.query(Customer).offset(skip).limit(limit).all()


def get_customer(db: Session, customer_id: int) -> Optional[Customer]:
    """Get customer by ID (sync)"""
    return db.query(Customer).filter(Customer.customer_id == customer_id).first()


def create_customer(db: Session, customer: CustomerCreate) -> Customer:
    """Create a new customer (sync)"""
    db_customer = Customer(
        customer_name=customer.customer_name,
        country=customer.country
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def update_customer(db: Session, customer_id: int, customer_update: CustomerUpdate) -> Optional[Customer]:
    """Update customer (sync)"""
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return None
    
    update_data = customer_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_customer, field, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer


def delete_customer(db: Session, customer_id: int) -> Optional[Customer]:
    """Delete customer (sync)"""
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return None
    
    db.delete(db_customer)
    db.commit()
    return db_customer
