# File: migrate_database.py
"""
Migration script to add unsubscribe_token and digest_type fields
Run this script to update existing database schema
"""
import sqlite3
import hashlib
import secrets
from datetime import datetime
import os

def migrate_database():
    """Add new fields to existing database"""
    db_path = "data/users.db"
    
    if not os.path.exists(db_path):
        print("Database doesn't exist yet. No migration needed.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if unsubscribe_token column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'unsubscribe_token' not in columns:
            print("Adding unsubscribe_token column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN unsubscribe_token TEXT")
            
            # Generate tokens for existing users
            cursor.execute("SELECT id, email FROM users WHERE unsubscribe_token IS NULL")
            users = cursor.fetchall()
            
            for user_id, email in users:
                token = generate_unsubscribe_token(email)
                cursor.execute(
                    "UPDATE users SET unsubscribe_token = ? WHERE id = ?",
                    (token, user_id)
                )
            
            print(f"Generated unsubscribe tokens for {len(users)} existing users")
        
        # Check if digest_type column exists in digest_history
        cursor.execute("PRAGMA table_info(digest_history)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'digest_type' not in columns:
            print("Adding digest_type column to digest_history table...")
            cursor.execute("ALTER TABLE digest_history ADD COLUMN digest_type TEXT DEFAULT 'daily'")
            
            # Update existing records
            cursor.execute("UPDATE digest_history SET digest_type = 'daily' WHERE digest_type IS NULL")
            print("Updated existing digest history records")
        
        # Create unique index on unsubscribe_token if it doesn't exist
        try:
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_unsubscribe_token ON users(unsubscribe_token)")
        except sqlite3.OperationalError:
            pass  # Index might already exist
        
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

def generate_unsubscribe_token(email: str) -> str:
    """Generate unique unsubscribe token"""
    random_part = secrets.token_hex(16)
    token_data = f"{email}:{random_part}:{datetime.utcnow().isoformat()}"
    return hashlib.sha256(token_data.encode()).hexdigest()[:32]

if __name__ == "__main__":
    migrate_database()