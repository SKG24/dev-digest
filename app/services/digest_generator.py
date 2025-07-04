# File: app/services/digest_generator.py
import asyncio
from sqlalchemy.orm import Session
from app.services.github_service import GitHubService
from app.services.stackoverflow_service import StackOverflowService
from app.services.email_service import EmailService
from app.services.fault_tolerance import retry_with_backoff, CircuitBreaker
from app.database import User, UserPreferences, DigestHistory
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DigestGenerator:
    def __init__(self):
        self.github_service = GitHubService()
        self.stackoverflow_service = StackOverflowService()
        self.email_service = EmailService()
        self.github_circuit_breaker = CircuitBreaker()
        self.stackoverflow_circuit_breaker = CircuitBreaker()
    
    async def generate_and_send_digest(self, db: Session, user_id: int) -> bool:
        """Generate and send digest for a user"""
        try:
            # Get user and preferences
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                return False
            
            preferences = db.query(UserPreferences).filter(UserPreferences.user_id == user_id).first()
            if not preferences:
                return False
            
            # Parse preferences
            repositories = json.loads(preferences.repositories or "[]")
            languages = json.loads(preferences.languages or "[]")
            stackoverflow_tags = json.loads(preferences.stackoverflow_tags or "[]")
            
            # Fetch data from all sources
            digest_data = await self._fetch_digest_data(repositories, languages, stackoverflow_tags)
            
            # Count total items
            total_items = (len(digest_data.get('github_issues', [])) +
                          len(digest_data.get('github_pulls', [])) +
                          len(digest_data.get('trending_repos', [])) +
                          len(digest_data.get('stackoverflow_questions', [])))
            
            # Send email if there's content
            if total_items > 0:
                success = self.email_service.send_digest_email(user.email, user.name, digest_data)
                status = "sent" if success else "failed"
                error_message = None if success else "Failed to send email"
            else:
                status = "skipped"
                error_message = "No new content available"
                success = True
            
            # Log to history
            history = DigestHistory(
                user_id=user_id,
                status=status,
                items_count=total_items,
                error_message=error_message
            )
            db.add(history)
            db.commit()
            
            return success
            
        except Exception as e:
            logger.error(f"Error generating digest for user {user_id}: {e}")
            
            # Log error to history
            history = DigestHistory(
                user_id=user_id,
                status="failed",
                items_count=0,
                error_message=str(e)
            )
            db.add(history)
            db.commit()
            
            return False
    
    async def _fetch_digest_data(self, repositories: list, languages: list, stackoverflow_tags: list) -> dict:
        """Fetch data from all sources with fault tolerance"""
        digest_data = {}
        
        # Fetch GitHub data
        try:
            github_issues = await self._fetch_github_issues(repositories)
            github_pulls = await self._fetch_github_pulls(repositories)
            trending_repos = await self._fetch_trending_repos(languages)
            
            digest_data.update({
                'github_issues': github_issues,
                'github_pulls': github_pulls,
                'trending_repos': trending_repos
            })
        except Exception as e:
            logger.error(f"Error fetching GitHub data: {e}")
            digest_data.update({
                'github_issues': [],
                'github_pulls': [],
                'trending_repos': []
            })
        
        # Fetch Stack Overflow data
        try:
            stackoverflow_questions = await self._fetch_stackoverflow_questions(stackoverflow_tags)
            digest_data['stackoverflow_questions'] = stackoverflow_questions
        except Exception as e:
            logger.error(f"Error fetching Stack Overflow data: {e}")
            digest_data['stackoverflow_questions'] = []
        
        return digest_data
    
    @retry_with_backoff(max_retries=3)
    async def _fetch_github_issues(self, repositories: list) -> list:
        """Fetch GitHub issues with retries"""
        if not repositories:
            return []
        
        return await asyncio.get_event_loop().run_in_executor(
            None, self.github_service.get_repository_issues, repositories
        )
    
    @retry_with_backoff(max_retries=3)
    async def _fetch_github_pulls(self, repositories: list) -> list:
        """Fetch GitHub pull requests with retries"""
        if not repositories:
            return []
        
        return await asyncio.get_event_loop().run_in_executor(
            None, self.github_service.get_repository_pulls, repositories
        )
    
    @retry_with_backoff(max_retries=3)
    async def _fetch_trending_repos(self, languages: list) -> list:
        """Fetch trending repositories with retries"""
        if not languages:
            return []
        
        return await asyncio.get_event_loop().run_in_executor(
            None, self.github_service.get_trending_repositories, languages
        )
    
    @retry_with_backoff(max_retries=3)
    async def _fetch_stackoverflow_questions(self, tags: list) -> list:
        """Fetch Stack Overflow questions with retries"""
        if not tags:
            return []
        
        return await asyncio.get_event_loop().run_in_executor(
            None, self.stackoverflow_service.get_questions_by_tags, tags
        )
