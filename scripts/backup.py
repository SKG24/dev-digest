# File: scripts/backup.py
#!/usr/bin/env python3
"""
Database backup script for Dev Digest
Creates compressed backups of the SQLite database
"""

import os
import shutil
import gzip
import datetime
from pathlib import Path
import logging

def backup_database():
    """Create a backup of the database"""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Database path
    db_path = Path("data/users.db")
    if not db_path.exists():
        logger.error(f"Database file not found: {db_path}")
        return False
    
    # Backup directory
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"users_backup_{timestamp}.db.gz"
    backup_path = backup_dir / backup_filename
    
    try:
        # Create compressed backup
        with open(db_path, 'rb') as f_in:
            with gzip.open(backup_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        logger.info(f"Database backup created: {backup_path}")
        
        # Remove old backups (keep last 7 days)
        cleanup_old_backups(backup_dir, days=7)
        
        return True
        
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False

def cleanup_old_backups(backup_dir: Path, days: int = 7):
    """Remove backups older than specified days"""
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    
    for backup_file in backup_dir.glob("users_backup_*.db.gz"):
        if backup_file.stat().st_mtime < cutoff_date.timestamp():
            backup_file.unlink()
            print(f"Removed old backup: {backup_file}")

def restore_database(backup_path: str):
    """Restore database from backup"""
    backup_file = Path(backup_path)
    if not backup_file.exists():
        print(f"Backup file not found: {backup_path}")
        return False
    
    db_path = Path("data/users.db")
    
    try:
        # Create backup of current database
        if db_path.exists():
            current_backup = db_path.with_suffix(".db.current")
            shutil.copy2(db_path, current_backup)
            print(f"Current database backed up to: {current_backup}")
        
        # Restore from backup
        with gzip.open(backup_file, 'rb') as f_in:
            with open(db_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        print(f"Database restored from: {backup_path}")
        return True
        
    except Exception as e:
        print(f"Restore failed: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        if len(sys.argv) != 3:
            print("Usage: python backup.py restore <backup_file>")
            sys.exit(1)
        restore_database(sys.argv[2])
    else:
        backup_database()