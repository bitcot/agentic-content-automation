import os
import anthropic
from sqlalchemy.orm import Session

def load_brand_context(db: Session, keys: list[str]) -> dict:
    """Pull specific keys from brand_context table for agent use."""
    from models import BrandContext
    rows = db.query(BrandContext).filter(BrandContext.key.in_(keys)).all()
    return {r.key: r.value for r in rows}

class ICPAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def score_topic(self, topic: str, angle: str = "", db: Session = None) -> dict:
        """
        Score a topic against Bitcot's ICP. Returns score (0.0–1.0) + decision.
        Loads live brand context from memory layer before scoring.
        """
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

        system_prompt = f"""You are Bitcot's ICP Scoring Agent. Your job is to score content topics against our ideal client profile.

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

        try:
            response = self.client.messages.create(
                model="claude-opus-4-7",
                max_tokens=512,
                system=system_prompt,
                messages=[{"role": "user", "content": user_msg}]
            )
            text = response.content[0].text.strip()
            # Extract JSON
            import json, re
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                result = json.loads(m.group())
                return result
            return {"score": 0.5, "decision": "RESHAPE", "reasoning": "Could not parse score.", "persona_match": "unknown", "reshape_suggestion": ""}
        except Exception as e:
            return {"score": 0.5, "decision": "RESHAPE", "reasoning": f"ICP agent error: {str(e)}", "persona_match": "unknown", "reshape_suggestion": ""}

    def enhance_topic(self, topic: str, db: Session = None) -> dict:
        """Takes a basic topic and suggests an ICP-aligned title and angle."""
        ctx = {}
        if db:
            ctx = load_brand_context(db, ["persona_1_cto", "avoid_topics", "vertical_healthcare_ai", "vertical_devops_security"])
            
        system_prompt = f"""You are an expert Content Strategist for Bitcot. 
Your goal is to take a basic, generic topic and enhance it to perfectly align with Bitcot's Ideal Customer Profile (ICP).

Target Personas: {ctx.get("persona_1_cto", "CTO/VP Engineering")}
Avoid: {ctx.get("avoid_topics", "Generic listicles, non-enterprise content")}

Return ONLY a JSON object with this exact structure:
{{
  "enhanced_topic": "<The new, punchy, enterprise-focused topic title>",
  "enhanced_angle": "<1-sentence angle/hook to guide the writer>"
}}
"""
        try:
            response = self.client.messages.create(
                model="claude-opus-4-7",
                max_tokens=256,
                system=system_prompt,
                messages=[{"role": "user", "content": f"Enhance this basic topic: {topic}"}]
            )
            text = response.content[0].text.strip()
            import json, re
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                return json.loads(m.group())
            return {"enhanced_topic": topic, "enhanced_angle": "Focus on enterprise ROI."}
        except Exception as e:
            return {"enhanced_topic": topic, "enhanced_angle": f"Error: {str(e)}"}
