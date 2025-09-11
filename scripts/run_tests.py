#!/usr/bin/env python3
"""
Test runner with coverage and reporting
"""
import os
import sys
import subprocess
from pathlib import Path

def install_test_dependencies():
    """Install testing dependencies if not present"""
    try:
        import pytest
        import pytest_cov
        import httpx  # Required for TestClient
    except ImportError:
        print("📦 Installing test dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "pytest", "pytest-cov", "pytest-asyncio", "httpx"
        ])

def run_tests(coverage=True, verbose=True):
    """Run the test suite"""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🧪 Running Retail Insights Test Suite")
    print("=" * 40)
    
    cmd = [sys.executable, "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend([
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
    
    cmd.append("tests/")
    
    result = subprocess.run(cmd)
    
    if coverage:
        print("\n📊 Coverage report generated in htmlcov/")
        print("   Open htmlcov/index.html in your browser to view detailed coverage")
    
    return result.returncode == 0

def run_linting():
    """Run code quality checks"""
    print("\n🔍 Running code quality checks...")
    
    try:
        # Try to run flake8 if available
        subprocess.run([sys.executable, "-m", "flake8", "app/", "tests/"], check=False)
    except FileNotFoundError:
        print("💡 Install flake8 for code linting: pip install flake8")

def main():
    install_test_dependencies()
    
    # Run tests
    success = run_tests()
    
    # Run linting
    run_linting()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
