import os
import json
import re
import anthropic
from sqlalchemy.orm import Session

def load_brand_context(db: Session, keys: list[str]) -> dict:
    """Pull specific keys from brand_context table."""
    from models import BrandContext
    rows = db.query(BrandContext).filter(BrandContext.key.in_(keys)).all()
    return {r.key: r.value for r in rows}

class WriterAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def generate_draft(self, topic: str, icp_result: dict, tone: str = "thought_leader", db: Session = None) -> dict:
        """
        Generate multi-format content (Blog, LinkedIn, X thread).
        Loads all voice rules, approved stats, and format rules from memory layer first.
        """
        # Load rich context from memory layer
        ctx = {}
        if db:
            ctx = load_brand_context(db, [
                "founder",
                "voice_rule_1_hook", "voice_rule_2_brand_mention", "voice_rule_3_paragraphs",
                "voice_rule_4_h2_endings", "voice_rule_5_real_numbers", "voice_rule_6_tone",
                "voice_rule_7_banned_words", "voice_rule_8_blog_cta",
                "voice_rule_9_x_threads", "voice_rule_10_linkedin_url",
                "hook_pattern_a", "hook_pattern_b", "hook_pattern_c", "hook_pattern_d",
                "hook_banned_a", "hook_banned_b", "hook_banned_c",
                "format_linkedin_articles", "format_linkedin_hashtags",
                "format_x_threads", "repost_trigger_pattern",
                "approved_stats_healthcare", "approved_stats_enterprise_ai",
                "approved_stats_digital_transformation", "approved_stats_devops", "approved_stats_ecommerce",
                "seo_service_pages_buried", "seo_internal_link_rule",
                "persona_1_cto", "persona_2_ceo", "persona_3_pm",
                "case_studies", "proof_points",
                "competitor_post_inspiration",
            ])

        persona_match = icp_result.get("persona_match", "CTO/VP Engineering")

        # Build voice rules block
        voice_rules = "\n".join([
            ctx.get("voice_rule_1_hook", ""),
            ctx.get("voice_rule_2_brand_mention", ""),
            ctx.get("voice_rule_3_paragraphs", ""),
            ctx.get("voice_rule_4_h2_endings", ""),
            ctx.get("voice_rule_5_real_numbers", ""),
            ctx.get("voice_rule_6_tone", ""),
            ctx.get("voice_rule_7_banned_words", ""),
            ctx.get("voice_rule_8_blog_cta", ""),
            ctx.get("voice_rule_9_x_threads", ""),
            ctx.get("voice_rule_10_linkedin_url", ""),
        ])

        # Build hook patterns block
        hook_patterns = "\n".join([
            ctx.get("hook_pattern_a", ""),
            ctx.get("hook_pattern_b", ""),
            ctx.get("hook_pattern_c", ""),
            ctx.get("hook_pattern_d", ""),
        ])

        # Build approved stats block
        approved_stats = "\n".join([
            ctx.get("approved_stats_healthcare", ""),
            ctx.get("approved_stats_enterprise_ai", ""),
            ctx.get("approved_stats_digital_transformation", ""),
            ctx.get("approved_stats_devops", ""),
            ctx.get("approved_stats_ecommerce", ""),
        ])

        # SEO internal linking rule
        seo_rule = ctx.get("seo_internal_link_rule", "")
        buried_pages = ctx.get("seo_service_pages_buried", "")

        # Case studies for reference
        case_studies = ctx.get("case_studies", "")

        system_prompt = f"""You are ghostwriting content for Raj Sanghvi, Founder of Bitcot Technology.
{ctx.get("founder", "Voice: confident, direct, founder who has seen things go wrong many times.")}

You will produce THREE pieces of content for the same topic: a Blog Post, a LinkedIn Post, and an X Thread.

═══ VOICE RULES — NON-NEGOTIABLE ═══
{voice_rules}

═══ COMPETITOR INSPIRATION (Successful Post Structures to Model) ═══
{ctx.get("competitor_post_inspiration", "")}

═══ WINNING HOOK PATTERNS (use one of these) ═══
{hook_patterns}

═══ BANNED HOOKS (reject and rewrite if you find yourself using these) ═══
{ctx.get("hook_banned_a", "")}
{ctx.get("hook_banned_b", "")}
{ctx.get("hook_banned_c", "")}

═══ APPROVED STATS LIBRARY (use freely — already verified) ═══
{approved_stats}

═══ TARGET PERSONA FOR THIS PIECE ═══
{persona_match}

═══ REAL CASE STUDIES YOU CAN REFERENCE ═══
{case_studies}

═══ SEO INTERNAL LINKING (for blog post only) ═══
{seo_rule}
Service pages to link to: {buried_pages}

═══ HALLUCINATION RULE ═══
Any statistic NOT in the approved stats library above MUST be tagged: [NEEDS HUMAN CHECK: describe what to verify]

═══ OUTPUT FORMAT ═══
Return ONLY valid JSON with this exact structure:
{{
  "blog": {{
    "title": "...",
    "meta_description": "...",
    "body": "...",
    "seo_keywords": ["keyword1", "keyword2", "keyword3"],
    "internal_links": ["service page 1", "service page 2"],
    "word_count": <integer>
  }},
  "linkedin": {{
    "post": "...",
    "hook_pattern_used": "A|B|C|D",
    "hashtags": ["#tag1", "#tag2", "#tag3"],
    "first_comment": "Blog link: https://www.bitcot.com/blog/[slug]",
    "estimated_engagement": "..."
  }},
  "x_thread": {{
    "tweets": ["tweet 1 hook", "tweet 2", "tweet 3", "tweet 4", "tweet 5", "tweet 6 DM hook"],
    "dm_keyword": "KEYWORD_IN_CAPS"
  }},
  "needs_human_check": <true|false>,
  "check_flags": ["list of [NEEDS HUMAN CHECK] items found"]
}}

CRITICAL: Maximum 3 hashtags on LinkedIn. Blog URL never in LinkedIn post body — it goes in first_comment only."""

        user_msg = f"""Topic: {topic}
ICP Score: {icp_result.get('score', 0.7):.2f}
Persona: {persona_match}
Tone: {tone}
ICP Reasoning: {icp_result.get('reasoning', '')}

Generate the full Blog + LinkedIn + X Thread now."""

        try:
            response = self.client.messages.create(
                model="claude-opus-4-7",
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_msg}]
            )
            text = response.content[0].text.strip()

            # Extract JSON
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                result = json.loads(m.group())
                # Enforce: scan for untagged stats
                blog_body = result.get("blog", {}).get("body", "")
                li_post = result.get("linkedin", {}).get("post", "")
                check_flags = result.get("check_flags", [])

                return {
                    "topic": topic,
                    "icp_score": icp_result.get("score", 0.0),
                    "persona_match": persona_match,
                    "blog": result.get("blog", {}),
                    "linkedin": result.get("linkedin", {}),
                    "x_thread": result.get("x_thread", {}),
                    "needs_human_check": result.get("needs_human_check", True),
                    "check_flags": check_flags,
                    "status": "pending_review",
                }
            else:
                raise ValueError("No JSON found in Claude response")

        except json.JSONDecodeError as e:
            return {
                "topic": topic,
                "icp_score": icp_result.get("score", 0.0),
                "persona_match": persona_match,
                "blog": {"title": topic, "body": text, "meta_description": "", "seo_keywords": [], "internal_links": [], "word_count": 0},
                "linkedin": {"post": "", "hook_pattern_used": "", "hashtags": [], "first_comment": "", "estimated_engagement": ""},
                "x_thread": {"tweets": [], "dm_keyword": ""},
                "needs_human_check": True,
                "check_flags": [f"JSON parse error: {str(e)}"],
                "status": "pending_review",
            }
        except Exception as e:
            raise RuntimeError(f"WriterAgent error: {str(e)}")
