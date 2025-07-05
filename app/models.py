# File: app/models.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    github_username: str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    name: str
    github_username: str
    email: str
    is_active: bool
    timezone: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class PreferencesUpdate(BaseModel):
    repositories: Optional[str] = ""
    languages: Optional[str] = ""
    stackoverflow_tags: Optional[str] = ""
    digest_time: Optional[str] = "20:00"
    timezone: Optional[str] = "UTC"

class DigestHistoryResponse(BaseModel):
    id: int
    sent_at: datetime
    status: str
    items_count: int
    error_message: Optional[str]
    
    class Config:
        orm_mode = True

class SystemHealth(BaseModel):
    total_users: int
    active_users: int
    digests_sent_today: int
    scheduler_status: str
    last_run: Optional[datetime]
    errors_count: int