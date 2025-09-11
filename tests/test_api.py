import pytest
from fastapi.testclient import TestClient

def test_root_endpoint(client: TestClient):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to Retail Insights API!"
    assert data["version"] == "1.0.0"

def test_health_check(client: TestClient):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "retail-insights-api"

def test_create_customer(client: TestClient, sample_customer_data):
    """Test creating a customer"""
    response = client.post("/customers/", json=sample_customer_data)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_name"] == sample_customer_data["customer_name"]
    assert data["country"] == sample_customer_data["country"]
    assert "customer_id" in data

def test_get_customers(client: TestClient, sample_customer_data):
    """Test getting all customers"""
    # Create a customer first
    client.post("/customers/", json=sample_customer_data)
    
    response = client.get("/customers/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_customer_by_id(client: TestClient, sample_customer_data):
    """Test getting a customer by ID"""
    # Create a customer first
    create_response = client.post("/customers/", json=sample_customer_data)
    customer_id = create_response.json()["customer_id"]
    
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == customer_id

def test_update_customer(client: TestClient, sample_customer_data):
    """Test updating a customer"""
    # Create a customer first
    create_response = client.post("/customers/", json=sample_customer_data)
    customer_id = create_response.json()["customer_id"]
    
    updated_data = {
        "customer_name": "Jane Doe",
        "country": "Canada"
    }
    
    response = client.put(f"/customers/{customer_id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_name"] == updated_data["customer_name"]
    assert data["country"] == updated_data["country"]

def test_delete_customer(client: TestClient, sample_customer_data):
    """Test deleting a customer"""
    # Create a customer first
    create_response = client.post("/customers/", json=sample_customer_data)
    customer_id = create_response.json()["customer_id"]
    
    response = client.delete(f"/customers/{customer_id}")
    assert response.status_code == 200
    
    # Verify customer is deleted
    get_response = client.get(f"/customers/{customer_id}")
    assert get_response.status_code == 404

def test_create_product(client: TestClient, sample_product_data):
    """Test creating a product"""
    response = client.post("/products/", json=sample_product_data)
    assert response.status_code == 200
    data = response.json()
    assert data["stock_code"] == sample_product_data["stock_code"]
    assert data["description"] == sample_product_data["description"]

def test_get_products(client: TestClient, sample_product_data):
    """Test getting all products"""
    # Create a product first
    client.post("/products/", json=sample_product_data)
    
    response = client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_create_order(client: TestClient, sample_customer_data, sample_order_data):
    """Test creating an order"""
    # Create a customer first
    customer_response = client.post("/customers/", json=sample_customer_data)
    customer_id = customer_response.json()["customer_id"]
    
    order_data = sample_order_data.copy()
    order_data["customer_id"] = customer_id
    
    response = client.post("/orders/", json=order_data)
    assert response.status_code == 200
    data = response.json()
    assert data["invoice_no"] == order_data["invoice_no"]
    assert data["customer_id"] == customer_id

def test_invalid_customer_id(client: TestClient):
    """Test getting a non-existent customer"""
    response = client.get("/customers/99999")
    assert response.status_code == 404

def test_invalid_product_id(client: TestClient):
    """Test getting a non-existent product"""
    response = client.get("/products/99999")
    assert response.status_code == 404
