# Retail Insights API

A comprehensive retail analytics platform built with **FastAPI**, **PostgreSQL**, **Docker**, and **Jupyter** for advanced data analysis, machine learning, and production-ready deployment.

## 🚀 Features

- **🔐 Secure Authentication**: JWT-based authentication system with password hashing
- **🛡️ Security Headers**: Comprehensive security middleware and input validation
- **📊 RESTful API**: Complete CRUD operations for customers, products, orders, and order items
- **📈 Advanced Analytics**: Real-time analytics with customer insights, sales trends, and KPI tracking
- **🤖 Machine Learning**: Demand forecasting, customer segmentation, and predictive analytics
- **🌐 External Data Integration**: Market data APIs and external service integration
- **📚 Interactive Documentation**: Auto-generated Swagger/OpenAPI docs at `/docs`
- **🗄️ Database Integration**: PostgreSQL with async SQLAlchemy ORM support
- **🐳 Docker Ready**: Complete containerization with multi-service architecture
- **📓 Jupyter Integration**: Data analysis notebooks with ML model development
- **🏗️ Production Infrastructure**: Nginx reverse proxy, Redis caching, and health monitoring
- **🔧 Development Tools**: Comprehensive Makefile and helper scripts

## 🏗️ Project Structure

```
retail-insights/
├── app/
│   ├── crud/           # Database operations (async support)
│   ├── routers/        # API endpoints (auth, customers, products, orders, analytics, ml)
│   ├── schemas/        # Pydantic models (including analytics schemas)
│   ├── ml/             # Machine learning models and services
│   ├── services/       # External API integrations
│   ├── database.py     # Database configuration (async + sync)
│   ├── dependencies.py # FastAPI dependencies
│   ├── auth.py         # Authentication utilities
│   └── main.py         # FastAPI application
├── notebooks/          # Jupyter notebooks for data analysis
├── nginx/              # Nginx configuration for production
├── scripts/            # Helper scripts and database initialization
├── data/               # Data files and models
├── models/             # ML model storage
├── logs/               # Application logs
├── tests/              # Unit/integration tests
├── docker-compose.yml  # Production Docker setup
├── docker-compose.dev.yml # Development Docker setup
├── Dockerfile          # Production container
├── Dockerfile.dev      # Development container
├── Dockerfile.jupyter  # Jupyter container
├── requirements.txt    # Python dependencies
├── Makefile           # Development commands
└── README.md
```

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip or conda for package management

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd retail-insights
```

### 2. Set Up Development Environment

```bash
# Create virtual environment and install dependencies
make setup
source venv/bin/activate  # On Windows: venv\Scripts\activate
make install

# Or using conda
conda create -n retail-insights python=3.8
conda activate retail-insights
make install
```

### 4. Environment Configuration

Create a PostgreSQL database and set up environment variables:

```bash
# Create .env file from template
cp env.sample .env
```

Edit `.env` with your database credentials and security settings:

```env
# Database Configuration (REQUIRED)
DB_USER=retail_user
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=retail_insights_db

# Application Configuration
APP_ENV=development
APP_DEBUG=false

# Security Configuration (REQUIRED)
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**🔐 Generate Secure Keys:**

```bash
# Generate secure keys for production
python scripts/generate_keys.py
```

**⚠️ Security Note:** Never commit your `.env` file to version control!

### 5. Initialize Database

```bash
# Option 1: Automatic initialization (recommended)
# Database tables will be created automatically when you start the application

# Option 2: Manual initialization
make init-db
```

### 6. Start the API Server

**Option 1: Using Makefile (recommended)**

```bash
make dev
```

**Option 2: Direct uvicorn command**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:

- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐳 Docker Deployment

### Quick Start with Docker

The fastest way to get started is using Docker Compose:

```bash
# Clone and start all services
git clone <repository-url>
cd retail-insights
docker-compose up -d

# Or for development with hot reload
docker-compose -f docker-compose.dev.yml up -d
```

### Docker Services

The Docker setup includes:

- **PostgreSQL Database**: Persistent data storage
- **Redis Cache**: Session and data caching
- **FastAPI Application**: Main API server
- **Jupyter Lab**: Data analysis environment
- **Nginx**: Reverse proxy and load balancer (production)

### Environment Configuration

Create a `.env` file for Docker configuration:

```env
# Database Configuration
DB_NAME=retail_insights
DB_USER=postgres
DB_PASSWORD=your_secure_password_here
DB_HOST=db
DB_PORT=5432

# Application Configuration
APP_ENV=production
APP_DEBUG=false

# Security Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis Configuration
REDIS_URL=redis://redis:6379
```

### Docker Commands

```bash
# Start all services
docker-compose up -d

# Start in development mode (with hot reload)
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down

# Rebuild and start
docker-compose up --build -d

# Access Jupyter Lab
# Open http://localhost:8888 in your browser

# Access API documentation
# Open http://localhost:8000/docs in your browser
```

### Production Deployment

For production deployment:

```bash
# Use production compose file
docker-compose -f docker-compose.yml up -d

# With Nginx reverse proxy
# API will be available at http://localhost (port 80)
# Jupyter at http://localhost:8888
```

### Individual Container Management

```bash
# Build specific containers
docker build -t retail-insights-api .
docker build -f Dockerfile.dev -t retail-insights-dev .
docker build -f Dockerfile.jupyter -t retail-insights-jupyter .

# Run individual containers
docker run -p 8000:8000 retail-insights-api
docker run -p 8888:8888 retail-insights-jupyter
```

## 📚 API Usage Examples

### Using curl

```bash
# Create a customer
curl -X POST "http://localhost:8000/customers/" \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "John Doe", "country": "USA"}'

# Get all customers
curl -X GET "http://localhost:8000/customers/"

# Create a product
curl -X POST "http://localhost:8000/products/" \
  -H "Content-Type: application/json" \
  -d '{"stock_code": "PROD001", "description": "Sample Product"}'

# Create an order
curl -X POST "http://localhost:8000/orders/" \
  -H "Content-Type: application/json" \
  -d '{"invoice_no": "INV001", "customer_id": 1, "invoice_date": "2024-01-01T10:00:00", "country": "USA"}'
```

### Using HTTPie

```bash
# Create a customer
http POST localhost:8000/customers/ customer_name="Jane Smith" country="UK"

# Get customer by ID
http GET localhost:8000/customers/1

# Update customer
http PUT localhost:8000/customers/1 customer_name="Jane Doe" country="UK"

# Delete customer
http DELETE localhost:8000/customers/1
```

### Using Python requests

```python
import requests

# Create a customer
response = requests.post(
    "http://localhost:8000/customers/",
    json={"customer_name": "Alice Johnson", "country": "Canada"}
)
print(response.json())

# Get all products
response = requests.get("http://localhost:8000/products/")
print(response.json())
```

## 🔐 Authentication

The API uses JWT-based authentication. All endpoints except `/auth/*` require authentication.

### Register a New User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password123"
  }'
```

### Login and Get Token

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password123"
  }'
```

Response:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include the token in the Authorization header for all protected endpoints:

```bash
curl -X GET "http://localhost:8000/customers/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### Get Current User Info

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer your_token_here"
```

### Python Example with Authentication

```python
import requests

# Login
login_response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": "john_doe", "password": "secure_password123"}
)
token = login_response.json()["access_token"]

# Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/customers/", headers=headers)
print(response.json())
```

## 📊 Analytics & Machine Learning

### Real-time Analytics API

The platform provides comprehensive analytics through RESTful endpoints:

```bash
# Get top customers by revenue
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/analytics/top-customers?limit=10"

# Get sales trends for the last 30 days
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/analytics/sales-trends?days=30"

# Get customer segmentation analysis
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/analytics/customer-segments"

# Get key performance indicators
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/analytics/kpis"
```

### Machine Learning Capabilities

#### Demand Forecasting

```bash
# Generate demand forecast for a product
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "forecast_days": 30}' \
  "http://localhost:8000/ml/forecast"
```

#### Customer Segmentation

```bash
# Run customer segmentation analysis
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"method": "rfm", "segments": 5}' \
  "http://localhost:8000/ml/segment-customers"
```

### Jupyter Lab Integration

Start Jupyter Lab for advanced data analysis:

```bash
# Using Docker (recommended)
docker-compose up jupyter

# Or locally
make notebook
```

Access Jupyter Lab at http://localhost:8888

### Analytics Features

- 💰 **Revenue Analytics**: Total revenue, trends, and forecasting
- 📦 **Product Performance**: Top products, inventory analysis, demand forecasting
- 🌍 **Geographic Analysis**: Sales by country, regional trends
- 👥 **Customer Insights**: Segmentation, lifetime value, behavior analysis
- 📈 **Sales Trends**: Time-series analysis, seasonal patterns
- 🎯 **KPI Dashboard**: Real-time key performance indicators
- 🤖 **ML Models**: Automated forecasting and segmentation
- 📊 **Data Visualization**: Interactive charts and reports

## 🔧 API Endpoints

### Authentication (No Auth Required)

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user information (requires auth)

### Customers (Authentication Required)

- `GET /customers/` - List all customers
- `GET /customers/{id}` - Get customer by ID
- `POST /customers/` - Create new customer
- `PUT /customers/{id}` - Update customer
- `DELETE /customers/{id}` - Delete customer

### Products (Authentication Required)

- `GET /products/` - List all products
- `GET /products/{id}` - Get product by ID
- `POST /products/` - Create new product
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product

### Orders (Authentication Required)

- `GET /orders/` - List all orders
- `GET /orders/{id}` - Get order by ID
- `POST /orders/` - Create new order
- `PUT /orders/{id}` - Update order
- `DELETE /orders/{id}` - Delete order

### Order Items (Authentication Required)

- `GET /order-items/` - List all order items
- `GET /order-items/{id}` - Get order item by ID
- `POST /order-items/` - Create new order item
- `PUT /order-items/{id}` - Update order item
- `DELETE /order-items/{id}` - Delete order item

### Analytics (Authentication Required)

- `GET /analytics/top-customers` - Get top customers by revenue
- `GET /analytics/top-products` - Get top products by sales
- `GET /analytics/sales-trends` - Get sales trends over time
- `GET /analytics/revenue-by-country` - Get revenue breakdown by country
- `GET /analytics/customer-segments` - Get customer segmentation analysis
- `GET /analytics/kpis` - Get key performance indicators

### Machine Learning (Authentication Required)

- `POST /ml/forecast` - Generate demand forecasting
- `POST /ml/segment-customers` - Run customer segmentation
- `GET /ml/models` - List available ML models
- `POST /ml/train` - Train new ML models
- `GET /ml/predictions` - Get prediction results

### External Data (Authentication Required)

- `GET /external-data/market-trends` - Get market trend data
- `GET /external-data/competitor-analysis` - Get competitor analysis
- `POST /external-data/sync` - Sync external data sources
- `GET /external-data/sources` - List available data sources

### Health & Status (No Auth Required)

- `GET /` - Welcome message
- `GET /health` - Health check endpoint

## 🧪 Testing

**Option 1: Using Makefile (recommended)**

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run fast tests (no coverage)
make test-fast
```

**Option 2: Direct pytest commands**

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run with verbose output
pytest -v tests/
```

## 🔧 Makefile Commands

The project includes a comprehensive Makefile for easy development workflow:

### Quick Commands

```bash
make help          # Show all available commands
make setup         # Create virtual environment
make install       # Install dependencies
make dev           # Start development server
make test          # Run test suite
make test-cov      # Run tests with coverage
make test-fast     # Run tests without coverage (faster)
make init-db       # Initialize database tables
make seed-db       # Seed database with sample data
make notebook      # Start Jupyter Lab
make clean         # Clean up temporary files
make check         # Run all quality checks (lint + test)
make status        # Show project status
make quickstart    # Quick setup for new developers
```

### Development Workflow

```bash
# Complete setup for new developers
make quickstart
source venv/bin/activate
make install
make init-db
make dev
```

### Code Quality

```bash
make lint          # Run code linting
make format        # Format code with black
make check         # Run linting and tests
```

### Docker Commands (Optional)

```bash
make docker-build  # Build Docker image
make docker-run    # Run Docker container
```

## 🔧 Development Scripts

The project also includes several helper scripts in the `scripts/` directory:

### `generate_keys.py`

Generate secure keys for JWT and application secrets:

```bash
python scripts/generate_keys.py
```

### `init_db.py`

Initialize the database with all required tables:

```bash
python scripts/init_db.py
```

### `run_dev.py`

Start the development server with environment checks:

```bash
python scripts/run_dev.py
```

### `run_tests.py`

Run the complete test suite with coverage and linting:

```bash
python scripts/run_tests.py
```

### `seed.py`

Seed the database with sample data (if available):

```bash
python scripts/seed.py
```

## 🔄 Development Workflow

1. **Quick Setup**: `make quickstart` and follow the instructions
2. **Environment Setup**: `cp env.sample .env` and configure your settings
3. **Generate Keys**: `python scripts/generate_keys.py` and update `.env`
4. **Start the API**: `make dev` (or `uvicorn app.main:app --reload`)
5. **Register User**: Use `/auth/register` endpoint to create your first user
6. **Login**: Get your JWT token from `/auth/login`
7. **Open Documentation**: Visit http://localhost:8000/docs
8. **Test Endpoints**: Use the interactive Swagger UI with authentication
9. **Analyze Data**: `make notebook` and run `notebooks/kpis.ipynb`
10. **Run Tests**: `make test` to ensure everything works
11. **Code Quality**: `make check` for linting and testing
12. **Iterate**: Make changes and test with `--reload` for auto-restart

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔒 Security

This API implements comprehensive security measures:

### Implemented Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for secure password storage
- **Security Headers**: XSS protection, CSRF prevention, and more
- **Input Validation**: Pydantic models for request validation
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **Environment Security**: No hardcoded credentials

### Security Best Practices

- Always use HTTPS in production
- Keep JWT secrets secure and rotate regularly
- Never commit `.env` files to version control
- Use strong passwords and database credentials
- Monitor authentication attempts and failures

### Security Documentation

For detailed security information, vulnerability reporting, and deployment guidelines, see [SECURITY.md](SECURITY.md).

### Quick Security Setup

```bash
# Generate secure keys
python scripts/generate_keys.py

# Update your .env with secure values
# Never commit .env to version control!
```

## 📞 Support

- **Documentation**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **Email**: yurileonel.001@gmail.com

---

**Built with FastAPI, PostgreSQL, and modern Python tools**
