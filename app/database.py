# File: app/database.py (UPDATED WITH UNSUBSCRIBE TOKEN)
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/users.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    github_username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    timezone = Column(String(50), default="UTC")
    unsubscribe_token = Column(String(64), unique=True, index=True)  # New field
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    digest_history = relationship("DigestHistory", back_populates="user")

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    repositories = Column(Text)  # JSON string
    languages = Column(Text)     # JSON string
    stackoverflow_tags = Column(Text)  # JSON string
    max_items_per_section = Column(Integer, default=5)
    digest_time = Column(String(5), default="20:00")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="preferences")

class DigestHistory(Base):
    __tablename__ = "digest_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="sent")  # sent, failed, skipped
    items_count = Column(Integer, default=0)
    error_message = Column(Text)
    digest_type = Column(String(20), default="daily")  # daily, welcome
    
    user = relationship("User", back_populates="digest_history")

def init_db():
    """Initialize database tables"""
    import os
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()