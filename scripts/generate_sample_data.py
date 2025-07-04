# File: scripts/generate_sample_data.py
#!/usr/bin/env python3
"""
Generate sample data for testing Dev Digest
Creates test users and digest history
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, User, UserPreferences, DigestHistory
from datetime import datetime, timedelta
import random

def generate_sample_data():
    """Generate sample data for testing"""
    db = SessionLocal()
    
    try:
        # Sample users
        users_data = [
            {
                "name": "John Doe",
                "github_username": "johndoe",
                "email": "john@example.com",
                "repos": ["microsoft/vscode", "facebook/react"],
                "languages": ["python", "javascript"],
                "tags": ["python", "react", "javascript"]
            },
            {
                "name": "Jane Smith",
                "github_username": "janesmith",
                "email": "jane@example.com",
                "repos": ["google/tensorflow", "pytorch/pytorch"],
                "languages": ["python", "c++"],
                "tags": ["python", "machine-learning", "tensorflow"]
            },
            {
                "name": "Bob Wilson",
                "github_username": "bobwilson",
                "email": "bob@example.com",
                "repos": ["golang/go", "kubernetes/kubernetes"],
                "languages": ["go", "rust"],
                "tags": ["go", "kubernetes", "docker"]
            }
        ]
        
        # Create users
        for user_data in users_data:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if existing_user:
                continue
            
            # Create user
            user = User(
                name=user_data["name"],
                github_username=user_data["github_username"],
                email=user_data["email"],
                is_active=True,
                timezone="UTC"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create preferences
            preferences = UserPreferences(
                user_id=user.id,
                repositories=str(user_data["repos"]).replace("'", '"'),
                languages=str(user_data["languages"]).replace("'", '"'),
                stackoverflow_tags=str(user_data["tags"]).replace("'", '"'),
                max_items_per_section=5,
                digest_time="20:00"
            )
            db.add(preferences)
            
            # Create sample digest history
            for i in range(7):  # Last 7 days
                date = datetime.utcnow() - timedelta(days=i)
                status = random.choice(["sent", "sent", "sent", "failed", "skipped"])
                items_count = random.randint(5, 15) if status == "sent" else 0
                error_message = "SMTP connection failed" if status == "failed" else None
                
                history = DigestHistory(
                    user_id=user.id,
                    sent_at=date,
                    status=status,
                    items_count=items_count,
                    error_message=error_message
                )
                db.add(history)
            
            print(f"Created user: {user.name} ({user.email})")
        
        db.commit()
        print("✅ Sample data generated successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error generating sample data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_sample_data()