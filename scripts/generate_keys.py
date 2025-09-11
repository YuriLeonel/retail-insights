#!/usr/bin/env python3
"""
Generate secure keys for the .env file
"""
import secrets
import string

def generate_secret_key(length=32):
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_jwt_secret(length=64):
    """Generate a secure JWT secret key"""
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    print("🔐 Generating secure keys for .env file")
    print("=" * 50)
    
    secret_key = generate_secret_key()
    jwt_secret = generate_jwt_secret()
    
    print(f"SECRET_KEY={secret_key}")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print("\n⚠️  IMPORTANT: Keep these keys secure and never commit them to version control!")
    print("Add these to your .env file and ensure .env is in your .gitignore")
