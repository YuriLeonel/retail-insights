from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.dependencies import get_db
from app.database import get_async_db_dependency
from app.schemas.customers import CustomerCreate, CustomerUpdate, CustomerResponse
from app.crud import customers as crud_customers
from app.auth import get_current_user_async

router = APIRouter()


@router.get("/", response_model=List[CustomerResponse], summary="List all customers")
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Retrieve a list of customers with optional pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    """
    customers = await crud_customers.get_customers_async(db, skip=skip, limit=limit)
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse, summary="Get customer by ID")
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Retrieve a specific customer by their ID.
    
    - **customer_id**: The ID of the customer to retrieve
    """
    customer = await crud_customers.get_customer_async(db, customer_id=customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED, summary="Create a new customer")
async def create_customer(
    customer: CustomerCreate,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Create a new customer.
    
    - **customer_name**: The name of the customer
    - **country**: The country where the customer is located
    """
    return await crud_customers.create_customer_async(db, customer=customer)


@router.put("/{customer_id}", response_model=CustomerResponse, summary="Update customer")
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Update an existing customer.
    
    - **customer_id**: The ID of the customer to update
    - **customer_name**: The new name of the customer (optional)
    - **country**: The new country of the customer (optional)
    """
    customer = await crud_customers.update_customer_async(db, customer_id=customer_id, customer_update=customer_update)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer


@router.delete("/{customer_id}", response_model=CustomerResponse, summary="Delete customer")
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_async_db_dependency),
    current_user = Depends(get_current_user_async)
):
    """
    Delete a customer by their ID.
    
    - **customer_id**: The ID of the customer to delete
    """
    customer = await crud_customers.delete_customer_async(db, customer_id=customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer