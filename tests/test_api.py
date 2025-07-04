# File: tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import Mock, patch

client = TestClient(app)

class TestAPI:
    def test_home_page(self):
        """Test home page loads"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Dev Digest" in response.text
    
    def test_signup_page(self):
        """Test signup page loads"""
        response = client.get("/signup")
        assert response.status_code == 200
        assert "Create Your Account" in response.text
    
    @patch('app.services.user_service.UserService.create_user')
    def test_signup_post_valid(self, mock_create_user):
        """Test valid signup"""
        mock_user = Mock()
        mock_user.id = 1
        mock_create_user.return_value = mock_user
        
        response = client.post("/signup", data={
            "name": "Test User",
            "github_username": "testuser",
            "email": "test@example.com"
        })
        
        assert response.status_code == 302  # Redirect to dashboard
    
    @patch('app.services.user_service.UserService.create_user')
    def test_signup_post_invalid(self, mock_create_user):
        """Test invalid signup"""
        mock_create_user.side_effect = ValueError("Invalid email format")
        
        response = client.post("/signup", data={
            "name": "Test User",
            "github_username": "testuser",
            "email": "invalid-email"
        })
        
        assert response.status_code == 200
        assert "Invalid email format" in response.text
    
    def test_dashboard_unauthorized(self):
        """Test dashboard access without authentication"""
        response = client.get("/dashboard")
        assert response.status_code == 401
    
    def test_admin_login_page(self):
        """Test admin login page"""
        response = client.get("/admin/login")
        assert response.status_code == 200
        assert "Admin Login" in response.text
    
    @patch.dict('os.environ', {'ADMIN_PASSWORD': 'testpassword'})
    def test_admin_login_valid(self):
        """Test valid admin login"""
        response = client.post("/admin/login", data={"password": "testpassword"})
        assert response.status_code == 302  # Redirect to admin dashboard
    
    @patch.dict('os.environ', {'ADMIN_PASSWORD': 'testpassword'})
    def test_admin_login_invalid(self):
        """Test invalid admin login"""
        response = client.post("/admin/login", data={"password": "wrongpassword"})
        assert response.status_code == 200
        assert "Invalid password" in response.text
