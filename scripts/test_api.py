#!/usr/bin/env python3
"""
Manual API testing script for Retail Insights API
This script helps you test the API endpoints manually
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api" if BASE_URL != "http://localhost:8000" else BASE_URL

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        
    def wait_for_api(self, max_attempts: int = 30) -> bool:
        """Wait for API to be ready"""
        print("⏳ Waiting for API to be ready...")
        for attempt in range(max_attempts):
            try:
                response = self.session.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ API is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            print(f"   Attempt {attempt + 1}/{max_attempts}...")
            time.sleep(2)
        
        print("❌ API failed to start within expected time")
        return False
    
    def register_user(self, username: str = "testuser", email: str = "test@example.com", password: str = "testpass123") -> bool:
        """Register a new user"""
        print(f"👤 Registering user: {username}")
        
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        
        try:
            response = self.session.post(f"{self.base_url}/auth/register", json=data)
            if response.status_code == 200:
                print("✅ User registered successfully!")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def login(self, username: str = "testuser", password: str = "testpass123") -> bool:
        """Login and get access token"""
        print(f"🔐 Logging in as: {username}")
        
        data = {
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(f"{self.base_url}/auth/login", json=data)
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                print("✅ Login successful!")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_endpoint(self, method: str, endpoint: str, data: Dict[Any, Any] = None, description: str = "") -> bool:
        """Test a specific endpoint"""
        url = f"{self.base_url}{endpoint}"
        print(f"🧪 Testing {method.upper()} {endpoint}")
        if description:
            print(f"   {description}")
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                print(f"❌ Unsupported method: {method}")
                return False
            
            if response.status_code in [200, 201]:
                print(f"✅ Success: {response.status_code}")
                if response.content:
                    try:
                        result = response.json()
                        if isinstance(result, list) and len(result) > 0:
                            print(f"   📊 Returned {len(result)} items")
                        elif isinstance(result, dict):
                            print(f"   📊 Response keys: {list(result.keys())}")
                    except:
                        print(f"   📄 Response: {response.text[:100]}...")
                return True
            else:
                print(f"❌ Failed: {response.status_code} - {response.text[:200]}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Retail Insights API Tests")
        print("=" * 50)
        
        # Wait for API
        if not self.wait_for_api():
            return
        
        # Test health endpoint
        print("\n1. Testing Health Endpoint")
        self.test_endpoint("GET", "/health", description="Basic health check")
        
        # Test root endpoint
        print("\n2. Testing Root Endpoint")
        self.test_endpoint("GET", "/", description="API information")
        
        # Register and login
        print("\n3. Testing Authentication")
        self.register_user()
        if not self.login():
            print("❌ Cannot proceed without authentication")
            return
        
        # Test protected endpoints
        print("\n4. Testing Protected Endpoints")
        
        # Analytics endpoints
        print("\n   📊 Analytics Endpoints:")
        self.test_endpoint("GET", "/analytics/health", description="Analytics health check")
        self.test_endpoint("GET", "/analytics/kpis", description="Get KPIs")
        self.test_endpoint("GET", "/analytics/top-customers", description="Get top customers")
        self.test_endpoint("GET", "/analytics/top-products", description="Get top products")
        self.test_endpoint("GET", "/analytics/sales-trends", description="Get sales trends")
        self.test_endpoint("GET", "/analytics/customer-segments", description="Get customer segments")
        self.test_endpoint("GET", "/analytics/dashboard", description="Get analytics dashboard")
        
        # External data endpoints
        print("\n   🌐 External Data Endpoints:")
        self.test_endpoint("GET", "/external/health", description="External data health check")
        self.test_endpoint("GET", "/external/currency/supported", description="Get supported currencies")
        self.test_endpoint("GET", "/external/currency/rates", description="Get currency rates")
        self.test_endpoint("GET", "/external/currency/convert?amount=100&from_currency=USD&to_currency=EUR", description="Convert currency")
        
        # ML endpoints
        print("\n   🤖 Machine Learning Endpoints:")
        self.test_endpoint("GET", "/ml/health", description="ML health check")
        self.test_endpoint("GET", "/ml/models/status", description="Get model status")
        self.test_endpoint("GET", "/ml/insights", description="Get ML insights")
        
        # Test ML model training (this might take a while)
        print("\n   🧠 Training ML Models:")
        print("   ⚠️  Note: Model training requires data. This might fail if no data is available.")
        self.test_endpoint("POST", "/ml/train/segmentation", description="Train segmentation model")
        self.test_endpoint("POST", "/ml/train/churn", description="Train churn model")
        
        print("\n" + "=" * 50)
        print("✅ API testing completed!")
        print(f"🌐 API Documentation: {self.base_url}/docs")
        print(f"📊 ReDoc Documentation: {self.base_url}/redoc")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Retail Insights API")
    parser.add_argument("--url", default=BASE_URL, help="API base URL")
    parser.add_argument("--username", default="testuser", help="Test username")
    parser.add_argument("--password", default="testpass123", help="Test password")
    
    args = parser.parse_args()
    
    tester = APITester(args.url)
    tester.run_all_tests()

if __name__ == "__main__":
    main()
