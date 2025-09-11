from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.schemas.orders import OrderCreate, OrderUpdate, OrderResponse
from app.crud import orders as crud_orders

router = APIRouter()


@router.get("/", response_model=List[OrderResponse], summary="List all orders")
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of orders with optional pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    """
    orders = crud_orders.get_orders(db, skip=skip, limit=limit)
    return orders


@router.get("/{order_id}", response_model=OrderResponse, summary="Get order by ID")
async def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific order by its ID.
    
    - **order_id**: The ID of the order to retrieve
    """
    order = crud_orders.get_order(db, order_id=order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, summary="Create a new order")
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new order.
    
    - **invoice_no**: The invoice number for the order
    - **customer_id**: The ID of the customer placing the order
    - **invoice_date**: The date when the invoice was created
    - **country**: The country where the order was placed
    """
    return crud_orders.create_order(db, order=order)


@router.put("/{order_id}", response_model=OrderResponse, summary="Update order")
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing order.
    
    - **order_id**: The ID of the order to update
    - **invoice_no**: The new invoice number (optional)
    - **customer_id**: The new customer ID (optional)
    - **invoice_date**: The new invoice date (optional)
    - **country**: The new country (optional)
    """
    order = crud_orders.update_order(db, order_id=order_id, order_update=order_update)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


@router.delete("/{order_id}", response_model=OrderResponse, summary="Delete order")
async def delete_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an order by its ID.
    
    - **order_id**: The ID of the order to delete
    """
    order = crud_orders.delete_order(db, order_id=order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order