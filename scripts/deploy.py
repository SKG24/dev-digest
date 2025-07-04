# File: scripts/deploy.py
#!/usr/bin/env python3
"""
Production deployment script for Dev Digest
Handles deployment, health checks, and rollback
"""

import os
import subprocess
import sys
import time
import requests
from pathlib import Path

def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run shell command and return result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"Command failed: {cmd}")
        print(f"Error: {result.stderr}")
        sys.exit(1)
    
    return result

def health_check(url: str = "http://localhost:8000", timeout: int = 30) -> bool:
    """Check if the application is healthy"""
    print(f"Performing health check: {url}")
    
    for i in range(timeout):
        try:
            response = requests.get(f"{url}/", timeout=5)
            if response.status_code == 200:
                print("✅ Health check passed")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"Waiting for application to start... ({i+1}/{timeout})")
        time.sleep(1)
    
    print("❌ Health check failed")
    return False

def deploy():
    """Deploy the application"""
    print("🚀 Starting deployment...")
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("❌ .env file not found. Please create it from .env.example")
        sys.exit(1)
    
    # Run database backup
    print("📁 Creating database backup...")
    run_command("python scripts/backup.py")
    
    # Run tests
    print("🧪 Running tests...")
    result = run_command("python -m pytest tests/ -v --tb=short", check=False)
    if result.returncode != 0:
        print("❌ Tests failed. Deployment aborted.")
        sys.exit(1)
    
    # Build and start containers
    print("🐳 Building and starting containers...")
    run_command("docker-compose down")
    run_command("docker-compose build")
    run_command("docker-compose up -d")
    
    # Wait for containers to start
    time.sleep(10)
    
    # Health check
    if not health_check():
        print("❌ Deployment failed health check")
        rollback()
        sys.exit(1)
    
    print("✅ Deployment completed successfully!")
    print("🌐 Application available at: http://localhost:8000")
    print("👤 Admin panel: http://localhost:8000/admin/login")

def rollback():
    """Rollback to previous version"""
    print("🔄 Rolling back...")
    
    # Stop current containers
    run_command("docker-compose down")
    
    # Restore database if needed
    # This would typically restore from a backup
    print("📁 Database rollback not implemented")
    
    print("✅ Rollback completed")

def status():
    """Check deployment status"""
    print("📊 Checking deployment status...")
    
    result = run_command("docker-compose ps", check=False)
    print(result.stdout)
    
    if health_check():
        print("✅ Application is running healthy")
    else:
        print("❌ Application is not responding")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy.py [deploy|rollback|status]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "deploy":
        deploy()
    elif command == "rollback":
        rollback()
    elif command == "status":
        status()
    else:
        print("Invalid command. Use: deploy, rollback, or status")
        sys.exit(1)
