# Retail Insights API - Development Makefile

.PHONY: help install setup dev test test-cov clean lint format init-db seed-db notebook docker-build docker-run

help: ## Show this help message
	@echo "Retail Insights API - Available Commands:"
	@echo "=========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	pip install -r requirements.txt

setup: ## Set up the development environment
	@echo "🔧 Setting up Retail Insights development environment..."
	python -m venv venv
	@echo "✅ Virtual environment created. Activate it with: source venv/bin/activate"
	@echo "Then run: make install"

dev: ## Start development server
	@echo "🚀 Starting development server..."
	python scripts/run_dev.py

test: ## Run tests
	@echo "🧪 Running test suite..."
	python scripts/run_tests.py

test-cov: ## Run tests with coverage report
	@echo "🧪 Running tests with coverage..."
	pytest --cov=app --cov-report=html --cov-report=term-missing tests/

test-fast: ## Run tests without coverage (faster)
	@echo "⚡ Running fast tests..."
	pytest tests/ -v

lint: ## Run code linting
	@echo "🔍 Running linter..."
	flake8 app/ tests/ --max-line-length=88 --extend-ignore=E203,W503

format: ## Format code with black
	@echo "🎨 Formatting code..."
	black app/ tests/ scripts/

init-db: ## Initialize database tables
	@echo "🗄️  Initializing database..."
	python scripts/init_db.py

seed-db: ## Seed database with sample data
	@echo "🌱 Seeding database..."
	python scripts/seed.py

notebook: ## Start Jupyter Lab for analytics
	@echo "📊 Starting Jupyter Lab..."
	jupyter lab

clean: ## Clean up temporary files
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf test.db

check: ## Run all quality checks
	@echo "✅ Running all quality checks..."
	make lint
	make test

api-docs: ## Open API documentation
	@echo "📖 Opening API documentation..."
	@echo "Make sure the server is running, then visit:"
	@echo "  - Swagger UI: http://localhost:8000/docs"
	@echo "  - ReDoc: http://localhost:8000/redoc"

status: ## Show project status
	@echo "📊 Retail Insights Project Status"
	@echo "================================="
	@echo "Python version: $(shell python --version)"
	@echo "Virtual env: $(VIRTUAL_ENV)"
	@echo "Dependencies: $(shell pip list | wc -l) packages installed"
	@echo "Tests: $(shell find tests/ -name "*.py" -not -name "__*" | wc -l) test files"
	@echo "API endpoints: $(shell find app/routers/ -name "*.py" | wc -l) router files"

# Docker commands
docker-dev: ## Start development environment with Docker
	@echo "🐳 Starting development environment with Docker..."
	./scripts/docker-setup.sh

docker-dev-stop: ## Stop development environment
	@echo "🛑 Stopping development environment..."
	docker compose -f docker-compose.dev.yml down

docker-dev-logs: ## View development logs
	@echo "📋 Viewing development logs..."
	docker compose -f docker-compose.dev.yml logs -f

docker-dev-restart: ## Restart development environment
	@echo "🔄 Restarting development environment..."
	docker compose -f docker-compose.dev.yml restart

docker-build: ## Build Docker image
	docker build -t retail-insights-api .

docker-run: ## Run Docker container
	docker run -p 8000:8000 --env-file .env retail-insights-api

# Quick start for new developers
quickstart: ## Quick setup for new developers
	@echo "🚀 Quick Start for Retail Insights API"
	@echo "======================================"
	@echo "1. Creating virtual environment..."
	make setup
	@echo "2. Please activate the virtual environment:"
	@echo "   source venv/bin/activate"
	@echo "3. Then run: make install && make init-db && make dev"
