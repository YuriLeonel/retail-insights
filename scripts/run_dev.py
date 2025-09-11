#!/usr/bin/env python3
"""
Development server runner with environment setup
"""
import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if environment is properly set up"""
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    if not env_file.exists():
        print("⚠️  No .env file found. Creating one with default values...")
        env_content = """# Database Configuration (REQUIRED - Update with your actual credentials)
DB_USER=your_username
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name

# Application Configuration
APP_ENV=development
APP_DEBUG=false

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Security Configuration (REQUIRED - Generate secure keys)
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file. Please update it with your database credentials.")
        return False
    return True

def check_database():
    """Check if database is accessible"""
    try:
        import psycopg2
        from dotenv import load_dotenv
        
        load_dotenv()
        
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", "5432")
        )
        conn.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Make sure PostgreSQL is running and credentials are correct in .env")
        return False

def run_server():
    """Run the development server"""
    print("🚀 Starting Retail Insights API server...")
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Run with uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--reload",
        "--host", os.getenv("API_HOST", "0.0.0.0"),
        "--port", os.getenv("API_PORT", "8000")
    ]
    
    subprocess.run(cmd)

def main():
    print("🔧 Retail Insights Development Server")
    print("=" * 40)
    
    if not check_environment():
        return
    
    if not check_database():
        print("\n💡 To set up PostgreSQL:")
        print("   sudo apt install postgresql postgresql-contrib")
        print("   sudo -u postgres createuser --interactive")
        print("   sudo -u postgres createdb retail_db")
        return
    
    run_server()

if __name__ == "__main__":
    main()
