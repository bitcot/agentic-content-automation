import os
import re
import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from sqlalchemy.orm import Session
from agents.logger import emit_agent_log

def load_brand_context(db: Session, keys: list[str]) -> dict:
    """Pull specific keys from brand_context table for agent use."""
    from models import BrandContext
    rows = db.query(BrandContext).filter(BrandContext.key.in_(keys)).all()
    return {r.key: r.value for r in rows}

class ICPAgent:
    def __init__(self):
        self.model_name = "claude-3-5-sonnet-20241022"

    def score_topic(self, topic: str, angle: str = "", target_persona: str = "", db: Session = None) -> dict:
        """
        Score a topic against Bitcot's ICP. Returns score (0.0–1.0) + decision.
        Loads live brand context from memory layer before scoring.
        Uses LangChain ChatAnthropic for completion.
        """
        emit_agent_log("ICPAgent", f"Evaluating topic: '{topic}' for ICP alignment.", {"angle": angle})

        # Pull relevant context from memory layer
        ctx = {}
        if db:
            ctx = load_brand_context(db, [
                "persona_1_cto", "persona_2_ceo", "persona_3_pm",
                "icp_geography", "icp_geo_problem", "icp_score_threshold",
                "vertical_healthcare_ai", "vertical_devops_security",
                "vertical_digital_transformation", "vertical_ai_roi",
                "matrix_q2_double_down", "matrix_q3_rethink",
                "hook_banned_a", "hook_banned_b", "hook_banned_c",
                "avoid_topics", "competitors_direct",
            ])

        # Build system prompt from live memory
        personas_block = "\n".join([
            ctx.get("persona_1_cto", "CTO/VP Engineering — primary target."),
            ctx.get("persona_2_ceo", "CEO/Founder — high-value decision maker."),
            ctx.get("persona_3_pm", "Product Manager — researcher before decision."),
        ])
        
        if target_persona:
            personas_block += f"\n\nCRITICAL OVERRIDE: The user has explicitly specified a custom persona for this generation: '{target_persona}'. You MUST accept this persona as a high-value target and score the topic based on how well it appeals to '{target_persona}', ignoring if it doesn't match the default 3 personas."

        # Read playbook
        playbook_path = os.path.join(os.path.dirname(__file__), "content_playbook.txt")
        playbook_content = ""
        if os.path.exists(playbook_path):
            with open(playbook_path, "r", encoding="utf-8") as f:
                playbook_content = f.read()

        system_prompt = f"""You are Bitcot's ICP Scoring Agent. Your job is to score content topics against our ideal client profile.

=== CONTENT WRITING FOUNDATIONS PLAYBOOK ===
{playbook_content}

=== IDEAL PERSONAS ===
{personas_block}

=== GEOGRAPHY RULE ===
{ctx.get("icp_geo_problem", "USA is the target. India traffic does not convert.")}

=== HIGH-VALUE VERTICALS (score higher) ===
{ctx.get("vertical_healthcare_ai", "")}
{ctx.get("vertical_devops_security", "")}
{ctx.get("vertical_digital_transformation", "")}
{ctx.get("vertical_ai_roi", "")}

=== TOPICS TO REJECT ===
{ctx.get("avoid_topics", "India-focused outsourcing, generic listicles, non-enterprise content.")}
{ctx.get("matrix_q3_rethink", "Low engagement + low conversion topics.")}

=== BROAD SOFTWARE ICP RULES (CRITICAL) ===
1. We are a software development company. High-value topics include NOT ONLY CTO decision pieces, but also:
   - General tech trending news (e.g. LangChain events, AI breakthroughs, new frontend frameworks).
   - Developer-focused insights or pain points.
   - Product Manager strategy pieces.
2. DO NOT reject event recaps or trending software topics just because they lack "CTO-specific pain points". These serve as excellent top-of-funnel brand awareness content.
3. Only reject topics that are entirely unrelated to software engineering, tech, AI, or B2B business.

=== BANNED HOOKS (reject if topic only works with these) ===
{ctx.get("hook_banned_a", "")}
{ctx.get("hook_banned_b", "")}
{ctx.get("hook_banned_c", "")}

=== SCORING INSTRUCTIONS ===
Return ONLY a JSON object with these exact fields:
{{
  "score": <float 0.0 to 1.0>,
  "decision": "<PASS|RESHAPE|REJECT>",
  "persona_match": "<which persona this best serves>",
  "reasoning": "<1-2 sentences why>",
  "reshape_suggestion": "<if RESHAPE, what angle would make it ICP-matched>"
}}

Score above 0.65 = PASS (enters pipeline).
Score 0.5-0.65 = RESHAPE (reframe the angle).
Score below 0.5 = REJECT (blocked for 7 days).
"""

        user_msg = f"Topic: {topic}"
        if angle:
            user_msg += f"\nProposed angle: {angle}"
        if target_persona:
            user_msg += f"\nTarget Persona: {target_persona}"

        try:
            chat = ChatAnthropic(
                model=self.model_name,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                timeout=120.0,
                max_tokens=512
            )
            response = chat.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_msg)
            ])
            text = response.content.strip()

            # Extract JSON
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                result = json.loads(m.group())
                return result
            return {"score": 0.5, "decision": "RESHAPE", "reasoning": "Could not parse score.", "persona_match": "unknown", "reshape_suggestion": ""}
        except Exception as e:
            return {"score": 0.5, "decision": "RESHAPE", "reasoning": f"ICP agent error: {str(e)}", "persona_match": "unknown", "reshape_suggestion": ""}

    def enhance_topic(self, topic: str, angle: str = "", target_persona: str = "", direction: str = "", image_idea: str = "", db: Session = None) -> dict:
        """Takes a basic topic and suggests a highly creative, ICP-aligned title and angle."""
        ctx = {}
        if db:
            ctx = load_brand_context(db, ["persona_1_cto", "avoid_topics", "vertical_healthcare_ai", "vertical_devops_security"])
            
        # Read playbook
        playbook_path = os.path.join(os.path.dirname(__file__), "content_playbook.txt")
        playbook_content = ""
        if os.path.exists(playbook_path):
            with open(playbook_path, "r", encoding="utf-8") as f:
                playbook_content = f.read()

        system_prompt = f"""You are an elite, highly creative Content Strategist for Bitcot. 
Your goal is to take a basic, generic topic and enhance it into a punchy, unique, and deeply contrarian or highly specific enterprise topic.

=== CONTENT WRITING FOUNDATIONS PLAYBOOK ===
{playbook_content}

CRITICAL INSTRUCTION: Avoid formulaic patterns. Do NOT just output "Unlocking ROI in Enterprise AI" every time. Be wildly creative, specific, and provocative while still targeting our ICP.
If the user provides an 'angle' or opinion, you MUST amplify and build upon that specific angle rather than falling back to generic data.
If the user provides a 'direction' for enhancement, you MUST aggressively steer the topic, angle, and image idea toward that exact direction.

Target Personas: {target_persona if target_persona else ctx.get("persona_1_cto", "CTO/VP Engineering")}
Avoid: {ctx.get("avoid_topics", "Generic listicles, non-enterprise content")}

Return ONLY a JSON object with this exact structure:
{{
  "enhanced_topic": "<A highly unique, punchy, non-formulaic enterprise-focused topic title>",
  "enhanced_angle": "<1-2 sentence controversial or specific hook/angle building on the user's input>",
  "enhanced_image_idea": "<A highly detailed image idea building on the user's input, optimized for the direction>"
}}
"""
        user_msg = f"Enhance this basic topic: {topic}"
        if angle:
            user_msg += f"\nUser's proposed angle/opinion to amplify: {angle}"
        if direction:
            user_msg += f"\nSpecific Direction from user (MUST FOLLOW): {direction}"
        if image_idea:
            user_msg += f"\nOriginal Image Idea: {image_idea}"

        try:
            chat = ChatAnthropic(
                model=self.model_name,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                timeout=120.0,
                max_tokens=350
            )
            response = chat.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_msg)
            ])
            text = response.content.strip()

            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                return json.loads(m.group())
            return {"enhanced_topic": topic, "enhanced_angle": "Focus on highly specific enterprise applications.", "enhanced_image_idea": image_idea}
        except Exception as e:
            return {"enhanced_topic": topic, "enhanced_angle": f"Error: {str(e)}", "enhanced_image_idea": image_idea}
