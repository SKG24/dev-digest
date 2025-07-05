# File: app/services/github_service.py (UPDATED WITH BETTER ERROR HANDLING)
import requests
import os
from typing import List, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Dev-Digest-Bot/1.0"
        }
        
        # Add authorization header if token is available
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    def get_repository_issues(self, repositories: List[str]) -> List[Dict]:
        """Get recent issues from repositories"""
        issues = []
        
        for repo in repositories[:5]:  # Limit to 5 repos to avoid rate limiting
            try:
                # Clean repository name
                repo = repo.strip()
                if not repo or '/' not in repo:
                    continue
                
                url = f"{self.base_url}/repos/{repo}/issues"
                params = {
                    "state": "open",
                    "sort": "created",
                    "direction": "desc",
                    "per_page": 5  # Get fewer items per repo to avoid rate limiting
                }
                
                logger.info(f"Fetching issues from {repo}")
                response = requests.get(url, headers=self.headers, params=params, timeout=15)
                
                if response.status_code == 200:
                    repo_issues = response.json()
                    for issue in repo_issues:
                        # Skip pull requests (GitHub API includes PRs in issues)
                        if "pull_request" not in issue:
                            issues.append({
                                "title": issue["title"],
                                "repository": repo,
                                "user": issue["user"]["login"],
                                "url": issue["html_url"],
                                "created_at": issue["created_at"]
                            })
                elif response.status_code == 404:
                    logger.warning(f"Repository {repo} not found")
                elif response.status_code == 403:
                    logger.warning(f"Rate limited or access forbidden for {repo}")
                else:
                    logger.error(f"Error fetching issues for {repo}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Exception fetching issues for {repo}: {e}")
                continue
        
        return issues[:10]  # Return top 10 issues
    
    def get_repository_pulls(self, repositories: List[str]) -> List[Dict]:
        """Get recent pull requests from repositories"""
        pulls = []
        
        for repo in repositories[:5]:  # Limit to 5 repos to avoid rate limiting
            try:
                # Clean repository name
                repo = repo.strip()
                if not repo or '/' not in repo:
                    continue
                
                url = f"{self.base_url}/repos/{repo}/pulls"
                params = {
                    "state": "open",
                    "sort": "created",
                    "direction": "desc",
                    "per_page": 5  # Get fewer items per repo to avoid rate limiting
                }
                
                logger.info(f"Fetching pull requests from {repo}")
                response = requests.get(url, headers=self.headers, params=params, timeout=15)
                
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
                elif response.status_code == 404:
                    logger.warning(f"Repository {repo} not found")
                elif response.status_code == 403:
                    logger.warning(f"Rate limited or access forbidden for {repo}")
                else:
                    logger.error(f"Error fetching pulls for {repo}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Exception fetching pulls for {repo}: {e}")
                continue
        
        return pulls[:10]  # Return top 10 pull requests
    
    def get_trending_repositories(self, languages: List[str]) -> List[Dict]:
        """Get trending repositories for given languages"""
        trending = []
        
        for lang in languages[:3]:  # Limit to 3 languages to avoid rate limiting
            try:
                # Clean language name
                lang = lang.strip().lower()
                if not lang:
                    continue
                
                # Search for repositories created in the last week with good activity
                since_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
                url = f"{self.base_url}/search/repositories"
                params = {
                    "q": f"language:{lang} pushed:>{since_date}",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 5
                }
                
                logger.info(f"Fetching trending repositories for {lang}")
                response = requests.get(url, headers=self.headers, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    repos = data.get("items", [])
                    for repo in repos:
                        trending.append({
                            "name": repo["full_name"],
                            "language": repo.get("language", "Unknown"),
                            "stars": repo["stargazers_count"],
                            "description": (repo.get("description", "No description available") or "No description available")[:100] + "..." if len(repo.get("description", "")) > 100 else repo.get("description", "No description available"),
                            "url": repo["html_url"]
                        })
                elif response.status_code == 403:
                    logger.warning(f"Rate limited searching for {lang} repositories")
                else:
                    logger.error(f"Error fetching trending repos for {lang}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Exception fetching trending repos for {lang}: {e}")
                continue
        
        # If no trending repos found, get some popular repos as fallback
        if not trending:
            trending = self._get_fallback_repos(languages)
        
        return trending[:10]  # Return top 10 trending repositories
    
    def _get_fallback_repos(self, languages: List[str]) -> List[Dict]:
        """Get fallback repositories when trending search fails"""
        fallback_repos = []
        
        # Popular repositories by language
        popular_repos = {
            "python": ["python/cpython", "psf/requests", "django/django", "flask/flask"],
            "javascript": ["microsoft/vscode", "facebook/react", "nodejs/node", "vercel/next.js"],
            "java": ["spring-projects/spring-boot", "elastic/elasticsearch", "apache/kafka"],
            "go": ["golang/go", "kubernetes/kubernetes", "docker/docker-ce"],
            "rust": ["rust-lang/rust", "tokio-rs/tokio", "serde-rs/serde"],
            "typescript": ["microsoft/TypeScript", "angular/angular", "nestjs/nest"],
            "php": ["laravel/laravel", "symfony/symfony", "composer/composer"],
            "ruby": ["rails/rails", "ruby/ruby", "jekyll/jekyll"],
            "c++": ["microsoft/terminal", "facebook/folly", "google/protobuf"],
            "c#": ["dotnet/core", "aspnet/AspNetCore", "mono/mono"]
        }
        
        for lang in languages[:3]:
            lang_repos = popular_repos.get(lang.lower(), [])
            for repo_name in lang_repos[:2]:  # Get 2 repos per language
                fallback_repos.append({
                    "name": repo_name,
                    "language": lang.title(),
                    "stars": "⭐ Popular",
                    "description": f"Popular {lang} repository",
                    "url": f"https://github.com/{repo_name}"
                })
        
        return fallback_repos
    
    def check_rate_limit(self) -> Dict:
        """Check GitHub API rate limit status"""
        try:
            url = f"{self.base_url}/rate_limit"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Status code: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return {"error": str(e)}