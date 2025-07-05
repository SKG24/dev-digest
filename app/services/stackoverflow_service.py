# File: app/services/stackoverflow_service.py
import requests
from typing import List, Dict
from datetime import datetime, timedelta
import time

class StackOverflowService:
    def __init__(self):
        self.base_url = "https://api.stackexchange.com/2.3"
        self.site = "stackoverflow"
        self.session = requests.Session()
    
    def get_questions_by_tags(self, tags: List[str], days_back: int = 1) -> List[Dict]:
        """Get recent questions for specified tags"""
        questions = []
        from_date = int((datetime.utcnow() - timedelta(days=days_back)).timestamp())
        
        try:
            url = f"{self.base_url}/questions"
            params = {
                "site": self.site,
                "tagged": ";".join(tags),
                "fromdate": from_date,
                "sort": "activity",
                "order": "desc",
                "pagesize": 20
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            for question in data.get("items", []):
                questions.append({
                    "title": question["title"],
                    "url": f"https://stackoverflow.com/questions/{question['question_id']}",
                    "score": question["score"],
                    "tags": question["tags"],
                    "created_at": datetime.fromtimestamp(question["creation_date"]).isoformat(),
                    "is_answered": question.get("is_answered", False)
                })
            
            # Respect API rate limits
            time.sleep(0.1)
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Stack Overflow questions: {e}")
        
        return sorted(questions, key=lambda x: x["score"], reverse=True)

