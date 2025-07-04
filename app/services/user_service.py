# File: app/services/user_service.py
from sqlalchemy.orm import Session
from app.database import User, UserPreferences, DigestHistory
from datetime import datetime, timedelta
import json
import re

class UserService:
    def create_user(self, db: Session, name: str, github_username: str, email: str) -> User:
        """Create a new user with validation"""
        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Invalid email format")
        
        # Check if user already exists
        if db.query(User).filter(User.email == email).first():
            raise ValueError("User with this email already exists")
        
        if db.query(User).filter(User.github_username == github_username).first():
            raise ValueError("User with this GitHub username already exists")
        
        # Create user
        user = User(
            name=name.strip(),
            github_username=github_username.strip(),
            email=email.strip().lower()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create default preferences
        preferences = UserPreferences(
            user_id=user.id,
            repositories=json.dumps([]),
            languages=json.dumps(["python"]),
            stackoverflow_tags=json.dumps(["python"])
        )
        db.add(preferences)
        db.commit()
        
        return user
    
    def get_user_by_id(self, db: Session, user_id: int) -> User:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_preferences(self, db: Session, user_id: int) -> UserPreferences:
        """Get user preferences"""
        preferences = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
        if not preferences:
            # Create default preferences if none exist
            preferences = UserPreferences(
                user_id=user_id,
                repositories=json.dumps([]),
                languages=json.dumps(["python"]),
                stackoverflow_tags=json.dumps(["python"])
            )
            db.add(preferences)
            db.commit()
            db.refresh(preferences)
        return preferences
    
    def update_preferences(self, db: Session, user_id: int, repositories: str, 
                         languages: str, stackoverflow_tags: str, digest_time: str, timezone: str):
        """Update user preferences"""
        preferences = self.get_user_preferences(db, user_id)
        
        # Parse and validate input
        repo_list = [r.strip() for r in repositories.split(',') if r.strip()]
        lang_list = [l.strip() for l in languages.split(',') if l.strip()]
        tag_list = [t.strip() for t in stackoverflow_tags.split(',') if t.strip()]
        
        # Validate time format
        if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', digest_time):
            raise ValueError("Invalid time format. Use HH:MM")
        
        # Update preferences
        preferences.repositories = json.dumps(repo_list)
        preferences.languages = json.dumps(lang_list)
        preferences.stackoverflow_tags = json.dumps(tag_list)
        preferences.digest_time = digest_time
        
        # Update user timezone
        user = self.get_user_by_id(db, user_id)
        user.timezone = timezone
        user.updated_at = datetime.utcnow()
        
        db.commit()
    
    def toggle_user_status(self, db: Session, user_id: int):
        """Toggle user active status"""
        user = self.get_user_by_id(db, user_id)
        if user:
            user.is_active = not user.is_active
            user.updated_at = datetime.utcnow()
            db.commit()
    
    def get_digest_history(self, db: Session, user_id: int, limit: int = 10) -> list:
        """Get user's digest history"""
        return db.query(DigestHistory).filter(
            DigestHistory.user_id == user_id
        ).order_by(DigestHistory.sent_at.desc()).limit(limit).all()
    
    def get_user_stats(self, db: Session, user_id: int) -> dict:
        """Get user statistics"""
        history = db.query(DigestHistory).filter(DigestHistory.user_id == user_id)
        
        return {
            "total_digests": history.count(),
            "last_digest": history.order_by(DigestHistory.sent_at.desc()).first(),
            "success_rate": self._calculate_success_rate(history.all())
        }
    
    def get_all_users(self, db: Session) -> list:
        """Get all users for admin panel"""
        return db.query(User).order_by(User.created_at.desc()).all()
    
    def _calculate_success_rate(self, history: list) -> float:
        """Calculate digest success rate"""
        if not history:
            return 0.0
        
        successful = sum(1 for h in history if h.status == "sent")
        return (successful / len(history)) * 100
