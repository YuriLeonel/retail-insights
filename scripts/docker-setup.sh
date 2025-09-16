#!/bin/bash

# Docker setup script for Retail Insights API
# This script helps set up the development environment

set -e

echo "🚀 Setting up Retail Insights API with Docker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Database Configuration
DB_NAME=retail_insights
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Application Configuration
APP_ENV=development
APP_DEBUG=true

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# External API Keys (optional)
OPENWEATHER_API_KEY=
NEWS_API_KEY=
EOF
    echo "✅ Created .env file. Please update the values as needed."
else
    echo "✅ .env file already exists."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p models logs data notebooks nginx/ssl

# Build and start services
echo "🔨 Building and starting services..."
docker compose -f docker-compose.dev.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker compose -f docker-compose.dev.yml ps

# Run database migrations (if needed)
echo "🗄️ Setting up database..."
docker compose -f docker-compose.dev.yml exec api python -c "
from app.database import init_db, init_async_db
import asyncio
init_db()
asyncio.run(init_async_db())
print('Database initialized successfully!')
"

echo "✅ Setup complete!"
echo ""
echo "🌐 Services available at:"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Jupyter: http://localhost:8888"
echo ""
echo "🔧 Useful commands:"
echo "   - View logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "   - Stop services: docker-compose -f docker-compose.dev.yml down"
echo "   - Restart services: docker-compose -f docker-compose.dev.yml restart"
echo "   - Access database: docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d retail_insights"
