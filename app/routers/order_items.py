from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db
from app.database import get_async_db_dependency
from app.auth import get_current_user_async
from app.schemas.order_items import OrderItemCreate, OrderItemUpdate, OrderItemResponse
from app.crud import order_items as crud_order_items

router = APIRouter()


@router.get("/", response_model=List[OrderItemResponse], summary="List all order items")
async def list_order_items(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Retrieve a list of order items with optional pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    """
    order_items = await crud_order_items.get_order_items_async(db, skip=skip, limit=limit)
    return order_items


@router.get("/{order_item_id}", response_model=OrderItemResponse, summary="Get order item by ID")
async def get_order_item(
    order_item_id: int,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Retrieve a specific order item by its ID.
    
    - **order_item_id**: The ID of the order item to retrieve
    """
    order_item = await crud_order_items.get_order_item_async(db, order_item_id=order_item_id)
    if order_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )
    return order_item


@router.post("/", response_model=OrderItemResponse, status_code=status.HTTP_201_CREATED, summary="Create a new order item")
async def create_order_item(
    order_item: OrderItemCreate,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Create a new order item.
    
    - **order_id**: The ID of the order this item belongs to
    - **product_id**: The ID of the product being ordered
    - **quantity**: The quantity of the product ordered
    - **unit_price**: The price per unit of the product
    """
    return await crud_order_items.create_order_item_async(db, order_item=order_item)


@router.put("/{order_item_id}", response_model=OrderItemResponse, summary="Update order item")
async def update_order_item(
    order_item_id: int,
    order_item_update: OrderItemUpdate,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Update an existing order item.
    
    - **order_item_id**: The ID of the order item to update
    - **order_id**: The new order ID (optional)
    - **product_id**: The new product ID (optional)
    - **quantity**: The new quantity (optional)
    - **unit_price**: The new unit price (optional)
    """
    order_item = await crud_order_items.update_order_item_async(db, order_item_id=order_item_id, order_item_update=order_item_update)
    if order_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )
    return order_item


@router.delete("/{order_item_id}", response_model=OrderItemResponse, summary="Delete order item")
async def delete_order_item(
    order_item_id: int,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Delete an order item by its ID.
    
    - **order_item_id**: The ID of the order item to delete
    """
    order_item = await crud_order_items.delete_order_item_async(db, order_item_id=order_item_id)
    if order_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )
    return order_item