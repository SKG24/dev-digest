# File: tests/test_services.py
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from app.services.github_service import GitHubService
from app.services.stackoverflow_service import StackOverflowService
from app.services.email_service import EmailService
from app.services.user_service import UserService
from app.services.digest_generator import DigestGenerator
from app.database import User, UserPreferences
from datetime import datetime

class TestGitHubService:
    @pytest.fixture
    def github_service(self):
        return GitHubService()
    
    @patch('app.services.github_service.requests.Session.get')
    def test_get_repository_issues(self, mock_get, github_service):
        """Test fetching repository issues"""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "title": "Test Issue",
                "html_url": "https://github.com/test/repo/issues/1",
                "created_at": "2024-01-15T10:00:00Z",
                "user": {"login": "testuser"},
                "pull_request": None
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        issues = github_service.get_repository_issues(['test/repo'])
        
        assert len(issues) == 1
        assert issues[0]['title'] == 'Test Issue'
        assert issues[0]['repository'] == 'test/repo'
    
    @patch('app.services.github_service.requests.Session.get')
    def test_get_repository_issues_api_error(self, mock_get, github_service):
        """Test handling API errors"""
        mock_get.side_effect = Exception("API Error")
        
        issues = github_service.get_repository_issues(['test/repo'])
        
        assert issues == []
    
    @patch('app.services.github_service.requests.Session.get')
    def test_get_trending_repositories(self, mock_get, github_service):
        """Test fetching trending repositories"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {
                    "full_name": "test/trending-repo",
                    "description": "A trending repository",
                    "html_url": "https://github.com/test/trending-repo",
                    "stargazers_count": 100,
                    "language": "Python"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        trending = github_service.get_trending_repositories(['python'])
        
        assert len(trending) == 1
        assert trending[0]['name'] == 'test/trending-repo'
        assert trending[0]['stars'] == 100

class TestStackOverflowService:
    @pytest.fixture
    def stackoverflow_service(self):
        return StackOverflowService()
    
    @patch('app.services.stackoverflow_service.requests.Session.get')
    def test_get_questions_by_tags(self, mock_get, stackoverflow_service):
        """Test fetching Stack Overflow questions"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "items": [
                {
                    "title": "How to test Python code?",
                    "question_id": 12345,
                    "score": 10,
                    "tags": ["python", "testing"],
                    "creation_date": 1642248000,
                    "is_answered": True
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        questions = stackoverflow_service.get_questions_by_tags(['python'])
        
        assert len(questions) == 1
        assert questions[0]['title'] == 'How to test Python code?'
        assert questions[0]['score'] == 10

class TestEmailService:
    @pytest.fixture
    def email_service(self):
        return EmailService()
    
    @patch('app.services.email_service.smtplib.SMTP')
    def test_send_digest_email(self, mock_smtp, email_service):
        """Test sending digest email"""
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        digest_data = {
            'github_issues': [
                {
                    'title': 'Test Issue',
                    'repository': 'test/repo',
                    'user': 'testuser',
                    'url': 'https://github.com/test/repo/issues/1'
                }
            ],
            'github_pulls': [],
            'trending_repos': [],
            'stackoverflow_questions': []
        }
        
        result = email_service.send_digest_email('test@example.com', 'Test User', digest_data)
        
        assert result == True
        mock_server.send_message.assert_called_once()
    
    @patch('app.services.email_service.smtplib.SMTP')
    def test_send_digest_email_failure(self, mock_smtp, email_service):
        """Test email sending failure"""
        mock_smtp.side_effect = Exception("SMTP Error")
        
        digest_data = {'github_issues': [], 'github_pulls': [], 'trending_repos': [], 'stackoverflow_questions': []}
        
        result = email_service.send_digest_email('test@example.com', 'Test User', digest_data)
        
        assert result == False

class TestUserService:
    @pytest.fixture
    def user_service(self):
        return UserService()
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    def test_create_user_valid(self, user_service, mock_db):
        """Test creating a valid user"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        user = user_service.create_user(mock_db, "Test User", "testuser", "test@example.com")
        
        assert mock_db.add.called
        assert mock_db.commit.called
    
    def test_create_user_duplicate_email(self, user_service, mock_db):
        """Test creating user with duplicate email"""
        mock_db.query.return_value.filter.return_value.first.return_value = Mock()
        
        with pytest.raises(ValueError, match="User with this email already exists"):
            user_service.create_user(mock_db, "Test User", "testuser", "test@example.com")
    
    def test_create_user_invalid_email(self, user_service, mock_db):
        """Test creating user with invalid email"""
        with pytest.raises(ValueError, match="Invalid email format"):
            user_service.create_user(mock_db, "Test User", "testuser", "invalid-email")
    
    def test_update_preferences(self, user_service, mock_db):
        """Test updating user preferences"""
        mock_preferences = Mock()
        mock_user = Mock()
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_preferences, mock_user]
        
        user_service.update_preferences(
            mock_db, 1, "test/repo", "python", "python", "20:00", "UTC"
        )
        
        assert mock_db.commit.called
    
    def test_update_preferences_invalid_time(self, user_service, mock_db):
        """Test updating preferences with invalid time format"""
        mock_preferences = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_preferences
        
        with pytest.raises(ValueError, match="Invalid time format"):
            user_service.update_preferences(
                mock_db, 1, "test/repo", "python", "python", "25:00", "UTC"
            )

class TestDigestGenerator:
    @pytest.fixture
    def digest_generator(self):
        return DigestGenerator()
    
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def mock_user(self):
        user = Mock()
        user.id = 1
        user.name = "Test User"
        user.email = "test@example.com"
        user.is_active = True
        return user
    
    @pytest.fixture
    def mock_preferences(self):
        prefs = Mock()
        prefs.repositories = '["test/repo"]'
        prefs.languages = '["python"]'
        prefs.stackoverflow_tags = '["python"]'
        return prefs
    
    @patch('app.services.digest_generator.DigestGenerator._fetch_digest_data')
    @patch('app.services.digest_generator.EmailService.send_digest_email')
    @pytest.mark.asyncio
    async def test_generate_and_send_digest(self, mock_send_email, mock_fetch_data, 
                                          digest_generator, mock_db, mock_user, mock_preferences):
        """Test generating and sending digest"""
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_user, mock_preferences]
        mock_fetch_data.return_value = {
            'github_issues': [{'title': 'Test Issue'}],
            'github_pulls': [],
            'trending_repos': [],
            'stackoverflow_questions': []
        }
        mock_send_email.return_value = True
        
        result = await digest_generator.generate_and_send_digest(mock_db, 1)
        
        assert result == True
        mock_send_email.assert_called_once()
        mock_db.add.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_and_send_digest_inactive_user(self, digest_generator, mock_db):
        """Test generating digest for inactive user"""
        mock_user = Mock()
        mock_user.is_active = False
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = await digest_generator.generate_and_send_digest(mock_db, 1)
        
        assert result == False