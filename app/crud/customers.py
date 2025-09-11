from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import Customer
from app.schemas.customers import CustomerCreate, CustomerUpdate


def get_customers(db: Session, skip: int = 0, limit: int = 100) -> List[Customer]:
    return db.query(Customer).offset(skip).limit(limit).all()


def get_customer(db: Session, customer_id: int) -> Optional[Customer]:
    return db.query(Customer).filter(Customer.customer_id == customer_id).first()


def create_customer(db: Session, customer: CustomerCreate) -> Customer:
    db_customer = Customer(
        customer_name=customer.customer_name,
        country=customer.country
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def update_customer(db: Session, customer_id: int, customer_update: CustomerUpdate) -> Optional[Customer]:
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
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return None
    
    db.delete(db_customer)
    db.commit()
    return db_customer
