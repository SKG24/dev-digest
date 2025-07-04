# File: app/services/github_service.py
import requests
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json

class GitHubService:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_repository_issues(self, repositories: List[str], days_back: int = 1) -> List[Dict]:
        """Get recent issues from repositories"""
        issues = []
        since_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
        
        for repo in repositories:
            try:
                url = f"{self.base_url}/repos/{repo}/issues"
                params = {
                    "state": "open",
                    "since": since_date,
                    "per_page": 10
                }
                
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                repo_issues = response.json()
                for issue in repo_issues:
                    # Skip pull requests (they appear as issues in GitHub API)
                    if not issue.get("pull_request"):
                        issues.append({
                            "repository": repo,
                            "title": issue["title"],
                            "url": issue["html_url"],
                            "created_at": issue["created_at"],
                            "user": issue["user"]["login"]
                        })
            except requests.exceptions.RequestException as e:
                print(f"Error fetching issues for {repo}: {e}")
                continue
        
        return sorted(issues, key=lambda x: x["created_at"], reverse=True)
    
    def get_repository_pulls(self, repositories: List[str], days_back: int = 1) -> List[Dict]:
        """Get recent pull requests from repositories"""
        pulls = []
        since_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
        
        for repo in repositories:
            try:
                url = f"{self.base_url}/repos/{repo}/pulls"
                params = {
                    "state": "open",
                    "sort": "created",
                    "direction": "desc",
                    "per_page": 10
                }
                
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                repo_pulls = response.json()
                for pull in repo_pulls:
                    # Filter by date
                    if pull["created_at"] >= since_date:
                        pulls.append({
                            "repository": repo,
                            "title": pull["title"],
                            "url": pull["html_url"],
                            "created_at": pull["created_at"],
                            "user": pull["user"]["login"]
                        })
            except requests.exceptions.RequestException as e:
                print(f"Error fetching PRs for {repo}: {e}")
                continue
        
        return sorted(pulls, key=lambda x: x["created_at"], reverse=True)
    
    def get_trending_repositories(self, languages: List[str], days_back: int = 1) -> List[Dict]:
        """Get trending repositories for specified languages"""
        trending = []
        since_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        for language in languages:
            try:
                url = f"{self.base_url}/search/repositories"
                params = {
                    "q": f"language:{language} created:>{since_date}",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 5
                }
                
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                results = response.json()
                for repo in results.get("items", []):
                    trending.append({
                        "name": repo["full_name"],
                        "description": repo["description"] or "No description",
                        "url": repo["html_url"],
                        "stars": repo["stargazers_count"],
                        "language": repo["language"]
                    })
            except requests.exceptions.RequestException as e:
                print(f"Error fetching trending repos for {language}: {e}")
                continue
        
        return sorted(trending, key=lambda x: x["stars"], reverse=True)