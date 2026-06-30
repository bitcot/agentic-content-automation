import os
import json
import requests
from bs4 import BeautifulSoup
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

class RepurposingAgent:
    def __init__(self):
        self.model = ChatAnthropic(
            model_name="claude-3-opus-20240229",
            temperature=0.3,
            max_tokens=4000
        )
        
    def _log(self, msg: str):
        print(f"[Repurposing Agent] {msg}")
        try:
            r.publish('agent_logs', json.dumps({"agent": "Repurposing Agent", "message": msg}))
        except:
            pass
            
    def fetch_url_content(self, url: str) -> str:
        self._log(f"Fetching content from URL: {url}")
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
            text = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
            return text
        except Exception as e:
            self._log(f"Error fetching URL: {str(e)}")
            return ""

    def repurpose(self, source_text: str, source_url: str = "") -> dict:
        self._log("Initiating content repurposing...")
        
        if source_url and not source_text:
            source_text = self.fetch_url_content(source_url)
            
        if not source_text:
            return {"error": "No source content provided or found."}
            
        system_prompt = """You are an expert content repurposer. 
Take the provided source material and extract the core thesis.
Generate the following:
1. THREE distinct LinkedIn posts (each taking a different angle: e.g., controversial, educational, story-driven).
2. ONE Twitter (X) thread (5-7 tweets) summarizing the main points.

Return your response strictly as a JSON object with this structure:
{
  "linkedin_posts": [
    {"angle": "...", "content": "..."},
    {"angle": "...", "content": "..."},
    {"angle": "...", "content": "..."}
  ],
  "x_thread": ["tweet 1", "tweet 2", "tweet 3", "..."]
}
"""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Source Material:\n{source_text[:15000]}") # Truncate if too long
        ]
        
        self._log("Analyzing source material and generating variations...")
        try:
            response = self.model.invoke(messages)
            text = response.content
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(text)
            self._log("Successfully generated repurposed content.")
            return result
        except Exception as e:
            self._log(f"Repurposing failed: {str(e)}")
            return {"error": str(e)}
