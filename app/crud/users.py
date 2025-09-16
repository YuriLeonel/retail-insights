"""
User CRUD operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional
from app.models import User
from app.schemas.auth import UserCreate
from app.auth import get_password_hash, verify_password


# Async CRUD operations
async def get_user_by_username_async(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username (async)"""
    result = await db.execute(
        select(User).filter(User.username == username)
    )
    return result.scalar_one_or_none()


async def get_user_by_email_async(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email (async)"""
    result = await db.execute(
        select(User).filter(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_async(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID (async)"""
    result = await db.execute(
        select(User).filter(User.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_user_async(db: AsyncSession, user: UserCreate) -> User:
    """Create a new user (async)"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_admin=user.is_admin
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user_async(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """Authenticate a user (async)"""
    user = await get_user_by_username_async(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# Sync CRUD operations (for backward compatibility)
def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username (sync)"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email (sync)"""
    return db.query(User).filter(User.email == email).first()


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID (sync)"""
    return db.query(User).filter(User.user_id == user_id).first()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user (sync)"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user (sync)"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
