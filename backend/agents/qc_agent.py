import os
import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
import redis

# Redis for websockets
r = redis.Redis(host='localhost', port=6379, db=0)

class QCAgent:
    def __init__(self):
        self.model = ChatAnthropic(
            model_name="claude-3-opus-20240229",
            temperature=0.2,
            max_tokens=4000
        )
        
    def _log(self, msg: str):
        print(f"[QC Agent] {msg}")
        try:
            r.publish('agent_logs', json.dumps({"agent": "QC Agent", "message": msg}))
        except:
            pass

    def review_and_revise(self, draft: str, topic: str, tone: str) -> dict:
        self._log(f"Initiating Quality Control review for topic: {topic}")
        
        system_prompt = """You are the QC Agent for Bitcot, acting as both a Devil's Advocate and an SEO/Quality Manager.
Your job is to brutally critique the provided content draft and then rewrite it to fix the issues.

Look for:
1. Fluff: Are there corporate buzzwords (synergy, revolutionize, paradigm shift)?
2. Value: Does it provide concrete, actionable value or just high-level generalizations?
3. SEO/Structure: Are there headers? Are paragraphs short and readable?

You must return a JSON object with two keys:
- "critique": A string summarizing your brutal critique.
- "revised_draft": The final rewritten and improved text.
"""
        
        self._log("Analyzing draft for fluff, structure, and value gaps...")
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Topic: {topic}\nIntended Tone: {tone}\n\nDraft:\n{draft}")
        ]
        
        try:
            response = self.model.invoke(messages)
            
            # Extract JSON block
            text = response.content
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(text)
            
            self._log(f"Critique finished: {result.get('critique', 'Minor adjustments made.')}")
            self._log("Applied revisions successfully.")
            return result
        except Exception as e:
            self._log(f"Error during QC: {str(e)}")
            return {"critique": "QC bypassed due to error.", "revised_draft": draft}
