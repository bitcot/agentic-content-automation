import os
import re
import requests
import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from ddgs import DDGS

class TrendAgent:
    def __init__(self):
        self.model_name = "claude-opus-4-7"
        self.ddgs = DDGS()

    def discover_trends(self) -> list:
        """
        Scrapes HackerNews and DuckDuckGo for trending software/AI news.
        Passes the batch to Claude (via LangChain) to select the top 3 that match our ICP.
        """
        headlines = []

        # 1. Fetch from HackerNews
        try:
            hn_resp = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
            if hn_resp.status_code == 200:
                top_ids = hn_resp.json()[:30] # Get top 30
                for item_id in top_ids:
                    item_resp = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json", timeout=5)
                    if item_resp.status_code == 200:
                        data = item_resp.json()
                        if data and "title" in data and not data["title"].startswith("Ask HN"):
                            headlines.append(data["title"])
        except Exception as e:
            print(f"HN Fetch error: {e}")

        # 2. Fetch from DuckDuckGo News
        try:
            ddg_news = self.ddgs.news("Enterprise AI OR Software Engineering OR Cloud Infrastructure", max_results=20)
            for item in ddg_news:
                if "title" in item:
                    headlines.append(item["title"])
        except Exception as e:
            print(f"DDG News error: {e}")

        if not headlines:
            headlines = [
                "OpenAI releases new fine-tuning API for enterprise",
                "Why 60% of GenAI pilots fail in production",
                "The state of Rust in 2026",
                "Next.js 16 drops new Turbopack updates"
            ]

        # 3. Use Claude to pick the top 3
        import datetime
        current_date = datetime.date.today().isoformat()
        headlines_text = "\n".join([f"- {h}" for h in headlines])
        
        system_prompt = """You are an elite B2B Content Strategist for a software engineering agency.
Your job is to read a list of raw, trending news headlines and select the TOP 3 that would make the best thought-leadership content for our target audience (CTOs, VPs of Engineering, Product Managers).

CRITICAL RECENCY RULE:
Today's date is """ + current_date + """. 
You MUST strictly ignore any "hot topic" that peaked more than 6 months ago. Do not select topics that are stale or yesterday's news. Past topics/data are ONLY allowed if explicitly framed as a retrospective case study or a historical justification for a present problem.

Criteria for selection:
- Must be highly relevant to B2B software development, enterprise AI, cloud architecture, or engineering leadership.
- Avoid consumer tech, politics, or generic startup drama.
- Favor topics that allow us to provide deep, contrarian, or architectural insights.

Return ONLY a valid JSON array of 3 objects with this exact structure:
[
  {
    "topic": "The selected headline or a slightly refined version of it",
    "score": 0.95, // Float between 0.80 and 0.99
    "reasoning": "1-2 sentences explaining why this matters to a CTO/VP Engineering"
  }
]
"""
        
        try:
            chat = ChatAnthropic(
                model=self.model_name,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                timeout=120.0,
                max_tokens=1000
            )
            response = chat.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Here are the trending headlines:\n{headlines_text}\n\nSelect the top 3 and return as JSON.")
            ])
            text = response.content.strip()
            
            import json_repair
            m = re.search(r'\[.*\]', text, re.DOTALL)
            if m:
                result = json_repair.loads(m.group())
                return result
            else:
                return []
        except Exception as e:
            print(f"Trend selection error: {e}")
            return []
