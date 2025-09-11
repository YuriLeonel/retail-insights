import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models import Base

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_customer_data():
    return {
        "customer_name": "John Doe",
        "country": "USA"
    }

@pytest.fixture
def sample_product_data():
    return {
        "stock_code": "PROD001",
        "description": "Test Product"
    }

@pytest.fixture
def sample_order_data():
    return {
        "invoice_no": "INV001",
        "customer_id": 1,
        "invoice_date": "2024-01-01T10:00:00",
        "country": "USA"
    }
