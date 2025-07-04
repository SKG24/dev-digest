# File: setup.py
#!/usr/bin/env python3
import os
import subprocess
import sys

def setup_project():
    """Setup the Dev Digest project"""
    print("Setting up Dev Digest project...")
    
    # Create necessary directories
    directories = [
        'data',
        'logs',
        'static/css',
        'static/js',
        'templates/admin',
        'tests'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Install dependencies
    print("\nInstalling Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("\nCreating .env file...")
        with open('.env', 'w') as f:
            f.write("""# GitHub API Token (required)
GITHUB_TOKEN=your_github_personal_access_token_here

# Email Configuration (required)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com

# Application Settings
SECRET_KEY=dev-digest-secret-key-123
ADMIN_PASSWORD=admin123
APP_URL=http://localhost:8000

# Database
DATABASE_URL=sqlite:///data/users.db

# Logging
LOG_LEVEL=INFO
""")
        print("✅ Created .env file - please update with your credentials")
    
    # Initialize database
    print("\nInitializing database...")
    try:
        from app.database import init_db
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Update .env file with your GitHub token and email credentials")
    print("2. Run the application: python -m app.main")
    print("3. Visit http://localhost:8000 to access the application")
    print("4. Visit http://localhost:8000/admin/login to access admin panel")
    
    return True

if __name__ == "__main__":
    setup_project()