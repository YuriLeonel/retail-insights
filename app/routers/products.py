from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db
from app.database import get_async_db_dependency
from app.auth import get_current_user_async
from app.schemas.products import ProductCreate, ProductUpdate, ProductResponse
from app.crud import products as crud_products

router = APIRouter()


@router.get("/", response_model=List[ProductResponse], summary="List all products")
async def list_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Retrieve a list of products with optional pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    """
    products = await crud_products.get_products_async(db, skip=skip, limit=limit)
    return products


@router.get("/{product_id}", response_model=ProductResponse, summary="Get product by ID")
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Retrieve a specific product by its ID.
    
    - **product_id**: The ID of the product to retrieve
    """
    product = await crud_products.get_product_async(db, product_id=product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, summary="Create a new product")
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Create a new product.
    
    - **stock_code**: The unique stock code for the product
    - **description**: The description of the product
    """
    return await crud_products.create_product_async(db, product=product)


@router.put("/{product_id}", response_model=ProductResponse, summary="Update product")
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Update an existing product.
    
    - **product_id**: The ID of the product to update
    - **stock_code**: The new stock code for the product (optional)
    - **description**: The new description of the product (optional)
    """
    product = await crud_products.update_product_async(db, product_id=product_id, product_update=product_update)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.delete("/{product_id}", response_model=ProductResponse, summary="Delete product")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Delete a product by its ID.
    
    - **product_id**: The ID of the product to delete
    """
    product = await crud_products.delete_product_async(db, product_id=product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product