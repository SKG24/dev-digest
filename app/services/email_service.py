# File: app/services/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
import os
from datetime import datetime

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("EMAIL_FROM", self.smtp_user)
    
    def send_digest_email(self, to_email: str, user_name: str, digest_data: Dict) -> bool:
        """Send digest email to user"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = f"Your Dev Digest - {datetime.now().strftime('%B %d, %Y')}"
            
            # Create email body
            body = self._create_email_body(user_name, digest_data)
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending email to {to_email}: {e}")
            return False
    
    def _create_email_body(self, user_name: str, digest_data: Dict) -> str:
        """Create email body from digest data"""
        body = f"""
Hello {user_name},

Here's your daily development digest for {datetime.now().strftime('%B %d, %Y')}:

"""
        
        # GitHub Issues
        issues = digest_data.get('github_issues', [])
        if issues:
            body += "📋 GITHUB ISSUES\n"
            body += "=" * 50 + "\n"
            for issue in issues[:5]:
                body += f"• {issue['title']}\n"
                body += f"  Repository: {issue['repository']}\n"
                body += f"  Author: {issue['user']}\n"
                body += f"  URL: {issue['url']}\n\n"
        
        # Pull Requests
        pulls = digest_data.get('github_pulls', [])
        if pulls:
            body += "🔄 PULL REQUESTS\n"
            body += "=" * 50 + "\n"
            for pull in pulls[:5]:
                body += f"• {pull['title']}\n"
                body += f"  Repository: {pull['repository']}\n"
                body += f"  Author: {pull['user']}\n"
                body += f"  URL: {pull['url']}\n\n"
        
        # Trending Repositories
        trending = digest_data.get('trending_repos', [])
        if trending:
            body += "🌟 TRENDING REPOSITORIES\n"
            body += "=" * 50 + "\n"
            for repo in trending[:5]:
                body += f"• {repo['name']} ({repo['language']})\n"
                body += f"  Stars: {repo['stars']}\n"
                body += f"  {repo['description']}\n"
                body += f"  URL: {repo['url']}\n\n"
        
        # Stack Overflow Questions
        questions = digest_data.get('stackoverflow_questions', [])
        if questions:
            body += "❓ STACK OVERFLOW QUESTIONS\n"
            body += "=" * 50 + "\n"
            for question in questions[:5]:
                body += f"• {question['title']}\n"
                body += f"  Score: {question['score']}\n"
                body += f"  Tags: {', '.join(question['tags'])}\n"
                body += f"  URL: {question['url']}\n\n"
        
        body += f"""
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC

---
Dev Digest - Your personalized coding updates
To unsubscribe or update preferences, visit: {os.getenv('APP_URL', 'http://localhost:8000')}/settings
"""
        
        return body