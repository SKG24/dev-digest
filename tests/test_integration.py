# File: tests/test_integration.py
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from app.services.digest_generator import DigestGenerator
from app.services.scheduler_service import SchedulerService
from app.database import User, UserPreferences

class TestIntegration:
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.mark.asyncio
    async def test_end_to_end_digest_generation(self, mock_db):
        """Test complete digest generation workflow"""
        # Setup mocks
        mock_user = Mock()
        mock_user.id = 1
        mock_user.name = "Test User"
        mock_user.email = "test@example.com"
        mock_user.is_active = True
        
        mock_preferences = Mock()
        mock_preferences.repositories = '["microsoft/vscode"]'
        mock_preferences.languages = '["python"]'
        mock_preferences.stackoverflow_tags = '["python"]'
        
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_user, mock_preferences]
        
        # Mock all external services
        with patch('app.services.github_service.GitHubService.get_repository_issues') as mock_issues, \
             patch('app.services.github_service.GitHubService.get_repository_pulls') as mock_pulls, \
             patch('app.services.github_service.GitHubService.get_trending_repositories') as mock_trending, \
             patch('app.services.stackoverflow_service.StackOverflowService.get_questions_by_tags') as mock_questions, \
             patch('app.services.email_service.EmailService.send_digest_email') as mock_send_email:
            
            # Configure mocks
            mock_issues.return_value = [{'title': 'Test Issue', 'repository': 'microsoft/vscode', 'user': 'testuser', 'url': 'https://github.com/microsoft/vscode/issues/1'}]
            mock_pulls.return_value = []
            mock_trending.return_value = [{'name': 'test/repo', 'stars': 100, 'language': 'Python', 'description': 'Test repo', 'url': 'https://github.com/test/repo'}]
            mock_questions.return_value = [{'title': 'How to test?', 'score': 5, 'tags': ['python'], 'url': 'https://stackoverflow.com/questions/123'}]
            mock_send_email.return_value = True
            
            # Run test
            digest_generator = DigestGenerator()
            result = await digest_generator.generate_and_send_digest(mock_db, 1)
            
            # Verify results
            assert result == True
            mock_send_email.assert_called_once()
            mock_db.add.assert_called_once()
    
    def test_scheduler_system_health(self):
        """Test scheduler system health reporting"""
        with patch('app.services.scheduler_service.get_db') as mock_get_db:
            mock_db = Mock()
            mock_get_db.return_value = mock_db
            
            # Configure mocks
            mock_db.query.return_value.count.side_effect = [10, 8, 5, 2]  # total_users, active_users, digests_today, errors_today
            mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
            
            scheduler_service = SchedulerService()
            health = scheduler_service.get_system_health()
            
            assert health['total_users'] == 10
            assert health['active_users'] == 8
            assert health['digests_sent_today'] == 5
            assert health['errors_count'] == 2