# File: app/services/scheduler_service.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy.orm import Session
from app.database import get_db, User, UserPreferences, DigestHistory
from app.services.digest_generator import DigestGenerator
import asyncio
import logging
from datetime import datetime, timedelta
import json
import pytz

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        jobstores = {
            'default': SQLAlchemyJobStore(url='sqlite:///data/scheduler.db')
        }
        
        self.scheduler = BackgroundScheduler(jobstores=jobstores)
        self.digest_generator = DigestGenerator()
        self.is_running = False
    
    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            
            # Schedule daily digest job
            self.scheduler.add_job(
                func=self.run_daily_digests,
                trigger=CronTrigger(hour=20, minute=0),  # 8 PM UTC
                id='daily_digests',
                replace_existing=True
            )
            
            logger.info("Scheduler started successfully")
    
    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler stopped")
    
    def run_daily_digests(self):
        """Run daily digest generation for all active users"""
        logger.info("Starting daily digest generation")
        
        try:
            db = next(get_db())
            active_users = db.query(User).filter(User.is_active == True).all()
            
            for user in active_users:
                try:
                    # Run digest generation in event loop
                    asyncio.run(self.digest_generator.generate_and_send_digest(db, user.id))
                    logger.info(f"Digest generated for user {user.id}")
                except Exception as e:
                    logger.error(f"Error generating digest for user {user.id}: {e}")
            
            logger.info(f"Daily digest generation completed for {len(active_users)} users")
            
        except Exception as e:
            logger.error(f"Error in daily digest generation: {e}")
        finally:
            db.close()
    
    def get_system_health(self) -> dict:
        """Get system health information"""
        try:
            db = next(get_db())
            
            # Get user statistics
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            
            # Get digest statistics
            today = datetime.utcnow().date()
            digests_today = db.query(DigestHistory).filter(
                DigestHistory.sent_at >= today,
                DigestHistory.status == "sent"
            ).count()
            
            # Get error count
            errors_today = db.query(DigestHistory).filter(
                DigestHistory.sent_at >= today,
                DigestHistory.status == "failed"
            ).count()
            
            # Get last successful run
            last_run = db.query(DigestHistory).filter(
                DigestHistory.status == "sent"
            ).order_by(DigestHistory.sent_at.desc()).first()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "digests_sent_today": digests_today,
                "scheduler_status": "running" if self.is_running else "stopped",
                "last_run": last_run.sent_at if last_run else None,
                "errors_count": errors_today
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                "total_users": 0,
                "active_users": 0,
                "digests_sent_today": 0,
                "scheduler_status": "error",
                "last_run": None,
                "errors_count": 0
            }
        finally:
            db.close()

