# File: app/services/monitoring_service.py
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session
from app.database import get_db, User, DigestHistory
import logging

logger = logging.getLogger("dev_digest.monitoring")

class MonitoringService:
    """Service for system monitoring and metrics"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def get_system_metrics(self) -> Dict:
        """Get current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used / (1024 * 1024),
                "memory_total_mb": memory.total / (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_used_gb": disk.used / (1024 * 1024 * 1024),
                "disk_total_gb": disk.total / (1024 * 1024 * 1024),
                "uptime_seconds": time.time() - self.start_time
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def get_application_metrics(self, db: Session) -> Dict:
        """Get application-specific metrics"""
        try:
            now = datetime.utcnow()
            today = now.date()
            week_ago = now - timedelta(days=7)
            
            # User metrics
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            new_users_today = db.query(User).filter(User.created_at >= today).count()
            
            # Digest metrics
            total_digests = db.query(DigestHistory).count()
            digests_today = db.query(DigestHistory).filter(DigestHistory.sent_at >= today).count()
            successful_digests_today = db.query(DigestHistory).filter(
                DigestHistory.sent_at >= today,
                DigestHistory.status == "sent"
            ).count()
            
            # Success rate
            success_rate = 0.0
            if digests_today > 0:
                success_rate = (successful_digests_today / digests_today) * 100
            
            # Error metrics
            errors_today = db.query(DigestHistory).filter(
                DigestHistory.sent_at >= today,
                DigestHistory.status == "failed"
            ).count()
            
            # Weekly trends
            weekly_digests = db.query(DigestHistory).filter(DigestHistory.sent_at >= week_ago).count()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "new_users_today": new_users_today,
                "total_digests": total_digests,
                "digests_today": digests_today,
                "successful_digests_today": successful_digests_today,
                "success_rate": success_rate,
                "errors_today": errors_today,
                "weekly_digests": weekly_digests
            }
        except Exception as e:
            logger.error(f"Error getting application metrics: {e}")
            return {}
    
    def get_health_check(self) -> Dict:
        """Get health check status"""
        try:
            db = next(get_db())
            
            # Check database
            db_healthy = True
            try:
                db.execute("SELECT 1")
            except Exception:
                db_healthy = False
            
            # Check system resources
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_healthy = (
                memory.percent < 90 and
                disk.percent < 90 and
                psutil.cpu_percent(interval=1) < 90
            )
            
            overall_healthy = db_healthy and system_healthy
            
            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "database": "healthy" if db_healthy else "unhealthy",
                "system": "healthy" if system_healthy else "unhealthy",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            db.close()
