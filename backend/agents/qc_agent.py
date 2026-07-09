import os
import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from agents.logger import emit_agent_log

class QCAgent:
    def __init__(self):
        self.model_name = "claude-3-5-sonnet-20240620"

    def evaluate_draft(self, draft: dict, topic: str) -> dict:
        emit_agent_log("QC Agent", f"Initiating Quality Control review for topic: {topic}")
        emit_agent_log("QC Agent", "Analyzing draft for fluff, structure, and value gaps...")
        
        blog_data = draft.get("blog", {})
        body = blog_data.get("body", "")
        
        # Word count check
        word_count = len(body.split())
        
        system_prompt = """You are the Senior Quality Control Agent for Bitcot's premier blog content.
Your job is to rigorously evaluate a generated blog draft.
A high-quality Bitcot blog MUST have:
1. At least 1,500 words.
2. Deep technical sections (e.g., 'Complete Architecture', 'Implementation Frameworks').
3. At least 2 HTML tables.
4. An H2 section '## Frequently Asked Questions (FAQs)'.
5. An H2 section exactly '## Looking for your premier development partner?' followed by a CTA to /lets-talk/.
6. Zero fluff or generic filler statements.

Evaluate the draft against these criteria. If it fails ANY criterion, set "status" to "rejected" and provide specific "feedback" so the WriterAgent can rewrite it.
Return ONLY valid JSON in this format:
{
  "status": "approved" | "rejected",
  "feedback": "string explaining what needs to be fixed"
}
"""

        user_msg = f"Draft Body:\n{body}\n\nDraft Word Count: {word_count}\n\nEvaluate now."

        try:
            chat = ChatAnthropic(
                model=self.model_name,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                timeout=300.0,
                max_tokens=1024
            )
            response = chat.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_msg)
            ])
            text = response.content.strip()
            
            import re
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                result = json.loads(m.group())
                
                if result.get("status") == "rejected":
                    emit_agent_log("QC Agent", f"QC Failed: {result.get('feedback')}")
                else:
                    emit_agent_log("QC Agent", "QC Passed: Content meets premier standards.")
                    
                return result
            else:
                emit_agent_log("QC Agent", "Failed to parse JSON from QC response")
                return {"status": "rejected", "feedback": "QC Agent failed to output valid JSON"}
        except Exception as e:
            emit_agent_log("QC Agent", f"Error during QC: {str(e)}")
            return {"status": "rejected", "feedback": f"Error during QC: {str(e)}"}
