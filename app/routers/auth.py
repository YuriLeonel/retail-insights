"""
Authentication router
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, get_async_db_dependency
from app.schemas.auth import UserCreate, UserResponse, Token, LoginRequest
from app.crud import users as crud_users
from app.auth import create_access_token, get_current_user, get_current_user_async, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_async_db_dependency)
):
    """
    Register a new user.
    
    - **username**: Unique username
    - **email**: Valid email address
    - **password**: Secure password
    """
    # Check if user already exists
    db_user = await crud_users.get_user_by_username_async(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    db_user = await crud_users.get_user_by_email_async(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    return await crud_users.create_user_async(db=db, user=user)

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_async_db_dependency)
):
    """
    Login and get access token.
    
    - **username**: Your username
    - **password**: Your password
    """
    user = await crud_users.authenticate_user_async(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user = Depends(get_current_user_async)):
    """
    Get current user information.
    """
    return current_user
