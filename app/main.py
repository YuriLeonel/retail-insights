from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
import os

from app.routers import customers, products, orders, order_items, auth
from app.database import init_db
from app.auth import get_current_user

load_dotenv()
env = os.getenv("APP_ENV")
debug = os.getenv("APP_DEBUG", "false").lower() == "true"

app = FastAPI(
    title="Retail Insights API",
    description="""
    A comprehensive retail analytics API built with FastAPI and PostgreSQL.
    
    ## Features
    
    * **Authentication**: Secure JWT-based authentication system
    * **Customer Management**: Create, read, update, and delete customer records
    * **Product Catalog**: Manage product inventory with stock codes and descriptions
    * **Order Processing**: Handle customer orders and order tracking
    * **Order Items**: Manage individual items within orders with quantities and pricing
    
    ## Security
    
    This API requires authentication for all endpoints except `/auth/login` and `/auth/register`.
    Use the authentication endpoints to obtain a JWT token, then include it in the Authorization header.
    
    ## Getting Started
    
    1. Register a new user at `/auth/register`
    2. Login at `/auth/login` to get your access token
    3. Use the token in the Authorization header: `Bearer <your_token>`
    4. Explore the protected endpoints below
    """,
    version="1.0.0",
    contact={
        "name": "Retail Insights Team",
        "email": "contact@retailinsights.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    debug=debug,
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Configure for your frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()

# Include routers
# Authentication router (no auth required)
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

# Protected routers (require authentication)
app.include_router(
    customers.router,
    prefix="/customers",
    tags=["Customers"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Customer not found"}},
)

app.include_router(
    products.router,
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Product not found"}},
)

app.include_router(
    orders.router,
    prefix="/orders",
    tags=["Orders"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Order not found"}},
)

app.include_router(
    order_items.router,
    prefix="/order-items",
    tags=["Order Items"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Order item not found"}},
)

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint that returns a welcome message.
    
    This endpoint can be used to verify that the API is running correctly.
    """
    return {
        "message": "Welcome to Retail Insights API!",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancer probes.
    
    Returns the current status of the API service.
    """
    return {
        "status": "healthy",
        "service": "retail-insights-api",
        "version": "1.0.0"
    }
