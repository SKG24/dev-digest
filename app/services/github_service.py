# File: app/services/github_service.py
import requests
import os
from typing import List, Dict
from datetime import datetime, timedelta

class GitHubService:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}" if self.token else None,
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_repository_issues(self, repositories: List[str]) -> List[Dict]:
        """Get recent issues from repositories"""
        issues = []
        for repo in repositories[:5]:  # Limit to 5 repos
            try:
                url = f"{self.base_url}/repos/{repo}/issues"
                params = {
                    "state": "open",
                    "sort": "created",
                    "direction": "desc",
                    "per_page": 3
                }
                
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                if response.status_code == 200:
                    repo_issues = response.json()
                    for issue in repo_issues:
                        if "pull_request" not in issue:  # Exclude PRs
                            issues.append({
                                "title": issue["title"],
                                "repository": repo,
                                "user": issue["user"]["login"],
                                "url": issue["html_url"],
                                "created_at": issue["created_at"]
                            })
            except Exception as e:
                print(f"Error fetching issues for {repo}: {e}")
                continue
        
        return issues[:10]  # Return top 10
    
    def get_repository_pulls(self, repositories: List[str]) -> List[Dict]:
        """Get recent pull requests from repositories"""
        pulls = []
        for repo in repositories[:5]:  # Limit to 5 repos
            try:
                url = f"{self.base_url}/repos/{repo}/pulls"
                params = {
                    "state": "open",
                    "sort": "created",
                    "direction": "desc",
                    "per_page": 3
                }
                
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                if response.status_code == 200:
                    repo_pulls = response.json()
                    for pull in repo_pulls:
                        pulls.append({
                            "title": pull["title"],
                            "repository": repo,
                            "user": pull["user"]["login"],
                            "url": pull["html_url"],
                            "created_at": pull["created_at"]
                        })
            except Exception as e:
                print(f"Error fetching pulls for {repo}: {e}")
                continue
        
        return pulls[:10]  # Return top 10
    
    def get_trending_repositories(self, languages: List[str]) -> List[Dict]:
        """Get trending repositories for given languages"""
        trending = []
        for lang in languages[:3]:  # Limit to 3 languages
            try:
                # Search for repositories created in the last week
                since_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
                url = f"{self.base_url}/search/repositories"
                params = {
                    "q": f"language:{lang} created:>{since_date}",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 5
                }
                
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                if response.status_code == 200:
                    repos = response.json().get("items", [])
                    for repo in repos:
                        trending.append({
                            "name": repo["full_name"],
                            "language": repo.get("language", "Unknown"),
                            "stars": repo["stargazers_count"],
                            "description": repo.get("description", "No description")[:100] + "...",
                            "url": repo["html_url"]
                        })
            except Exception as e:
                print(f"Error fetching trending repos for {lang}: {e}")
                continue
        
        return trending[:10]  # Return top 10