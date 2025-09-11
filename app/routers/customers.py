from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.schemas.customers import CustomerCreate, CustomerUpdate, CustomerResponse
from app.crud import customers as crud_customers

router = APIRouter()


@router.get("/", response_model=List[CustomerResponse], summary="List all customers")
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of customers with optional pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    """
    customers = crud_customers.get_customers(db, skip=skip, limit=limit)
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse, summary="Get customer by ID")
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific customer by their ID.
    
    - **customer_id**: The ID of the customer to retrieve
    """
    customer = crud_customers.get_customer(db, customer_id=customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED, summary="Create a new customer")
async def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new customer.
    
    - **customer_name**: The name of the customer
    - **country**: The country where the customer is located
    """
    return crud_customers.create_customer(db, customer=customer)


@router.put("/{customer_id}", response_model=CustomerResponse, summary="Update customer")
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing customer.
    
    - **customer_id**: The ID of the customer to update
    - **customer_name**: The new name of the customer (optional)
    - **country**: The new country of the customer (optional)
    """
    customer = crud_customers.update_customer(db, customer_id=customer_id, customer_update=customer_update)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer


@router.delete("/{customer_id}", response_model=CustomerResponse, summary="Delete customer")
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a customer by their ID.
    
    - **customer_id**: The ID of the customer to delete
    """
    customer = crud_customers.delete_customer(db, customer_id=customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer