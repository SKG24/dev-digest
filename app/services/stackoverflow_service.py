# File: app/services/stackoverflow_service.py
import requests
from typing import List, Dict
from datetime import datetime, timedelta

class StackOverflowService:
    def __init__(self):
        self.base_url = "https://api.stackexchange.com/2.3"
    
    def get_questions_by_tags(self, tags: List[str]) -> List[Dict]:
        """Get recent questions for given tags"""
        questions = []
        
        # Join tags with semicolon for Stack Overflow API
        tags_str = ";".join(tags[:5])  # Limit to 5 tags
        
        try:
            url = f"{self.base_url}/questions"
            params = {
                "site": "stackoverflow",
                "tagged": tags_str,
                "sort": "activity",
                "order": "desc",
                "pagesize": 10,
                "filter": "default"
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("items", []):
                    questions.append({
                        "title": item["title"],
                        "score": item["score"],
                        "tags": item["tags"],
                        "url": item["link"],
                        "creation_date": item["creation_date"]
                    })
        except Exception as e:
            print(f"Error fetching Stack Overflow questions: {e}")
        
        return questions[:10]  # Return top 10