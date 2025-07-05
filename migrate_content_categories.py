# File: migrate_content_categories.py
"""
Migration script to add content_categories field to user_preferences table
Run this script to update existing database schema
"""
import sqlite3
import json
import os

def migrate_content_categories():
    """Add content_categories field to user_preferences table"""
    db_path = "data/users.db"
    
    if not os.path.exists(db_path):
        print("Database doesn't exist yet. No migration needed.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if content_categories column exists
        cursor.execute("PRAGMA table_info(user_preferences)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'content_categories' not in columns:
            print("Adding content_categories column to user_preferences table...")
            cursor.execute("ALTER TABLE user_preferences ADD COLUMN content_categories TEXT")
            
            # Update existing records with default categories
            default_categories = json.dumps(["career-advice", "ai-ml", "opensource", "productivity"])
            cursor.execute(
                "UPDATE user_preferences SET content_categories = ? WHERE content_categories IS NULL",
                (default_categories,)
            )
            
            # Count updated records
            cursor.execute("SELECT COUNT(*) FROM user_preferences")
            count = cursor.fetchone()[0]
            
            print(f"Updated {count} user preference records with default content categories")
        else:
            print("content_categories column already exists")
        
        conn.commit()
        print("Content categories migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_content_categories()