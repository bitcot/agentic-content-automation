import os
import requests
from pydantic import BaseModel
from base64 import b64encode
from agents.logger import emit_agent_log

class SEOPackage(BaseModel):
    topic: str
    target_keyword: str
    volume: int
    serp_gap_identified: bool
    title_tag_suggestion: str

class SEOAgent:
    def __init__(self):
        self.login = os.getenv("DATAFORSEO_LOGIN")
        self.password = os.getenv("DATAFORSEO_PASSWORD")
        self.api_url = "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_suggestions/live"

    def analyze_topic(self, topic: str) -> SEOPackage:
        """
        Analyzes a topic for SEO opportunities using DataForSEO API.
        Extracts keyword volume and suggests titles.
        """
        emit_agent_log("SEOAgent", f"Analyzing SEO opportunities for: '{topic}'", {"topic": topic})
        if not self.login or not self.password:
            # Fallback to sandbox if API keys aren't provided yet
            return SEOPackage(
                topic=topic,
                target_keyword=f"{topic.lower()} solutions",
                volume=1200,
                serp_gap_identified=True,
                title_tag_suggestion=f"The Ultimate Guide to {topic.title()}"
            )

        try:
            credentials = b64encode(f"{self.login}:{self.password}".encode('utf-8')).decode('utf-8')
            headers = {
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json'
            }
            payload = [{
                "keyword": topic,
                "location_code": 2840, # US
                "language_code": "en",
                "limit": 1
            }]

            response = requests.post(self.api_url, json=payload, headers=headers)
            data = response.json()

            if data.get("status_code") == 20000 and data["tasks"][0]["result"]:
                kw_data = data["tasks"][0]["result"][0]["items"][0]
                target_kw = kw_data.get("keyword", topic)
                sv = kw_data.get("keyword_info", {}).get("search_volume", 0)

                return SEOPackage(
                    topic=topic,
                    target_keyword=target_kw,
                    volume=sv,
                    serp_gap_identified=True if sv > 100 else False,
                    title_tag_suggestion=f"How to Solve {target_kw.title()} in 2026"
                )
        except Exception as e:
            print(f"SEO Agent API Error: {e}")
            
        # Fallback on failure
        return SEOPackage(
            topic=topic,
            target_keyword=topic,
            volume=0,
            serp_gap_identified=False,
            title_tag_suggestion=f"Insights on {topic}"
        )
