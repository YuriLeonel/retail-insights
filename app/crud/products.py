from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import Product
from app.schemas.products import ProductCreate, ProductUpdate


# Async CRUD operations
async def get_products_async(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Product]:
    """Get products with pagination (async)"""
    result = await db.execute(
        select(Product).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_product_async(db: AsyncSession, product_id: int) -> Optional[Product]:
    """Get product by ID (async)"""
    result = await db.execute(
        select(Product).filter(Product.product_id == product_id)
    )
    return result.scalar_one_or_none()


async def create_product_async(db: AsyncSession, product: ProductCreate) -> Product:
    """Create a new product (async)"""
    db_product = Product(
        stock_code=product.stock_code,
        description=product.description
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def update_product_async(db: AsyncSession, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
    """Update product (async)"""
    db_product = await get_product_async(db, product_id)
    if not db_product:
        return None
    
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def delete_product_async(db: AsyncSession, product_id: int) -> Optional[Product]:
    """Delete product (async)"""
    db_product = await get_product_async(db, product_id)
    if not db_product:
        return None
    
    await db.delete(db_product)
    await db.commit()
    return db_product


# Sync CRUD operations (for backward compatibility)
def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    """Get products with pagination (sync)"""
    return db.query(Product).offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int) -> Optional[Product]:
    """Get product by ID (sync)"""
    return db.query(Product).filter(Product.product_id == product_id).first()


def create_product(db: Session, product: ProductCreate) -> Product:
    """Create a new product (sync)"""
    db_product = Product(
        stock_code=product.stock_code,
        description=product.description
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
    """Update product (sync)"""
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> Optional[Product]:
    """Delete product (sync)"""
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    
    db.delete(db_product)
    db.commit()
    return db_product
