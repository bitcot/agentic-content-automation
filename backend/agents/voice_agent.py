import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from database import SessionLocal
import models
from agents.logger import emit_agent_log

class VoiceAgent:
    def __init__(self):
        self.model_name = "claude-opus-4-7"
        
    def clone_voice(self, sample_text: str, persona_name: str) -> str:
        """
        Analyzes a sample text and extracts the stylistic persona into a rulebook.
        Saves it to the BrandContext database.
        """
        emit_agent_log("VoiceAgent", f"Analyzing sample text to clone persona: {persona_name}")
        
        system_prompt = (
            "You are an expert ghostwriter and linguist. Analyze the following sample text provided by the user. "
            "Extract the exact stylistic DNA of the author. "
            "Identify:\n"
            "- Vocabulary and typical phrases used.\n"
            "- Sentence length and pacing (e.g., short punchy sentences vs long complex ones).\n"
            "- Tone (e.g., authoritative, conversational, contrarian, academic).\n"
            "- Formatting habits (use of line breaks, bullet points, capitalization).\n"
            "Output a concise 'Voice & Tone Rulebook' (bullet points) that will be injected into another AI writer's system prompt "
            "so it can perfectly mimic this author's voice. Do NOT output anything other than the rules."
        )
        
        try:
            chat = ChatAnthropic(
                model=self.model_name,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                max_tokens=1024
            )
            response = chat.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"SAMPLE TEXT:\n\n{sample_text}")
            ])
            
            rulebook = response.content.strip()
            
            # Save to Database
            db = SessionLocal()
            try:
                key_name = f"voice_persona_{persona_name.lower().replace(' ', '_')}"
                bc = db.query(models.BrandContext).filter_by(key=key_name).first()
                if bc:
                    bc.value = rulebook
                else:
                    bc = models.BrandContext(key=key_name, value=rulebook)
                    db.add(bc)
                db.commit()
                emit_agent_log("VoiceAgent", f"Successfully saved persona '{persona_name}' to database.")
                return rulebook
            finally:
                db.close()
                
        except Exception as e:
            emit_agent_log("VoiceAgent", f"Error extracting voice: {e}")
            raise e
