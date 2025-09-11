# Retail Insights API

A comprehensive retail analytics platform built with **FastAPI**, **PostgreSQL**, and **Jupyter** for data analysis and machine learning capabilities.

## 🚀 Features

- **🔐 Secure Authentication**: JWT-based authentication system with password hashing
- **🛡️ Security Headers**: Comprehensive security middleware and input validation
- **📊 RESTful API**: Complete CRUD operations for customers, products, orders, and order items
- **📚 Interactive Documentation**: Auto-generated Swagger/OpenAPI docs at `/docs`
- **🗄️ Database Integration**: PostgreSQL with SQLAlchemy ORM
- **📈 Analytics Ready**: Jupyter notebooks for KPI analysis and insights
- **🏗️ Scalable Architecture**: Modular design with separate routers, schemas, and CRUD operations
- **🔧 Development Tools**: Helper scripts for setup, testing, and development

## 🏗️ Project Structure

```
retail-insights/
├── app/
│   ├── crud/           # Database operations
│   ├── routers/        # API endpoints
│   ├── schemas/        # Pydantic models
│   ├── database.py     # Database configuration
│   ├── dependencies.py # FastAPI dependencies
│   ├── models.py       # SQLAlchemy models
│   └── main.py         # FastAPI application
├── notebooks/
│   └── kpis.ipynb      # Analytics and KPIs
├── data/               # Data files
├── docs/               # Documentation
├── scripts/            # Helper scripts
├── tests/              # Unit/integration tests
├── requirements.txt    # Python dependencies
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

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n retail-insights python=3.8
conda activate retail-insights
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
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
python scripts/init_db.py
```

### 6. Start the API Server

**Option 1: Using the development script (recommended)**

```bash
python scripts/run_dev.py
```

**Option 2: Direct uvicorn command**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:

- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

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

## 📊 Analytics & Notebooks

### Starting Jupyter Lab

```bash
jupyter lab
```

Navigate to `notebooks/kpis.ipynb` for:

- Total sales revenue analysis
- Top 10 products by sales
- Sales performance by country
- Customer insights and spending patterns

### Key Performance Indicators (KPIs)

The analytics notebook provides insights on:

- 💰 **Total Revenue**: Sum of all order items
- 📦 **Order Volume**: Number of orders and items
- 🏆 **Top Products**: Best-selling products
- 🌍 **Geographic Analysis**: Sales by country
- 👥 **Customer Analytics**: Top customers and spending patterns

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

### Health & Status (No Auth Required)

- `GET /` - Welcome message
- `GET /health` - Health check endpoint

## 🧪 Testing

**Option 1: Using the test runner script (recommended)**

```bash
python scripts/run_tests.py
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

## 🔧 Development Scripts

The project includes several helper scripts in the `scripts/` directory:

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

1. **Setup Environment**: `cp env.sample .env` and configure your settings
2. **Generate Keys**: `python scripts/generate_keys.py` and update `.env`
3. **Start the API**: `python scripts/run_dev.py` (or `uvicorn app.main:app --reload`)
4. **Register User**: Use `/auth/register` endpoint to create your first user
5. **Login**: Get your JWT token from `/auth/login`
6. **Open Documentation**: Visit http://localhost:8000/docs
7. **Test Endpoints**: Use the interactive Swagger UI with authentication
8. **Analyze Data**: Open Jupyter and run `notebooks/kpis.ipynb`
9. **Run Tests**: `python scripts/run_tests.py` to ensure everything works
10. **Iterate**: Make changes and test with `--reload` for auto-restart

## 🗺️ Roadmap

### Phase 1: Foundation ✅

- [x] CRUD API endpoints
- [x] Database models and schemas
- [x] Interactive API documentation
- [x] Basic analytics notebook

### Phase 2: Authentication & Authorization ✅

- [x] User authentication (JWT)
- [x] Password hashing with bcrypt
- [x] Security headers and middleware
- [x] Request validation and sanitization
- [ ] Role-based access control
- [ ] API rate limiting

### Phase 3: Advanced Analytics

- [ ] Customer segmentation (RFM analysis)
- [ ] Market basket analysis
- [ ] Seasonal trend analysis
- [ ] Real-time dashboards

### Phase 4: Machine Learning

- [ ] Sales forecasting models
- [ ] Customer lifetime value prediction
- [ ] Recommendation systems
- [ ] Anomaly detection

### Phase 5: Production Ready

- [ ] Docker containerization
- [ ] CI/CD pipelines
- [ ] Monitoring and logging
- [ ] Performance optimization
- [ ] Automated testing suite

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
