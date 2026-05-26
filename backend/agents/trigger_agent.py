import os
import json
import requests
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Topics Bitcot has already published — loaded from DB to prevent cannibalization
def get_recent_topics(db: Session, days: int = 5) -> list[str]:
    """Returns topics published in the last `days` days."""
    from models import ContentLog
    cutoff = datetime.utcnow() - timedelta(days=days)
    logs = db.query(ContentLog).filter(
        ContentLog.created_at >= cutoff,
        ContentLog.status.in_(["published", "pending_review"])
    ).all()
    return [log.topic.lower() for log in logs]


class TriggerAgent:
    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.api_url = "https://api.perplexity.ai/chat/completions"

        # Seed categories aligned with Bitcot's ICP
        self.seed_categories = [
            "Enterprise AI adoption challenges",
            "Healthcare AI and HIPAA compliance",
            "Technical debt and legacy system modernization",
            "Fintech software development"
        ]

    def _get_trending_topics(self) -> list[dict]:
        """
        Uses Perplexity API to search the live web for breaking news and 
        trending discussions relevant to Bitcot's seed categories.
        """
        if not self.api_key:
            print("Warning: PERPLEXITY_API_KEY not set. Falling back to static seeds.")
            return [
                {"topic": cat, "is_spike": False, "context": "Fallback static context"}
                for cat in self.seed_categories
            ]

        prompt = f"""
        You are a senior tech industry researcher analyzing the internet right now.
        Bitcot is a software engineering agency targeting Enterprise CTOs.
        
        Search the live web for the last 24-48 hours. Find 3 trending topics or breaking 
        news stories highly relevant to these categories: {', '.join(self.seed_categories)}.
        
        Determine if the topic is a sudden 'spike' in interest (e.g., a massive data breach, a new regulation, a major tech launch) or just a general trend.
        
        You MUST return ONLY valid JSON in this exact format, with no markdown formatting or extra text:
        [
          {{
            "topic": "The specific trending topic (e.g. Hospital System Data Breach due to AI Wrapper)",
            "is_spike": true,
            "context": "2 sentences explaining exactly what happened today and why CTOs care."
          }}
        ]
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar", # Sonar has internet access
            "messages": [
                {"role": "system", "content": "You output only pure JSON arrays."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            content = response.json()["choices"][0]["message"]["content"]
            # Clean up potential markdown formatting
            content = content.replace("```json", "").replace("```", "").strip()
            
            topics = json.loads(content)
            return topics
        except Exception as e:
            print(f"Perplexity API Error: {e}")
            # Fallback
            return [
                {"topic": self.seed_categories[0], "is_spike": False, "context": "Fallback static context"}
            ]

    def select_topic(self, db: Session, mode: str = "scheduled") -> dict:
        """
        Main entry point. Uses Perplexity to select the best topic for today.
        Enforces the 5-day anti-cannibalization window.
        """
        recent_topics = get_recent_topics(db, days=5)
        candidates = self._get_trending_topics()

        for candidate in candidates:
            topic_lower = candidate.get("topic", "").lower()
            
            # Anti-cannibalization check
            is_cannibalized = any(
                topic_lower in recent or recent in topic_lower
                for recent in recent_topics
            )
            
            if not is_cannibalized:
                is_spike = candidate.get("is_spike", False)
                
                # Mode A: only return if it's an acute spike
                if mode == "spike":
                    if is_spike:
                        return {
                            "selected_topic": candidate["topic"],
                            "mode": "Mode A — Spike Detected",
                            "spike_confirmed": True,
                            "context": candidate.get("context", ""),
                            "source": "Perplexity Live Web Search"
                        }
                # Mode B: Scheduled, take the first non-cannibalized topic
                else:
                    return {
                        "selected_topic": candidate["topic"],
                        "mode": "Mode B — Scheduled",
                        "spike_confirmed": is_spike,
                        "context": candidate.get("context", ""),
                        "source": "Perplexity Live Web Search"
                    }

        # Fallback: use first seed keyword if everything was cannibalized or failed
        return {
            "selected_topic": self.seed_categories[0],
            "mode": mode,
            "spike_confirmed": False,
            "context": "Fallback topic used due to cannibalization limits.",
            "source": "fallback_seed"
        }
