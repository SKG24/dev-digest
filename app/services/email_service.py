# File: app/services/email_service.py (UPDATED WITH HTML TEMPLATES)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("EMAIL_FROM", self.smtp_user)
        self.app_url = os.getenv("APP_URL", "http://localhost:8000")
        
        # Setup Jinja2 environment for email templates
        template_dir = Path(__file__).parent.parent.parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Send welcome email to new user"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = "Welcome to Dev Digest! 🎉"
            
            # Render HTML template
            template = self.jinja_env.get_template('email/welcome_email.html')
            html_content = template.render(
                user_name=user_name,
                app_url=self.app_url,
                settings_url=f"{self.app_url}/settings",
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            )
            
            # Create plain text version
            text_content = f"""
Hello {user_name},

Welcome to Dev Digest! 🎉

We're excited to have you join our community of developers who stay updated with the latest in tech.

What to expect:
• Daily personalized digests with GitHub issues, pull requests, and trending repositories
• Stack Overflow blog articles on career advice, AI/ML, open source, and productivity
• Customizable preferences to match your tech stack
• Delivered straight to your inbox at your preferred time

Your first digest is on its way! You can customize your preferences anytime at:
{self.app_url}/settings

Happy coding!
The Dev Digest Team

---
Dev Digest - Your personalized coding updates
Visit: {self.app_url}
"""
            
            # Attach both versions
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending welcome email to {to_email}: {e}")
            return False
    
    def send_digest_email(self, to_email: str, user_name: str, digest_data: Dict, 
                         unsubscribe_token: str = None, is_welcome: bool = False) -> bool:
        """Send digest email to user"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            if is_welcome:
                msg['Subject'] = f"Your Welcome Dev Digest! 🚀"
            else:
                msg['Subject'] = f"Your Dev Digest - {datetime.now().strftime('%B %d, %Y')}"
            
            # Calculate total items
            total_items = (
                len(digest_data.get('github_issues', [])) +
                len(digest_data.get('github_pulls', [])) +
                len(digest_data.get('trending_repos', [])) +
                sum(len(articles) for articles in digest_data.get('blog_articles', {}).values())
            )
            
            # Render HTML template
            template = self.jinja_env.get_template('email/digest_email.html')
            html_content = template.render(
                user_name=user_name,
                digest_data=digest_data,
                is_welcome=is_welcome,
                date=datetime.now().strftime('%B %d, %Y'),
                total_items=total_items,
                app_url=self.app_url,
                settings_url=f"{self.app_url}/settings",
                unsubscribe_url=f"{self.app_url}/unsubscribe/{unsubscribe_token}" if unsubscribe_token else None,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            )
            
            # Create plain text version
            text_content = self._create_text_email_body(user_name, digest_data, unsubscribe_token, is_welcome)
            
            # Attach both versions
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending digest email to {to_email}: {e}")
            return False
    
    def _create_text_email_body(self, user_name: str, digest_data: Dict, 
                               unsubscribe_token: str = None, is_welcome: bool = False) -> str:
        """Create plain text email body from digest data"""
        
        if is_welcome:
            greeting = f"Welcome to Dev Digest, {user_name}! 🚀\n\nHere's your first personalized digest:"
        else:
            greeting = f"Hello {user_name},\n\nHere's your daily development digest for {datetime.now().strftime('%B %d, %Y')}:"
        
        body = f"""
{greeting}

"""
        
        # GitHub Updates
        github_sections = []
        if digest_data.get('github_issues'):
            github_sections.append("📋 RECENT GITHUB ISSUES")
            github_sections.append("=" * 50)
            for issue in digest_data['github_issues'][:3]:
                github_sections.append(f"• {issue['title']}")
                github_sections.append(f"  Repository: {issue['repository']}")
                github_sections.append(f"  Author: {issue['user']}")
                github_sections.append(f"  URL: {issue['url']}\n")
        
        if digest_data.get('github_pulls'):
            github_sections.append("🔄 PULL REQUESTS")
            github_sections.append("=" * 50)
            for pull in digest_data['github_pulls'][:3]:
                github_sections.append(f"• {pull['title']}")
                github_sections.append(f"  Repository: {pull['repository']}")
                github_sections.append(f"  Author: {pull['user']}")
                github_sections.append(f"  URL: {pull['url']}\n")
        
        if digest_data.get('trending_repos'):
            github_sections.append("🌟 TRENDING REPOSITORIES")
            github_sections.append("=" * 50)
            for repo in digest_data['trending_repos'][:3]:
                github_sections.append(f"• {repo['name']} ({repo['language']})")
                github_sections.append(f"  Stars: {repo['stars']}")
                github_sections.append(f"  {repo['description']}")
                github_sections.append(f"  URL: {repo['url']}\n")
        
        if github_sections:
            body += "\n".join(github_sections) + "\n\n"
        
        # Stack Overflow Blog Articles
        if digest_data.get('blog_articles'):
            body += "📚 STACK OVERFLOW BLOG ARTICLES\n"
            body += "=" * 50 + "\n"
            
            for category, articles in digest_data['blog_articles'].items():
                if articles:
                    category_names = {
                        'career-advice': '💼 Career Advice',
                        'ai-ml': '🤖 AI & Machine Learning',
                        'opensource': '🔓 Open Source',
                        'productivity': '⚡ Productivity'
                    }
                    
                    body += f"\n{category_names.get(category, category.title())}\n"
                    body += "-" * 30 + "\n"
                    
                    for article in articles[:3]:
                        body += f"• {article['title']}\n"
                        body += f"  {article['description']}\n"
                        body += f"  URL: {article['url']}\n\n"
        
        # Footer
        footer = f"""
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC

---
Dev Digest - Your personalized coding updates
"""
        
        if is_welcome:
            footer += f"""
🎉 This is your welcome digest! You'll receive daily digests at your preferred time.
Customize your preferences: {self.app_url}/settings
"""
        
        if unsubscribe_token:
            footer += f"""
To unsubscribe: {self.app_url}/unsubscribe/{unsubscribe_token}
Update preferences: {self.app_url}/settings
"""
        else:
            footer += f"Visit: {self.app_url}"
        
        body += footer
        
        return body